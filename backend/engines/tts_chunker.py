from __future__ import annotations

import re
from domain.tts_chunk import TTSChunk


class TTSChunker:
    """
    Pure semantic text chunker designed for Text-To-Speech (TTS) synthesis.
    Splits narration text around natural linguistic boundaries (Scene -> Paragraph ->
    Sentence -> Semicolon/Colon -> Comma -> Word -> Char fallback) while strictly
    guaranteeing that text is never rewritten or mutated.
    """

    DEFAULT_SAFE_MAX_CHARS: int = 2200
    ABSOLUTE_POLLY_LIMIT: int = 2900

    # Common abbreviations where a period does not signal sentence end
    ABBREVIATIONS: set[str] = {
        "u.s.", "u.k.", "e.g.", "i.e.", "vs.", "etc.", "dr.", "mr.", "mrs.", "ms.",
        "prof.", "inc.", "corp.", "ltd.", "co.", "approx.", "dept.", "fig.", "no.",
        "al.", "est.", "jan.", "feb.", "mar.", "apr.", "jun.", "jul.", "aug.", "sep.",
        "oct.", "nov.", "dec."
    }

    def __init__(self, safe_max_chars: int = DEFAULT_SAFE_MAX_CHARS):
        if safe_max_chars <= 0:
            raise ValueError("safe_max_chars must be a positive integer.")
        if safe_max_chars > self.ABSOLUTE_POLLY_LIMIT:
            raise ValueError(
                f"safe_max_chars ({safe_max_chars}) cannot exceed the absolute limit "
                f"({self.ABSOLUTE_POLLY_LIMIT}) to prevent AWS Polly rejection."
            )
        self.safe_max_chars = safe_max_chars

    def chunk_sections(self, sections: list[tuple[str, str]]) -> list[TTSChunk]:
        """
        Takes an ordered list of (source_id, text) tuples (e.g. [('hook', hook_text),
        ('idea_01', idea1_text), ...]) and returns an ordered list of TTSChunks.
        """
        chunks: list[TTSChunk] = []
        seq = 1

        for source_id, raw_text in sections:
            clean_text = raw_text.strip()
            if not clean_text:
                continue

            # If the entire scene/idea fits within safe limits, keep it whole!
            if len(clean_text) <= self.safe_max_chars:
                chunks.append(
                    TTSChunk(
                        chunk_id=f"chunk_{seq:03d}",
                        source_id=source_id,
                        sequence=seq,
                        text=clean_text,
                        char_count=len(clean_text),
                    )
                )
                seq += 1
            else:
                # Hierarchical subdivision needed for this section
                sub_texts = self._split_hierarchical(clean_text, self.safe_max_chars)
                for sub_text in sub_texts:
                    clean_sub = sub_text.strip()
                    if not clean_sub:
                        continue
                    chunks.append(
                        TTSChunk(
                            chunk_id=f"chunk_{seq:03d}",
                            source_id=source_id,
                            sequence=seq,
                            text=clean_sub,
                            char_count=len(clean_sub),
                        )
                    )
                    seq += 1

        return chunks

    def chunk_text(self, text: str, source_id: str = "narration") -> list[TTSChunk]:
        """Convenience method for chunking a single body of text."""
        return self.chunk_sections([(source_id, text)])

    def _split_hierarchical(self, text: str, max_chars: int) -> list[str]:
        r"""
        Cascade through linguistic boundaries:
        1. Paragraphs (\n\n)
        2. Sentences (. ! ?)
        3. Semicolons & Colons (; :)
        4. Commas (,)
        5. Word boundaries (\s+)
        6. Character slices (hard fallback)
        """
        if len(text) <= max_chars:
            return [text]

        # Level 1: Try splitting by paragraphs
        para_boundaries = self._find_paragraph_boundaries(text)
        if para_boundaries:
            return self._pack_boundaries(text, para_boundaries, max_chars, next_level=self._split_sentences)

        # If no paragraph boundaries, go directly to sentences
        return self._split_sentences(text, max_chars)

    def _split_sentences(self, text: str, max_chars: int) -> list[str]:
        if len(text) <= max_chars:
            return [text]

        sentence_boundaries = self._find_sentence_boundaries(text)
        if sentence_boundaries:
            return self._pack_boundaries(text, sentence_boundaries, max_chars, next_level=self._split_semicolons)

        return self._split_semicolons(text, max_chars)

    def _split_semicolons(self, text: str, max_chars: int) -> list[str]:
        if len(text) <= max_chars:
            return [text]

        semi_boundaries = self._find_regex_boundaries(text, r'([;:])(\s+)')
        if semi_boundaries:
            return self._pack_boundaries(text, semi_boundaries, max_chars, next_level=self._split_commas)

        return self._split_commas(text, max_chars)

    def _split_commas(self, text: str, max_chars: int) -> list[str]:
        if len(text) <= max_chars:
            return [text]

        comma_boundaries = self._find_regex_boundaries(text, r'(,)(\s+)')
        if comma_boundaries:
            return self._pack_boundaries(text, comma_boundaries, max_chars, next_level=self._split_words)

        return self._split_words(text, max_chars)

    def _split_words(self, text: str, max_chars: int) -> list[str]:
        if len(text) <= max_chars:
            return [text]

        word_boundaries = self._find_regex_boundaries(text, r'(\s+)')
        if word_boundaries:
            return self._pack_boundaries(text, word_boundaries, max_chars, next_level=self._split_chars)

        return self._split_chars(text, max_chars)

    def _split_chars(self, text: str, max_chars: int) -> list[str]:
        """Ultimate fallback: slices string strictly at max_chars boundary."""
        chunks = []
        for i in range(0, len(text), max_chars):
            chunks.append(text[i:i + max_chars])
        return chunks

    def _pack_boundaries(
        self,
        text: str,
        boundaries: list[int],
        max_chars: int,
        next_level: callable,
    ) -> list[str]:
        """
        Slices text into segments at the specified boundaries and greedily packs
        them into chunks <= max_chars. If an individual segment exceeds max_chars,
        it delegates to next_level.
        """
        segments: list[str] = []
        prev = 0
        for b in boundaries:
            if b > prev:
                segments.append(text[prev:b])
                prev = b
        if prev < len(text):
            segments.append(text[prev:])

        packed: list[str] = []
        current = ""

        for seg in segments:
            # If a single segment is too large, recursively subdivide it
            if len(seg) > max_chars:
                if current:
                    packed.append(current)
                    current = ""
                sub_pieces = next_level(seg, max_chars)
                for piece in sub_pieces:
                    if len(current) + len(piece) <= max_chars:
                        current += piece
                    else:
                        if current:
                            packed.append(current)
                        current = piece
            else:
                if len(current) + len(seg) <= max_chars:
                    current += seg
                else:
                    if current:
                        packed.append(current)
                    current = seg

        if current:
            packed.append(current)

        return packed

    def _find_paragraph_boundaries(self, text: str) -> list[int]:
        r"""Finds slice indices at paragraph breaks (\n\s*\n+)."""
        pattern = re.compile(r'(\n\s*\n+)')
        boundaries: list[int] = []
        for m in pattern.finditer(text):
            boundaries.append(m.end(1))
        return boundaries

    @staticmethod
    def reconstruct_text(chunks: list[TTSChunk], separator: str = " ") -> str:
        """
        Reconstructs the full narration text from an ordered list of TTSChunks.
        By default, joins chunk texts with a single space.
        """
        return separator.join(c.text for c in chunks)

    def _find_sentence_boundaries(self, text: str) -> list[int]:
        """
        Finds slice indices at sentence terminators (. ! ? followed optionally by quotes
        and then whitespace), carefully avoiding decimals (e.g. 3.2%) and common
        abbreviations (e.g. U.S., e.g., Dr.).
        """
        pattern = re.compile(r'([.!?]+["\'”’]*)(\s+)')
        boundaries: list[int] = []

        for m in pattern.finditer(text):
            punct = m.group(1)
            ws_end = m.end(2)
            prefix = text[:m.start(1)]
            suffix = text[m.end(1):]

            # 1. Decimals: if punct starts with "." and adjacent to digits on both sides, skip
            if punct.startswith(".") and prefix and prefix[-1].isdigit() and suffix and suffix[0].isdigit():
                continue

            # 2. Known abbreviations or initials
            last_word_match = re.search(r'([a-zA-Z0-9\.]+)$', prefix)
            if last_word_match:
                candidate = (last_word_match.group(1) + punct).lower()
                base_word = last_word_match.group(1).lower()

                if candidate in self.ABBREVIATIONS or base_word in self.ABBREVIATIONS:
                    continue

                # Single letter initial (e.g. "J." or " A.")
                if re.match(r'^[a-zA-Z]\.$', last_word_match.group(1) + punct):
                    continue

            boundaries.append(ws_end)

        return boundaries

    def _find_regex_boundaries(self, text: str, regex_pattern: str) -> list[int]:
        """Finds slice indices at regex match ends."""
        pattern = re.compile(regex_pattern)
        boundaries: list[int] = []
        for m in pattern.finditer(text):
            # Split point is at the end of the whitespace following the punctuation
            boundaries.append(m.end(0))
        return boundaries
