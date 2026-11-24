"""Dub Proof Agent with local speech: uv run python source/demo1/build.py en|fr|es|de."""

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from narration import scene_duration, write_audio_track, write_manifest
from speech import synthesize


def timestamp(value):
    hours, minutes, seconds = value.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def read_srt(path):
    rows = []
    pending = []
    start = None
    previous_end = 0
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = block.splitlines()
        begin, end = [timestamp(t.strip()) for t in lines[1].split("-->")]
        if begin < previous_end or end <= begin:
            raise ValueError(f"Invalid or overlapping SRT cue: {block}")
        previous_end = end
        text = " ".join(line.strip() for line in lines[2:]).strip()
        if not text:
            raise ValueError(f"Empty SRT cue: {block}")
        if start is None:
            start = begin
        pending.append(text)
        if re.search(r'[.!?]["\u201d]?\s*$', text) or len(" ".join(pending)) >= 350:
            rows.append((start, " ".join(pending)))
            pending, start = [], None
    if pending:
        rows.append((start, " ".join(pending)))
    return rows


def read_rows(language):
    if language == "en":
        return read_srt(ROOT / "demo1" / "en.srt")
    return [
        (float(start), text)
        for start, text in (
            line.split("\t", 1)
            for line in (ROOT / "demo1" / f"{language}.tsv").read_text(
                encoding="utf-8"
            ).strip().splitlines()
        )
    ]


def duration(path):
    return float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(path),
    ]))


def build(language):
    src = ROOT / "assets" / "demo1-original-EN.mp4"
    end = duration(src)
    work = ROOT / "build" / f"demo1-{language}"
    work.mkdir(parents=True, exist_ok=True)
    output = ROOT / "output" / language.upper() / f"demo1-proof-agent-{language.upper()}.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = read_rows(language)
    if not rows or rows[0][0] != 0:
        raise ValueError("Narration must start at source time zero")
    if any(not text.strip() or start < 0 or start >= end for start, text in rows):
        raise ValueError("Empty narration or cue outside the source recording")
    if any(a[0] >= b[0] for a, b in zip(rows, rows[1:])):
        raise ValueError("Narration cue timestamps must increase")
    audio = []
    for i, (_, text) in enumerate(rows):
        wav = work / f"seg{i}.wav"
        synthesize(text, language, wav)
        audio.append((wav, duration(wav)))
    cues = []
    parts = []
    offset = 0
    for i, ((start, text), (wav, ad)) in enumerate(zip(rows, audio)):
        stop = rows[i + 1][0] if i + 1 < len(rows) else end
        source_duration = stop - start
        total = scene_duration(source_duration, ad, lead=0.15, tail=0.35)
        part = work / f"seg{i}.mp4"
        filters = (
            f"[0:v]setpts=PTS-STARTPTS,fps=30,"
            f"tpad=stop_mode=clone:stop_duration={total-source_duration+0.1},"
            f"trim=duration={total},format=yuv420p[v]"
        )
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", str(start), "-t", str(source_duration),
            "-i", str(src), "-filter_complex", filters,
            "-map", "[v]", "-an", "-t", str(total), "-r", "30",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            str(part),
        ], check=True)
        cues.append(dict(
            text=text, spoken_text=text, wav=str(wav.resolve()), start=offset,
            duration=total, audio_start=offset + 0.15, audio_duration=ad,
            source_start=start, source_end=stop,
        ))
        offset += total
        parts.append(part)
        print(i, round(total, 2), flush=True)
    listing = work / "list.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    track = work / "voice.wav"
    write_audio_track(cues, track)
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
        "-i", str(listing), "-i", str(track), "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", str(output),
    ], check=True)
    write_manifest(output, language, cues)
    print(output, duration(output), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language", choices=["en", "fr", "es", "de"])
    build(parser.parse_args().language)
