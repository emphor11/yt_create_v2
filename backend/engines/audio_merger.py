import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from domain.tts_chunk import TTSChunkResult
from domain.voice_track import WordTimestamp
from pydantic import BaseModel


class AudioStreamInfo(BaseModel):
    codec_name: str
    sample_rate: int
    channels: int
    format_name: str


class AudioConcatCompatibilityError(Exception):
    """Raised when audio chunks have incompatible stream parameters for stream-copy concat."""

    def __init__(
        self,
        message: str,
        incompatible_property: str | None = None,
        chunk_1_id: str | None = None,
        chunk_1_value: Any = None,
        chunk_2_id: str | None = None,
        chunk_2_value: Any = None,
    ):
        super().__init__(message)
        self.incompatible_property = incompatible_property
        self.chunk_1_id = chunk_1_id
        self.chunk_1_value = chunk_1_value
        self.chunk_2_id = chunk_2_id
        self.chunk_2_value = chunk_2_value


class AudioMergeError(Exception):
    """Raised when audio concatenation or FFmpeg execution fails."""


class AudioDurationMismatchError(Exception):
    """Raised when merged audio duration deviates from sum of chunk durations beyond tolerance."""

    def __init__(self, master_duration_ms: int, expected_duration_ms: int, tolerance_ms: int):
        super().__init__(
            f"Merged master audio duration ({master_duration_ms}ms) deviates from expected sum "
            f"of chunk durations ({expected_duration_ms}ms) by {abs(master_duration_ms - expected_duration_ms)}ms, "
            f"exceeding container tolerance of {tolerance_ms}ms."
        )
        self.master_duration_ms = master_duration_ms
        self.expected_duration_ms = expected_duration_ms
        self.tolerance_ms = tolerance_ms


def polly_byte_to_char_offset(text: str, byte_offset: int) -> int:
    """
    Converts an AWS Polly UTF-8 byte offset into a Python character index.
    AWS Polly speech marks output 'start' and 'end' as UTF-8 byte offsets,
    which diverge from Python string character indices when multibyte Unicode
    characters (e.g. emojis, curly quotes, dashes, non-ASCII letters) are present.
    """
    if byte_offset <= 0:
        return 0
    text_bytes = text.encode("utf-8")
    clamped_offset = min(byte_offset, len(text_bytes))
    return len(text_bytes[:clamped_offset].decode("utf-8", errors="ignore"))


class AudioMerger:
    """
    Handles verification of chunk audio stream compatibility, stream-copy concatenation
    via FFmpeg, duration validation, and calculation of global word timestamps.
    """

    def __init__(self, default_tolerance_ms: int = 300) -> None:
        self.default_tolerance_ms = default_tolerance_ms

    def probe_audio(self, audio_path: Path) -> AudioStreamInfo:
        """
        Probes an audio file with ffprobe to retrieve codec, sample rate, channels, and format.
        """
        if not audio_path.exists() or audio_path.stat().st_size == 0:
            raise AudioMergeError(f"Audio file does not exist or is empty: {audio_path}")

        try:
            res = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-select_streams", "a:0",
                    "-show_entries", "stream=codec_name,sample_rate,channels:format=format_name",
                    "-of", "json",
                    str(audio_path),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if res.returncode != 0:
                raise AudioMergeError(
                    f"ffprobe failed on {audio_path} (return code {res.returncode}): {res.stderr.strip()}"
                )

            data = json.loads(res.stdout)
            streams = data.get("streams", [])
            if not streams:
                raise AudioMergeError(f"No audio streams found in {audio_path}")

            stream = streams[0]
            format_info = data.get("format", {})
            codec_name = stream.get("codec_name", "").lower()
            sample_rate = int(stream.get("sample_rate", 0))
            channels = int(stream.get("channels", 0))
            format_name = format_info.get("format_name", "").lower()

            return AudioStreamInfo(
                codec_name=codec_name,
                sample_rate=sample_rate,
                channels=channels,
                format_name=format_name,
            )
        except (subprocess.SubprocessError, json.JSONDecodeError, ValueError) as exc:
            if isinstance(exc, AudioMergeError):
                raise
            raise AudioMergeError(f"Failed to probe audio stream for {audio_path}: {exc}") from exc

    def verify_stream_compatibility(self, chunks: list[TTSChunkResult]) -> None:
        """
        Verifies that all chunk audio files have identical stream properties
        (codec, sample_rate, channels) required for safe stream-copy concatenation.
        Raises AudioConcatCompatibilityError if parameters mismatch.
        """
        if len(chunks) <= 1:
            return

        baseline_chunk = chunks[0]
        baseline_info = self.probe_audio(Path(baseline_chunk.audio_path))

        for chunk in chunks[1:]:
            info = self.probe_audio(Path(chunk.audio_path))

            # Codec check
            if info.codec_name != baseline_info.codec_name:
                raise AudioConcatCompatibilityError(
                    message=(
                        f"Incompatible audio codec between '{baseline_chunk.chunk_id}' "
                        f"({baseline_info.codec_name}) and '{chunk.chunk_id}' ({info.codec_name})."
                    ),
                    incompatible_property="codec_name",
                    chunk_1_id=baseline_chunk.chunk_id,
                    chunk_1_value=baseline_info.codec_name,
                    chunk_2_id=chunk.chunk_id,
                    chunk_2_value=info.codec_name,
                )

            # Sample rate check
            if info.sample_rate != baseline_info.sample_rate:
                raise AudioConcatCompatibilityError(
                    message=(
                        f"Incompatible sample rate between '{baseline_chunk.chunk_id}' "
                        f"({baseline_info.sample_rate}Hz) and '{chunk.chunk_id}' ({info.sample_rate}Hz)."
                    ),
                    incompatible_property="sample_rate",
                    chunk_1_id=baseline_chunk.chunk_id,
                    chunk_1_value=baseline_info.sample_rate,
                    chunk_2_id=chunk.chunk_id,
                    chunk_2_value=info.sample_rate,
                )

            # Channels check
            if info.channels != baseline_info.channels:
                raise AudioConcatCompatibilityError(
                    message=(
                        f"Incompatible audio channel count between '{baseline_chunk.chunk_id}' "
                        f"({baseline_info.channels}) and '{chunk.chunk_id}' ({info.channels})."
                    ),
                    incompatible_property="channels",
                    chunk_1_id=baseline_chunk.chunk_id,
                    chunk_1_value=baseline_info.channels,
                    chunk_2_id=chunk.chunk_id,
                    chunk_2_value=info.channels,
                )

    def compute_global_word_timestamps(
        self,
        chunk_results: list[TTSChunkResult],
    ) -> list[WordTimestamp]:
        """
        Converts chunk-local word timestamps into one globally ordered list of WordTimestamps.
        Preserves original word values and local timestamps in the chunk results.
        
        Formula:
          offset(chunk_0) = 0
          offset(chunk_k) = sum(actual_duration_ms of chunks 0 .. k-1)
          global_start_ms = offset + local_start_ms
          global_end_ms = offset + local_end_ms
          
        Ensures strict non-decreasing monotonicity across chunk boundaries.
        """
        sorted_chunks = sorted(chunk_results, key=lambda c: c.sequence)
        global_timestamps: list[WordTimestamp] = []

        cumulative_offset_ms = 0
        prev_end_ms = 0

        is_single_chunk = len(sorted_chunks) == 1

        for chunk in sorted_chunks:
            chunk_offset_ms = cumulative_offset_ms

            for ts_dict in chunk.word_timestamps:
                word = ts_dict.get("word", "")
                local_start = int(ts_dict.get("start_ms", 0))
                local_end = int(ts_dict.get("end_ms", local_start + max(50, len(word) * 45)))

                g_start_ms = chunk_offset_ms + local_start
                g_end_ms = chunk_offset_ms + local_end

                # Enforce global monotonicity
                if g_start_ms < prev_end_ms:
                    g_start_ms = prev_end_ms
                if g_end_ms <= g_start_ms:
                    g_end_ms = g_start_ms + max(50, len(word) * 45)

                # Maintain offset semantics
                if is_single_chunk:
                    start_char = ts_dict.get("start_char")
                    end_char = ts_dict.get("end_char")
                else:
                    # For multi-chunk: raw byte offsets remain preserved in chunk.word_timestamps.
                    # Global timestamps leave char offsets as None since downstream section
                    # alignment does not require global text offsets.
                    start_char = None
                    end_char = None

                ts = WordTimestamp(
                    word=word,
                    start_ms=g_start_ms,
                    end_ms=g_end_ms,
                    start_char=start_char,
                    end_char=end_char,
                )
                global_timestamps.append(ts)
                prev_end_ms = g_end_ms

            # Advance offset using actual measured audio duration
            cumulative_offset_ms += chunk.duration_ms

        return global_timestamps

    def concat_audio_files(
        self,
        chunk_paths: list[Path],
        output_path: Path,
    ) -> tuple[float, int]:
        """
        Concatenates chunk audio files into a single master audio file using
        FFmpeg stream copy demuxer (-f concat -safe 0 -c copy).
        Returns (duration_seconds, duration_ms) measured from the merged output.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if len(chunk_paths) == 1:
            single_path = chunk_paths[0]
            if single_path != output_path:
                shutil.copyfile(single_path, output_path)
            return self._measure_duration(output_path)

        # Write FFmpeg concat list file
        concat_list_path = output_path.parent / f"{output_path.stem}_concat_list.txt"
        try:
            with open(concat_list_path, "w", encoding="utf-8") as f:
                for path in chunk_paths:
                    escaped_path = str(path.resolve()).replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")

            cmd = [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_list_path),
                "-c", "copy",
                str(output_path),
            ]
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if res.returncode != 0:
                raise AudioMergeError(
                    f"FFmpeg concat failed with return code {res.returncode}: {res.stderr.strip()}"
                )
        finally:
            if concat_list_path.exists():
                try:
                    concat_list_path.unlink()
                except OSError:
                    pass

        return self._measure_duration(output_path)

    def _measure_duration(self, audio_path: Path) -> tuple[float, int]:
        """Measures duration of audio file using ffprobe."""
        if not audio_path.exists() or audio_path.stat().st_size == 0:
            raise AudioMergeError(f"Output audio file does not exist or is empty: {audio_path}")

        try:
            res = subprocess.run(
                [
                    "ffprobe",
                    "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(audio_path),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                dur_sec = float(res.stdout.strip())
                return dur_sec, int(round(dur_sec * 1000))
        except Exception as exc:
            raise AudioMergeError(f"Failed to measure duration of merged audio {audio_path}: {exc}") from exc

        raise AudioMergeError(f"Could not determine duration of {audio_path}")

    def merge_chunks(
        self,
        chunk_results: list[TTSChunkResult],
        output_path: Path,
        tolerance_ms: int | None = None,
    ) -> tuple[float, list[WordTimestamp]]:
        """
        Orchestrates full Step 3 merge:
        1. Preserves exact deterministic chunk ordering (by sequence)
        2. Single chunk fast-path (offset=0, exact copy, unchanged timestamps)
        3. Multi-chunk: verifies audio stream compatibility
        4. Concatenates chunk audio files via FFmpeg stream-copy
        5. Validates master duration against sum of chunk durations within tolerance
        6. Converts local word timestamps to global timestamps using cumulative physical duration
        """
        if not chunk_results:
            raise AudioMergeError("Cannot merge an empty list of TTSChunkResults.")

        sorted_chunks = sorted(chunk_results, key=lambda c: c.sequence)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Single chunk handling (Requirement 17)
        if len(sorted_chunks) == 1:
            single = sorted_chunks[0]
            single_path = Path(single.audio_path)
            if single_path != output_path:
                shutil.copyfile(single_path, output_path)

            global_timestamps = self.compute_global_word_timestamps(sorted_chunks)
            return single.duration_seconds, global_timestamps

        # 2. Verify stream compatibility across all chunks (Requirement 12)
        self.verify_stream_compatibility(sorted_chunks)

        # 3. Concatenate audio files preserving exact chunk order (Requirement 11 & 13)
        chunk_paths = [Path(c.audio_path) for c in sorted_chunks]
        master_duration_sec, master_duration_ms = self.concat_audio_files(chunk_paths, output_path)

        # 4. Validate master duration against sum of chunk durations (Requirement 15)
        expected_duration_ms = sum(c.duration_ms for c in sorted_chunks)
        effective_tolerance = tolerance_ms if tolerance_ms is not None else max(
            self.default_tolerance_ms, len(sorted_chunks) * 80
        )

        diff_ms = abs(master_duration_ms - expected_duration_ms)
        if diff_ms > effective_tolerance:
            raise AudioDurationMismatchError(
                master_duration_ms=master_duration_ms,
                expected_duration_ms=expected_duration_ms,
                tolerance_ms=effective_tolerance,
            )

        # 5. Compute global word timestamps (Requirement 4-9)
        global_timestamps = self.compute_global_word_timestamps(sorted_chunks)

        return master_duration_sec, global_timestamps
