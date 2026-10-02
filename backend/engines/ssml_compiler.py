from __future__ import annotations

import html
import os
import re
from typing import Sequence, Any

from domain.script_visual_strategy import VoiceCue


class SSMLCompilerError(Exception):
    """Raised when SSML compilation encounters unrecoverable structural errors."""


class SSMLCompiler:
    """
    Deterministic SSML Compiler.
    
    Translates pure canonical narration text and semantic VoiceCue instructions into
    well-formed, valid Amazon Polly Neural SSML.
    
    Key Principles:
    - Pure narration text is escaped for XML characters (&, <, >) deterministically.
    - Performance cues (pause, rate, volume, pronunciation) are anchored safely to words.
    - Anchors are replaced in reverse order of index to prevent character offset drift.
    - Zero arbitrary XML generation from LLMs; only strictly permitted Neural SSML is produced.
    """

    def __init__(self, default_rate: int | None = None):
        if default_rate is None:
            env_val = os.getenv("POLLY_GLOBAL_RATE")
            if env_val and env_val.strip():
                try:
                    parsed = int(env_val.strip())
                    if 50 <= parsed <= 150:
                        default_rate = parsed
                except ValueError:
                    default_rate = None
        self.default_rate = default_rate

    def compile(
        self,
        text: str,
        voice_cues: Sequence[VoiceCue | dict[str, Any]] | None = None,
        section_mark: str | None = None,
    ) -> str:
        """
        Compiles plain text and voice cues into a complete <speak> SSML document.
        
        Args:
            text: Pure canonical plain-text narration.
            voice_cues: Optional list of VoiceCue instances or dicts.
            section_mark: Optional timing mark name inserted at the start of the section.
        """
        raw_text = text.strip()
        if not raw_text:
            return "<speak></speak>"

        # If already wrapped in <speak>, return directly
        if raw_text.startswith("<speak>") and raw_text.endswith("</speak>"):
            return raw_text

        cues: list[VoiceCue] = []
        if voice_cues:
            for c in voice_cues:
                if isinstance(c, dict):
                    cues.append(VoiceCue.model_validate(c))
                elif isinstance(c, VoiceCue):
                    cues.append(c)

        # Locate non-overlapping spans for each valid anchor in the plain text
        spans: list[tuple[int, int, VoiceCue]] = []
        for cue in cues:
            if not cue.anchor or not cue.anchor.strip():
                continue

            match_span = self._find_anchor_span(raw_text, cue.anchor.strip(), spans)
            if match_span is not None:
                start_idx, end_idx = match_span
                spans.append((start_idx, end_idx, cue))

        # Sort spans in ascending order by start index
        spans.sort(key=lambda s: s[0])

        # Build segments: interleave escaped plain text with SSML-wrapped anchors
        segments: list[str] = []
        curr_idx = 0

        # Optional leading section mark (e.g. for timeline synchronization)
        if section_mark:
            clean_mark = html.escape(section_mark.strip(), quote=True)
            segments.append(f'<mark name="{clean_mark}"/>')

        for start_idx, end_idx, cue in spans:
            # Segment of plain text before the anchor
            if start_idx > curr_idx:
                prefix = raw_text[curr_idx:start_idx]
                segments.append(html.escape(prefix))

            # The matched anchor substring from the original text
            anchor_text = raw_text[start_idx:end_idx]
            wrapped_anchor = self._render_cue(anchor_text, cue)
            segments.append(wrapped_anchor)

            curr_idx = end_idx

        # Trailing plain text after the last anchor
        if curr_idx < len(raw_text):
            suffix = raw_text[curr_idx:]
            segments.append(html.escape(suffix))

        body = "".join(segments)

        # Optional global rate wrapper if default_rate is configured and body is not already wrapped
        if self.default_rate is not None and self.default_rate != 100 and 80 <= self.default_rate <= 120:
            body = f'<prosody rate="{self.default_rate}%">{body}</prosody>'

        return f"<speak>{body}</speak>"

    def _find_anchor_span(
        self,
        text: str,
        anchor: str,
        existing_spans: list[tuple[int, int, VoiceCue]],
    ) -> tuple[int, int] | None:
        """
        Finds the start and end indices of the anchor in text, avoiding overlap with existing spans.
        Tries exact match first, then case-insensitive match.
        """
        # 1. Exact match
        pos = text.find(anchor)
        while pos != -1:
            end_pos = pos + len(anchor)
            if not self._overlaps(pos, end_pos, existing_spans):
                return (pos, end_pos)
            pos = text.find(anchor, pos + 1)

        # 2. Case-insensitive match fallback
        pattern = re.compile(re.escape(anchor), re.IGNORECASE)
        for match in pattern.finditer(text):
            s, e = match.span()
            if not self._overlaps(s, e, existing_spans):
                return (s, e)

        return None

    def _overlaps(
        self,
        start: int,
        end: int,
        spans: list[tuple[int, int, VoiceCue]],
    ) -> bool:
        """Returns True if [start, end) overlaps with any span in spans."""
        for s_start, s_end, _ in spans:
            if max(start, s_start) < min(end, s_end):
                return True
        return False

    def _render_cue(self, anchor_text: str, cue: VoiceCue) -> str:
        """Renders a single matched anchor into valid Polly Neural SSML."""
        escaped_anchor = html.escape(anchor_text)

        # 1. Pronunciation alias (<sub> tag)
        if cue.pronunciation and cue.pronunciation.strip():
            clean_alias = html.escape(cue.pronunciation.strip(), quote=True)
            escaped_anchor = f'<sub alias="{clean_alias}">{escaped_anchor}</sub>'

        # 2. Prosody shifts (rate_percent/rate and volume_db)
        prosody_attrs: list[str] = []
        effective_rate = cue.rate_percent if cue.rate_percent is not None else cue.rate
        if effective_rate is not None and 90 <= effective_rate <= 110:
            prosody_attrs.append(f'rate="{effective_rate}%"')

        if cue.volume_db is not None and -6 <= cue.volume_db <= 6:
            vol_str = f"+{cue.volume_db}dB" if cue.volume_db > 0 else f"{cue.volume_db}dB"
            prosody_attrs.append(f'volume="{vol_str}"')

        if prosody_attrs:
            attr_str = " ".join(prosody_attrs)
            escaped_anchor = f'<prosody {attr_str}>{escaped_anchor}</prosody>'

        # 3. Leading breathing pause (<break> tag before anchor)
        if cue.pause_before_ms is not None and cue.pause_before_ms > 0:
            bounded_pause_before = max(100, min(1000, cue.pause_before_ms))
            escaped_anchor = f'<break time="{bounded_pause_before}ms"/>{escaped_anchor}'

        # 4. Trailing breathing pause (<break> tag after anchor)
        if cue.pause_after_ms is not None and cue.pause_after_ms > 0:
            bounded_pause_after = max(100, min(1000, cue.pause_after_ms))
            escaped_anchor = f'{escaped_anchor}<break time="{bounded_pause_after}ms"/>'

        # 5. Optional marker tag for cue_id
        if cue.cue_id and cue.cue_id.strip():
            clean_cue_id = html.escape(cue.cue_id.strip(), quote=True)
            escaped_anchor = f'<mark name="{clean_cue_id}"/>{escaped_anchor}'

        return escaped_anchor
