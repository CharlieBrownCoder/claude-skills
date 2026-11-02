# The source log

Every article ends with an HTML comment listing what was checked, so the
next person (or the refresh) can re-verify without redoing the research.
Comments do not render; the log is for editors, not readers.

## Format

```markdown
<!-- Sources checked YYYY-MM-DD:
https://example.com/page : what this page confirms, with a short quote where a quote settles it.
https://example.com/other (last updated YYYY-MM-DD) : what it confirms.
NOT OPENED (only while VERIFY-PENDING markers remain): https://vendor.example/help (403 from the session).
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

## Claims waiting on a source: VERIFY-PENDING

Some primary sources cannot be opened from a build session: a vendor's help
center behind a bot wall, a page that needs a login. The claim may stay in a
DRAFT only when its source exists and says so in search results or
reporting you could open; otherwise cut it.

1. Put the marker right after the claim, on its own line or at the end of
   the paragraph:

   ```markdown
   <!-- VERIFY-PENDING: what to confirm; the URL to open, and what you saw instead -->
   ```

   An empty marker fails the checker even in a draft.
2. In the source log, add a `NOT OPENED` line naming each unopened URL and
   why (the status code, the wall).
3. Run the checker with `--draft`: each marker is a WARN. At promote it runs
   without `--draft` and each marker FAILS.
4. Clearing one: a person opens the source, corrects or cuts the claim,
   moves the URL from `NOT OPENED` to a normal log line, and deletes the
   marker.

The word itself in prose (as in this file, or a log line that mentions the
convention) is not a marker; only `<!-- VERIFY-PENDING` opens one.

## Method provenance (when a method came from someone else)

When the piece teaches a method someone else taught publicly, add a second
comment above the source log, whether or not the article credits them in
the body:

```markdown
<!-- Method provenance (internal): <method> follows <person>'s <where and
when, with a URL>. <Credit in the body, or why not: the profile's rule or
the owner's call, with its date>. -->
```
