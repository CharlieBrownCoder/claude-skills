# manifest-voice

This marketplace is the home of the `manifest-voice` skill from 2026-11-02 (Nate:
"move the voice skills into the marketplace"). The skill folder,
`skills/manifest-voice/`, was copied byte for byte from the claude.ai synced skill of
the same name on that date (SKILL.md sha256 starts `16dfeb349d197dfc`). From here on:

- Edit the skill here. Bump `version` in `.claude-plugin/plugin.json` with
  every change, or installed copies keep the cached one.
- Any other copy is stale by definition: the claude.ai synced skill until it
  is removed or replaced from this folder, and any vendored copy in another
  repo (narsil-brain-v1/infra/skills/narsil-voice in Narsil-Creative/narsil).

Enable it in a repo with `"enabledPlugins": { "manifest-voice@claude-skills": true }`
beside the `extraKnownMarketplaces` entry in the root README.
