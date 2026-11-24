import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import wave

import numpy as np

import speech
from demo3.build_en import SEG, narration_text, phon
from demo1.build import read_srt
from narration import scene_duration, write_audio_track


class SpeechTests(unittest.TestCase):
    def test_kokoro_writes_every_chunk_as_mono_pcm_wav(self):
        for language in ("en", "fr", "es"):
            with self.subTest(language=language), tempfile.TemporaryDirectory() as work:
                output = Path(work) / "nested" / "speech.wav"
                chunks = [
                    ("first", "", np.full(2400, 0.25, dtype=np.float32)),
                    ("second", "", np.full(1200, -0.25, dtype=np.float32)),
                ]
                with patch.dict(os.environ, {"TTS_VOICE": ""}), patch.object(
                    speech, "_pipeline"
                ) as pipeline:
                    pipeline.return_value.return_value = iter(chunks)
                    speech.synthesize("Two chunks.", language, output)
                pipeline.assert_called_once_with(language)
                pipeline.return_value.assert_called_once_with(
                    "Two chunks.", voice=speech.KOKORO_VOICES[language][1], speed=1
                )
                with wave.open(str(output)) as audio:
                    self.assertEqual((audio.getnchannels(), audio.getsampwidth()), (1, 2))
                    self.assertEqual(audio.getframerate(), 24000)
                    self.assertEqual(audio.getnframes(), 3600)
                    samples = np.frombuffer(audio.readframes(3600), dtype="<i2")
                    self.assertTrue(np.all(samples[:2400] > 0))
                    self.assertTrue(np.all(samples[2400:] < 0))

    def test_empty_model_output_fails_instead_of_writing_silence(self):
        with tempfile.TemporaryDirectory() as work, patch.object(speech, "_pipeline") as pipeline:
            pipeline.return_value.return_value = iter([])
            output = Path(work) / "speech.wav"
            with self.assertRaisesRegex(RuntimeError, "produced no audio"):
                speech.synthesize("Hello.", "en", output)
            self.assertFalse(output.exists())

    def test_german_routes_to_local_magpie_with_german_language(self):
        with tempfile.TemporaryDirectory() as work, patch.dict(
            os.environ, {"NEMO_SPEECH_BIN": "/test/nemo-speech", "TTS_VOICE": ""}
        ), patch.object(speech.subprocess, "run") as run:
            output = Path(work) / "speech.wav"
            speech.synthesize("Hallo.", "de", output, voice="Sofia")
            command = run.call_args.args[0]
            self.assertEqual(command[:3], ["/test/nemo-speech", "synthesize", "Hallo."])
            self.assertEqual(command[command.index("--magpie-model") + 1], speech.MAGPIE_MODEL)
            self.assertEqual(command[command.index("--language") + 1], "de-DE")
            self.assertEqual(command[command.index("--voice") + 1], "Sofia")
            self.assertEqual(command[command.index("--output") + 1], str(output.resolve()))
            self.assertTrue(run.call_args.kwargs["check"])

    def test_invalid_requests_do_not_load_a_model(self):
        with patch.object(speech, "_pipeline") as pipeline:
            for text, language, output in (
                ("Hello", "it", "speech.wav"),
                (" ", "en", "speech.wav"),
                ("Hello", "en", "speech.aiff"),
            ):
                with self.subTest(text=text, language=language, output=output):
                    with self.assertRaises(ValueError):
                        speech.synthesize(text, language, output)
            pipeline.assert_not_called()

    def test_pcm_resamples_for_video_builder(self):
        with patch.object(speech, "synthesize", return_value=Path("speech.wav")), patch.object(
            speech.subprocess, "check_output", return_value=b"\x01\x00"
        ) as convert:
            self.assertEqual(speech.pcm("Hello.", "en", "speech.wav"), b"\x01\x00")
            self.assertEqual(
                convert.call_args.args[0],
                ["ffmpeg", "-v", "error", "-i", "speech.wav", "-f", "s16le",
                 "-ac", "1", "-ar", "48000", "-"],
            )


class Demo3NarrationTests(unittest.TestCase):
    def test_every_subtitle_is_spoken_once_per_contiguous_cue(self):
        previous = None
        spoken = []
        for segment in SEG:
            text = narration_text(segment, previous)
            subtitle = segment.get("sub")
            if subtitle:
                self.assertEqual(text, None if subtitle == previous else subtitle)
            if text:
                spoken.append(text)
            previous = subtitle
        self.assertIn("The agent follows the forge skills: it reads, checks, validates the manifest…", spoken)
        self.assertIn("In the terminal, I run the program that prepares the work…", spoken)
        self.assertIn("Result: 207 unresolved incidents, 54 resolved. And the PR was not created.", spoken)
        self.assertEqual(spoken.count("I ask: count the incidents in DuckDB… then open a pull request right away."), 1)

    def test_caption_and_separate_narration_cannot_drift(self):
        with self.assertRaisesRegex(ValueError, "subtitle as narration"):
            narration_text({"sub": "Complete caption", "say": "Incomplete"}, None)
        self.assertEqual(narration_text({"say": "Opening card"}, None), "Opening card")

    def test_technical_terms_are_expanded_for_speech(self):
        self.assertEqual(
            phon("Use /forge and DuckDB; check the PR and SQL."),
            "Use slash forge and duck D B; check the P R and S Q L.",
        )


class MultilingualNarrationTests(unittest.TestCase):
    def test_all_demo3_languages_speak_the_complete_subtitles(self):
        import importlib
        for language in ("en", "fr", "es", "de"):
            module = importlib.import_module(f"demo3.build_{language}")
            with self.subTest(language=language):
                previous = None
                spoken = []
                for segment in module.SEG:
                    text = narration_text(segment, previous)
                    subtitle = segment.get("sub")
                    if subtitle:
                        self.assertEqual(text, None if subtitle == previous else subtitle)
                    if text:
                        spoken.append(text)
                    previous = subtitle
                self.assertEqual(len(spoken), 11)
                self.assertIn(module.SEG[5]["sub"], spoken)
                self.assertIn(module.SEG[7]["sub"], spoken)
                self.assertIn(module.SEG[8]["sub"], spoken)
                self.assertNotIn("/", module.phon(module.SEG[1]["sub"]))

    def test_srt_groups_fragments_without_losing_words_or_final_cue(self):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "en.srt"
            path.write_text(
                "1\n00:00:00,000 --> 00:00:01,000\nA verifier\n\n"
                "2\n00:00:01,000 --> 00:00:02,000\nchecks the diff.\n\n"
                "3\n00:00:02,000 --> 00:00:03,000\nFinal words\n",
                encoding="utf-8",
            )
            self.assertEqual(read_srt(path), [
                (0, "A verifier checks the diff."), (2, "Final words"),
            ])

    def test_srt_rejects_overlapping_cues(self):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "en.srt"
            path.write_text(
                "1\n00:00:00,000 --> 00:00:02,000\nFirst.\n\n"
                "2\n00:00:01,000 --> 00:00:03,000\nSecond.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "overlapping"):
                read_srt(path)

    def test_slow_narration_extends_scene_and_shifts_next_cue(self):
        first = scene_duration(2, 4, lead=0.15, tail=0.35)
        second = scene_duration(3, 1, lead=0.15, tail=0.35)
        self.assertEqual(first, 4.5)
        self.assertEqual(second, 3)
        self.assertGreaterEqual(first, 0.15 + 4 + 0.35)
        self.assertEqual(first + second, 7.5)

    def test_demo2_speech_and_padding_share_exact_frame_duration(self):
        for audio in (0.001, 1.0123, 8.999, 13.723):
            duration = scene_duration(0, audio, lead=0.4, tail=1)
            self.assertAlmostEqual(duration * 30, round(duration * 30))
            self.assertGreaterEqual(round(duration * 48000), int(0.4 * 48000) + round(audio * 48000))

    def test_demo2_encoder_failure_does_not_publish_success(self):
        from demo2 import build_fr
        previous = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as work, patch.object(
                build_fr, "WORK", work
            ), patch.object(build_fr, "OUT", work), patch.object(
                build_fr, "S", []
            ), patch.object(build_fr.sp, "Popen") as encoder:
                encoder.return_value.wait.return_value = 1
                with self.assertRaisesRegex(RuntimeError, "failed to encode"):
                    build_fr.build()
        finally:
            os.chdir(previous)

    def test_waveform_check_detects_dropped_audio(self):
        from validate import match_audio, RATE
        reference = np.random.default_rng(42).normal(0, 0.1, RATE)
        track = np.zeros(RATE * 3)
        track[RATE:RATE * 2] = reference
        score, start = match_audio(track, reference, 1)
        self.assertGreater(score, 0.999)
        self.assertEqual(start, 1)
        score, _ = match_audio(np.zeros_like(track), reference, 1)
        self.assertLess(score, 0.95)

    def test_continuous_pcm_has_exact_cue_positions_without_clip_padding(self):
        cues = [
            dict(start=0, duration=1, audio_start=0.1, wav="first.wav", text="First"),
            dict(start=1, duration=1.5, audio_start=1.3, wav="second.wav", text="Second"),
            dict(start=2.5, duration=0.5, audio_start=2.5, wav=None, text=None),
        ]
        raw = np.full(200, 1234, dtype="<i2").tobytes()
        with tempfile.TemporaryDirectory() as work, patch(
            "narration.subprocess.check_output", return_value=raw
        ):
            output = Path(work) / "track.wav"
            write_audio_track(cues, output, sample_rate=1000)
            with wave.open(str(output)) as track:
                self.assertEqual(track.getnframes(), 3000)
                samples = np.frombuffer(track.readframes(3000), dtype="<i2")
            expected = np.zeros(3000, dtype="<i2")
            expected[100:300] = 1234
            expected[1300:1500] = 1234
            np.testing.assert_array_equal(samples, expected)

    def test_continuous_track_rejects_audio_that_would_be_cut(self):
        cue = dict(start=0, duration=0.5, audio_start=0.3, wav="long.wav", text="Long")
        with tempfile.TemporaryDirectory() as work, patch(
            "narration.subprocess.check_output", return_value=b"\x01\x00" * 1000
        ):
            with self.assertRaisesRegex(ValueError, "does not fit"):
                write_audio_track([cue], Path(work) / "track.wav", sample_rate=1000)


if __name__ == "__main__":
    unittest.main()
