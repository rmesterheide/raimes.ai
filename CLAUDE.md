# raimes.ai

Personal blog, Hugo + PaperMod, deployed to GitHub Pages. Posts are English.

## Status (2026-10-08)
- Domain switched to raimes.ai on 2026-10-08 (registered at GoDaddy, expires 2028-10-08). raimes.de stays as a secondary name and should forward to raimes.ai once it lives at GoDaddy.
- Live via GitHub Pages (repo rmesterheide/raimes.de, workflow deploy, HTTPS enforced).
- raimes.de DNS at df.eu: apex A -> 185.199.108.153, www CNAME -> rmesterheide.github.io (both live).
- df.eu cancellation submitted 2026-10-08: hosting ends 09.11.2026, domain marked for provider transfer (must leave by 18.07.2027).
- raimes.ai DNS at GoDaddy done 2026-10-08: 4 A records -> GitHub Pages IPs, www CNAME -> rmesterheide.github.io. GitHub Pages custom domain = raimes.ai.
- raimes.de and www.raimes.de redirect to raimes.ai via the tiny Pages repo rmesterheide/raimes-de-redirect (local: ../raimes-de-redirect), HTTPS enforced. Keep raimes.de DNS on the GitHub IPs after the transfer.
- raimes.de transfer to GoDaddy started 2026-10-08 (order 4173484041) but blocked: auth code rejected until df.eu stores the AuthInfo at DENIC. Ask df.eu support if it does not clear by itself.
- Old WordPress still answers at blog.raimes.de via the wildcard A record until the hosting ends.

## Conventions
- Editorial plan and post backlog: `EDITORIAL.md`. One post per week at most, drafts stay `draft: true` until Raiko says publish.
- Posts go in `content/posts/<slug>.md`, front matter per `archetypes/posts.md`.
- Keep `draft: true` until Raiko says publish.
- Check locally with `hugo server -D` before pushing; every push to `main` deploys.
- Theme is a git submodule in `themes/PaperMod`; do not edit files there,
  override via `layouts/` instead.
