# Editorial plan for raimes.ai

One post per week at most. One learning per post, not a chronicle. English only.

## Format

- 600 to 1200 words. One problem, one solution, one code block or screenshot.
- Fixed structure: starting point, what broke, what fixed it, what I would do differently.
- Three tags are enough: `claude-code`, `homelab`, `private-ai`. No numbered series; every post stands alone.
- Publish on Tuesdays. If a week has nothing worth saying, skip it. No filler.

## Workflow

1. At the end of a work session, add candidates to the backlog below with a one-sentence learning.
2. Friday: Claude drafts the next post from CLAUDE.md files, memory and notes as `draft: true` in `content/posts/`.
3. Raiko reads, cuts, corrects. Tuesday: `draft: false`, push, done.
4. Before publishing, check: no secrets, no tokens, no customer names, no home-network IPs, no order numbers, no children's names.

## Backlog (in publishing order)

| Week | Working title | Core learning | Status |
|---|---|---|---|
| 1 | A voice assistant for a five-year-old, built on Home Assistant and Claude | The slow parts are the pause detection and the voice, not speech recognition; two wake words give two personas | drafted 2026-10-08 |
| 2 | Moving a dead WordPress to Hugo on GitHub Pages in one evening | Pages via API, one custom domain per site, a router caching "domain does not exist" for a fresh domain | notes in CLAUDE.md |
| 3 | Let Claude read your terminal | `script` plus rsync instead of screenshots, including the window-size bug and the setsid fix | notes in shell-setup |
| 4 | A Mac mini as always-on control room for Claude Code | Sessions on the mini, Remote Control, SMB share | LinkedIn draft exists |
| 5 | One fact per file: how I run Claude Code memory | Memory folder, index, feedback rules such as "never guess click paths" | memory folder |
| 6 | What an RTX 4090 at home is actually for | Whisper benchmark (2,259 clips), LoRA training, solar power | benchmark README exists |
| 7 | Claude in Chrome: the tab group trap | Two browsers, keep the group open, verify with osascript | memory note |
| 8 | Cost guardrails for hobby cloud projects | Billing cap, bucket access costs, deploys stay with the human | homelab notes |
| later | Local voice for the adults' pipeline: Whisper on the mini, Piper on the Pi | Offline operation, word list fixes proper names | planned |
| later | Transferring a .de domain: AuthInfo, DENIC and the waiting game | The losing provider has to store the AuthInfo first | in progress |
| later | Skills as team rules | When a skill beats a memory note | skills folder |
