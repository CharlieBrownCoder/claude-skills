# Article Writer: design record

Status: APPROVED (Nate, 2026-10-25: "approved"). Build step 2 in progress.
Home: `CharlieBrownCoder/claude-skills` (private), a Claude Code plugin
marketplace. Internal use only, across Nate's own repos and orgs.

## 1. What it is

One skill, `article-writer`, that takes a topic, a source document, a
customer question or an existing article and produces a publish-ready draft
in the right brand's voice, with its brief, its safety pass, its internal
links and its source log. The method comes from the Narsil Brain
(`Narsil-Creative/narsil`); the brand comes from a profile file in the repo
it runs in.

What it is not: a voice skill (it loads one), a keyword research tool, or a
publisher. It writes to the repo's drafts folder and stops. A human
promotes.

## 2. Why a plugin, and why this repo

- The skill must work in repos that cannot read the brain, so it carries its
  own references instead of reading playbooks by path.
- One marketplace repo means one copy. Copying a skill into each repo is how
  `narsil-voice` became two different files (the brain's 228 lines against
  the synced 287).
- A personal-account repo is readable from every org Nate works in, which an
  org-owned repo is not guaranteed to be.

## 3. Repo layout

```
claude-skills/
  .claude-plugin/marketplace.json        lists the plugins
  plugins/article-writer/
    .claude-plugin/plugin.json
    skills/article-writer/
      SKILL.md                           the workflow, short
      references/
        method.md                        the writing method (§5)
        brief-template.md                the brief, field by field
        safety-pass.md                   the pre-draft checklist (§6)
        source-log.md                    the closing sources comment spec
        profile-template.md              what a repo profile holds (§4)
        modes.md                         playbook / question / refresh
        provenance.md                    which brain file each rule came from
      scripts/
        check_article.py                 portable checks (§8), stdlib only
  docs/
    article-writer-design.md             this file
  README.md                              install steps
```

## 4. The per-repo profile

`.claude/article-writer.md` in each repo that uses the skill. With no
profile, the skill asks for the fields once and offers to save the file.

| Field | Example (narsilcreative.com) |
|---|---|
| brand, site | Narsil Creative, narsilcreative.com |
| voice skill | `narsil-voice` (must be loaded before drafting) |
| brand facts | pointer to the repo's file (`site/content/EDITORIAL.md` §Brand facts) |
| articles dir, drafts dir | `site/content/articles/`, `site/content/drafts/` |
| frontmatter schema | pointer, or inline YAML |
| bylines | rule for who signs what |
| length | 1,200-1,800 words |
| link targets | money pages, method page, how many links |
| date causality | yes/no (a backdated piece links only older pages) |
| FAQ rule | count, the brand-entity FAQ, never promise rich results |
| banned extras | brand-specific words on top of the core list |
| repo checks | `python3 site/scripts/content-gates.py` (run after the core checks) |
| source library | path to playbooks if the repo has one, else none |

The profile is the only place a brand rule lives. The core never names
Narsil, Manifest or Jax Humor.

## 5. The method (core, every brand)

Distilled from the brain into Narsil's own words. No transcripts, nothing
from the grey-area list (brain CLAUDE.md rule 1), and method credit follows
rule 2: the skill's text teaches the method, so `provenance.md` credits each
source; an article the skill writes credits the method it teaches unless the
profile or Nate says otherwise.

1. Answer first: the first sentence answers the title. TL;DR before the fold.
2. The five placements: keyword in title, meta description (155 chars max),
   slug, H1, and the opening of the first sentence.
3. Match and outdo: read the pages that rank for the keyword, list what they
   cover, cover it and add what they lack (first-hand detail, a giveaway).
4. One against-interest moment per substantial piece.
5. One copyable giveaway (checklist, template, prompt).
6. Stats are named-source or cut.
7. One service mention near the end, never in the body.
8. Internal links per the profile, with descriptive anchors.
9. Reads human: the voice skill's de-slop rules win; the core adds only the
   em dash ban and the banned-word list.

## 6. The safety pass (before a word is drafted)

1. Overlap: search the articles and drafts dirs for the keyword and its close
   variants. If a page already serves the intent, stop and propose a refresh.
2. Source check (playbook mode): drop everything under
   `## Source transcript (INTERNAL — never ships)`; refuse a source on the
   grey-area list; record the attribution call.
3. Proof: no unattributed client figure, ever, and never as a projection.
4. Freshness: every platform claim (a Google feature, a policy, a price) is
   checked against a dated primary source at draft time and logged.
5. Competing tools: apply the profile's rule (Narsil: never name another
   brand's tool that does what ours does).

## 7. Workflow and modes

Brief → safety pass → outline → draft → links → source log → checks → save
to drafts → report (what it claims, what it could not verify, what Nate must
decide).

- playbook: a source document is the input (the Narsil calendar's mode).
- question: a customer question; interviews the owner one question at a time
  (absorbs `question-to-blog`'s interview step; that skill can retire after).
- refresh: an existing article; keeps its slug and datePublished, bumps
  dateUpdated, re-runs freshness on every claim.

## 8. Portable checks (`check_article.py`)

Each check states the mutation that proves it and is seen to fail before it
ships.

| Check | Proven by |
|---|---|
| no em dash (body, frontmatter) | a fixture with one em dash fails |
| core banned words | a fixture with one banned word fails |
| meta description <= 155 chars | 156 fails, 155 passes |
| keyword in the five placements | dropping it from each placement fails, one at a time |
| quarantine heading absent | a fixture carrying the heading fails |
| source-log comment present and non-empty | removing it fails |
| no `[IMAGE: ...]` placeholder | one placeholder fails |
| frontmatter fields the profile requires | dropping each fails |

Then the profile's repo checks run, if any.

## 9. Install in a repo

`.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "cb-skills": {
      "source": { "source": "github", "repo": "CharlieBrownCoder/claude-skills" }
    }
  },
  "enabledPlugins": { "article-writer@cb-skills": true }
}
```

Plus the repo's `.claude/article-writer.md`. To verify in build step 2: the
exact settings keys against the current Claude Code docs, and that a session
in another org (cloud sessions included) can read the private marketplace.

## 10. Keeping it in step with the brain

v1: the references are distilled by hand and `provenance.md` records the brain
commit and file each rule came from. v2: a script in the brain re-exports the
references and a check fails when the two differ. A brain change reaches the
skill on purpose, never by memory.

## 11. Build order

1. Approve this record.
2. Marketplace skeleton, the plugin, the references, `check_article.py` with
   its fixtures, each check seen to fail.
3. Narsil profile in `Narsil-Creative/narsil`; trial on calendar #12
   (ChatGPT ads, draft due Nov 30); compare against an approved article.
4. A second profile in one non-Narsil repo to prove the core is brand-neutral.

## 12. Open, not blocking

- Move the voice skills (`narsil-voice`, `manifest-voice`, `jaxhumor-voice`)
  into this marketplace so each has one copy. Recommended, separate step.
- A claude.ai upload for use outside Claude Code: per claude.ai org, a copy to
  keep in step; only if needed.
- Client sites: a profile per client repo works the same way; no core change.
