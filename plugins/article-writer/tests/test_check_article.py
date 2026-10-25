"""Every check in check_article.py, proven by its own failure.

GOOD is a fixture that passes every check. Each MUTATIONS entry changes one
thing and must make exactly the named check report, by name, while every
other check stays clean. A mutation that trips a second check, or none, fails
the test: that is how a hollow check would show.

Run: python3 -m unittest discover -s plugins/article-writer/tests
"""
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "skills", "article-writer", "scripts")
sys.path.insert(0, SCRIPTS)

import check_article as ca  # noqa: E402

GOOD = """---
title: "How to Write a Meta Description That Gets Clicks"
slug: write-meta-description
description: "How to write a meta description that earns the click: lead with the answer, keep it under 155 characters, and match the search."
keyword: write a meta description
tldr: "Lead with the answer and stay under the limit."
faqs:
  - q: "How long should it be?"
    a: "Under 155 characters, so it is not cut off."
---

To write a meta description that gets clicks, lead with the answer the searcher wants and stop before the cut-off.

## Why it matters

A description is the pitch under your title. It does not change rankings; it changes whether anyone picks you.

We unlock the template with an email, and this is the highest-leverage edit on the page.

<!-- Sources checked 2026-10-25:
https://developers.google.com/search/docs/appearance/snippet : Google may use the meta description for the snippet; an em dash — quoted from a source is fine here.
Internal: none.
-->
"""

TOO_LONG = "x" * 156

MUTATIONS = {
    # name: (check expected to fire, old text, new text)
    "required field missing": ("required", 'tldr: "Lead with the answer and stay under the limit."\n', ""),
    "description over the limit": ("description", 'description: "How to write', f'description: "{TOO_LONG} How to write'),
    "em dash in the body": ("em_dash", "stop before the cut-off.", "stop — before the cut-off."),
    "em dash in the frontmatter": ("em_dash", 'tldr: "Lead with', 'tldr: "Lead — with'),
    "banned word": ("banned", "It does not change rankings", "It does not delve into rankings"),
    "banned inflection": ("banned", "It does not change rankings", "It is leveraging rankings"),
    "unlock as hype": ("banned", "We unlock the template with an email", "We unlock growth with an email"),
    "leverage verb beside the noun": ("banned", "highest-leverage edit", "highest-leverage edit we leverage"),
    # The real heading carries an em dash, which the em dash check also (and
    # rightly) reports; this form isolates the heading check.
    "internal heading": ("internal_heading", "Internal: none.\n-->\n", "Internal: none.\n-->\n\n## Source transcript\n"),
    "internal heading inside a comment": ("internal_heading", "Internal: none.", "Internal: none. INTERNAL — never ships"),
    "image placeholder": ("placeholder", "## Why it matters", "[IMAGE: a chart]\n\n## Why it matters"),
    "source log removed": ("source_log", "<!-- Sources checked 2026-10-25:", "<!-- Notes 2026-10-25:"),
    "source log emptied": ("source_log",
                           "https://developers.google.com/search/docs/appearance/snippet : Google may use the meta description for the snippet; an em dash — quoted from a source is fine here.\nInternal: none.\n",
                           "https://developers.google.com/search/docs/appearance/snippet\n"),
    "keyword out of the title": ("placements", 'title: "How to Write a Meta Description That Gets Clicks"', 'title: "Meta Descriptions That Get Clicks"'),
    "keyword out of the description": ("placements", 'description: "How to write a meta description that earns', 'description: "A meta description that earns'),
    "keyword out of the slug": ("placements", "slug: write-meta-description", "slug: snippet-guide"),
    "keyword out of the first sentence": ("placements", "To write a meta description that gets clicks, lead", "To get clicks, lead"),
    "keyword out of a body H1": ("placements", "To write a meta description", "# Snippets that win\n\nTo write a meta description"),
}


# The fixture's profile: the defaults, plus tldr as a required field so the
# required check has a field to lose that no other check reads.
CFG = dict(ca.DEFAULTS, required="title, slug, description, keyword, tldr")


def results_for(text, cfg=None, keyword=None):
    return ca.run(text, cfg or CFG, keyword)


class GoodFixture(unittest.TestCase):
    def test_passes_every_check(self):
        # Positive twin: the fixture is clean, so each mutation below is
        # measured against a known-good baseline.
        self.assertEqual({k: v for k, v in results_for(GOOD).items() if v}, {})

    def test_quoted_em_dash_in_source_log_is_ignored(self):
        self.assertIn("—", GOOD)
        self.assertEqual(results_for(GOOD)["em_dash"], [])


class DescriptionBoundary(unittest.TestCase):
    # Mutation: `>` loosened to an off-by-one. A far-over fixture cannot see
    # it; the limit itself and one past it can.
    def with_description(self, n):
        old = GOOD.split('description: "', 1)[1].split('"', 1)[0]
        desc = ("Write a meta description " + "x" * n)[:n]
        return GOOD.replace(old, desc)

    def test_at_the_limit_passes(self):
        self.assertEqual(results_for(self.with_description(155))["description"], [])

    def test_one_over_fails(self):
        self.assertTrue(results_for(self.with_description(156))["description"])


class Mutations(unittest.TestCase):
    def test_each_mutation_fires_exactly_its_check(self):
        for label, (check, old, new) in MUTATIONS.items():
            with self.subTest(label):
                self.assertEqual(GOOD.count(old), 1, f"fixture anchor not unique: {old!r}")
                fired = {k: v for k, v in results_for(GOOD.replace(old, new)).items() if v}
                self.assertEqual(set(fired), {check}, f"{label}: fired {fired}")


class Profile(unittest.TestCase):
    def write(self, body):
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
        f.write(body)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_unknown_key_is_an_error(self):
        path = self.write("```checks\ndescription_maks: 150\n```\n")
        with self.assertRaises(ca.UsageError):
            ca.read_profile(path)

    def test_limit_from_profile(self):
        cfg = ca.read_profile(self.write("```checks\ndescription_max: 100\n```\n"))
        self.assertTrue(results_for(GOOD, cfg)["description"])
        self.assertFalse(results_for(GOOD)["description"])  # twin: the default passes

    def test_banned_extra_and_allow(self):
        cfg = ca.read_profile(self.write("```checks\nbanned_extra: honest\nbanned_allow: folks\n```\n"))
        self.assertTrue(results_for(GOOD.replace("It does not", "Honest, it does not"), cfg)["banned"])
        self.assertFalse(results_for(GOOD.replace("It does not", "Folks, it does not"), cfg)["banned"])
        self.assertTrue(results_for(GOOD.replace("It does not", "Folks, it does not"))["banned"])

    def test_allow_must_name_a_core_word(self):
        cfg = ca.read_profile(self.write("```checks\nbanned_allow: nonsense\n```\n"))
        with self.assertRaises(ca.UsageError):
            results_for(GOOD, cfg)

    def test_source_log_optional(self):
        cfg = ca.read_profile(self.write("```checks\nsource_log: optional\n```\n"))
        text = GOOD.replace("<!-- Sources checked 2026-10-25:", "<!-- Notes:")
        self.assertFalse(results_for(text, cfg)["source_log"])
        self.assertTrue(results_for(text)["source_log"])


class Cli(unittest.TestCase):
    """Exit codes and severities, through the real entry point."""

    def run_cli(self, text, profile=None):
        with tempfile.TemporaryDirectory() as d:
            art = os.path.join(d, "a.md")
            open(art, "w").write(text)
            cmd = [sys.executable, os.path.join(SCRIPTS, "check_article.py"), art]
            if profile is not None:
                prof = os.path.join(d, "p.md")
                open(prof, "w").write(profile)
                cmd += ["--profile", prof]
            p = subprocess.run(cmd, capture_output=True, text=True)
            return p.returncode, p.stdout + p.stderr

    def test_clean_exits_0(self):
        code, out = self.run_cli(GOOD)
        self.assertEqual(code, 0, out)
        self.assertIn("PASS", out)

    def test_failure_exits_1(self):
        code, out = self.run_cli(GOOD.replace("It does not", "It does not delve"))
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL banned", out)

    def test_placement_warns_by_default_and_fails_on_request(self):
        text = GOOD.replace("slug: write-meta-description", "slug: snippet-guide")
        code, out = self.run_cli(text)
        self.assertEqual(code, 0, out)
        self.assertIn("WARN placements", out)
        code, out = self.run_cli(text, "```checks\nplacements_fail: yes\n```\n")
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL placements", out)

    def test_bad_profile_exits_2(self):
        code, out = self.run_cli(GOOD, "```checks\nbogus: 1\n```\n")
        self.assertEqual(code, 2, out)
        self.assertIn("unknown key", out)


if __name__ == "__main__":
    unittest.main()
