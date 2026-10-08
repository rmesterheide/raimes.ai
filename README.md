# raimes.de

Personal blog about Claude Code, private AI and homelab topics.
Built with [Hugo](https://gohugo.io) and the
[PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme,
deployed to GitHub Pages by the workflow in `.github/workflows/hugo.yaml`.

## Local workflow

```bash
# first clone: pull the theme submodule
git submodule update --init --recursive

# live preview with drafts at http://localhost:1313
hugo server -D

# new post (creates content/posts/<slug>.md as draft)
hugo new posts/my-post-title.md
```

Set `draft: false` in the front matter to publish. Every push to `main`
rebuilds and deploys the site.

## Theme update

```bash
git submodule update --remote --merge themes/PaperMod
```
