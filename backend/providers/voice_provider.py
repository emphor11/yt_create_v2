import json
import os
from pathlib import Path
from typing import Protocol

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


class PollyVoiceProvider:
    def __init__(self, voice_id: str = "Matthew", engine: str = "neural", region_name: str = "us-east-1"):
        self.voice_id = voice_id
        self.engine = engine
        self.region_name = region_name

    def synthesize(self, text: str, output_path: Path) -> tuple[float, list[WordTimestamp]]:
        import boto3
        
        # Instantiate boto3 polly client
        client = boto3.client("polly", region_name=self.region_name)

        # 1. Synthesize speech audio stream (MP3)
        audio_response = client.synthesize_speech(
            Engine=self.engine,
            OutputFormat="mp3",
            Text=text,
            VoiceId=self.voice_id,
        )
        
        # Write binary stream to output path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if "AudioStream" in audio_response:
            with open(output_path, "wb") as f:
                f.write(audio_response["AudioStream"].read())

        # 2. Synthesize speech marks (JSON) for word timestamps
        marks_response = client.synthesize_speech(
            Engine=self.engine,
            OutputFormat="json",
            SpeechMarkTypes=["word"],
            Text=text,
            VoiceId=self.voice_id,
        )

        word_timestamps: list[WordTimestamp] = []
        if "AudioStream" in marks_response:
            # Speech marks are returned as a line-delimited JSON stream
            content = marks_response["AudioStream"].read().decode("utf-8")
            for line in content.splitlines():
                if not line.strip():
                    continue
                mark = json.loads(line)
                if mark.get("type") == "word":
                    # Polly returns time offset in milliseconds from start
                    start_ms = mark["time"]
                    # Estimate end time of this word (we will look ahead or approximate word length in ms)
                    word_timestamps.append(
                        WordTimestamp(
                            word=mark["value"],
                            start_ms=start_ms,
                            # End time can be approximated or completed during pass 2 below
                            end_ms=start_ms + max(100, len(mark["value"]) * 45),
                        )
                    )

        # Complete and adjust end timestamps based on next word start
        for idx in range(len(word_timestamps)):
            if idx < len(word_timestamps) - 1:
                # Next word start forms the boundary of the current word
                word_timestamps[idx].end_ms = min(
                    word_timestamps[idx].end_ms,
                    word_timestamps[idx + 1].start_ms - 1
                )
                if word_timestamps[idx].end_ms < word_timestamps[idx].start_ms:
                    word_timestamps[idx].end_ms = word_timestamps[idx].start_ms + 50

        # Determine duration
        duration_seconds = 1.0
        if word_timestamps:
            duration_seconds = word_timestamps[-1].end_ms / 1000.0
        elif output_path.exists():
            # Fallback estimation based on file size if no speech marks
            duration_seconds = max(1.0, output_path.stat().st_size / 16000.0) # ~128kbps approx

        return duration_seconds, word_timestamps


class FallbackVoiceProvider:
    """
    A robust fallback provider that generates a mock MP3 structure and linear
    timestamps, preventing API/AWS credential requirements from blocking local
    runs and tests.
    """
    def __init__(self, voice_id: str = "FallbackVoice"):
        self.voice_id = voice_id

    def synthesize(self, text: str, output_path: Path) -> tuple[float, list[WordTimestamp]]:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write a dummy valid MP3 header containing silence bytes
        # 128 bytes of dummy mock data
        dummy_mp3_bytes = b"\xFF\xFB\x90\x44" + b"\x00" * 124
        output_path.write_bytes(dummy_mp3_bytes)

        # Split text into words and generate linear 300ms intervals
        words = [w.strip() for w in text.split() if w.strip()]
        if not words:
            words = ["Silence"]

        word_timestamps: list[WordTimestamp] = []
        current_ms = 0
        for w in words:
            # strip punctuation for word representation
            clean_word = "".join(char for char in w if char.isalnum() or char in "'-")
            if not clean_word:
                clean_word = w
            
            # approximate reading speed of 320ms per word
            duration_ms = max(150, len(clean_word) * 45 + 80)
            word_timestamps.append(
                WordTimestamp(
                    word=clean_word,
                    start_ms=current_ms,
                    end_ms=current_ms + duration_ms
                )
            )
            current_ms += duration_ms + 40 # 40ms silence gap between words

        duration_seconds = current_ms / 1000.0
        return duration_seconds, word_timestamps
