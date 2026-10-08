# raimes.de

Personal blog, Hugo + PaperMod, deployed to GitHub Pages. Posts are English.

## Status (2026-10-08)
- Live at https://raimes.de via GitHub Pages (repo rmesterheide/raimes.de, workflow deploy, HTTPS enforced, Let's Encrypt cert).
- DNS still at df.eu: apex A record -> 185.199.108.153. The www CNAME to rmesterheide.github.io is still missing.
- df.eu cancellation submitted 2026-10-08: hosting ends 09.11.2026, domain marked for provider transfer (must leave by 18.07.2027).
- Next: get the auth code at df.eu (Domain-Einstellungen > Authcode > Anzeigen), transfer raimes.de to GoDaddy, then rebuild DNS there (4 A records + www CNAME).
- Old WordPress still answers at blog.raimes.de via the wildcard A record until the hosting ends.

## Conventions
- Posts go in `content/posts/<slug>.md`, front matter per `archetypes/posts.md`.
- Keep `draft: true` until Raiko says publish.
- Check locally with `hugo server -D` before pushing; every push to `main` deploys.
- Theme is a git submodule in `themes/PaperMod`; do not edit files there,
  override via `layouts/` instead.
