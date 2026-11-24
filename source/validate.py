"""Validate staged local narration: uv run python source/validate.py [--language en] [--decks]."""

import argparse
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import re
import subprocess

import numpy as np
from pptx import Presentation
from PIL import Image

from demo1.build import read_rows
from narration import narration_text
from speech import KOKORO_VOICES, MAGPIE_MODEL

ROOT = Path(__file__).resolve().parent
NAMES = ("demo1-proof-agent", "demo2-dataforge", "demo3-vscode")
RATE = 16000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def decode_audio(path):
    return np.frombuffer(subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le",
        "-ac", "1", "-ar", str(RATE), "-",
    ]), dtype="<f4")


def match_audio(track, reference, expected_start):
    # Search around the expected cue to allow for AAC/concat encoder padding.
    padding = round(0.15 * RATE)
    start = round(expected_start * RATE)
    low = max(0, start - padding)
    high = min(len(track), start + len(reference) + padding)
    target = track[low:high].astype(np.float64)
    reference = reference.astype(np.float64)
    require(len(target) >= len(reference), "Final audio is shorter than its narration cue")
    size = 1 << (len(target) + len(reference) - 1).bit_length()
    correlation = np.fft.irfft(
        np.fft.rfft(target, size) * np.fft.rfft(reference[::-1], size), size,
    )[len(reference) - 1:len(target)]
    energy = np.concatenate(([0.0], np.cumsum(target * target)))
    windows = energy[len(reference):] - energy[:-len(reference)]
    reference_energy = np.dot(reference, reference)
    require(reference_energy > 0.001, "Narration waveform is empty or silent")
    scores = correlation / np.sqrt(np.maximum(windows * reference_energy, 1e-20))
    best = int(np.argmax(scores))
    return float(scores[best]), (low + best) / RATE


def expected_cues(demo, language):
    if demo == 1:
        return [text for _, text in read_rows(language)]
    module = importlib.import_module(f"demo{demo}.build_{language}")
    if demo == 2:
        return [text for text, _ in module.S]
    result = []
    previous = None
    for segment in module.SEG:
        result.append(narration_text(segment, previous))
        previous = segment.get("sub")
    return result


def validate_video(demo, language):
    video = ROOT / "output" / language.upper() / f"{NAMES[demo-1]}-{language.upper()}.mp4"
    manifest = json.loads(video.with_suffix(".json").read_text(encoding="utf-8"))
    require(manifest["language"] == language, f"Wrong language: {video}")
    require(
        manifest["model"] == (MAGPIE_MODEL if language == "de" else "hexgrad/Kokoro-82M"),
        f"Wrong local model: {video}",
    )
    require(
        manifest["voice"] == (os.environ.get("TTS_VOICE") or (
            "Sofia" if language == "de" else KOKORO_VOICES[language][1]
        )),
        f"Unexpected voice: {video}",
    )
    cues = manifest["cues"]
    require([cue["text"] for cue in cues] == expected_cues(demo, language),
            f"Missing, extra, or changed narration cues: {video}")
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video),
    ]))
    streams = {stream["codec_type"]: stream for stream in probe["streams"]}
    require(set(streams) == {"video", "audio"}, f"Missing/extra streams: {video}")
    vs, aus = streams["video"], streams["audio"]
    require(vs["codec_name"] == "h264" and aus["codec_name"] == "aac", f"Wrong codecs: {video}")
    require((vs["width"], vs["height"]) == (1920, 1200 if demo == 3 else 1080),
            f"Wrong dimensions: {video}")
    require(vs["r_frame_rate"] == "30/1", f"Wrong frame rate: {video}")
    require(aus["sample_rate"] == "48000", f"Wrong audio sample rate: {video}")
    require(abs(float(vs["duration"]) - float(aus["duration"])) < 0.12,
            f"Audio/video end drift: {video}")
    end = cues[-1]["start"] + cues[-1]["duration"]
    require(abs(float(probe["format"]["duration"]) - end) < 0.15,
            f"Unexpected/truncated duration: {video}")
    subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(video),
                    "-map", "0:v", "-map", "0:a", "-f", "null", "-"], check=True)
    track = decode_audio(video)
    scores = []
    previous_end = 0
    for index, cue in enumerate(cues):
        require(abs(cue["start"] - previous_end) < 1 / 30,
                f"Noncontiguous scene {index}: {video}")
        previous_end = cue["start"] + cue["duration"]
        if not cue["text"]:
            require(not cue["wav"] and cue["audio_duration"] == 0,
                    f"Unexpected narration on silent cue {index}: {video}")
            silence = track[
                round((cue["start"] + 0.05) * RATE):
                round((previous_end - 0.05) * RATE)
            ]
            require(len(silence) > 0 and np.max(np.abs(silence)) < 0.002,
                    f"Unexpected sound on silent cue {index}: {video}")
            continue
        reference = decode_audio(cue["wav"])
        require(len(reference) > 0, f"Empty cue {index}: {video}")
        require(abs(len(reference) / RATE - cue["audio_duration"]) < 0.01,
                f"Cue duration differs from waveform {index}: {video}")
        require(cue["audio_start"] + len(reference) / RATE < previous_end,
                f"Narration cut off by scene {index}: {video}")
        score, actual_start = match_audio(track, reference, cue["audio_start"])
        require(score >= 0.95,
                f"Missing/damaged narration cue {index} (correlation {score:.3f}): {video}")
        require(abs(actual_start - cue["audio_start"]) < 0.10,
                f"Misplaced narration cue {index}: {video}")
        scores.append(score)
    if demo == 1:
        require(cues[0]["source_start"] == 0, "Demo 1 loses its opening")
        for before, after in zip(cues, cues[1:]):
            require(before["source_end"] == after["source_start"], "Demo 1 loses source footage")
        original_end = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", str(ROOT / "assets" / "demo1-original-EN.mp4"),
        ]))
        require(abs(cues[-1]["source_end"] - original_end) < 0.001,
                "Demo 1 loses its final source footage")
    print(f"{video.name}: {end:.2f}s; {len(scores)} spoken cues; "
          f"minimum waveform correlation {min(scores):.4f}", flush=True)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).digest()


def validate_deck(language):
    output = ROOT / "output" / language.upper()
    deck = output / f"talk-build-once-run-on-any-agent-{language.upper()}.pptx"
    presentation = Presentation(deck)
    notes = importlib.import_module(f"deck.notes_{language}").N
    require(len(presentation.slides) == 16, f"Wrong slide count: {deck}")
    for number, slide in enumerate(presentation.slides, 1):
        require(slide.notes_slide.notes_text_frame.text == notes[number],
                f"Changed notes on slide {number}: {deck}")
    for number, name in zip((6, 8, 9), NAMES):
        slide = presentation.slides[number - 1]
        movies = [shape for shape in slide.shapes if shape.shape_type == 16]
        require(len(movies) == 1, f"Missing embedded movie on slide {number}: {deck}")
        relationship = movies[0]._element.xpath(".//a:videoFile")[0].get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link"
        )
        embedded = slide.part.rels[relationship].target_part.blob
        standalone = output / f"{name}-{language.upper()}.mp4"
        require(hashlib.sha256(embedded).digest() == digest(standalone),
                f"Stale embedded video on slide {number}: {deck}")
        poster_id = movies[0]._element.xpath(".//a:blip")[0].get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"
        )
        poster = Image.open(io.BytesIO(slide.part.rels[poster_id].target_part.blob)).convert("RGB")
        frame = subprocess.check_output([
            "ffmpeg", "-v", "error", "-ss", "2", "-i", str(standalone),
            "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-",
        ])
        expected = Image.open(io.BytesIO(frame)).convert("RGB")
        require(poster.size == expected.size and poster.tobytes() == expected.tobytes(),
                f"Stale poster on slide {number}: {deck}")
    pdf = deck.with_name(deck.stem + "-notes.pdf").read_bytes()
    require(len(re.findall(rb"/Type\s*/Page\b", pdf)) == 16, f"Wrong notes PDF page count: {deck}")
    print(f"{deck.name}: 16 slides/notes pages; all three embedded videos match", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=["en", "fr", "es", "de"])
    parser.add_argument("--decks", action="store_true")
    args = parser.parse_args()
    for language in ([args.language] if args.language else ["en", "fr", "es", "de"]):
        for demo in (1, 2, 3):
            validate_video(demo, language)
        if args.decks:
            validate_deck(language)
