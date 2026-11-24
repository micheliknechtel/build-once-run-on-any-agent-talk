# Build once, run on any agent — source kit

Everything needed to **edit and regenerate** the talk deck and the 3 demo videos in FR / EN / ES / DE.
Python dependencies are isolated in the repository's `.venv/`. Narration is
generated locally with Kokoro (EN / FR / ES) or NVIDIA Magpie (DE), not macOS `say`.

## Setup (macOS)

Run these commands from the **repository root**, not `source/`:

```bash
brew install uv ffmpeg espeak-ng
uv sync --locked
```

`uv` installs the Python 3.12 version selected by `.python-version` and creates
`.venv/` without changing the system Python. `pyproject.toml` declares the
dependencies; `uv.lock` pins the resolved packages. Use `uv run --locked ...` for
every build, or activate the environment with `source .venv/bin/activate`.
To recreate it on another machine, repeat `uv sync --locked`.

The configured public PyPI mirror is `https://mirrors.aliyun.com/pypi/simple/`:
the default `files.pythonhosted.org` download host was unreachable during setup.
To return to upstream PyPI when reachable, change the index URL in
`pyproject.toml` to `https://pypi.org/simple/`, then run `uv lock && uv sync`.
Do not install these packages into the global Python environment.

The renderers still use macOS Arial and Menlo fonts. Homebrew installs native
tools outside `.venv/`; Python libraries stay inside it.

## Narration models

All demo builders use [`speech.py`](speech.py). There is no fallback to `say`
or a hosted speech API. The first run downloads model weights; synthesis runs
on this machine. Allow several hundred MB for each model stack.

| Language | Model | Default voice |
|---|---|---|
| EN | [hexgrad/Kokoro-82M](https://github.com/hexgrad/kokoro) | `bf_emma` (female, British English) |
| FR | Kokoro-82M | `ff_siwis` (female) |
| ES | Kokoro-82M | `ef_dora` (female) |
| DE | [nvidia/magpie_tts_multilingual_357m](https://huggingface.co/nvidia/magpie_tts_multilingual_357m) | `Sofia` (female), speaking German |

Kokoro runs on CPU and produces 24 kHz mono WAV. The shared helper explicitly uses
Homebrew's eSpeak library/data on macOS, avoiding the bundled library's broken
build-machine data path. The English spaCy model is installed by `uv sync`;
no runtime `pip` command is needed. Kokoro weights/voices use Hugging Face's
normal local cache. Kokoro weights are Apache-2.0 licensed; Magpie and NanoCodec
use the NVIDIA Open Model License (see their model cards).

### German setup (Apple Silicon)

Magpie runs locally through NVIDIA's official
[NeMo-Speech.cpp](https://github.com/NVIDIA/NeMo-Speech.cpp) native Metal runtime.
This avoids adding the full NeMo/CUDA Python stack to the Mac environment.
From the repository root, install the pinned runtime and verify its checksum:

```bash
mkdir -p .tools/nemo-speech
gh release download v0.3.0 --repo NVIDIA/NeMo-Speech.cpp \
  --pattern 'nemo-speech-0.3.0-macos-aarch64-metal.tar.gz*' \
  --dir .tools/nemo-speech
(
  cd .tools/nemo-speech
  shasum -a 256 -c nemo-speech-0.3.0-macos-aarch64-metal.tar.gz.sha256
)
tar -xzf .tools/nemo-speech/nemo-speech-0.3.0-macos-aarch64-metal.tar.gz \
  -C .tools/nemo-speech
NEMO_SPEECH_MODEL_DIR="$PWD/.tools/models" \
  .tools/nemo-speech/nemo-speech-0.3.0-macos-aarch64-metal/bin/nemo-speech pull magpie
```

The runtime index pins Magpie v2607, its tokenizer, and the companion NanoCodec
decoder, and verifies model sizes and SHA-256 hashes. `.tools/` is ignored by Git.
`speech.py` finds this runtime automatically. For another platform/install,
follow NVIDIA's installation instructions and set `NEMO_SPEECH_BIN` to the
absolute path of the executable (or put `nemo-speech` on `PATH`).

### Generate a standalone audio track

```bash
uv run --locked python source/speech.py --language en \
  --text "Write the skills once, and reuse them across platforms." \
  --output source/output/EN/narration.wav
uv run --locked python source/speech.py --language de \
  --text "Dieselben Skills funktionieren mit einem anderen Agenten." \
  --output source/output/DE/narration.wav
```

Use `--voice` for standalone generation, or `TTS_VOICE` for a demo build:
`TTS_VOICE=af_heart uv run --locked python source/demo2/build_en.py`.
Choose a voice compatible with the language (`b` for British English, `f` for
French, `e` for Spanish). Magpie voices include Aria, Jason, John, Leo, and Sofia.

## Layout
| Folder | What | How it's made |
|---|---|---|
| `assets/` | original EN Proof-Agent video, real VS Code screen recording (`demo3-screen-recording.mov`, **only in the release zip**, 334 MB), GitHub issue/PR screenshots, title cards | inputs |
| `demo1/` | `build.py` + `fr.tsv` `es.tsv` `de.tsv` (`start_seconds<TAB>text`), `en.srt` = English narration input | dubs the original video with local model speech, extending scenes when needed |
| `demo2/` | `build_<lang>.py` | fully generated: PIL frames (terminal, issue, PR) + local model narration → ffmpeg |
| `demo3/` | `build_<lang>.py` | cuts of the real VS Code recording + title cards + local model narration |
| `deck/` | `base-deck-FR.pptx`, `notes_<lang>.py`, `slides/` (PNG renders), `build_deck.py`, `mkpdf.py` | swaps videos + posters into the deck, writes speaker notes, makes the notes PDF |

Outputs go to `source/output/<LANG>/`, temp files and per-segment WAV files to
`source/build/` (both safe to delete). Existing published files in the top-level
`EN/`, `FR/`, `ES/`, `DE/` folders do not change unless explicitly copied there.

## Rebuild

Demo 3 needs the original 334 MB VS Code recording, which is intentionally
distributed only in the source-kit release and ignored by Git. Download it once
from the repository root before building demo 3:

```bash
mkdir -p source/build source/assets
gh release download source-kit-v1 \
  --repo micheliknechtel/build-once-run-on-any-agent-talk \
  --pattern 'build-once-run-on-any-agent-source-kit.zip' \
  --dir source/build
unzip -p source/build/build-once-run-on-any-agent-source-kit.zip \
  source/assets/demo3-screen-recording.mov \
  > source/assets/demo3-screen-recording.mov
rm source/build/build-once-run-on-any-agent-source-kit.zip
```

Then run the desired language builder. The built video goes to
`source/output/<LANG>/`.

```bash
uv run --locked python source/demo1/build.py de   # en | fr | es | de
uv run --locked python source/demo2/build_de.py   # build_fr / build_en / build_es / build_de
uv run --locked python source/demo3/build_de.py
uv run --locked python source/deck/build_deck.py de  # needs 3 videos in source/output/DE
```

For the rewritten English demo 2:

```bash
uv run --locked python source/demo2/build_en.py
ffprobe -v error -show_entries format=duration \
  -show_entries stream=codec_type,codec_name,width,height,sample_rate \
  -of json source/output/EN/demo2-dataforge-EN.mp4
cp source/output/EN/demo2-dataforge-EN.mp4 EN/demo2-dataforge-EN.mp4
```

The narration strings and subtitles share the `S` list in `demo2/build_en.py`.
Scene lengths are computed from generated speech, with lead-in and tail pauses.
The rebuilt video is 1920×1080 at 30 fps, with H.264 video and AAC audio.
In every `demo3/build_<lang>.py`, each `sub` is both the displayed subtitle and the
narration; a subtitle spanning consecutive clips is spoken once. Title cards can
use a separate `say` field, but a scene cannot define both `sub` and `say`.
Technical-term pronunciation replacements apply only to speech, not captions.
Each language keeps its own current wording; rebuilding does not translate or
copy English script changes into the other languages.

All builders keep the complete generated speech and align scene durations to
video frames. Demo 1 groups English SRT fragments into coherent cues, retaining
their words. If speech exceeds the original scene window, the video holds its
last frame and shifts subsequent scenes and audio together. Demo 3 also holds
frames as needed; demo 2 derives scene lengths from speech. Speech is not sped up
to fit the old runtime. Intentional end cards and repeated-caption continuation
clips can be silent.
For demos 1 and 3, narration is joined as continuous PCM before a single AAC
encode, avoiding accumulated encoder padding between scenes.

The existing English demo 1 transcript includes apparent transcription errors
(for example, `CoQL` and `merge bottom`). These are preserved rather than silently
rewritten; review `demo1/en.srt` against the original before editorial corrections.
Updating a standalone video does **not** replace the video embedded in an
existing deck: put the other two videos in `source/output/EN/` and run the deck
builder separately if you also want a refreshed deck and notes PDF.
The deck builder requires all three rebuilt videos; it no longer falls back to
the original English demo 1. It refreshes all demo posters and the corresponding
movie rectangles in the notes PDF's slide previews. Unchanged slide areas reuse
the existing rasterized slide images; this is not a full presentation re-render.

Focused helper tests: `uv run --locked python -m unittest discover -s source -p 'test_*.py'`.

### Rebuild the complete four-language kit

After setup and downloading the demo 3 recording, run from the repository root.
Leave `TTS_VOICE` unset to use the four female voices above:

```bash
uv run --locked python -m unittest discover -s source -p 'test_*.py' &&
(
  set -e
  for lang in en fr es de; do
    uv run --locked python source/demo1/build.py "$lang"
    uv run --locked python "source/demo2/build_${lang}.py"
    uv run --locked python "source/demo3/build_${lang}.py"
    uv run --locked python source/validate.py --language "$lang"
    uv run --locked python source/deck/build_deck.py "$lang"
    uv run --locked python source/validate.py --language "$lang" --decks
  done
)
```

Each video has an adjacent JSON build manifest recording model, voice, intended
text, pronunciation text, cue timing, and intermediate WAV paths. Keep
`source/build/` until validation is finished. Validation checks script coverage,
frame/stream properties, full decoding, scene padding, and each synthesized
waveform's placement in the final AAC track. Deck checks verify slide/notes page
counts, unchanged speaker notes, and byte-identical embedded videos.
These checks detect missing or truncated audio, but do **not** establish that the
model pronounced every word intelligibly. Listen to the rebuilt videos for
pronunciation and naturalness before presenting them.

Only after all checks and audio review, replace published files explicitly:

```bash
for lang in EN FR ES DE; do
  cp "source/output/$lang/"*.mp4 "$lang/"
  cp "source/output/$lang/"*.pptx "$lang/"
  cp "source/output/$lang/"*-notes.pdf "$lang/"
done
```

This refreshes 12 standalone videos, four decks, and four notes PDFs. It does not
update the `source-kit-v1` GitHub release. Model weights and intermediate files
remain local and ignored by Git.

## Common edits
- **Change narration text** → edit the text strings in the script (demo 2/3), `demo1/en.srt` (English demo 1), or the translated `.tsv` (other demo 1 languages). Long cues extend scenes instead of speeding up speech.
- **Change the voice** → set `TTS_VOICE` for a build, or edit the defaults in `speech.py`.
- **Change speaker notes** → edit `deck/notes_<lang>.py`, rerun `build_deck.py`.
- **New language** → copy the `_en` files, translate the strings, and add an explicitly supported model/language mapping in `speech.py`.

## Notes
- The VS Code chat in the demo 3 recording is in French for all languages (it's the real session).
- Demo 2 shows a real repo: issue #1 and PR #2 in `micheliknechtel/dataforge-demo`.
- Source talk & demos: https://github.com/githubevents/build-once-run-on-any-agent
