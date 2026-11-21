---
name: "chatgpt-business-hub-builder"
description: "Build a ChatGPT Business Hub profile, its cover photo, and Business Agent (instructions, Business Info, tagline, conversation starters) for Narsil Creative or a client, from their live site."
---

# ChatGPT Business Hub builder

Builds everything a business pastes or uploads into ChatGPT Business Hub: the profile fields, the cover photo and, when the business is eligible, the Business Agent (instructions, Business Info, tagline, conversation starters). The agent sells toward one next step, with results, values, and candor, and never makes a claim the business's own site can't back.

Input: the business's website URL, plus which next step the agent should drive (book a call, buy, sign up). For Narsil Creative, also read `narsil-facts.md` and load the narsil-voice skill.

## Platform facts (verified November 2026; recheck if a field looks different)

- Business Hub launched in beta on November 10, 2026. Any eligible business where ChatGPT is available can claim a profile. Verification routes: phone, email, website domain, or Shopify. After approval, the person managing the listing passes a Persona ID check before publishing profile changes, connecting a feed, seeing insights, or creating an agent.
- Business Agents: eligible US ecommerce and online service businesses with a website only. Local stores and restaurants can claim a profile but can't publish an agent yet. OpenAI reviews category and intended use before an agent goes live.
- Profile fields: About, Location, Contact, Hours, Photos; website, description, category, logo, cover photo; delivery and return policy; "More about your business" (300 characters). Edits publish after OpenAI review.
- Images: logo 300 x 300 px recommended, cover photo 1200 x 400 px recommended. JPEG, PNG, GIF and WebP are supported.
- How the profile card shows the cover (observed on one desktop card, 2026-11-21, not documented by OpenAI): the whole 3:1 image at about 420 px wide, so everything is about a third of its drawn size. The logo sits over the bottom-left corner, the menu and close buttons sit over the top-right corner, and the lower part is darkened by a fade.
- Agent fields: instructions (sections "Who you are" and "What you can do"), Business Info (sections the instructions reference by name), agent tagline (one sentence on how the agent helps), and optional conversation starters (questions customers can select).
- The agent answers from what the business provides and links out. It can't take a booking, check an order, or act for the customer. Businesses never see chat transcripts; insights are aggregate (mentions, website clicks, discovery topics, 28 days) and appear only above a volume threshold.
- Claiming does not guarantee placement or recommendations. Never tell a client otherwise.

## Workflow

1. **Eligibility.** Classify the business: agent-eligible (US ecommerce or online service with a website) or profile-only. Profile-only gets steps 2, 3, 4, 5, and 10, plus a one-line note on why there's no agent.
2. **Facts.** Fetch the live site: home, pricing, services or products, about, contact, policies (returns, delivery, cancellation), results or reviews page. Record every price, limit, plan, URL, and policy with its source page. If the site contradicts itself or a facts file, list the conflict; don't pick silently. If a results page is empty, the agent cites no client results.
3. **Next step.** Confirm the one action the agent drives and its exact URL. Read that page so the agent can say what the visitor gets (call length, what's covered, what they keep). A booking pitch built on what the call delivers beats any adjective.
4. **Profile.** Write description, category, "More about your business" (300 characters, count it), hours, contact, delivery and return policy. Answer-first, specific, no superlatives.
5. **Cover photo.** Build it with the section below and check the card preview before delivering.
6. **Agent instructions.** Use the template below. Keep the owner's existing wording wherever it passes the rules.
7. **Business Info.** Use the template below. Every number exact, every section name matching what the instructions reference.
8. **Tagline and starters.** Tagline: one sentence, outcome first, then scope. Starters: 3-4 questions in the customer's voice ("I," "my"), in this order of intent: pain ("Why doesn't ChatGPT recommend my business?"), fit ("Should I hire you or use the software?"), first move ("What would you fix first for a [type] business?"), next step ("What do I get from the free call?"). Skip starters about branded method names; customers don't click what they haven't heard of.
9. **QA.** Check every number and URL against its source page, and read every word on the cover in the card preview. For Narsil, run the narsil-voice lint script. Write the test script (below).
10. **Deliver.** One Markdown file in paste order: profile fields, tagline, starters, instructions, Business Info, then a discrepancy list and the test script. With it, `cover.png`, `cover@2x.png` and `card-preview.png`. Short summary in chat.

## Cover photo

The cover sells the end result and the values in the half second before someone reads the profile. On the card it is shown at about a third of its size, so it carries three things and no more:

- **Label:** what the business is, in a few words ("AI SEO, AEO, GEO").
- **Headline:** the result the customer wants, six words or fewer, on one line, with one word or phrase in the accent colour ("Be the business they name.").
- **Subline:** up to three short items, where or how the result shows up ("On Google · In AI Overviews · In ChatGPT").

Rules:

- Headline and subline are never smaller than 40 px on the 1200 px canvas, which is 14 px on the card. The label is the one smaller line, at 26 px in capitals. Paragraphs, cards, chips and mock screenshots turn illegible; the first Narsil draft had three result cards and none could be read.
- Keep two corners empty. The logo covers the bottom-left (about x 72 to 270, y 314 to 400 on the canvas). The buttons cover the top-right (about x 928 to 1166, y 28 to 132).
- Nothing important in the bottom fifth, which the fade darkens.
- Colours, typeface and logo come from the business's own site. Don't put the logo on the cover; the card already shows it.
- Clean hands apply to images too: no "#1", no star ratings, no ranking or recommendation shown as promised, no other company's logo. Every claim on the cover is one the site backs.

Build it:

1. Copy `examples/narsil-cover.json`, and set the label, headline, emphasis, subline, colours, font files and logo file for the business. Paths are relative to the config file.
2. Run `node scripts/build-cover.js config.json out/`. It needs Playwright with Chromium. It shrinks any line that runs past the right margin and exits with a warning if a line still doesn't fit at the minimum size; shorten that line.
3. Open `out/card-preview.png`. Every word must be readable, and nothing may sit under the logo or the buttons.
4. Deliver `cover.png` (1200 x 400). `cover@2x.png` (2400 x 800) is for an uploader that accepts the larger size.

The preview is a mock built from one screenshot. After the client uploads, ask for a screenshot of the real card, on desktop and on a phone, and adjust if anything is cut.

A Google Business Profile asks for the same two images at the same sizes, but its crop has not been checked. Don't assume this cover fits there.

## Agent instructions template

```
# Who you are
You are [Business]'s [sales guide / product guide]. Visitors come to you with [the problem, in their words]. Your job is to understand that problem, show how [Business] solves it, and get them to [next step].

Be friendly, direct, and specific. Lead with results and values. You can't [book, buy, contact staff] yourself. The visitor takes those steps; you make the next one obvious.

# How you sound
Write like a founder texting one busy customer.
- One idea per line. Short sentences. Most replies under 80 words.
- Mirror what they want before you talk about what we do.
- Use concrete numbers from Business Info. Never an adjective where a number exists.
- No emojis, no exclamation points, no dashes.
- End each reply with one question or one next step.

# What you sell on
**Results.** [Outcomes the customer cares about. Proof only from Business Info. Never invent a result, number, or quote.]
**Values.** [How the business works, from its own site: published pricing, policies, guarantees it actually offers.]
**Candor.** [Who shouldn't buy, and where to send them instead.]

# What you can do
**Understand the visitor's goal** [qualifying questions, one per reply]
**Explain [the product or method]** [cite the Business Info section by name]
**Recommend a fit** [compare options, then recommend one and say why]
**Answer pricing and process questions** [published terms only; point to the pricing page for current details]
**Get them to [next step]** [the URL, what they get, ask once, fallback offer if not ready, respect a no]

# Lines you don't cross
- No guarantees of results or timing beyond what the site states.
- No fake urgency, invented discounts, custom quotes, or availability claims.
- No account or order details.

# Example
[Two-turn exchange: qualify, then recommend with a real price and the next-step link.]
```

## Business Info template

```
# [Business] at a glance
[What it is, who it serves, where, one credibility line from the about page.]

## Services and fit
[Each option: who it's for in one line. Then "Who shouldn't buy yet" and where to send them.]

## [Method or how it works]
[Steps or phases, with typical timelines labeled as typical, not guaranteed.]

## How [Business] works
[Values and terms from the site: reporting, policies, commitments and the reason for them, results-page status.]

## [Products or plans]
[Exact limits and prices per plan; trial and cancellation terms.]

## Pricing and next steps
[Every published price. Then each next step with its URL and what the visitor gets. Close with: the agent can't [actions]; the visitor completes each step.]
```

## Voice rules

The agent uses the Tight register of the sales-email-voice skill adapted for chat: one idea per line, mirror the customer's want, concrete numbers, one ask, permission to say no. Drop its ellipses, CAPS, exclamation points, and countdowns. Follow the business's own voice skill when one exists (narsil-voice for Narsil Creative and Narsil SEO).

Clean hands: never write an agent that promises rankings, recommendations, or results the site doesn't state, or that offers fake reviews, paid links, or anything that couldn't survive being public. Flag it and offer the clean version.

## Test script (deliver with every agent)

Run in Agent builder with Test in ChatGPT:
1. Click each starter; check the answer is specific and ends with one question or step.
2. Ask for a price that isn't published. Expect: no quote, pointer to pricing page or next step.
3. Ask for a guarantee. Expect: typical timeline, no promise.
4. Ask for something off-limits (fake reviews, an account change). Expect: a clean no and a redirect.
5. Say "not ready yet." Expect: the fallback offer once, then no repeat ask.
6. Ask "did you book it?" after the booking link. Expect: the visitor books it themselves.