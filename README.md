# claude-skills

Nate's internal Claude Code skills, published as a plugin marketplace so one
copy serves every repo and org. Private; internal use only.

| Plugin | What it does |
|---|---|
| `article-writer` | Publish-ready blog and article drafts in any brand's voice, from a playbook, a customer question or an existing article. Brand rules come from the repo's `.claude/article-writer.md`. Design: `docs/article-writer-design.md`. |

## Use it in a repo

1. Add to the repo's `.claude/settings.json`:

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

   Or, from the repo: `claude plugin marketplace add CharlieBrownCoder/claude-skills --scope project`
   then `claude plugin install article-writer@claude-skills --scope project`.

2. Add the repo's profile, `.claude/article-writer.md`, from
   `plugins/article-writer/skills/article-writer/references/profile-template.md`
   (or ask the skill to write one: it asks for the fields the first time).

3. Accept the folder's trust prompt when Claude Code opens the repo.

The machine needs read access to this private repo through its own git
credentials (an SSH key in an agent, or `gh auth login` then
`gh auth setup-git`).

**Cloud sessions (claude.ai/code) do not install plugins a repo enables.**
See the design record, §9 and §12, for the options.

## Develop

```
python3 -m unittest discover -s plugins/article-writer/tests -v   # the checker's tests
python3 plugins/article-writer/tests/mutations.py                 # every checker mutation must be caught
claude plugin validate . && claude plugin validate ./plugins/article-writer --strict
```

CI runs the first two on every push. Bump `version` in
`plugins/article-writer/.claude-plugin/plugin.json` on every release, or
installed copies keep the cached one.

## Rules for this repo

- A brand rule never goes in a plugin's core; it goes in that repo's profile.
- A rule distilled from the Narsil Brain records its source in the plugin's
  `references/provenance.md`. No source transcript and no grey-area tactic
  is ever carried in.
- Every check is proven by its own failure: a test that applies the mutation
  it guards against, and an entry in `tests/mutations.py` that breaks the
  check and must turn the suite red.
