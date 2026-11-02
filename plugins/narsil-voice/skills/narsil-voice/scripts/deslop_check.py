#!/usr/bin/env python3
"""Lint a draft against the Narsil de-slop rules.

Usage:
    python3 deslop_check.py draft.md [more.md ...]
    cat draft.txt | python3 deslop_check.py

Exact checks: dashes, hard-banned words, rationed-word clusters, "actually",
exclamation points, bold-lead bullets, chatbot and email filler.
Heuristic checks: not-X-but-Y contrasts, staged run-ups, title-case H2s,
rhetorical questions. Heuristics can miss or over-flag; judge each hit.
Code blocks, inline code, URLs, and HTML comments are ignored.
"""
import re
import sys

MAX_SHOW = 6

HARD_BANS = [
    (r"\bdelv(e|es|ed|ing)\b", "delve"),
    (r"\btapestr(y|ies)\b", "tapestry"),
    (r"\bhonest(ly)?\b", "honest"),
    (r"\btreasure troves?\b", "treasure trove"),
    (r"\bleverag(e|es|ed|ing)\b", "leverage (banned as a verb)"),
    (r"\butili[sz](e|es|ed|ing|ation)\b", "utilize"),
    (r"\bunlock(s|ed|ing)?\b", "unlock"),
    (r"\bunleash(es|ed|ing)?\b", "unleash"),
    (r"\bsupercharg(e|es|ed|ing)\b", "supercharge"),
    (r"\belevat(e|es|ed|ing)\b", "elevate"),
    (r"\bempower(s|ed|ing|ment)?\b", "empower"),
    (r"\bgame[- ]changers?\b", "game-changer"),
    (r"\brevolutionary\b", "revolutionary"),
    (r"\bcutting[- ]edge\b", "cutting-edge"),
    (r"\bgroundbreaking\b", "groundbreaking"),
    (r"\bembark(s|ed|ing)?\b", "embark"),
    (r"\bendeavou?rs?\b", "endeavor"),
    (r"\benlightening\b", "enlightening"),
    (r"\besteemed\b", "esteemed"),
    (r"\bshed(s|ding)? light\b", "shed light"),
    (r"\belucidat(e|es|ed|ing)\b", "elucidate"),
    (r"\bunravel(s|ed|ing|led|ling)?\b", "unravel"),
    (r"\bsynerg(y|ies|istic)\b", "synergy"),
    (r"\bholistic(ally)?\b", "holistic"),
    (r"\bparamount\b", "paramount"),
    (r"\bpivotal\b", "pivotal"),
    (r"\bseamless(ly)?\b", "seamless"),
    (r"\bstreamlined?\b", "streamlined"),
    (r"\bin today's\b", "in today's ..."),
    (r"\bever[- ]evolving\b", "ever-evolving"),
    (r"\b10x\b", "10x"),
    (r"\blandscapes?\b", "landscape (banned as metaphor)"),
    (r"\btestament\b", "testament"),
    (r"\bfoster(s|ed|ing)?\b", "foster"),
    (r"\bcultivat(e|es|ed|ing)\b", "cultivate"),
    (r"\bamplif(y|ies|ied|ying)\b", "amplify"),
    (r"\bresonat(e|es|ed|ing)\b", "resonate"),
    (r"\brobust\b", "robust (banned as praise)"),
    (r"\bfolks\b", "folks"),
    (r"\badditionally\b", "additionally"),
    (r"\bbolster(s|ed|ing)?\b", "bolster"),
    (r"\bdeep[- ]dives?\b", "deep dive"),
    (r"\bgarner(s|ed|ing)?\b", "garner"),
    (r"\bmeticulous(ly)?\b", "meticulous"),
    (r"\bshowcas(e|es|ed|ing)\b", "showcase"),
    (r"\bquietly\b", "quietly"),
    (r"\bvibrant\b", "vibrant"),
    (r"\bboast(s|ed|ing)?\b", "boasts"),
    (r"\bnestled\b", "nestled"),
    (r"\bin the heart of\b", "in the heart of"),
    (r"\bbreathtaking\b", "breathtaking"),
    (r"\bstunning(ly)?\b", "stunning"),
    (r"\brenowned\b", "renowned"),
    (r"\bmust[- ]visit\b", "must-visit"),
    (r"\bdiverse array\b", "diverse array"),
]

RATIONED = [
    "insights", "comprehensive", "crucial", "significant", "valuable",
    "invaluable", "explore", "enhance", "expertise", "intricate", "nuanced",
    "multifaceted", "profound", "facilitate", "encompass", "underscores",
    "discern", "integral", "perspectives", "complexity", "implications",
    "adapt", "promote", "emphasize", "recognize", "pertinent", "cognizant",
    "characterized", "key", "highlight", "enduring",
]
RATIONED_RE = {w: re.compile(r"\b" + w + r"(s|es|d|ed|ing|ly)?\b", re.I) for w in RATIONED}
RATIONED_RE["align with"] = re.compile(r"\balign(s|ed|ing)? with\b", re.I)
RATIONED_RE["interplay"] = re.compile(r"\binterplay\b", re.I)
RATIONED_RE["gate (figurative)"] = re.compile(r"\bgat(e|es|ed|ing)\b", re.I)

RUNUPS = [
    "here's the thing", "the thing is", "honestly?", "let's be honest",
    "real talk", "i'll be straight", "to be clear", "let's dive in",
    "let's dive", "here's what you need to know", "without further ado",
    "let's break this down", "let's explore", "don't get me wrong",
    "this isn't to say", "i'm not saying", "you might think",
    "at its core", "the real question is", "what really matters",
    "that's the real win", "read that again", "let that sink in",
]
RUNUP_START = re.compile(r"(^|[.!?]\s+)(Look|So|Now),\s", re.M)

FILLER = [
    "i hope this helps", "hope this finds you", "i wanted to reach out",
    "just checking in", "circling back", "touching base", "per my last email",
    "please don't hesitate", "at your earliest convenience",
    "let me know if",
    "feel free to", "bumping this", "did you see my last email",
    "great question", "i'm thrilled to announce", "humbled to share",
    "did you know",
]

CONTRAST = [
    re.compile(r"\bnot (just|only|merely|simply)\b", re.I),
    re.compile(r"\b(isn't|is not|aren't|are not|wasn't|doesn't|does not|don't|do not)\b[^.?!\n]{0,90}[.;]\s+(It|They|That|This|You|We)('s|'re| is| are| do| does)\b"),
    re.compile(r"\brather than\b", re.I),
    re.compile(r"\binstead of\b", re.I),
    re.compile(r",\s+not\s+(a|an|the|ten|two|three|just)?\s?\w+", re.I),
    re.compile(r"(^|[.!?]\s+)Not \w+[^.?!\n]{0,60}[.]"),
]

BOLD_LEAD = re.compile(r"^\s*([-*+]|\d+\.)\s+\*\*[^*]+?(:\*\*|\*\*\s*:|\.\*\*)")
HEADING = re.compile(r"^(#{2,3})\s+(.*)$")
SMALL = {"a", "an", "the", "and", "or", "but", "for", "nor", "of", "on", "in",
         "to", "at", "by", "vs", "vs.", "with", "from", "as", "is", "it"}
KEEP_CAPS = {"Reforge", "Method", "Assay", "Temper", "Forge", "Foundry",
             "Frontier", "SEO", "GEO", "AEO", "Advisory", "Narsil", "Creative",
             "Google", "ChatGPT", "AI", "Perplexity", "Claude", "Gemini",
             "Overviews", "Mode", "Search", "Console", "Ads", "Business",
             "Profile", "FAQ", "I", "LLM", "LLMs", "GA4", "GBP", "Bing"}


def clean_lines(text):
    """Blank out code, URLs, and comments while keeping line numbers."""
    out, in_fence, in_comment = [], False, False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
                line = line.split("-->", 1)[1]
            else:
                out.append("")
                continue
        if "<!--" in line:
            head, _, tail = line.partition("<!--")
            if "-->" in tail:
                line = head + tail.split("-->", 1)[1]
            else:
                line, in_comment = head, True
        line = re.sub(r"`[^`]*`", " ", line)
        line = re.sub(r"https?://\S+", " ", line)
        line = re.sub(r"\]\([^)]*\)", "]", line)
        out.append(line)
    return out


def loc(hits):
    shown = ", ".join(hits[:MAX_SHOW])
    more = len(hits) - MAX_SHOW
    return shown + (f", +{more} more" if more > 0 else "")


def check(name, text):
    lines = clean_lines(text)
    body = "\n".join(lines)
    words = len(re.findall(r"\b\w+\b", body))
    report = []

    def add(status, label, hits):
        report.append((status, label, hits))

    # Dashes
    dash_hits = []
    for i, l in enumerate(lines, 1):
        for m in re.finditer(r"—", l):
            dash_hits.append(f"L{i} em dash")
        for m in re.finditer(r"(\d)\s*–\s*(\d)", l):
            dash_hits.append(f"L{i} en dash in range (use '-')")
        for m in re.finditer(r"(?<!\d)\s*–\s*(?!\d)", l):
            dash_hits.append(f"L{i} en dash")
        stripped = re.sub(r"^\s*([-*+]|\|)\s", "", l)
        if re.search(r"\S\s+-{1,2}\s+\S", stripped) and not re.match(r"^\s*\|", l):
            dash_hits.append(f"L{i} spaced hyphen as dash")
    add("FAIL" if dash_hits else "PASS", "dashes as connectors", dash_hits)

    # Hard bans
    ban_hits = []
    for i, l in enumerate(lines, 1):
        for rx, label in HARD_BANS:
            for m in re.finditer(rx, l, re.I):
                ban_hits.append(f"L{i} {label}")
    add("FAIL" if ban_hits else "PASS", "hard-banned words", ban_hits)

    # Rationed words
    rat_hits, counts = [], {}
    for i, l in enumerate(lines, 1):
        for w, rx in RATIONED_RE.items():
            for m in rx.finditer(l):
                counts.setdefault(w, []).append(i)
    for w, ls in counts.items():
        if len(ls) >= 2:
            rat_hits.append(f"'{w}' x{len(ls)} (L{', L'.join(map(str, ls[:4]))})")
    paras = re.split(r"\n\s*\n", body)
    line_no = 1
    for p in paras:
        found = {w for w, rx in RATIONED_RE.items() if rx.search(p)}
        if len(found) >= 2:
            rat_hits.append(f"cluster near L{line_no}: {', '.join(sorted(found))}")
        line_no += p.count("\n") + 2
    add("WARN" if rat_hits else "PASS", "rationed words", rat_hits)

    # actually
    act = [f"L{i}" for i, l in enumerate(lines, 1) for _ in re.finditer(r"\bactually\b", l, re.I)]
    add("WARN" if act else "PASS", "'actually' (keep only real contrast)", act)

    # Exclamation points
    exc = [f"L{i}" for i, l in enumerate(lines, 1) for _ in re.finditer(r"!(?!\[)", l)]
    add("FAIL" if len(exc) > 1 else ("WARN" if exc else "PASS"), "exclamation points (max 1)", exc)

    # Contrasts
    con = []
    for i, l in enumerate(lines, 1):
        spans = []
        for rx in CONTRAST:
            for m in rx.finditer(l):
                if any(m.start() < e and m.end() > b for b, e in spans):
                    continue
                spans.append((m.start(), m.end()))
                snippet = m.group(0).strip()[:50]
                con.append(f"L{i} \"{snippet}\"")
    status = "FAIL" if len(con) > 2 else ("WARN" if con else "PASS")
    add(status, f"possible contrasts ({len(con)} found, cap 2; heuristic)", con)

    # Staged run-ups and "deep" sayings
    run = []
    low = [l.lower() for l in lines]
    for i, l in enumerate(low, 1):
        for p in RUNUPS:
            if p in l:
                run.append(f"L{i} \"{p}\"")
    for m in RUNUP_START.finditer(body):
        ln = body[: m.start()].count("\n") + 1
        run.append(f"L{ln} \"{m.group(2)},\" opener")
    add("FAIL" if run else "PASS", "staged run-ups and restatement closers", run)

    # Filler and chatbot residue
    fil = [f"L{i} \"{p}\"" for i, l in enumerate(low, 1) for p in FILLER if p in l]
    add("FAIL" if fil else "PASS", "filler and chatbot residue", fil)

    # Bold-lead bullets
    bold = [f"L{i}" for i, l in enumerate(lines, 1) if BOLD_LEAD.match(l)]
    add("FAIL" if len(bold) > 3 else ("WARN" if bold else "PASS"), "bold-lead bullets (one short list max)", bold)

    # Title-case H2/H3
    tc = []
    for i, l in enumerate(lines, 1):
        m = HEADING.match(l)
        if not m:
            continue
        ws = re.findall(r"[A-Za-z][\w'’.-]*", m.group(2))[1:]
        caps = [w for w in ws if w[0].isupper() and w not in KEEP_CAPS and w.lower() not in SMALL]
        lowers = [w for w in ws if w[0].islower() and w.lower() not in SMALL]
        if len(caps) >= 2 and len(caps) > len(lowers):
            tc.append(f"L{i} \"{m.group(2)[:50]}\"")
    add("WARN" if tc else "PASS", "H2/H3 in Title Case (use sentence case; heuristic)", tc)

    # Rhetorical questions outside headings and bold FAQ lines
    rq = []
    for i, l in enumerate(lines, 1):
        s = l.strip()
        if not s or HEADING.match(l) or s.startswith("#") or re.match(r"^\*\*.*\?\*\*$", s):
            continue
        for _ in re.finditer(r"\?(\s|$|\")", s):
            rq.append(f"L{i}")
    add("WARN" if len(rq) > 1 else "PASS", "questions in body (one rhetorical max)", rq)

    # Curly quotes (info)
    curly = len(re.findall(r"[“”]", body))
    add("INFO" if curly else "PASS", f"curly double quotes: {curly} (straight in drafts)", [])

    fails = sum(1 for s, _, _ in report if s == "FAIL")
    warns = sum(1 for s, _, _ in report if s == "WARN")
    print(f"deslop_check: {name} ({words:,} words) | {fails} fail, {warns} warn")
    for status, label, hits in report:
        if status == "PASS":
            continue
        line = f"  {status:4} {label}"
        if hits:
            line += f": {len(hits)} | {loc(hits)}"
        print(line)
    if not fails and not warns:
        print("  all checks passed")
    return fails


def main():
    args = sys.argv[1:]
    total = 0
    if not args:
        total += check("stdin", sys.stdin.read())
    for path in args:
        with open(path, encoding="utf-8") as f:
            total += check(path, f.read())
        print()
    sys.exit(0)


if __name__ == "__main__":
    main()
