"""Shared cue selection, frame-aligned timing, and build evidence."""

import json
import math
import os
from pathlib import Path
import subprocess
import wave

from speech import KOKORO_VOICES, MAGPIE_MODEL


def narration_text(segment, previous_subtitle):
    subtitle = segment.get("sub")
    if subtitle and segment.get("say"):
        raise ValueError("Use the subtitle as narration instead of a separate say field")
    if subtitle:
        return None if subtitle == previous_subtitle else subtitle
    return segment.get("say")


def scene_duration(video_duration, audio_duration, *, lead=0.3, tail=0.5, fps=30):
    return math.ceil(max(video_duration, lead + audio_duration + tail) * fps) / fps


def write_audio_track(cues, output, sample_rate=48000):
    """Encode AAC only after joining PCM, avoiding per-clip encoder padding."""
    cursor = 0
    with wave.open(str(output), "wb") as track:
        track.setnchannels(1)
        track.setsampwidth(2)
        track.setframerate(sample_rate)
        for cue in cues:
            end = round((cue["start"] + cue["duration"]) * sample_rate)
            if cue["wav"]:
                start = round(cue["audio_start"] * sample_rate)
                raw = subprocess.check_output([
                    "ffmpeg", "-v", "error", "-i", cue["wav"],
                    "-f", "s16le", "-ac", "1", "-ar", str(sample_rate), "-",
                ])
                if start < cursor or start + len(raw) // 2 > end:
                    raise ValueError(f"Narration does not fit its scene: {cue['text']}")
                track.writeframes(b"\0\0" * (start - cursor))
                track.writeframes(raw)
                cursor = start + len(raw) // 2
            track.writeframes(b"\0\0" * (end - cursor))
            cursor = end


def write_manifest(video, language, cues):
    video = Path(video)
    voice = os.environ.get("TTS_VOICE") or (
        "Sofia" if language == "de" else KOKORO_VOICES[language][1]
    )
    video.with_suffix(".json").write_text(
        json.dumps(
            {
                "video": str(video.resolve()),
                "language": language,
                "model": MAGPIE_MODEL if language == "de" else "hexgrad/Kokoro-82M",
                "voice": voice,
                "cues": cues,
            },
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
