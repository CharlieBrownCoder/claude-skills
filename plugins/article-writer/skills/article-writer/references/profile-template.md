# The repo profile: `.claude/article-writer.md`

One file per repo that uses the skill. It is the only place a brand rule
lives. Copy the template below, fill every field, delete the comments.
Pointers to files the repo already keeps (an editorial guide, a facts file)
beat copying them here: a copy drifts.

The `checks` block is read by `scripts/check_article.py`. It is plain
`key: value` lines inside a fenced block whose info string is `checks`.
Lists are comma-separated. Unknown keys fail the checker, so a typo is loud.

## Template

````markdown
# Article Writer profile: <Brand>

## Brand
- Brand: <name>
- Site: <domain>
- Voice skill: <skill name, e.g. narsil-voice>. Load before drafting.
- Brand facts: <path to the repo's facts file, or a short list here>
- Reader: <who reads this, one sentence>

## Where things live
- Published articles: <path>
- Drafts: <path>
- Source library: <path to playbooks or notes, or "none">
- Editorial guide: <path, or "none">

## Article shape
- Frontmatter: <path to the schema, or the YAML inline>
- Title case: <Title Case | sentence case>
- Length: <e.g. 1,200-1,800 words>
- Bylines: <who signs what>
- FAQs: <count, any required brand FAQ, or "none">
- CTA: <how the site adds one; usually "the template does, never in the body">

## Links
- Internal links per article: <e.g. 3-5>
- Always consider: <money pages, method page>
- Date causality: <yes | no> (yes: link only to pages dated before this one)

## Rules this brand adds
- <e.g. never name another brand's tool that does what ours does>
- <e.g. attribution: shipped text that teaches a method credits its source>

## Repo checks
- <command to run after the core checks, or "none">

```checks
description_max: 155
description_field: description
keyword_field: keyword
title_field: title
slug_field: slug
required: title, slug, description, keyword
banned_extra:
banned_allow:
placements: title, description, slug, h1, first_sentence
source_log: required
placements_fail: no
```
````

## The `checks` keys

| Key | Default | Meaning |
|---|---|---|
| `description_max` | 155 | Maximum meta description length in characters. |
| `description_field` | description | Frontmatter key of the meta description. |
| `keyword_field` | keyword | Frontmatter key of the target keyword. |
| `title_field` | title | Frontmatter key of the title (the H1 when the body has none). |
| `slug_field` | slug | Frontmatter key of the slug. |
| `required` | title, slug, description, keyword | Frontmatter keys that must be present and non-empty. |
| `banned_extra` | (empty) | Words banned for this brand on top of the core list. Whole words, case-insensitive. |
| `banned_allow` | (empty) | Core banned words this brand allows, by their list name (e.g. `folks`). |
| `placements` | all five | Which of the five placements the keyword must hit. Drop one only with a reason in the profile. |
| `source_log` | required | `required` or `optional`. |
| `placements_fail` | no | `no`: a placement miss is a WARN to fix or explain. `yes`: it fails the draft. |

## Example: narsilcreative.com

```markdown
# Article Writer profile: Narsil Creative

## Brand
- Brand: Narsil Creative
- Site: narsilcreative.com
- Voice skill: narsil-voice. Load before drafting.
- Brand facts: site/content/EDITORIAL.md, section "Brand facts"; product
  facts in narsil-brain-v1/data/narsil-seo-product-facts.md
- Reader: a business owner or in-house marketer burned by agencies before.

## Where things live
- Published articles: site/content/articles/
- Drafts: site/content/drafts/
- Source library: narsil-brain-v1/playbooks/ (bucket in TRIAGE.md)
- Editorial guide: site/content/EDITORIAL.md (it wins over this profile)

## Article shape
- Frontmatter: EDITORIAL.md, "Frontmatter schema (exact)"
- Title case: Title Case titles, sentence case H2s
- Length: 1,200-1,800 words
- Bylines: "Nate Morris" on money and authority posts, "The Narsil Team" on
  definitional and volume posts
- FAQs: 3-5 in frontmatter, exactly one brand-entity FAQ, never promise FAQ
  rich results
- CTA: the template appends it; never in the body

## Links
- Internal links per article: 3-5 to articles, plus one to a service page or
  /reforge-method/
- Date causality: yes

## Rules this brand adds
- Never name or link another brand's tool that does what a Narsil SEO tool
  does (EDITORIAL.md mechanics 9).
- Grey-area list, quarantine heading, attribution exceptions, proof rule and
  freshness rule: narsil/CLAUDE.md, "Hard rules".
- "honest" and its family are banned in published copy.

## Repo checks
- python3 site/scripts/content-gates.py

```checks
description_max: 155
required: title, slug, description, category, author, datePublished, dateUpdated, keyword, tldr
banned_extra: honest, honestly, honesty
```
```
