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

Checked against the Claude Code plugin docs on 2026-10-25 and by a real
install (§13).

`.claude/settings.json` in the repo:

```json
{
  "extraKnownMarketplaces": {
    "claude-skills": {
      "source": { "source": "github", "repo": "CharlieBrownCoder/claude-skills" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "article-writer@claude-skills": true }
}
```

The key under `extraKnownMarketplaces` must be the marketplace's own `name`
(`claude-skills`). Or run, in the repo:
`claude plugin marketplace add CharlieBrownCoder/claude-skills --scope project`
then `claude plugin install article-writer@claude-skills --scope project`.
Then add the repo's `.claude/article-writer.md`.

What the docs say limits it:

- **Local Claude Code only.** The repo's settings are honoured after the
  folder's trust dialog is accepted. Private-repo access comes from the
  machine's own git credentials (SSH key in an agent, or `gh auth login` and
  `gh auth setup-git`); Claude Code has no token of its own, and background
  auto-update fails quietly if a credential would need a prompt.
- **Cloud sessions (claude.ai/code) do not install plugins a repo enables.**
  The documented path for cloud is the claude.ai organization's managed
  settings (Organization settings > Claude Code > Managed settings), set by an
  Owner, which applies to every member of that claude.ai org. Each claude.ai
  org that should have the skill in the cloud needs it set there, or the
  skill uploaded as a claude.ai skill. Open decision, §12.
- **Invocation.** Claude loads the skill from its description; by hand it is
  `/article-writer:article-writer`.

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

## 12. Open

- **Cloud sessions: DECIDED 2026-11-02 (Nate: "Managed settings").** Each
  claude.ai org that should have the skill in cloud sessions sets it in
  Organization settings > Claude Code > Managed settings (an Owner does
  this), with the same two keys as §9:

  ```json
  {
    "extraKnownMarketplaces": {
      "claude-skills": {
        "source": { "source": "github", "repo": "CharlieBrownCoder/claude-skills" },
        "autoUpdate": true
      }
    },
    "enabledPlugins": { "article-writer@claude-skills": true }
  }
  ```

  Consequences: the skill is on for every member of that org in every repo
  (about 200 tokens always on); no claude.ai skill upload, so there is one
  copy. Not yet seen working: that a cloud session can read this PRIVATE repo
  when it fetches the marketplace. The first cloud session after the setting
  is saved is the proof; if it cannot, the fix is access for the Claude
  GitHub App to this repo, not a second copy.
- **Voice skills: MOVED 2026-11-02 (Nate: "move the voice skills into the
  marketplace").** `narsil-voice` and `manifest-voice` are plugins here,
  copied byte for byte from the claude.ai synced skills, and this repo is
  their home from that date. `jaxhumor-voice` was NOT moved: the synced
  skill is a stub with no rules (its description is "Let's create a voice
  specific to Jax Humor"); Jax Humor's voice lives inside the
  `jaxhumor-writing` skill. Still owed for one copy each: removing the
  claude.ai synced copies, and replacing the vendored
  `narsil-brain-v1/infra/skills/narsil-voice` in Narsil-Creative/narsil.
- Client sites: a profile per client repo works the same way; no core change.

## 13. As built (step 2, 2026-10-25)

- The marketplace and plugin pass `claude plugin validate` (the plugin with
  `--strict`). A local install (`claude plugin marketplace add` then
  `claude plugin install article-writer@claude-skills`) reports one skill,
  about 200 tokens always on and about 1.4k when it runs.
- `check_article.py` runs eight checks: required frontmatter, description
  length, em dashes, banned words, the internal-only heading, image
  placeholders, the source log, and the five placements.
- Proof: 18 input mutations each fire exactly their named check on a clean
  fixture, plus boundary, profile and exit-code tests (14 tests); and 22
  mutations of the checker itself are each caught by the suite
  (`tests/mutations.py`, run in CI). One survived first: an off-by-one in the
  description limit, invisible to a fixture far over the limit; a 155/156
  boundary test now catches it.
- Calibration on narsilcreative.com's 88 live articles (Narsil checks
  block): the 7 written to the current standard (2026-10-22 on) pass with no
  warning. The rest fail only on the source log, a convention that predates
  them, except `humanize-ai-content`, which quotes slop words as specimens
  (exempt in the site's own gates too). Read literally, the five placements
  missed on 44 approved articles, mostly question keywords reworded in the
  title ("should i run google ads" in "Should You Run Google Ads?"). So a
  placement miss is a WARN by default, and `placements_fail: yes` makes it
  hard. A new rule for the writer, not a finding against those articles.
- The slug placement passes when the slug carries at least half the
  keyword's content words, plurals folded: slugs here are short on purpose.

## 14. VERIFY-PENDING (adopted 2026-11-02, Nate: "yes, adopt VERIFY-PENDING in the skill")

Found by the step 3 trial (Narsil calendar #12, ChatGPT ads): OpenAI's help
and announcement pages return 403 to the build container, directly and
through archives, and the rule "a claim with no source you can open today is
cut" would have gutted an article whose substance is that platform's rules.
The site already used `<!-- LINK-PENDING: slug -->` for the same shape of
debt, so the skill now has its twin.

- A draft may keep a claim whose primary source exists but cannot be opened
  from the session, only with `<!-- VERIFY-PENDING: claim; source -->` after
  it and a `NOT OPENED` line in the source log.
- `check_article.py --draft` reports each marker as a WARN; without
  `--draft` (promote) each FAILS. An empty marker fails either way. Only
  `<!-- VERIFY-PENDING` opens a marker; the word in prose does not.
- Proof: 19 input mutations, 17 tests, 29 checker mutations, each caught.
- Plugin version 0.2.0.

## 15. Build step 4: a second brand (Manifest, 2026-11-03)

Nate: "start build step 4 on the Manifest repo". Profile and trial in
`TheManifestApp/manifest-website`, branch `claude/article-writer-profile`.
The trial ran REFRESH mode (the one the Narsil trial did not exercise) on
the live post /blog/most-common-goals-people-set/.

What the second brand proved about the core:

- **Published articles are not always a folder.** Manifest's blog lives in
  Sanity. The profile can now name a listing command and a "read one
  article" command (the repo gained `scripts/blog-posts.py`, stdlib, reading
  the public dataset), and a "Promote" line says how a draft goes live.
  Plugin 0.3.0.
- **Not every platform has an updated date.** Sanity's post has only
  `pubDate`; refresh mode now records the refresh in the source log and the
  report when the platform has no field for it.
- **A brand ban is a phrase, not always a word.** The first Manifest profile
  banned "dominate" and failed a plain sentence ("Health and fitness
  dominate the top"); the rule is about hustle phrasing, so the profile bans
  "dominate your". The checker needed no change: `banned_extra` already
  takes phrases.
- **Everything else held unchanged:** the brief, the safety pass, the
  source log, VERIFY-PENDING (none needed: every source opened), the eight
  core checks, the Manifest voice plugin in place of narsil-voice.

What the refresh found in the live post: two wrong Strava claims (Quitter's
Day's origin, and "twice as much activity" where Strava reported 21% further
and 10% longer), one unsourced statistic (34% of under-30s), two unsourced
trend claims, two core-banned words, a 158-character description and no
source log. The draft fixes all of them and keeps the author's wording
everywhere else.

Blog length, SETTLED 2026-11-03 (Nate: "700-1,100 wins"): manifest-voice said
1,000-1,500 and manifest-blog-post 700-1,100. manifest-voice now says 700-1,100
(plugin 1.0.1) and so does Manifest's profile.
