---
title: "Hello again, raimes.de"
date: 2026-10-08T07:30:00+02:00
draft: false
tags: ["meta", "hugo", "claude-code"]
summary: "Why this site exists, what it replaces and how it is built."
---

This domain has had a WordPress install on it since 2015. Four posts, all
of them tests, the last one from 2022. That is not a blog, that is a
reminder that WordPress needs attention I was never going to give it.

So here is the restart. Static site, Markdown in Git, no database, nothing
to patch.

## What I want to write about

Over the last year most of my evenings went into three things that turned
out to be one thing:

1. **Claude Code** as the tool I actually get work done with. Not demos,
   the daily grind: how I structure projects, what I put in memory, which
   skills I wrote and which ones I deleted again.
2. **Private AI** at home. A 4090 in a workstation, a Mac mini as the
   always-on brain, and the question of what is worth running locally.
3. **The homelab** that holds it together. DNS, backups, power, the boring
   stuff that breaks at 2 a.m.

I keep notes on all of this anyway. Publishing them forces me to tidy them
up, and maybe saves someone else a weekend.

## How this site is built

- [Hugo](https://gohugo.io) with the
  [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme.
- Source lives in a public GitHub repo. Every push to `main` triggers a
  GitHub Action that builds the site and deploys it to GitHub Pages.
- The domain stays with my registrar, only the DNS records point at GitHub.
- Posts are plain Markdown files. Claude Code writes the first draft from my
  notes more often than not, I edit, Git keeps the history.

The whole setup took one evening, including writing this post. That is
roughly the time I used to spend per year ignoring WordPress update
notifications.

## What happens to the old posts

Nothing. They were tests. The old WordPress gets deleted together with the
hosting package once DNS has moved.
