"""deslop_check.py, proven by its own failure on the two rules the
article-writer core relies on it for beyond its own checker.

Mutations it exists to catch: the em dash rule removed from DASH checks,
or "delve" dropped from HARD_BANS. Each test pairs a failing input with a
clean twin, so a linter that flags everything fails too.

Run: python3 -m unittest discover -s plugins/narsil-voice/tests
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                      "skills", "narsil-voice", "scripts", "deslop_check.py")
CLEAN = "Search is shattered. We rebuild the pages that answer the question.\n"


def lint(text):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
    try:
        p = subprocess.run([sys.executable, SCRIPT, f.name], capture_output=True, text=True)
        out = p.stdout + p.stderr
        # The script exits 0 by design and reports in its summary line.
        m = re.search(r"\| (\d+) fail", out)
        return (int(m.group(1)) if m else -1), out
    finally:
        os.unlink(f.name)


class DeslopCheck(unittest.TestCase):
    def test_clean_text_has_no_failures(self):
        fails, out = lint(CLEAN)
        self.assertEqual(fails, 0, out)

    def test_em_dash_fails(self):
        fails, out = lint(CLEAN.replace("shattered.", "shattered — badly."))
        self.assertGreater(fails, 0, out)
        self.assertIn("em dash", out)

    def test_banned_word_fails(self):
        fails, out = lint(CLEAN.replace("rebuild", "delve into"))
        self.assertGreater(fails, 0, out)
        self.assertIn("delve", out)


if __name__ == "__main__":
    unittest.main()
