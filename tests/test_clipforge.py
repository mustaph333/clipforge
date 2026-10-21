import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from clipforge import script, subtitles  # noqa: E402


class ScriptTests(unittest.TestCase):
    def test_offline_script_shape(self):
        os.environ.pop("GEMINI_API_KEY", None)
        scenes = script.build_script("the old medina of Tangier")
        self.assertGreaterEqual(len(scenes), 4)
        self.assertTrue(any("Tangier" in s for s in scenes))
        self.assertTrue(all(s.strip() for s in scenes))


class SubtitleTests(unittest.TestCase):
    def test_srt_timing(self):
        srt = subtitles.make_srt(["hello world", "second line"], [1.5, 2.0])
        self.assertIn("00:00:00,000 --> 00:00:01,500", srt)
        self.assertIn("00:00:01,500 --> 00:00:03,500", srt)
        self.assertIn("hello world", srt)


if __name__ == "__main__":
    unittest.main()
