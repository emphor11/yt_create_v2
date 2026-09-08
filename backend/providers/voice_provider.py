import json
import os
import subprocess
from pathlib import Path
from typing import Any, Protocol

from domain.tts_chunk import TTSChunk, TTSChunkResult
from domain.voice_track import WordTimestamp


class VoiceProvider(Protocol):
    def synthesize(self, text: str, output_path: Path) -> tuple[float, list[WordTimestamp]]:
        """
        Synthesizes the text narration into an audio file at output_path.
        Returns a tuple of:
          - duration_seconds: float
          - list[WordTimestamp] containing word-level timestamps.
        """
        ...

    def synthesize_chunk(self, chunk: TTSChunk, output_dir: Path) -> TTSChunkResult:
        """Synthesizes a single TTSChunk into MP3 audio and JSON speech marks."""
        ...

    def synthesize_chunks(self, chunks: list[TTSChunk], output_dir: Path) -> list[TTSChunkResult]:
        """Synthesizes an ordered list of TTSChunks sequentially."""
        ...


class PollyChunkSynthesisError(Exception):
    """Raised when a specific TTSChunk fails during Polly speech or marks synthesis."""

    def __init__(self, chunk_id: str, stage: str, message: str, original_error: Exception | None = None):
        super().__init__(f"Failed to synthesize chunk '{chunk_id}' ({stage}): {message}")
        self.chunk_id = chunk_id
        self.stage = stage  # 'audio' or 'speech_marks'
        self.original_error = original_error


class PollyVoiceProvider:
    def __init__(self, voice_id: str = "Matthew", engine: str = "neural", region_name: str = "us-east-1"):
        self.voice_id = voice_id
        self.engine = engine
        self.region_name = region_name

    def synthesize_chunk(
        self,
        chunk: TTSChunk,
        output_dir: Path,
        client: Any = None,
    ) -> TTSChunkResult:
        """
        Synthesizes a single TTSChunk into an MP3 audio file and a JSON speech marks file.
        Preserves the exact chunk text sent to AWS Polly.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / f"{chunk.chunk_id}.mp3"
        marks_path = output_dir / f"{chunk.chunk_id}.marks.json"

        if client is None:
            import boto3
            client = boto3.client("polly", region_name=self.region_name)

        # 1. Synthesize speech audio stream (MP3)
        try:
            audio_response = client.synthesize_speech(
                Engine=self.engine,
                OutputFormat="mp3",
                Text=chunk.text,
                VoiceId=self.voice_id,
            )
        except Exception as exc:
            raise PollyChunkSynthesisError(
                chunk_id=chunk.chunk_id,
                stage="audio",
                message=str(exc),
                original_error=exc,
            ) from exc

        if "AudioStream" in audio_response:
            with open(audio_path, "wb") as f:
                f.write(audio_response["AudioStream"].read())
        else:
            raise PollyChunkSynthesisError(
                chunk_id=chunk.chunk_id,
                stage="audio",
                message="AWS Polly response did not contain AudioStream.",
            )

        # 2. Synthesize speech marks (JSON) for word timestamps
        try:
            marks_response = client.synthesize_speech(
                Engine=self.engine,
                OutputFormat="json",
                SpeechMarkTypes=["word"],
                Text=chunk.text,
                VoiceId=self.voice_id,
            )
        except Exception as exc:
            raise PollyChunkSynthesisError(
                chunk_id=chunk.chunk_id,
                stage="speech_marks",
                message=str(exc),
                original_error=exc,
            ) from exc

        word_timestamps: list[WordTimestamp] = []
        if "AudioStream" in marks_response:
            try:
                content = marks_response["AudioStream"].read().decode("utf-8")
                with open(marks_path, "w", encoding="utf-8") as f:
                    f.write(content)

                for line in content.splitlines():
                    if not line.strip():
                        continue
                    mark = json.loads(line)
                    if mark.get("type") == "word":
                        start_ms = mark["time"]
                        start_char = mark.get("start")
                        end_char = mark.get("end")
                        word_timestamps.append(
                            WordTimestamp(
                                word=mark["value"],
                                start_ms=start_ms,
                                end_ms=start_ms + max(100, len(mark["value"]) * 45),
                                start_char=start_char,
                                end_char=end_char,
                            )
                        )
            except Exception as exc:
                raise PollyChunkSynthesisError(
                    chunk_id=chunk.chunk_id,
                    stage="speech_marks",
                    message=f"Failed to read or parse speech marks JSON: {exc}",
                    original_error=exc,
                ) from exc
        else:
            raise PollyChunkSynthesisError(
                chunk_id=chunk.chunk_id,
                stage="speech_marks",
                message="AWS Polly speech marks response did not contain AudioStream.",
            )

        # Complete and adjust end timestamps based on next word start
        for idx in range(len(word_timestamps)):
            if idx < len(word_timestamps) - 1:
                word_timestamps[idx].end_ms = min(
                    word_timestamps[idx].end_ms,
                    word_timestamps[idx + 1].start_ms - 1
                )
                if word_timestamps[idx].end_ms < word_timestamps[idx].start_ms:
                    word_timestamps[idx].end_ms = word_timestamps[idx].start_ms + 50

        # Determine duration
        duration_seconds, duration_ms = self._measure_audio_duration(audio_path, word_timestamps)

        return TTSChunkResult(
            chunk_id=chunk.chunk_id,
            sequence=chunk.sequence,
            source_id=chunk.source_id,
            text=chunk.text,
            audio_path=str(audio_path),
            speech_marks_path=str(marks_path),
            word_timestamps=[ts.model_dump() for ts in word_timestamps],
            duration_ms=duration_ms,
            duration_seconds=duration_seconds,
        )

    def synthesize_chunks(
        self,
        chunks: list[TTSChunk],
        output_dir: Path,
        client: Any = None,
    ) -> list[TTSChunkResult]:
        """
        Synthesizes an ordered list of TTSChunks sequentially.
        Preserves strict chunk ordering.
        If any chunk fails, raises PollyChunkSynthesisError identifying the exact chunk.
        """
        if client is None:
            import boto3
            client = boto3.client("polly", region_name=self.region_name)

        results: list[TTSChunkResult] = []
        for chunk in chunks:
            result = self.synthesize_chunk(chunk, output_dir, client=client)
            results.append(result)
        return results

    def synthesize(self, text: str, output_path: Path) -> tuple[float, list[WordTimestamp]]:
        """
        Backward-compatible method: synthesizes full text as a single chunk.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        chunk = TTSChunk(
            chunk_id="chunk_001",
            source_id="narration",
            sequence=1,
            text=text,
            char_count=len(text),
        )
        result = self.synthesize_chunk(chunk, output_path.parent)

        # Ensure target output_path file is created
        if Path(result.audio_path) != output_path:
            import shutil
            shutil.copyfile(result.audio_path, output_path)

        timestamps = [WordTimestamp.model_validate(ts) for ts in result.word_timestamps]
        return result.duration_seconds, timestamps

    def _measure_audio_duration(
        self,
        audio_path: Path,
        word_timestamps: list[WordTimestamp],
    ) -> tuple[float, int]:
        """
        Measures actual audio duration in seconds and milliseconds.
        Attempts ffprobe first for actual physical audio duration,
        falling back to speech marks or file size estimation.
        """
        if audio_path.exists() and audio_path.stat().st_size > 0:
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
                    timeout=5,
                    check=False,
                )
                if res.returncode == 0 and res.stdout.strip():
                    dur_sec = float(res.stdout.strip())
                    return dur_sec, int(round(dur_sec * 1000))
            except Exception:
                pass

        if word_timestamps:
            dur_sec = word_timestamps[-1].end_ms / 1000.0
            return dur_sec, word_timestamps[-1].end_ms
        elif audio_path.exists():
            dur_sec = max(1.0, audio_path.stat().st_size / 16000.0)
            return dur_sec, int(dur_sec * 1000)

        return 1.0, 1000
