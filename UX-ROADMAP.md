# UX assessment and design roadmap for raimes.ai

Written 2026-10-17, the day the site moved from GitHub Pages to Hetzner. Reviewed as a UX designer would: live site at desktop (1440 px) and phone width (390 px), light and dark, plus the repo (`hugo.yaml`, `layouts/`, `EDITORIAL.md`). Six posts online, PaperMod theme with small overrides.

Companion to `EDITORIAL.md` (what we write) and `CLAUDE.md` (how the site is built). This file says what the reader experiences and what to change, in which order.

## 1. Who reads this site, and how they arrive

Three readers, and the order matters for every design decision:

1. **The LinkedIn arrival.** Raiko posts a link, the reader lands on a *post*, not on the home page. They read on a phone, in a feed break, and decide within ten seconds whether to keep reading. For them the post page *is* the home page.
2. **The searcher.** Lands from Google on a post about a specific pain (voice latency, GPU passthrough on VCF). Wants the answer, the snippet, the numbers, and then leaves. Comes back only if the site made itself memorable.
3. **The follower.** Has read two posts, wants to know when the next one appears. Needs a frictionless way to follow (RSS, LinkedIn) and a reason to trust the author.

Consequence: the end of a post (author, read next, follow) is worth more than the home hero. The home page is the second entrance, not the first. The access logs that now exist on Hetzner can confirm or correct this ranking within two weeks; check entry pages before investing in the home page.

## 2. What already works (keep it)

- **Fast and honest.** Home HTML 17 KB, CSS 18 KB, one self-hosted font (48 KB), no tracker, no cookie banner, no JavaScript beyond theme toggle and search. This is rare and is part of the brand. Never add a dependency that breaks it.
- **Readable measure.** About 720 px text column, 18 px body, generous line height. Long reads (8 to 10 minutes) stay comfortable.
- **Dark mode** follows the system and has its own accent values. Both modes look deliberate.
- **Topic colour coding** (teal for Homelab & AI, aubergine for VMware) is the one visual idea that is unmistakably this site. Build on it.
- **Trust signals** that most blogs lack: "How this post was written" aside, the correction policy on About, numbers with the hardware they were measured on, the editorial plan in the open repo.
- **TL;DR first** in every post. Readers who skim get the findings before the story.
- **Mobile is sound.** No horizontal overflow, nav scrolls, cards stack, text wraps cleanly.

## 3. What gets in the way (ranked by reader impact)

### 3.1 The home page shows one post above the fold
Every list card carries a full-width 1200 x 630 cover. On a 1440 x 900 screen the reader sees the intro and one card; on a phone one card fills the screen. The typographic covers repeat the title that stands directly below them, so the reader scrolls past the same words twice per post. Six posts become six screens.

Fix: hide covers in lists (`params.cover.hiddenInList: true`), keep them for social previews and optionally as a small thumbnail. Target: at least three posts visible above the fold on desktop, two on a phone.

### 3.2 One image weighs more than the rest of the site
The homelab architecture card is a 1.1 MB PNG and is used as that post's cover, so the home page and the posts list load it on every visit. Everything else on the home page together is under 300 KB.

Fix now: a typographic cover for the list and social preview, the card stays inside the post. Fix properly in phase 3: Hugo image processing (page resources in `assets/` or page bundles) that emits WebP plus a resized `srcset`.

### 3.3 Two taxonomies and five menu items for six posts
The menu reads Posts, Topics, Tags, Search, About. Topics and Tags both classify the same six posts; the Topics page is two chips on an empty screen; the Tags page is three chips. A reader who clicks Topics gets no posts, only another click.

Fix: menu becomes Posts, Topics, About, with search as an icon or a footer link. The Topics page lists the posts under each topic heading with its description, so one click answers "what is here". Tags stay as pages for later, out of the menu until there are twenty posts.

### 3.4 Titles are too long to scan
"GPU architecture for model serving on VMware Cloud Foundation: whatever you pass through pins the VM" is 101 characters. On a phone the h1 takes six lines; in Google and LinkedIn previews it is cut after about 60. Two of six titles are over 90 characters because the abbreviation rule (spell out VCF) and the "one learning per post" rule both push words into the title.

Fix: a two-line convention. `title` carries the subject in at most 60 characters, `summary` (already present) or a new `subtitle` field carries the learning. The single template shows the subtitle under the h1 as a deck line; list cards show title plus summary as today. Existing posts can be retitled without changing their URLs.

### 3.5 The TL;DR is a bold word, not a component
It is a bold paragraph followed by a bullet list of up to six items of two to three lines each. Visually it is indistinguishable from body text, and six long bullets are no longer a summary.

Fix: a `tldr` shortcode that renders an aside in the same style as the existing "How this post was written" box (left accent border, soft background). Editorial rule: at most three bullets of one line each. The rest of the findings belong in the body.

### 3.6 The post ends abruptly
After the last paragraph come the disclosure aside, a tag row, and prev/next links to whatever post was published before and after. There is no author line with a face, no "read next" by topic, no way to follow, no way to reply.

Fix: a post footer in four parts, in this order: (1) author block with a small photo, one sentence and the LinkedIn link; (2) two "read next" cards from the same topic; (3) one line "Follow: RSS or LinkedIn"; (4) one line "Found an error? Reply on LinkedIn or by mail." Comments (giscus) are not needed yet; a reply channel is.

### 3.7 Long reads with a collapsed table of contents
Posts of 8 to 10 minutes hide their structure behind a "Table of Contents" disclosure that most readers never open. This PaperMod version has no side table of contents.

Fix: on screens wider than about 1200 px, render the ToC as a sticky column to the right of the text (own layout override, the HTML already exists). On phones keep the disclosure. Secondary: show "Updated on" when a post was corrected, which makes the correction policy visible (`lastmod` from front matter or `enableGitInfo`).

### 3.8 Small technical gaps
- No HSTS, `X-Content-Type-Options`, `Referrer-Policy` or `Permissions-Policy` headers. Four lines in `.htaccess`.
- RSS carries summaries only. Homelab readers live in feed readers; `ShowFullTextinRSS: true` gives them the whole post and costs nothing.
- JSON-LD declares the site as an `Organization`. `schema.publisherType: Person` matches a personal blog.
- No skip-to-content link for keyboard and screen-reader users (PaperMod does not ship one).
- `Powered by Hugo & PaperMod` in the footer is theme advertising, not reader information.

## 4. Roadmap

Each phase has a measurable "done". Nothing in phase 0 or 1 needs a theme change.

### Phase 0, this weekend: quick wins (one evening, no risk)

Status 2026-10-17 evening: items 1 to 5 built on the preview, plus the author block from phase 1. Open: TL;DR bullets cut to three (editorial, Raiko), header check after deploy.
1. Covers off in lists; typographic cover for the homelab post; card stays in the body.
2. Menu to Posts, Topics, About; search behind an icon.
3. Topics page lists posts per topic.
4. `tldr` shortcode, applied to the six posts, bullets cut to three.
5. Security headers in `.htaccess`, full-text RSS, `publisherType: Person`, footer line without theme credit.

Done when: home page under 400 KB total, three posts above the fold at 1440 x 900, Topics page shows posts, feed reader shows full posts.

### Phase 1, next two weeks: the post page as home page
1. Title convention (60 characters plus deck line), retitle existing posts, URLs unchanged.
2. Post footer: author block (done 2026-10-17), read next by topic, follow line, reply line.
3. Sticky side ToC on wide screens; "Updated on" line.
4. Two signature components for a site that promises numbers: `measured` (a box with hardware, date, method, placed where the numbers start) and `try-it` (a labelled code block that says where it runs and what to expect, which `EDITORIAL.md` already demands in prose).
5. Skip link and visible focus styles.

Done when: a LinkedIn arrival on a phone sees title, deck, topic and TL;DR without scrolling, and reaches "read next" and "follow" at the end without searching.

### Phase 2, after ten posts (November): orientation and following
1. **Start here** page with three doors: "You run VMware", "You run a homelab", "You are a parent with a voice box". Each door lists three posts in reading order. Linked from the home intro instead of the current two inline links.
2. **Follow** page: what RSS is in two sentences, a copy button for the feed URL, LinkedIn, and nothing else. Newsletter only if the logs show returning readers asking for it.
3. **Lab** page (or `/now`): the current state of the homelab generated from the homelab repo, the same way the architecture card is generated. Few elements, dated, with a change log. This is the page competitors do not have.
4. **Numbers in the open**: a monthly post or a `/stats` page with visitor counts from the anonymised logs. The hosting move was made for exactly this; publishing it is on brand with the privacy stance and gives the "2-euro web host" post its follow-up.
5. Review the entry-page ranking in the logs and re-prioritise the home page accordingly.

Done when: a new reader can choose a path in one click, and following takes under ten seconds.

### Phase 3, winter: foundation decisions
1. **Image pipeline**: move post images to page bundles, let Hugo emit WebP and `srcset`. Fixes the weight problem for every future chart.
2. **Theme decision**: PaperMod stays as long as overrides are under about a third of its templates. If phases 1 and 2 push past that, build a small own theme from the overrides (the CSS is already ours; the templates would be list, single, taxonomy, footer). Candidates to borrow from if a switch is wanted: Hextra (docs-like, good ToC), Blowfish (richer cards). Recommendation today: stay, keep overriding.
3. **Comments**: giscus on GitHub Discussions if the reply line in the footer produces real replies. Otherwise not.
4. **Second language**: no. English stays; German readers from LinkedIn get the German LinkedIn text as their summary.

## 5. Principles to hold while doing all this

- **One signature per site.** The topic colours and the numbers are the signature. Every new component uses the topic colour and shows a number where it can.
- **Fewer, larger elements.** Five posts above the fold beat fifteen. Three bullets beat six. Three menu items beat five.
- **The post page is the product.** Measure success there: scroll depth is not available without a tracker, but entry pages, exit pages and return visits are in the logs.
- **Nothing that needs a cookie banner.** No embedded fonts from Google, no YouTube embeds without a click-to-load wrapper, no analytics script.
- **Check click paths before describing them.** Every UI change gets a screenshot at 1440 and 390 px before it ships (headless Chrome: the 390 px shot needs an iframe wrapper because Chrome's window minimum is about 500 px).
