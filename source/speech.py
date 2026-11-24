"""Local narration: Kokoro for EN/FR/ES, NVIDIA Magpie for DE."""

import argparse
from functools import lru_cache
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
NEMO_VERSION = "0.3.0"
KOKORO_VOICES = {"en": ("b", "bf_emma"), "fr": ("f", "ff_siwis"), "es": ("e", "ef_dora")}
MAGPIE_MODEL = "nvidia/magpie_tts_multilingual_357m"


@lru_cache(maxsize=3)
def _pipeline(language):
    from kokoro import KPipeline

    if sys.platform == "darwin":
        from phonemizer.backend.espeak.wrapper import EspeakWrapper

        executable = shutil.which("espeak-ng")
        if not executable:
            raise RuntimeError("Kokoro on macOS requires: brew install espeak-ng")
        prefix = Path(executable).resolve().parent.parent
        # The bundled macOS eSpeak library references a build-machine data path.
        EspeakWrapper.set_library(str(prefix / "lib" / "libespeak-ng.dylib"))
        EspeakWrapper.set_data_path(str(prefix / "share" / "espeak-ng-data"))
    return KPipeline(
        lang_code=KOKORO_VOICES[language][0],
        repo_id="hexgrad/Kokoro-82M",
        device="cpu",
    )


def synthesize(text, language, output, *, voice=None):
    """Write a mono WAV, keeping all inference and narration on this machine."""
    if language not in (*KOKORO_VOICES, "de"):
        raise ValueError(f"Unsupported narration language: {language}")
    if not text.strip():
        raise ValueError("Narration text must not be empty")
    output = Path(output).resolve()
    if output.suffix.lower() != ".wav":
        raise ValueError("Narration output must be a .wav file")
    output.parent.mkdir(parents=True, exist_ok=True)
    voice = voice or os.environ.get("TTS_VOICE")
    if language == "de":
        runtime = ROOT.parent / ".tools" / "nemo-speech" / (
            f"nemo-speech-{NEMO_VERSION}-macos-aarch64-metal/bin/nemo-speech"
        )
        executable = os.environ.get("NEMO_SPEECH_BIN") or (
            str(runtime) if runtime.is_file() else shutil.which("nemo-speech")
        )
        if not executable:
            raise RuntimeError("Install NeMo-Speech.cpp; see source/README.md (German setup).")
        env = os.environ.copy()
        env.setdefault("NEMO_SPEECH_MODEL_DIR", str(ROOT.parent / ".tools" / "models"))
        subprocess.run(
            [
                executable, "synthesize", text,
                "--magpie-model", MAGPIE_MODEL,
                "--language", "de-DE", "--voice", voice or "Sofia",
                "--seed", "1", "--output", str(output), "--force",
            ],
            env=env,
            check=True,
        )
    else:
        import numpy as np
        import soundfile as sf

        chunks = [
            audio.numpy() if hasattr(audio, "numpy") else np.asarray(audio)
            for _, _, audio in _pipeline(language)(
                text, voice=voice or KOKORO_VOICES[language][1], speed=1
            )
            if audio is not None and len(audio)
        ]
        if not chunks:
            raise RuntimeError(f"Kokoro produced no audio for {language}: {text!r}")
        sf.write(output, np.concatenate(chunks), 24000, subtype="PCM_16")
    return output


def pcm(text, language, output, sample_rate=48000):
    """Return signed 16-bit mono PCM at the rate expected by the video builder."""
    wav = synthesize(text, language, output)
    return subprocess.check_output(
        [
            "ffmpeg", "-v", "error", "-i", str(wav),
            "-f", "s16le", "-ac", "1", "-ar", str(sample_rate), "-",
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=["en", "fr", "es", "de"], required=True)
    parser.add_argument("--text", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--voice")
    args = parser.parse_args()
    synthesize(args.text, args.language, args.output, voice=args.voice)
