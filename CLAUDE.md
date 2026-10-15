# raimes.ai

Personal blog, Hugo + PaperMod, deployed to GitHub Pages. Posts are English.

## Status (2026-10-08)
- Domain switched to raimes.ai on 2026-10-08 (registered at GoDaddy, expires 2028-10-08). raimes.de stays as a secondary name and should forward to raimes.ai once it lives at GoDaddy.
- Live via GitHub Pages (repo rmesterheide/raimes.ai, workflow deploy, HTTPS enforced).
- raimes.de DNS (zone at GoDaddy, see below): apex A -> 185.199.108.153, www CNAME -> rmesterheide.github.io (both live).
- df.eu cancellation submitted 2026-10-08: hosting ends 09.11.2026, domain marked for provider transfer (must leave by 18.07.2027).
- raimes.ai DNS at GoDaddy done 2026-10-08: 4 A records -> GitHub Pages IPs, www CNAME -> rmesterheide.github.io. GitHub Pages custom domain = raimes.ai.
- raimes.de and www.raimes.de redirect to raimes.ai via the tiny Pages repo rmesterheide/raimes-de-redirect (local: ../raimes-de-redirect), HTTPS enforced. Keep raimes.de DNS on the GitHub IPs after the transfer.
- raimes.de transfer to GoDaddy started 2026-10-08 (order 4173484041) but blocked: GoDaddy tried 7 times on 08.-09.10., all rejected; transfer order stays open until about 07.11.2026. Cause as of 2026-10-12: the cancellation mail lists an authcode, but df.eu never sent the separate AuthInfo mail it promises for .de domains, and DENIC still shows the record unchanged since 2021, so no AuthInfo is stored. df.eu ticket DF-1152836 (domain D2116356) opened 09.10., only the auto-ack so far. Checked 2026-10-12 in the df.eu customer menu (domain page, "Authcode" > "Anzeigen"): df.eu shows the same code and claims it is stored; GoDaddy transfer page still says "Ungültiger Autorisierungscode" (code was always pasted, no typo); ticket still unanswered, df.eu warns of several days backlog. df.eu chat on 12.10. 11:33-11:54 (agent Sara Mustafa): only raised ticket priority from Medium to Highest, no AuthInfo action taken. Next: phone df.eu (+49 89 998 288 026) or use the chat in the customer menu, ask them to (re)create the AuthInfo1 at DENIC, then re-enter the code at dcc.godaddy.com/control/transfers. Fallback: GoDaddy requests an AuthInfo2 from DENIC, sent by letter to the holder.
- raimes.de DNS is NOT at df.eu: DENIC lists ns81/ns82.domaincontrol.com (GoDaddy) since 2021, the df.eu nameservers do not answer for the zone. Records live in the GoDaddy DNS zone.
- Old WordPress still answers at blog.raimes.de via the wildcard A record until the hosting ends.

## Drafts (2026-10-10)
- `content/posts/voice-box-deep-dive.md` (published 2026-10-10, https://raimes.ai/posts/voice-box-deep-dive/): follow-up to the voice post, corrects two claims from part 1 (cloud voice is not 2 s; the 4090 is now in use). Charts in `static/images/voice-box-deep-dive/` come from `../homelab/benchmarks/tts-voice/scripts/charts.py`. About 1,600 words, above the 1,200 guideline on purpose (deep dive); Raiko cuts. Snippet: the ESPHome filler-sound overlay with placeholders. Build checked with `hugo -D`. Lesson: a post date later than the deploy time makes Hugo skip the page (first push rendered a 404 until the date was moved back).

## Drafts (2026-10-15)
- `content/posts/private-ai-services-3-on-vcf-9-1-1.md` (published 2026-10-15, https://raimes.ai/posts/private-ai-services-3-on-vcf-9-1-1/): recap of the Explore on Tour session CLOB1084 (14.10.2026), TL;DR plus five highlights of PAIS 3.0 on VCF 9.1.1. Sources: Raiko's speaker notes and `../CLOB1084/notebooklm/00`-`02`, cross-checked against the Broadcom GA post of 03.09.2026. Only content that was spoken on stage or is in public docs; no co-speaker names, no roadmap beyond what Broadcom announced publicly. "Not in 9.1.1" section removed before publishing on Raiko's request. About 1,250 words. Still open: re-check the PAIS 3.0 release notes on TechDocs for the two known issues and the provider list (the TechDocs URL could not be fetched from here).

## Conventions
- Editorial plan and post backlog: `EDITORIAL.md`. One post per week at most, drafts stay `draft: true` until Raiko says publish.
- Posts go in `content/posts/<slug>.md`, front matter per `archetypes/posts.md`.
- Keep `draft: true` until Raiko says publish.
- Preview: a Hugo server with drafts runs permanently on the Mini (LaunchAgent `de.raimes.hugo-raimes`, see `../homelab/mac-mini/README.md`). Open `http://macmini01.local:1313/posts/<slug>/` in the MacBook browser; never give `localhost` links, Raiko reads the app on the MacBook. Still run `hugo -D` for a build check before pushing; every push to `main` deploys.
- Theme is a git submodule in `themes/PaperMod`; do not edit files there,
  override via `layouts/` instead.
