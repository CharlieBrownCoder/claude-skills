#!/usr/bin/env python3
"""Core checks for an article draft. Stdlib only, so it runs in any repo.

Usage:
    python3 check_article.py ARTICLE.md [--profile .claude/article-writer.md]
                             [--keyword "target phrase"]

Exit 0 when every check passes, 1 when any fails, 2 on a usage or profile
error (an unreadable file, an unknown key in the profile's checks block).

Every check names the mutation that proves it; the tests in
tests/test_check_article.py apply each one to a passing fixture and assert
that exactly that check fails, by name.

What is read where:
  - Voice checks (em dash, banned words, placeholders) read the frontmatter
    values and the body, with HTML comments, fenced code and inline code
    removed: a source log may quote a page that uses an em dash, and that
    quote never renders.
  - The internal-heading check reads the WHOLE file, comments included,
    because a transcript hidden in a comment still ships in the source.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# The core banned words: slop vocabulary, brand-neutral. Each carries the
# inflections a reader would still recognise as the same word, anchored so
# "elevator" and "folksy" pass. A brand removes one with `banned_allow` and
# adds its own with `banned_extra`.
CORE_BANNED = {
    "delve": r"delv(?:e|es|ed|ing)",
    "tapestry": r"tapestr(?:y|ies)",
    "treasure trove": r"treasure troves?",
    "leverage": r"leverag(?:e|es|ed|ing)",
    "utilize": r"utili[sz](?:e|es|ed|ing|ation)",
    "unlock": r"unlock(?:s|ed|ing)?",
    "unleash": r"unleash(?:es|ed|ing)?",
    "supercharge": r"supercharg(?:e|es|ed|ing)",
    "elevate": r"elevat(?:e|es|ed|ing)",
    "empower": r"empower(?:s|ed|ing|ment)?",
    "game-changer": r"game[- ]changers?",
    "revolutionary": r"revolutionary",
    "cutting-edge": r"cutting[- ]edge",
    "groundbreaking": r"groundbreaking",
    "embark": r"embark(?:s|ed|ing)?",
    "endeavor": r"endeavou?rs?",
    "shed light": r"shed(?:s|ding)? light",
    "elucidate": r"elucidat(?:e|es|ed|ing)",
    "unravel": r"unravel(?:s|ed|ing|led|ling)?",
    "synergy": r"synerg(?:y|ies|istic)",
    "holistic": r"holistic(?:ally)?",
    "paramount": r"paramount",
    "pivotal": r"pivotal",
    "seamless": r"seamless(?:ly)?",
    "streamline": r"streamlin(?:e|es|ed|ing)",
    "testament": r"testaments?",
    "foster": r"foster(?:s|ed|ing)?",
    "cultivate": r"cultivat(?:e|es|ed|ing)",
    "amplify": r"amplif(?:y|ies|ied|ying)",
    "resonate": r"resonat(?:e|es|ed|ing)",
    "folks": r"folks",
    "enlightening": r"enlightening",
    "esteemed": r"esteemed",
    "in today's": r"in today['\u2019]s",
    "ever-evolving": r"ever[- ]evolving",
    "10x": r"10x",
    "landscape": r"landscapes?",
    "robust": r"robust",
    "additionally": r"additionally",
    "bolster": r"bolster(?:s|ed|ing)?",
    "deep dive": r"deep[- ]dives?",
    "garner": r"garner(?:s|ed|ing)?",
    "meticulous": r"meticulous(?:ly)?",
    "showcase": r"showcas(?:e|es|ed|ing)",
    "quietly": r"quietly",
    "vibrant": r"vibrant",
    "boasts": r"boast(?:s|ed|ing)?",
    "nestled": r"nestled",
    "in the heart of": r"in the heart of",
    "breathtaking": r"breathtaking",
    "stunning": r"stunning(?:ly)?",
    "renowned": r"renowned",
    "must-visit": r"must[- ]visit",
    "diverse array": r"diverse array",
}

# "unlock" is slop when applied to an abstract payoff ("unlock growth"), and
# plain English for a real lock or gate ("unlock the template with an
# email"). Only the payoff sense fails.
UNLOCK_HYPE = re.compile(
    r"\bunlock\w*\s+(?:\w+\s+){0,2}"
    r"(growth|potential|value|success|results|revenue|traffic|rankings|"
    r"insights|opportunities|performance|power)\b",
    re.I,
)
# "leverage" is banned as a verb; "highest-leverage" is the noun.
LEVERAGE_NOUN = re.compile(r"[-\w]+-leverage\b", re.I)

EM_DASH = "\u2014"
INTERNAL_HEADING = re.compile(
    r"^#{1,6}\s*Source transcript\b|INTERNAL\s*\u2014\s*never ships", re.I | re.M)
PLACEHOLDER = re.compile(r"\[IMAGE:", re.I)
SOURCE_LOG = re.compile(r"<!--\s*Sources checked (\d{4}-\d{2}-\d{2}):(.*?)-->", re.S)

PLACEMENTS = ("title", "description", "slug", "h1", "first_sentence")
SLUG_STOPWORDS = {
    "a", "an", "the", "of", "for", "to", "in", "on", "and", "or", "is", "are",
    "what", "how", "why", "when", "do", "does", "can", "my", "your", "with",
    "vs", "versus", "it", "its", "be", "you", "i",
}

DEFAULTS = {
    "description_max": "155",
    "description_field": "description",
    "keyword_field": "keyword",
    "title_field": "title",
    "slug_field": "slug",
    "required": "title, slug, description, keyword",
    "banned_extra": "",
    "banned_allow": "",
    "placements": ", ".join(PLACEMENTS),
    "source_log": "required",
    "placements_fail": "no",
}


class UsageError(Exception):
    pass


# --- parsing ----------------------------------------------------------------

def read_profile(path: str | None) -> dict[str, str]:
    """The profile's ```checks block over the defaults. Unknown keys are an error."""
    cfg = dict(DEFAULTS)
    if not path:
        return cfg
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        raise UsageError(f"cannot read profile {path}: {e}")
    m = re.search(r"^```checks[ \t]*\n(.*?)^```", text, re.M | re.S)
    if not m:
        return cfg
    for n, line in enumerate(m.group(1).splitlines(), 1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            raise UsageError(f"profile checks line {n} is not key: value: {line!r}")
        key, value = (s.strip() for s in line.split(":", 1))
        if key not in DEFAULTS:
            raise UsageError(f"profile checks: unknown key {key!r} (known: {', '.join(DEFAULTS)})")
        cfg[key] = value
    return cfg


def split_list(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("\n---", 2)
    if len(parts) < 2:
        return "", text
    fm = parts[0][3:]
    body = parts[1].split("\n", 1)[1] if "\n" in parts[1] else ""
    return fm, body


def frontmatter_fields(fm: str) -> dict[str, str]:
    """Top-level `key: value` lines, quotes stripped. Nested blocks are skipped."""
    out: dict[str, str] = {}
    for line in fm.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        value = m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out[m.group(1)] = value
    return out


def strip_unrendered(text: str) -> str:
    """Remove HTML comments, fenced code and inline code, keeping line count."""
    blank = lambda m: "\n" * m.group(0).count("\n")
    return re.sub(r"```.*?```|<!--.*?-->|`[^`\n]*`", blank, text, flags=re.S)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"['\u2019]", "", text)
    return " " + re.sub(r"[^a-z0-9]+", " ", text).strip() + " "


def contains_keyword(text: str, keyword: str) -> bool:
    return normalize(keyword) in normalize(text)


def stem(word: str) -> str:
    """Fold a plain plural ("dentists" -> "dentist"); nothing cleverer."""
    return word[:-1] if len(word) > 3 and word.endswith("s") and not word.endswith("ss") else word


def first_sentence(body: str) -> str:
    """The first sentence of the first prose paragraph."""
    for raw in strip_unrendered(body).split("\n\n"):
        para = " ".join(l.strip() for l in raw.strip().splitlines())
        if not para or para.startswith(("#", "!", "{{", "|", ">", "-", "*", "<")):
            continue
        if re.match(r"^\d+\.\s", para):
            continue
        m = re.match(r"(.+?[.?!])(?:\s|$)", para)
        return m.group(1) if m else para
    return ""


def body_h1(body: str) -> str | None:
    for line in strip_unrendered(body).splitlines():
        if re.match(r"^#\s+\S", line):
            return line[1:].strip()
    return None


# --- the checks ---------------------------------------------------------------
# Each returns a list of failure messages; empty means pass.

def check_required(fields, cfg):
    # Mutation: delete any required key from the fixture's frontmatter.
    return [f"frontmatter {k!r} is missing or empty"
            for k in split_list(cfg["required"]) if not fields.get(k)]


def check_description(fields, cfg):
    # Mutation: lengthen the description to max + 1 characters.
    desc = fields.get(cfg["description_field"], "")
    limit = int(cfg["description_max"])
    if len(desc) > limit:
        return [f"description is {len(desc)} characters; the limit is {limit}"]
    return []


def check_em_dash(copy_text):
    # Mutation: put one em dash in the body or a frontmatter value.
    n = copy_text.count(EM_DASH)
    return [f"{n} em dash(es) in rendered copy"] if n else []


def banned_patterns(cfg):
    allow = {w.lower() for w in split_list(cfg["banned_allow"])}
    unknown = allow - set(CORE_BANNED)
    if unknown:
        raise UsageError(f"banned_allow names words not on the core list: {sorted(unknown)}")
    pats = {w: re.compile(rf"\b{f}\b", re.I) for w, f in CORE_BANNED.items() if w not in allow}
    for w in split_list(cfg["banned_extra"]):
        pats[w] = re.compile(rf"\b{re.escape(w)}\b", re.I)
    return pats


def check_banned(copy_text, cfg):
    # Mutation: add one banned word ("delve") to the body. Per line, so a
    # narrowing excuses only the line it is on.
    found: dict[str, str] = {}
    pats = banned_patterns(cfg)
    for line in copy_text.splitlines():
        for word, pat in pats.items():
            # The noun ("highest-leverage") is taken out before the verb is sought.
            m = pat.search(LEVERAGE_NOUN.sub("", line) if word == "leverage" else line)
            if not m:
                continue
            if word == "unlock" and not UNLOCK_HYPE.search(line):
                continue
            found.setdefault(word, m.group(0))
    return [f"banned word {w!r} (found {f!r})" for w, f in found.items()]


def check_internal_heading(full_text):
    # Mutation: append the quarantine heading, even inside a comment.
    return ["the file carries an internal-only source heading"] if INTERNAL_HEADING.search(full_text) else []


def check_placeholder(copy_text):
    # Mutation: add "[IMAGE: a chart]" to the body.
    return ["an [IMAGE: ...] placeholder is still in the copy"] if PLACEHOLDER.search(copy_text) else []


def check_source_log(full_text, cfg):
    # Mutations: delete the source log; or empty it to its opening line.
    if cfg["source_log"] == "optional":
        return []
    if cfg["source_log"] != "required":
        raise UsageError("source_log must be required or optional")
    m = SOURCE_LOG.search(full_text)
    if not m:
        return ["no '<!-- Sources checked YYYY-MM-DD:' comment"]
    lines = [l for l in m.group(2).splitlines() if l.strip()]
    # Accepted line shapes: "URL : what it confirms", "URL (what it confirms)",
    # "Internal: files". A bare URL says nothing about what was checked.
    if not any(re.match(r"\s*(https?://\S+\s+(?::\s*)?\S|Internal:\s*\S)", l) for l in lines):
        return ["the source log has no line saying what a source confirms"]
    return []


def check_placements(fields, body, cfg, keyword):
    # Mutations: remove the keyword from each placement in turn.
    wanted = split_list(cfg["placements"])
    bad = [p for p in wanted if p not in PLACEMENTS]
    if bad:
        raise UsageError(f"unknown placements {bad} (known: {', '.join(PLACEMENTS)})")
    if not keyword:
        return ["no keyword: set the frontmatter keyword or pass --keyword"]
    title = fields.get(cfg["title_field"], "")
    targets = {
        "title": title,
        "description": fields.get(cfg["description_field"], ""),
        "h1": body_h1(body) or title,
        "first_sentence": first_sentence(body),
    }
    out = []
    for p in wanted:
        if p == "slug":
            # A slug is short on purpose, so it carries the keyword's head, not
            # every word: at least half the content words, plurals folded.
            slug_words = {stem(w) for w in re.split(r"[-_/]+", fields.get(cfg["slug_field"], "").lower())}
            words = [stem(w) for w in normalize(keyword).split() if w not in SLUG_STOPWORDS]
            hits = [w for w in words if w in slug_words]
            if words and len(hits) * 2 < len(words):
                missing = [w for w in words if w not in slug_words]
                out.append(f"slug carries {len(hits)} of the keyword's {len(words)} content words "
                           f"(missing {', '.join(missing)}); it needs at least half")
        elif not contains_keyword(targets[p], keyword):
            out.append(f"keyword {keyword!r} not in the {p.replace('_', ' ')}")
    return out


# --- runner -------------------------------------------------------------------

def run(text: str, cfg: dict[str, str], keyword: str | None = None) -> dict[str, list[str]]:
    fm, body = split_frontmatter(text)
    fields = frontmatter_fields(fm)
    copy_text = strip_unrendered(fm + "\n" + body)
    keyword = keyword or fields.get(cfg["keyword_field"], "")
    return {
        "required": check_required(fields, cfg),
        "description": check_description(fields, cfg),
        "em_dash": check_em_dash(copy_text),
        "banned": check_banned(copy_text, cfg),
        "internal_heading": check_internal_heading(text),
        "placeholder": check_placeholder(copy_text),
        "source_log": check_source_log(text, cfg),
        "placements": check_placements(fields, body, cfg, keyword),
    }


# Checks that warn by default. Placements read the keyword literally, and a
# keyword phrased as a question ("should i run google ads") is often, and
# rightly, reworded in the title ("Should You Run Google Ads?"). On the first
# calibration (narsilcreative.com, 88 approved articles, 2026-10-25) a hard
# failure fired on 44 of them. So a placement miss is a WARN the report must
# fix or explain, and a profile that wants it hard sets placements_fail: yes.
def severity(name: str, cfg: dict[str, str]) -> str:
    if name == "placements":
        flag = cfg["placements_fail"].lower()
        if flag not in ("yes", "no"):
            raise UsageError("placements_fail must be yes or no")
        return "FAIL" if flag == "yes" else "WARN"
    return "FAIL"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("article")
    ap.add_argument("--profile")
    ap.add_argument("--keyword")
    args = ap.parse_args(argv)
    try:
        cfg = read_profile(args.profile)
        text = open(args.article, encoding="utf-8").read()
        results = run(text, cfg, args.keyword)
    except (UsageError, OSError, ValueError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2
    failed = warned = 0
    try:
        for name, problems in results.items():
            level = severity(name, cfg)
            for p in problems:
                print(f"{level} {name}: {p}")
                if level == "FAIL":
                    failed += 1
                else:
                    warned += 1
    except UsageError as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2
    if failed:
        print(f"{failed} failure(s), {warned} warning(s) in {args.article}")
        return 1
    note = f", {warned} warning(s) to fix or explain" if warned else ""
    print(f"PASS {args.article}: {len(results)} checks{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
