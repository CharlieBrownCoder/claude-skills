---
name: article-writer
description: "Write a publish-ready blog post or article draft for any of Nate's brands and sites, in that brand's voice, with its brief, safety pass, internal links, source log and checks. Use whenever someone asks to write, draft, outline or refresh a blog post or article, turn a playbook or document into an article, turn a customer question into a post, interview them for a post, or 'write the next one on the calendar'. Reads the repo's .claude/article-writer.md profile for the brand; with no profile, it asks once and offers to save one. Writes to the drafts folder and stops: a human promotes."
---

# Article Writer

One workflow for every brand. The method is the same everywhere; the brand
(voice, facts, folders, frontmatter, links, extra checks) comes from the
repo's profile. Nothing here names a brand: if a rule is brand-specific, it
belongs in the profile.

## Step 0: load the profile and the voice

1. Read `.claude/article-writer.md` in the repo root. If it is missing, read
   `references/profile-template.md`, ask the user for the fields it lists (one
   message, all at once), write the profile, and show it before going on.
2. Load the voice skill the profile names, before drafting a word. If that
   skill is not available in this session, say so and stop: a draft in the
   wrong voice costs more than no draft. The voice skill wins over anything in
   this skill on voice, tone, vocabulary and formatting.
3. Read the brand facts file the profile points to. Every price, name, bio
   line and URL comes from there or from a source you cite, never from memory.

## Step 1: pick the mode

Read `references/modes.md` for the mode's own steps.

- **playbook**: the input is a source document (a playbook, a spec, notes).
  The default when the user names a file or a calendar slot.
- **question**: the input is a customer question; you interview the owner,
  one question at a time, and write from their answers.
- **refresh**: the input is an existing article; keep its slug and publish
  date, re-check every claim.

## Step 2: the brief

Fill `references/brief-template.md` and show it to the user. Every field is
answered or marked as an assumption you made. Ask only when a missing answer
would change the piece; otherwise make the call and say so. Wait for a go on
the brief unless the user already said to write straight through.

## Step 3: the safety pass (before drafting)

Run every item in `references/safety-pass.md`. Two outcomes stop the piece:
an existing page already serves the intent (propose a refresh instead), or
the source is grey-area or unattributable (say which and why). Record every
call the pass made; they go in the report.

## Step 4: draft

Follow `references/method.md`: answer first, the five placements, cover what
the ranking pages cover and add what they lack, one against-interest moment,
one giveaway, stats named-source or cut, the service mention once near the
end. Respect the profile's length, byline, frontmatter and FAQ rules.

## Step 5: links and source log

- Internal links: the profile's count and targets. Link only to pages that
  exist now, and, when the profile sets date causality, only to pages dated
  before this one's publish date. Descriptive anchors, never "click here".
- Source log: an HTML comment at the foot of the article in the format of
  `references/source-log.md`. Every outside claim in the piece has a line.
  If a claim has no source you could open today, cut the claim.

## Step 6: checks

1. Run the core checks:
   `python3 <this skill's folder>/scripts/check_article.py <draft> --profile .claude/article-writer.md`
   Fix every FAIL. A WARN (a keyword placement that reads literally wrong,
   such as a question keyword reworded in the title) is fixed or explained
   in the report, one line each. Never edit the checker or the profile to
   make a draft pass; if a rule is wrong, tell the user.
2. Run the voice skill's own linter, if it has one.
3. Run the profile's repo checks, if it lists any.

## Step 7: save and report

Save to the profile's drafts folder (never straight into the published
folder) and report, in this order:

1. The file path, the title, the keyword, the word count.
2. The claims you could not verify, and what you cut.
3. The calls the safety pass made (overlap, attribution, freshness).
4. The decisions the user still has to make, one at a time.

Stop there. Promoting a draft, scheduling it, and committing or pushing are
the user's call.

## Hard rules

- Never invent a quote, a number, a result, a client or a promise. In
  question mode, only what the owner said; anonymize any client they mention.
- Never ship a source document's verbatim transcript or anything under a
  heading that marks it internal.
- Never promise rankings, citations, rich results or a timeframe.
- Never name or link a tool the profile says not to.
- A rule in the profile beats the default here; a rule in the voice skill
  beats both on voice.
