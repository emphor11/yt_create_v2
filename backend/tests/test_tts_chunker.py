import pytest
from domain.tts_chunk import TTSChunk
from engines.tts_chunker import TTSChunker


def test_chunker_initialization_guardrails():
    # Valid configurations
    chunker = TTSChunker(safe_max_chars=2200)
    assert chunker.safe_max_chars == 2200

    chunker_custom = TTSChunker(safe_max_chars=1500)
    assert chunker_custom.safe_max_chars == 1500

    # Invalid configurations
    with pytest.raises(ValueError, match="positive integer"):
        TTSChunker(safe_max_chars=0)

    with pytest.raises(ValueError, match="positive integer"):
        TTSChunker(safe_max_chars=-100)

    with pytest.raises(ValueError, match="cannot exceed the absolute limit"):
        TTSChunker(safe_max_chars=3000)


def test_short_scene_preserved_as_single_chunk():
    chunker = TTSChunker(safe_max_chars=2200)
    text = "Most corporate professionals trade their best hours for a paycheck, only to realize the trap too late."
    chunks = chunker.chunk_sections([("hook", text)])

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.chunk_id == "chunk_001"
    assert chunk.source_id == "hook"
    assert chunk.sequence == 1
    assert chunk.text == text
    assert chunk.char_count == len(text)


def test_standard_multi_scene_script_preserves_idea_boundaries():
    chunker = TTSChunker(safe_max_chars=2200)
    sections = [
        ("hook", "This is the hook narration. It runs for approximately forty words and hooks the viewer."),
        ("idea_01", "Here is idea number one. It introduces the core problem and explains why salaries do not keep up with inflation."),
        ("idea_02", "Idea number two delves into the compounding effect of index funds versus high-interest debt."),
        ("idea_03", "Idea number three outlines the four-step exit blueprint for employees wanting financial autonomy."),
    ]

    chunks = chunker.chunk_sections(sections)

    # Each section is well under 2,200 chars, so each gets exactly 1 chunk
    assert len(chunks) == 4
    for idx, (source_id, text) in enumerate(sections, start=1):
        chunk = chunks[idx - 1]
        assert chunk.chunk_id == f"chunk_{idx:03d}"
        assert chunk.source_id == source_id
        assert chunk.sequence == idx
        assert chunk.text == text
        assert chunk.char_count == len(text)


def test_long_scene_splits_on_paragraph_boundaries():
    chunker = TTSChunker(safe_max_chars=200)
    para1 = "Paragraph 1 discusses the macroeconomic conditions of 2024. Inflation remained sticky while rates stayed elevated."
    para2 = "Paragraph 2 explores corporate hiring freezes and the impact on junior developers across tech hubs worldwide."
    para3 = "Paragraph 3 concludes with actionable strategies for building independent income streams in uncertain times."

    full_text = f"{para1}\n\n{para2}\n\n{para3}"
    assert len(full_text) > 200  # Will trigger split

    chunks = chunker.chunk_sections([("idea_01", full_text)])

    # Verify every chunk is <= safe_max_chars
    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.char_count <= 200
        assert chunk.source_id == "idea_01"

    # Verify all words are preserved verbatim
    reconstructed_words = " ".join(c.text for c in chunks).split()
    assert reconstructed_words == full_text.split()


def test_long_paragraph_splits_on_sentences():
    chunker = TTSChunker(safe_max_chars=250)
    s1 = "The first quarter showed remarkable consumer resilience despite rising interest rates."
    s2 = "However, household debt reached an all-time high of seventeen trillion dollars."
    s3 = "Credit card delinquency rates jumped significantly among younger demographics."
    s4 = "Economists now predict a slowdown in consumer spending over the coming quarters."

    long_para = f"{s1} {s2} {s3} {s4}"
    assert len(long_para) > 250

    chunks = chunker.chunk_sections([("idea_02", long_para)])

    assert len(chunks) >= 2
    for chunk in chunks:
        assert chunk.char_count <= 250
        # Should end with a sentence terminator
        assert chunk.text[-1] in {".", "!", "?"}

    # Zero word loss or mutation
    assert " ".join(c.text for c in chunks).split() == long_para.split()


def test_abbreviations_and_decimals_not_split_prematurely():
    chunker = TTSChunker(safe_max_chars=180)
    text = (
        "The U.S. Federal Reserve held benchmark rates at 5.25%, Dr. Powell announced yesterday. "
        "Meanwhile, Q3 GDP grew by 3.2% across North America."
    )

    # If U.S., 5.25%, Dr., or 3.2% were treated as sentence breaks, it would chop mid-phrase
    chunks = chunker.chunk_sections([("news", text)])

    for chunk in chunks:
        assert chunk.char_count <= 180
        # Ensure abbreviations and decimals weren't broken
        if "U.S." in chunk.text:
            assert "U.S. Federal Reserve" in chunk.text
        if "5.25%" in chunk.text:
            assert "5.25%" in chunk.text
        if "Dr." in chunk.text:
            assert "Dr. Powell" in chunk.text
        if "3.2%" in chunk.text:
            assert "3.2%" in chunk.text

    assert " ".join(c.text for c in chunks).split() == text.split()


def test_semicolon_and_colon_splitting():
    chunker = TTSChunker(safe_max_chars=150)
    clause1 = "The initial investment required substantial capital"
    clause2 = "the operational costs exceeded initial estimates"
    clause3 = "and market adoption was slower than projected in Q1"

    long_sentence = f"{clause1}; {clause2}: {clause3}."
    assert len(long_sentence) > 150

    chunks = chunker.chunk_sections([("analysis", long_sentence)])

    for chunk in chunks:
        assert chunk.char_count <= 150

    assert " ".join(c.text for c in chunks).split() == long_sentence.split()


def test_comma_clause_splitting():
    chunker = TTSChunker(safe_max_chars=120)
    clause1 = "When analyzing real estate yields in high-interest environments"
    clause2 = "investors often forget about property taxes and maintenance"
    clause3 = "which drastically reduces the actual net return"

    sentence_with_commas = f"{clause1}, {clause2}, {clause3}."
    assert len(sentence_with_commas) > 120

    chunks = chunker.chunk_sections([("real_estate", sentence_with_commas)])

    for chunk in chunks:
        assert chunk.char_count <= 120

    assert " ".join(c.text for c in chunks).split() == sentence_with_commas.split()


def test_unbroken_giant_string_fallback():
    chunker = TTSChunker(safe_max_chars=100)
    # 250 characters with no punctuation or whitespace
    giant_unbroken = "X" * 250

    chunks = chunker.chunk_sections([("fallback", giant_unbroken)])

    assert len(chunks) == 3
    assert chunks[0].char_count == 100
    assert chunks[1].char_count == 100
    assert chunks[2].char_count == 50

    reconstructed = "".join(c.text for c in chunks)
    assert reconstructed == giant_unbroken


def test_sequence_numbering_across_multiple_sections():
    chunker = TTSChunker(safe_max_chars=100)
    s1 = "Short section one."
    s2 = "A slightly longer section two that will definitely exceed one hundred characters and need to be split into two separate chunks."
    s3 = "Short section three."

    chunks = chunker.chunk_sections([("s1", s1), ("s2", s2), ("s3", s3)])

    # Check strict 1-indexed sequential order
    sequences = [c.sequence for c in chunks]
    assert sequences == list(range(1, len(chunks) + 1))

    # Check chunk_id format
    for idx, c in enumerate(chunks, start=1):
        assert c.chunk_id == f"chunk_{idx:03d}"


def test_user_exact_example_preserves_period_and_percentage():
    """
    Explicit invariant test verifying the user's specific test case:
    'The market rose 3.2% in January. Investors became optimistic.'
    Guarantees:
    - Period '.' is never stripped or lost.
    - Percentage '3.2%' is never chopped into '3.2' and '%'.
    - Round-trip reconstruction matches the original source text exactly.
    """
    original = "The market rose 3.2% in January. Investors became optimistic."

    # Max chars 40 forces split between the two sentences (32 chars and 28 chars)
    chunker = TTSChunker(safe_max_chars=40)
    chunks = chunker.chunk_text(original, source_id="idea_01")

    assert len(chunks) == 2

    # Chunk 1 must retain the exact period and 3.2%
    assert chunks[0].text == "The market rose 3.2% in January."
    assert chunks[0].text.endswith(".")
    assert "3.2%" in chunks[0].text

    # Chunk 2 must retain the exact period
    assert chunks[1].text == "Investors became optimistic."
    assert chunks[1].text.endswith(".")

    # Exact round-trip reconstruction matches original character-for-character
    reconstructed = TTSChunker.reconstruct_text(chunks)
    assert reconstructed == original
    assert " ".join(c.text for c in chunks) == original


def test_quotes_sentence_boundary_exact_round_trip():
    """
    Verifies that sentences ending in quotation marks retain both the terminal
    punctuation and the closing quote without dropping characters.
    """
    original = 'The analyst warned, "Expect market turbulence." Retail traders ignored the advice.'

    chunker = TTSChunker(safe_max_chars=55)
    chunks = chunker.chunk_text(original, source_id="idea_02")

    assert len(chunks) == 2
    assert chunks[0].text == 'The analyst warned, "Expect market turbulence."'
    assert chunks[0].text.endswith('."')

    assert chunks[1].text == "Retail traders ignored the advice."
    assert chunks[1].text.endswith(".")

    reconstructed = TTSChunker.reconstruct_text(chunks)
    assert reconstructed == original


def test_multi_clause_round_trip_preserves_all_punctuation():
    """
    Verifies that clause-level comma splits preserve all commas and words exactly.
    """
    original = "When interest rates rise, borrowing costs escalate, and corporate valuations compress."

    chunker = TTSChunker(safe_max_chars=35)
    chunks = chunker.chunk_text(original, source_id="idea_03")

    assert len(chunks) >= 3
    # Check that commas are preserved on the split chunks
    assert chunks[0].text.endswith(",")
    assert chunks[1].text.endswith(",")
    assert chunks[-1].text.endswith(".")

    # Exact round-trip reconstruction
    assert " ".join(c.text for c in chunks) == original

