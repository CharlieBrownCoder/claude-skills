# chatgpt-business-hub-builder

This marketplace is the home of the `chatgpt-business-hub-builder` skill from
2026-11-21. Version 1.0.0 is the claude.ai synced skill of the same name, copied
byte for byte on that date (SKILL.md sha256 starts `4942c2f3f6ba1094`). From here on:

- Edit the skill here. Bump `version` in `.claude-plugin/plugin.json` with
  every change, or installed copies keep the cached one.
- Any other copy is stale by definition: the claude.ai synced skill until it
  is replaced from this folder.

Enable it in a repo with
`"enabledPlugins": { "chatgpt-business-hub-builder@claude-skills": true }`
beside the `extraKnownMarketplaces` entry in the root README.

## Cover photo (1.1.0)

Version 1.1.0 adds the cover photo step and `scripts/build-cover.js`, which
renders the 1200 x 400 cover, a 2400 x 800 copy and a mock of the profile
card. It needs Node with Playwright and Chromium.

`examples/narsil-cover.json` is the Narsil Creative cover. Its font and logo
paths are relative to the config file, and the files are not kept here: copy
`Geist-400.woff` and `Geist-700.woff` from `site/src/app/_fonts/` and
`narsil-tile.svg` from `site/public/brand/` in `Narsil-Creative/narsil` beside
the config before running it. Without the fonts the script falls back to the
system sans-serif.

The card layout the mock draws was measured from one desktop screenshot on
2026-11-21. OpenAI does not document it; recheck when a card looks different.

## Still owed

- `narsil-facts.md`. SKILL.md tells the reader to load it for Narsil Creative,
  and the synced skill did not carry it. Add it under
  `skills/chatgpt-business-hub-builder/` or drop the reference.
