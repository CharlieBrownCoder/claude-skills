# The source log

Every article ends with an HTML comment listing what was checked, so the
next person (or the refresh) can re-verify without redoing the research.
Comments do not render; the log is for editors, not readers.

## Format

```markdown
<!-- Sources checked YYYY-MM-DD:
https://example.com/page : what this page confirms, with a short quote where a quote settles it.
https://example.com/other (last updated YYYY-MM-DD) : what it confirms.
Internal: path/to/facts-file.md (which facts); path/to/source-playbook.md (what came from it).
-->
```

Rules:

1. The opening line is exactly `<!-- Sources checked ` followed by the date
   the checks were made and a colon. `check_article.py` looks for it.
2. One line per source: the URL, a space, a colon, a space, then what it
   confirms. Quote the sentence that settles a claim when there is one.
3. If the page shows a last-updated date, record it in brackets after the
   URL.
4. `Internal:` lists the repo files facts came from (prices, product names,
   bios) and the source document the piece was derived from.
5. Every outside claim in the article has a line. A claim with no line is cut.

## Method provenance (when a method came from someone else)

When the piece teaches a method someone else taught publicly, add a second
comment above the source log, whether or not the article credits them in
the body:

```markdown
<!-- Method provenance (internal): <method> follows <person>'s <where and
when, with a URL>. <Credit in the body, or why not: the profile's rule or
the owner's call, with its date>. -->
```
