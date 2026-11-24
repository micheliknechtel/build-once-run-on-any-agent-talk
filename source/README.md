# Build once, run on any agent — source kit

Everything needed to **edit and regenerate** the talk deck and the 3 demo videos in FR / EN / ES / DE.
No hidden tool: Python + Pillow + ffmpeg + the macOS `say` voices.

## Requirements (macOS)
```bash
brew install ffmpeg
pip3 install pillow python-pptx reportlab
```
Voices used (System Settings → Accessibility → Spoken Content → Manage Voices):
FR **Thomas** (demos 2-3) / **Amélie** (demo 1) · EN **Daniel** · ES **Mónica** · DE **Anna**.
Premium/Enhanced voices (e.g. Ava, Zoe, Evan) sound better — just change the voice name in the script.

## Layout
| Folder | What | How it's made |
|---|---|---|
| `assets/` | original EN Proof-Agent video, real VS Code screen recording (`demo3-screen-recording.mov`, **only in the release zip**, 334 MB), GitHub issue/PR screenshots, title cards | inputs |
| `demo1/` | `build.py` + `fr.tsv` `es.tsv` `de.tsv` (`start_seconds<TAB>text`), `en.srt` = original transcript | dubs the original video with `say`, timed per segment |
| `demo2/` | `build_<lang>.py` | fully generated: PIL frames (terminal, issue, PR) + `say` narration → ffmpeg |
| `demo3/` | `build_<lang>.py` | cuts of the real VS Code recording + title cards + `say` narration |
| `deck/` | `base-deck-FR.pptx`, `notes_<lang>.py`, `slides/` (PNG renders), `build_deck.py`, `mkpdf.py` | swaps videos + posters into the deck, writes speaker notes, makes the notes PDF |

Outputs go to `output/<LANG>/`, temp files to `build/` (both safe to delete).

## Rebuild
```bash
python3 demo1/build.py de          # fr | es | de  (EN = original video)
python3 demo2/build_de.py          # build_fr / build_en / build_es / build_de
python3 demo3/build_de.py
python3 deck/build_deck.py de      # needs the 3 videos in output/DE first
```

## Common edits
- **Change narration text** → edit the text strings in the script (demo 2/3) or the `.tsv` (demo 1). In demo 1, a line flagged `too long` will be sped up — shorten it.
- **Change the voice** → search for `'say','-v'` (demo 2/3) or `VOICE` (demo 1) and set another `say` voice (`say -v '?'` lists them).
- **Change speaker notes** → edit `deck/notes_<lang>.py`, rerun `build_deck.py`.
- **New language** → copy the `_en` files, translate the strings, pick a voice.

## Notes
- The VS Code chat in the demo 3 recording is in French for all languages (it's the real session).
- Demo 2 shows a real repo: issue #1 and PR #2 in `micheliknechtel/dataforge-demo`.
- Source talk & demos: https://github.com/githubevents/build-once-run-on-any-agent
