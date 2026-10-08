# raimes.de

Personal blog, Hugo + PaperMod, deployed to GitHub Pages. Posts are English.

## Status (2026-10-08)
- Repo scaffolded locally, builds clean with Hugo 0.167 extended.
- Not yet pushed to GitHub. Pages and DNS not yet switched.
- Old WordPress still lives at blog.raimes.de on df.eu cPanel hosting
  (7.99 EUR/month, billed monthly). Delete hosting after DNS has moved.

## Conventions
- Posts go in `content/posts/<slug>.md`, front matter per `archetypes/posts.md`.
- Keep `draft: true` until Raiko says publish.
- Check locally with `hugo server -D` before pushing; every push to `main` deploys.
- Theme is a git submodule in `themes/PaperMod`; do not edit files there,
  override via `layouts/` instead.
