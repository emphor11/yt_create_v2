import pytest
from domain.hook import Hook, VisualDirective as HookVisualDirective
from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea, VisualStrategyBeat
from domain.voice_track import VoiceTrack, WordTimestamp
from engines.video_assembly.timeline_builder import (
    TimelineBuilder,
    TimelineBuilderError,
    _compute_section_byte_spans,
    _find_section_for_byte_offset,
    _assign_words_to_sections,
)


# =========================================================================
# Test 1: User Instruction 1 - Section-2 words immediately after "\n\n"
# are NEVER accidentally assigned to Section 1
# =========================================================================
def test_section_2_words_immediately_after_double_newline_never_assigned_to_section_1():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Hook intro.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="First idea ends.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="b1_1", preferred_component="Typography", visual_goal="G1", trigger_word=None),
                ],
            ),
            VideoIdea(
                idea_id="idea_02",
                title="Idea 2",
                focus_concept="C2",
                core_teaching_point="P2",
                narration="Second idea begins.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="b2_1", preferred_component="Typography", visual_goal="G2", trigger_word=None),
                    VisualStrategyBeat(beat_id="b2_2", preferred_component="Typography", visual_goal="G3", trigger_word="begins"),
                ],
            ),
        ],
    )

    full_script = "Hook intro.\n\nFirst idea ends.\n\nSecond idea begins."
    full_bytes = full_script.encode("utf-8")

    # Byte ranges:
    # Hook: "Hook intro." -> [0, 11)
    # Idea 1: "First idea ends." -> [13, 29)
    # Idea 2: "Second idea begins." -> [31, 50)
    sec_0_start = full_bytes.find(b"Hook intro.")
    sec_1_start = full_bytes.find(b"First idea ends.")
    sec_2_start = full_bytes.find(b"Second idea begins.")

    assert sec_0_start == 0
    assert sec_1_start == 13
    assert sec_2_start == 31

    # Word timestamps with exact byte offsets
    word_timestamps = [
        # Hook
        WordTimestamp(word="Hook", start_ms=0, end_ms=300, start_char=0, end_char=4),
        WordTimestamp(word="intro", start_ms=300, end_ms=600, start_char=5, end_char=10),
        # Idea 1
        WordTimestamp(word="First", start_ms=1000, end_ms=1300, start_char=13, end_char=18),
        WordTimestamp(word="idea", start_ms=1300, end_ms=1600, start_char=19, end_char=23),
        WordTimestamp(word="ends", start_ms=1600, end_ms=1900, start_char=24, end_char=28),
        # Idea 2 (immediately after "\n\n", start_char=31)
        WordTimestamp(word="Second", start_ms=2500, end_ms=2800, start_char=31, end_char=37),
        WordTimestamp(word="idea", start_ms=2800, end_ms=3100, start_char=38, end_char=42),
        WordTimestamp(word="begins", start_ms=3100, end_ms=3500, start_char=43, end_char=49),
    ]

    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=4.0,
        full_script_text=full_script,
        word_timestamps=word_timestamps,
    )

    section_texts = ["Hook intro.", "First idea ends.", "Second idea begins."]
    section_ids = ["hook", "idea_01", "idea_02"]
    assigned = _assign_words_to_sections(section_texts, section_ids, vt)

    # Verify Section 0 (Hook)
    assert [w.word for w in assigned[0]] == ["Hook", "intro"]
    # Verify Section 1 (Idea 1)
    assert [w.word for w in assigned[1]] == ["First", "idea", "ends"]
    # Verify Section 2 (Idea 2): "Second" MUST be in Section 2, NEVER in Section 1!
    assert [w.word for w in assigned[2]] == ["Second", "idea", "begins"]

    # Verify timeline builds cleanly and trigger word in Section 2 resolves
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 4
    assert timeline[3].beat_id == "b2_2"


# =========================================================================
# Test 2: User Instruction 2 - Chunk-Source Mapping Fallthrough
# Only use chunk-source mapping when source_id is valid and matches a known section;
# otherwise fall through to byte-range mapping.
# =========================================================================
def test_chunk_source_fallback_to_byte_range_mapping_when_source_id_generic():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="Valuation reached $450B.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="Investors rejoiced.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="b1_1", preferred_component="Typography", visual_goal="G1", trigger_word=None),
                    VisualStrategyBeat(beat_id="b1_2", preferred_component="Typography", visual_goal="G2", trigger_word="rejoiced"),
                ],
            )
        ],
    )

    full_script = "Valuation reached $450B.\n\nInvestors rejoiced."
    # $450B expands into four hundred fifty billion (4 Polly words for 1 source word)
    word_timestamps = [
        # Hook words
        WordTimestamp(word="Valuation", start_ms=0, end_ms=300, start_char=0, end_char=9),
        WordTimestamp(word="reached", start_ms=300, end_ms=600, start_char=10, end_char=17),
        WordTimestamp(word="four", start_ms=600, end_ms=800, start_char=18, end_char=23),
        WordTimestamp(word="hundred", start_ms=800, end_ms=1000, start_char=18, end_char=23),
        WordTimestamp(word="fifty", start_ms=1000, end_ms=1200, start_char=18, end_char=23),
        WordTimestamp(word="billion", start_ms=1200, end_ms=1400, start_char=18, end_char=23),
        # Idea 1 words (offset 26 onwards)
        WordTimestamp(word="Investors", start_ms=1800, end_ms=2200, start_char=26, end_char=35),
        WordTimestamp(word="rejoiced", start_ms=2200, end_ms=2700, start_char=36, end_char=44),
    ]

    # Chunks have generic source_id="narration" (single-chunk synthesis provider)
    chunks = [
        {
            "chunk_id": "chunk_001",
            "sequence": 1,
            "source_id": "narration",  # NOT "hook" or "idea_01" -> must fall through!
            "word_timestamps": [{"word": w.word} for w in word_timestamps],
        }
    ]

    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=3.0,
        full_script_text=full_script,
        word_timestamps=word_timestamps,
        chunks=chunks,
    )

    section_texts = ["Valuation reached $450B.", "Investors rejoiced."]
    section_ids = ["hook", "idea_01"]

    # Even though chunks is present, source_id="narration" is not in section_ids,
    # so it falls through to Strategy 2 (byte-range mapping).
    assigned = _assign_words_to_sections(section_texts, section_ids, vt)

    # Hook receives all 6 words (Valuation, reached, four, hundred, fifty, billion)
    assert len(assigned[0]) == 6
    assert [w.word for w in assigned[0]] == ["Valuation", "reached", "four", "hundred", "fifty", "billion"]
    # Idea 1 receives Investors and rejoiced
    assert len(assigned[1]) == 2
    assert [w.word for w in assigned[1]] == ["Investors", "rejoiced"]

    # Verify timeline builds successfully
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 3


def test_chunk_source_mapping_used_when_source_ids_match_known_sections():
    # When chunks have valid and known source_ids ("hook", "idea_01"),
    # chunk-source mapping is directly utilized.
    chunks = [
        {
            "chunk_id": "chunk_001",
            "sequence": 1,
            "source_id": "hook",
            "word_timestamps": [
                {"word": "Hook", "start_char": 0, "end_char": 4},
                {"word": "one", "start_char": 5, "end_char": 8},
            ],
        },
        {
            "chunk_id": "chunk_002",
            "sequence": 2,
            "source_id": "idea_01",
            "word_timestamps": [
                {"word": "Idea", "start_char": 0, "end_char": 4},
                {"word": "two", "start_char": 5, "end_char": 8},
            ],
        },
    ]
    word_timestamps = [
        WordTimestamp(word="Hook", start_ms=0, end_ms=300),
        WordTimestamp(word="one", start_ms=300, end_ms=600),
        WordTimestamp(word="Idea", start_ms=1000, end_ms=1300),
        WordTimestamp(word="two", start_ms=1300, end_ms=1600),
    ]
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=2.0,
        full_script_text="Hook one.\n\nIdea two.",
        word_timestamps=word_timestamps,
        chunks=chunks,
    )

    section_texts = ["Hook one.", "Idea two."]
    section_ids = ["hook", "idea_01"]
    assigned = _assign_words_to_sections(section_texts, section_ids, vt)

    assert [w.word for w in assigned[0]] == ["Hook", "one"]
    assert [w.word for w in assigned[1]] == ["Idea", "two"]
    # Verify chunk-local start_char was preserved
    assert assigned[0][0].start_char == 0
    assert assigned[1][0].start_char == 0


# =========================================================================
# Test 3: Currency expansion ($450B -> four hundred fifty billion) does NOT
# spill over into the next section
# =========================================================================
def test_currency_expansion_does_not_shift_next_section_words():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="$450B caused concern",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="Investors panicked yesterday.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="b1_1", preferred_component="Typography", visual_goal="G1", trigger_word=None),
                    VisualStrategyBeat(beat_id="b1_2", preferred_component="Typography", visual_goal="G2", trigger_word="panicked"),
                ],
            )
        ],
    )

    full_script = "$450B caused concern\n\nInvestors panicked yesterday."
    # Source text byte positions:
    # "$450B caused concern": [0, 20)
    # "Investors panicked yesterday.": [22, 51)
    word_timestamps = [
        # Hook words (6 Polly words for 3 Python words)
        WordTimestamp(word="four", start_ms=0, end_ms=200, start_char=0, end_char=5),
        WordTimestamp(word="hundred", start_ms=200, end_ms=400, start_char=0, end_char=5),
        WordTimestamp(word="fifty", start_ms=400, end_ms=600, start_char=0, end_char=5),
        WordTimestamp(word="billion", start_ms=600, end_ms=800, start_char=0, end_char=5),
        WordTimestamp(word="caused", start_ms=800, end_ms=1100, start_char=6, end_char=12),
        WordTimestamp(word="concern", start_ms=1100, end_ms=1400, start_char=13, end_char=20),
        # Idea 1 words
        WordTimestamp(word="Investors", start_ms=1800, end_ms=2200, start_char=22, end_char=31),
        WordTimestamp(word="panicked", start_ms=2400, end_ms=2800, start_char=32, end_char=40),
        WordTimestamp(word="yesterday", start_ms=2800, end_ms=3200, start_char=41, end_char=50),
    ]

    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=3.5,
        full_script_text=full_script,
        word_timestamps=word_timestamps,
    )

    section_texts = ["$450B caused concern", "Investors panicked yesterday."]
    section_ids = ["hook", "idea_01"]
    assigned = _assign_words_to_sections(section_texts, section_ids, vt)

    # In the old text.split() approach:
    # Hook had 3 words ("$450B", "caused", "concern"), so assigned[0] took ["four", "hundred", "fifty"]
    # and ["billion", "caused", "concern"] leaked into Idea 1!
    # In the new robust byte-range mapping:
    assert len(assigned[0]) == 6
    assert [w.word for w in assigned[0]] == ["four", "hundred", "fifty", "billion", "caused", "concern"]
    assert len(assigned[1]) == 3
    assert [w.word for w in assigned[1]] == ["Investors", "panicked", "yesterday"]

    # Verify timeline builder resolves trigger word "panicked" in Idea 1 accurately
    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 3
    # Idea 1 beat 2 trigger "panicked" starts at 2400ms -> frame 72 (Beat 1 has frames 54..72 >= 15 frames)
    assert timeline[2].beat_id == "b1_2"
    assert timeline[2].start_frame == 72


# =========================================================================
# Test 4: Regression test - Compound/numeric expression occurring IMMEDIATELY
# before an idea boundary
# =========================================================================
def test_numeric_expression_immediately_before_idea_boundary():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="The rate rose 3.2%",  # "3.2%" is the very last token in Hook!
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="Investors cheered loudly.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="b1_1", preferred_component="Typography", visual_goal="G1", trigger_word=None),
                    VisualStrategyBeat(beat_id="b1_2", preferred_component="Typography", visual_goal="G2", trigger_word="cheered"),
                ],
            )
        ],
    )

    full_script = "The rate rose 3.2%\n\nInvestors cheered loudly."
    # "The rate rose 3.2%" -> [0, 18)
    # "Investors cheered loudly." -> [20, 45)
    word_timestamps = [
        # Hook words: "3.2%" expands into "three", "point", "two", "percent"
        WordTimestamp(word="The", start_ms=0, end_ms=200, start_char=0, end_char=3),
        WordTimestamp(word="rate", start_ms=200, end_ms=400, start_char=4, end_char=8),
        WordTimestamp(word="rose", start_ms=400, end_ms=600, start_char=9, end_char=13),
        WordTimestamp(word="three", start_ms=600, end_ms=800, start_char=14, end_char=18),
        WordTimestamp(word="point", start_ms=800, end_ms=1000, start_char=14, end_char=18),
        WordTimestamp(word="two", start_ms=1000, end_ms=1200, start_char=14, end_char=18),
        WordTimestamp(word="percent", start_ms=1200, end_ms=1400, start_char=14, end_char=18),
        # Idea 1 words (starts at byte 20)
        WordTimestamp(word="Investors", start_ms=1800, end_ms=2100, start_char=20, end_char=29),
        WordTimestamp(word="cheered", start_ms=2400, end_ms=2800, start_char=30, end_char=37),
        WordTimestamp(word="loudly", start_ms=2800, end_ms=3100, start_char=38, end_char=44),
    ]

    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=3.2,
        full_script_text=full_script,
        word_timestamps=word_timestamps,
    )

    section_texts = ["The rate rose 3.2%", "Investors cheered loudly."]
    section_ids = ["hook", "idea_01"]
    assigned = _assign_words_to_sections(section_texts, section_ids, vt)

    # Hook receives all 7 words including the 4 expanded tokens for "3.2%"
    assert len(assigned[0]) == 7
    assert [w.word for w in assigned[0]] == ["The", "rate", "rose", "three", "point", "two", "percent"]
    # Idea 1 receives exactly its 3 words, starting with "Investors"
    assert len(assigned[1]) == 3
    assert [w.word for w in assigned[1]] == ["Investors", "cheered", "loudly"]

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 3
    # Trigger "cheered" at 2400ms -> frame 72 (Beat 1 has frames 54..72 >= 15 frames)
    assert timeline[2].beat_id == "b1_2"
    assert timeline[2].start_frame == 72


# =========================================================================
# Test 5: Unicode and multibyte text handling (emojis, smart quotes, dashes)
# =========================================================================
def test_unicode_multibyte_byte_spans_accuracy():
    # 🚀 is 4 bytes in UTF-8: \xf0\x9f\x9a\x80
    # ’ is 3 bytes in UTF-8: \xe2\x80\x99
    # — is 3 bytes in UTF-8: \xe2\x80\x94
    section_texts = [
        "Tech 🚀 jumped $100M!",
        "Analysts’ mood improved — rapidly.",
    ]
    full_script = "\n\n".join(section_texts)
    full_bytes = full_script.encode("utf-8")

    spans = _compute_section_byte_spans(section_texts, full_script)

    # Section 0: "Tech 🚀 jumped $100M!"
    sec_0_bytes = section_texts[0].encode("utf-8")
    assert spans[0] == (0, len(sec_0_bytes))

    # Section 1 starts after \n\n (2 bytes)
    sec_1_bytes = section_texts[1].encode("utf-8")
    expected_sec_1_start = len(sec_0_bytes) + 2
    assert spans[1] == (expected_sec_1_start, expected_sec_1_start + len(sec_1_bytes))

    # Test word offset mapping for multibyte characters
    # In section 0: "$100M" starts at byte offset 18
    assert _find_section_for_byte_offset(18, spans) == 0
    # In section 1: "Analysts" starts at expected_sec_1_start
    assert _find_section_for_byte_offset(expected_sec_1_start, spans) == 1
    # Byte offset inside section 1
    assert _find_section_for_byte_offset(expected_sec_1_start + 10, spans) == 1


# =========================================================================
# Test 6: Abbreviations and large numbers
# =========================================================================
def test_abbreviations_and_large_numbers_section_isolation():
    builder = TimelineBuilder(fps=30)
    hook = Hook(
        conceptual_hook="Hook",
        script_text="The U.S. created 100,000 jobs.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="Growth continued.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="b1_1", preferred_component="Typography", visual_goal="G1", trigger_word=None),
                    VisualStrategyBeat(beat_id="b1_2", preferred_component="Typography", visual_goal="G2", trigger_word="continued"),
                ],
            )
        ],
    )

    full_script = "The U.S. created 100,000 jobs.\n\nGrowth continued."
    # "100,000" expands to "one hundred thousand"
    word_timestamps = [
        WordTimestamp(word="The", start_ms=0, end_ms=200, start_char=0, end_char=3),
        WordTimestamp(word="U", start_ms=200, end_ms=350, start_char=4, end_char=8),
        WordTimestamp(word="S", start_ms=350, end_ms=500, start_char=4, end_char=8),
        WordTimestamp(word="created", start_ms=500, end_ms=800, start_char=9, end_char=16),
        WordTimestamp(word="one", start_ms=800, end_ms=1000, start_char=17, end_char=24),
        WordTimestamp(word="hundred", start_ms=1000, end_ms=1200, start_char=17, end_char=24),
        WordTimestamp(word="thousand", start_ms=1200, end_ms=1400, start_char=17, end_char=24),
        WordTimestamp(word="jobs", start_ms=1400, end_ms=1700, start_char=25, end_char=29),
        # Idea 1 starts at byte 32
        WordTimestamp(word="Growth", start_ms=2000, end_ms=2300, start_char=32, end_char=38),
        WordTimestamp(word="continued", start_ms=2300, end_ms=2700, start_char=39, end_char=48),
    ]

    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=3.0,
        full_script_text=full_script,
        word_timestamps=word_timestamps,
    )

    section_texts = ["The U.S. created 100,000 jobs.", "Growth continued."]
    section_ids = ["hook", "idea_01"]
    assigned = _assign_words_to_sections(section_texts, section_ids, vt)

    assert len(assigned[0]) == 8
    assert [w.word for w in assigned[0]] == ["The", "U", "S", "created", "one", "hundred", "thousand", "jobs"]
    assert len(assigned[1]) == 2
    assert [w.word for w in assigned[1]] == ["Growth", "continued"]

    timeline = builder.build_timeline(hook=hook, strategy=strategy, voice_track=vt)
    assert len(timeline) == 3


# =========================================================================
# Test 7: Repeated words across sections correctly partitioned
# =========================================================================
def test_repeated_words_across_sections():
    hook = Hook(
        conceptual_hook="Hook",
        script_text="The market rose.",
        visual_directives=[
            HookVisualDirective(beat_id="h1", visual_instruction="Intro", trigger_word=None),
        ],
    )
    strategy = ScriptVisualStrategy(
        thesis="Thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Idea 1",
                focus_concept="C1",
                core_teaching_point="P1",
                narration="The market fell.",
                visual_sequence=[
                    VisualStrategyBeat(beat_id="b1_1", preferred_component="Typography", visual_goal="G1", trigger_word=None),
                ],
            )
        ],
    )

    full_script = "The market rose.\n\nThe market fell."
    word_timestamps = [
        # Hook: [0, 16)
        WordTimestamp(word="The", start_ms=0, end_ms=200, start_char=0, end_char=3),
        WordTimestamp(word="market", start_ms=200, end_ms=500, start_char=4, end_char=10),
        WordTimestamp(word="rose", start_ms=500, end_ms=800, start_char=11, end_char=15),
        # Idea 1: [18, 34)
        WordTimestamp(word="The", start_ms=1200, end_ms=1400, start_char=18, end_char=21),
        WordTimestamp(word="market", start_ms=1400, end_ms=1700, start_char=22, end_char=28),
        WordTimestamp(word="fell", start_ms=1700, end_ms=2000, start_char=29, end_char=33),
    ]

    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=2.5,
        full_script_text=full_script,
        word_timestamps=word_timestamps,
    )

    section_texts = ["The market rose.", "The market fell."]
    section_ids = ["hook", "idea_01"]
    assigned = _assign_words_to_sections(section_texts, section_ids, vt)

    assert [w.word for w in assigned[0]] == ["The", "market", "rose"]
    assert [w.word for w in assigned[1]] == ["The", "market", "fell"]
    assert assigned[0][0].start_ms == 0
    assert assigned[1][0].start_ms == 1200


# =========================================================================
# Test 8: Empty section handling
# =========================================================================
def test_empty_section_handling():
    section_texts = ["Hook intro.", "", "Idea two."]
    full_script = "Hook intro.\n\nIdea two."
    spans = _compute_section_byte_spans(section_texts, full_script)

    assert spans[0] == (0, 11)
    assert spans[1] == (11, 11)  # Empty section has length 0
    assert spans[2] == (13, 22)

    word_timestamps = [
        WordTimestamp(word="Hook", start_ms=0, end_ms=300, start_char=0, end_char=4),
        WordTimestamp(word="intro", start_ms=300, end_ms=600, start_char=5, end_char=10),
        WordTimestamp(word="Idea", start_ms=1000, end_ms=1300, start_char=13, end_char=17),
        WordTimestamp(word="two", start_ms=1300, end_ms=1600, start_char=18, end_char=21),
    ]

    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=2.0,
        full_script_text=full_script,
        word_timestamps=word_timestamps,
    )

    assigned = _assign_words_to_sections(section_texts, ["hook", "idea_01", "idea_02"], vt)
    assert len(assigned[0]) == 2
    assert len(assigned[1]) == 0  # Empty section gets 0 words
    assert len(assigned[2]) == 2


# =========================================================================
# Test 9: Backward compatibility fallback for mock tests without byte offsets
# =========================================================================
def test_backward_compatibility_fallback_without_byte_offsets_or_chunks():
    word_timestamps = [
        WordTimestamp(word="Hello", start_ms=0, end_ms=300),
        WordTimestamp(word="world", start_ms=300, end_ms=600),
        WordTimestamp(word="second", start_ms=1000, end_ms=1300),
        WordTimestamp(word="part", start_ms=1300, end_ms=1600),
    ]
    vt = VoiceTrack(
        voice_id="Matthew",
        audio_file_name="narration.mp3",
        storage_key="k",
        duration_seconds=2.0,
        full_script_text="Hello world.\n\nsecond part.",
        word_timestamps=word_timestamps,
    )

    section_texts = ["Hello world.", "second part."]
    section_ids = ["hook", "idea_01"]
    assigned = _assign_words_to_sections(section_texts, section_ids, vt)

    # Falls back to sequential count mapping cleanly
    assert [w.word for w in assigned[0]] == ["Hello", "world"]
    assert [w.word for w in assigned[1]] == ["second", "part"]
