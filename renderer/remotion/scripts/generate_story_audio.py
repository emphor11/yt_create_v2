#!/usr/bin/env python3
"""
Generates real spoken voice tracks and word-level timestamps using macOS TTS (Aman, en_IN) + ffmpeg.
Saves audible MP3s to renderer/remotion/public/ and emits word timestamp JSON data.
"""

import json
import subprocess
from pathlib import Path

PUBLIC_DIR = Path("renderer/remotion/public")
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

STORIES = {
    "loan_story": {
        "audio_file": "loan_narration.mp3",
        "chunks": [
            ("A 50 lakh rupee home loan starts at 8.5 percent interest.", 400),
            ("When the benchmark rate rises to 10.5 percent...", 350),
            ("...the monthly EMI surges to 49,919 rupees, adding a heavy burden.", 350),
            ("...snowballing into 15.6 lakh in extra interest over 20 years.", 350),
        ],
    },
    "inflation_story": {
        "audio_file": "inflation_narration.mp3",
        "chunks": [
            ("You keep 10 lakh rupees safely parked in a savings account.", 400),
            ("At a stubborn 7 percent annual inflation rate...", 350),
            ("...your real purchasing power is quietly cut in half over 10 years.", 350),
        ],
    },
    "salary_split_story": {
        "audio_file": "salary_split_narration.mp3",
        "chunks": [
            ("A 50 lakh rupee executive salary is not what hits your bank account.", 400),
            ("15 lakh goes to income taxes, and 10 lakh covers living expenses...", 350),
            ("...leaving you with exactly 25 lakh in real net savings.", 350),
        ],
    },
}

def generate_story(name, data):
    print(f"Generating voice audio for {name}...")
    chunk_files = []
    word_timestamps = []
    current_ms = 0

    for i, (text, pause_after) in enumerate(data["chunks"]):
        aiff_path = f"/tmp/{name}_chunk_{i}.aiff"
        subprocess.run(["say", "-v", "Aman", "-o", aiff_path, text], check=True)
        chunk_files.append(aiff_path)

        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", aiff_path],
            capture_output=True, text=True, check=True
        )
        dur_sec = float(res.stdout.strip())
        dur_ms = int(dur_sec * 1000)

        words = text.split()
        per_word = dur_ms / len(words)
        for j, w in enumerate(words):
            clean_w = w.strip(".,;:!?\"")
            s_ms = int(current_ms + j * per_word)
            e_ms = int(s_ms + per_word)
            word_timestamps.append({
                "word": clean_w,
                "start_ms": s_ms,
                "end_ms": e_ms,
            })
        current_ms += dur_ms + pause_after

    # Concatenate chunks into final MP3
    mp3_path = PUBLIC_DIR / data["audio_file"]
    filter_inputs = "".join(f"[{i}:a]" for i in range(len(chunk_files)))
    filter_complex = f"{filter_inputs}concat=n={len(chunk_files)}:v=0:a=1[out]"
    cmd = ["ffmpeg", "-y"]
    for f in chunk_files:
        cmd.extend(["-i", f])
    cmd.extend(["-filter_complex", filter_complex, "-map", "[out]", "-acodec", "libmp3lame", "-ar", "44100", "-ab", "128k", str(mp3_path)])
    subprocess.run(cmd, capture_output=True, check=True)

    # Check volume
    vol_res = subprocess.run(["ffmpeg", "-i", str(mp3_path), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    mean_vol = [l.strip() for l in vol_res.stderr.splitlines() if "mean_volume" in l]
    print(f"  ✓ Saved {mp3_path} ({mean_vol[0] if mean_vol else 'OK'})")

    # Save timestamps JSON
    json_path = PUBLIC_DIR / f"{name}_timestamps.json"
    full_text = " ".join(t[0] for t in data["chunks"])
    payload = {
        "audio_file": data["audio_file"],
        "total_duration_ms": current_ms,
        "full_text": full_text,
        "word_timestamps": word_timestamps,
    }
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  ✓ Saved timestamps to {json_path} ({len(word_timestamps)} words)")

if __name__ == "__main__":
    for name, data in STORIES.items():
        generate_story(name, data)
    print("\nAll story audio and word timestamps generated successfully!")
