import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Protocol

from domain.tts_chunk import TTSChunk, TTSChunkResult
from domain.voice_track import WordTimestamp, SpeechMark
from engines.ssml_compiler import SSMLCompiler
from engines.ssml_validator import SSMLValidator

logger = logging.getLogger(__name__)


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
    def __init__(
        self,
        voice_id: str | None = None,
        engine: str | None = None,
        region_name: str | None = None,
        compiler: SSMLCompiler | None = None,
        validator: SSMLValidator | None = None,
        enable_ssml: bool = True,
        global_rate: int | None = None,
    ):
        self.voice_id = voice_id or os.getenv("POLLY_VOICE_ID", "Kajal")
        self.engine = engine or os.getenv("POLLY_ENGINE", "neural")
        self.region_name = region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        resolved_rate = global_rate
        if resolved_rate is None:
            env_rate = os.getenv("POLLY_GLOBAL_RATE")
            if env_rate and env_rate.strip():
                try:
                    parsed = int(env_rate.strip())
                    if 50 <= parsed <= 150:
                        resolved_rate = parsed
                except ValueError:
                    resolved_rate = None

        self.compiler = compiler or SSMLCompiler(default_rate=resolved_rate)
        if compiler and resolved_rate is not None and getattr(self.compiler, "default_rate", None) is None:
            self.compiler.default_rate = resolved_rate

        self.validator = validator or SSMLValidator()
        self.enable_ssml = enable_ssml

    def synthesize_chunk(
        self,
        chunk: TTSChunk,
        output_dir: Path,
        client: Any = None,
    ) -> TTSChunkResult:
        """
        Synthesizes a single TTSChunk into an MP3 audio file and a JSON speech marks file.
        Uses compiled and validated SSML when enable_ssml is True, with fallback to plain text.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        audio_path = output_dir / f"{chunk.chunk_id}.mp3"
        marks_path = output_dir / f"{chunk.chunk_id}.marks.json"

        if client is None:
            import boto3
            client = boto3.client("polly", region_name=self.region_name)

        # 1. Determine text and SSML mode
        synthesize_text = chunk.text
        text_type = "text"

        has_cues = bool(getattr(chunk, "voice_cues", None))
        is_already_ssml = chunk.text.startswith("<speak>") and chunk.text.endswith("</speak>")
        has_global_rate = (
            getattr(self.compiler, "default_rate", None) is not None
            and self.compiler.default_rate != 100
        )

        if self.enable_ssml and (has_cues or is_already_ssml or has_global_rate):
            if is_already_ssml:
                compiled = chunk.text
            else:
                cues = getattr(chunk, "voice_cues", []) or []
                compiled = self.compiler.compile(
                    text=chunk.text,
                    voice_cues=cues,
                    section_mark=f"{chunk.source_id}_start",
                )

            validation = self.validator.validate(compiled)
            if validation.is_valid:
                synthesize_text = compiled
                text_type = "ssml"
            else:
                logger.warning(
                    "SSML validation failed for chunk '%s': %s. Falling back to plain text.",
                    chunk.chunk_id,
                    validation.errors,
                )
                synthesize_text = chunk.text
                text_type = "text"
        else:
            synthesize_text = chunk.text
            text_type = "text"

        # 2. Synthesize speech audio stream (MP3)
        try:
            audio_response = client.synthesize_speech(
                Engine=self.engine,
                OutputFormat="mp3",
                Text=synthesize_text,
                TextType=text_type,
                VoiceId=self.voice_id,
            )
        except Exception as exc:
            err_msg = str(exc)
            # Recoverable content error: retry with plain text if SSML was rejected
            if text_type == "ssml" and ("InvalidSsml" in err_msg or "ssml" in err_msg.lower()):
                logger.warning(
                    "AWS Polly rejected SSML for chunk '%s' (%s). Retrying with plain text fallback.",
                    chunk.chunk_id,
                    err_msg,
                )
                synthesize_text = chunk.text
                text_type = "text"
                try:
                    audio_response = client.synthesize_speech(
                        Engine=self.engine,
                        OutputFormat="mp3",
                        Text=synthesize_text,
                        TextType=text_type,
                        VoiceId=self.voice_id,
                    )
                except Exception as retry_exc:
                    raise PollyChunkSynthesisError(
                        chunk_id=chunk.chunk_id,
                        stage="audio",
                        message=str(retry_exc),
                        original_error=retry_exc,
                    ) from retry_exc
            else:
                # Configuration or connection error -> FAIL LOUDLY
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

        # 3. Synthesize speech marks (JSON) for word timestamps & SSML marks
        # Note: exactly matches the voice, engine, text, and text_type used for audio
        mark_types = ["word", "ssml"] if text_type == "ssml" else ["word"]
        try:
            marks_response = client.synthesize_speech(
                Engine=self.engine,
                OutputFormat="json",
                SpeechMarkTypes=mark_types,
                Text=synthesize_text,
                TextType=text_type,
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
        speech_marks: list[SpeechMark] = []

        if "AudioStream" in marks_response:
            try:
                content = marks_response["AudioStream"].read().decode("utf-8")
                with open(marks_path, "w", encoding="utf-8") as f:
                    f.write(content)

                for line in content.splitlines():
                    if not line.strip():
                        continue
                    mark = json.loads(line)
                    m_type = mark.get("type")
                    m_time = int(mark.get("time", 0))
                    m_val = str(mark.get("value", ""))
                    m_start = mark.get("start")
                    m_end = mark.get("end")

                    if m_type == "word":
                        word_timestamps.append(
                            WordTimestamp(
                                word=m_val,
                                start_ms=m_time,
                                end_ms=m_time + max(100, len(m_val) * 45),
                                start_char=m_start,
                                end_char=m_end,
                            )
                        )
                    elif m_type == "ssml":
                        speech_marks.append(
                            SpeechMark(
                                time_ms=m_time,
                                mark_type="ssml",
                                value=m_val,
                                start_char=m_start,
                                end_char=m_end,
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
            speech_marks=[sm.model_dump() for sm in speech_marks],
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
