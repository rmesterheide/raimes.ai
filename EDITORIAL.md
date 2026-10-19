# Editorial plan for raimes.ai

One post per week at most. One learning per post, not a chronicle. English only.

## Format

- 600 to 1200 words. One problem, one solution, and at least one thing the reader can try right away: a command, a config block, a prompt, a Home Assistant YAML snippet. Every snippet is copy-paste ready, says where it runs and what the expected result looks like. No secrets, no home IPs, placeholders in angle brackets.
- Fixed structure: starting point, what broke, what fixed it, what I would do differently.
- Three tags are enough: `claude-code`, `homelab`, `private-ai`. No numbered series; every post stands alone.
- Publish on Tuesdays. If a week has nothing worth saying, skip it. No filler.

## Workflow

1. At the end of a work session, add candidates to the backlog below with a one-sentence learning.
2. Friday: Claude drafts the next post from CLAUDE.md files, memory and notes as `draft: true` in `content/posts/`.
3. Raiko reads, cuts, corrects. Tuesday: `draft: false`, push, done.
4. Before publishing, check: no secrets, no tokens, no customer names, no home-network IPs, no order numbers, no children's names.

## Backlog (in publishing order)

Two threads alternate: the tools and infrastructure thread (Claude Code, homelab) and the family thread (what the five-year-old actually gets out of all this). Rule for the family posts (Raiko, 2026-10-09): no photos of the child, no generated images with his face, no name. He is "my five-year-old".

| Week | Working title | Core learning | Status |
|---|---|---|---|
| 1 | A voice assistant for a five-year-old, built on Home Assistant and Claude | The slow parts are the pause detection and the voice, not speech recognition; two wake words give two personas | published 2026-10-08 |
| 1b | The voice box, measured: where two seconds really go, and the one-second trick that fixed the feeling | HA plays only after the last token; cloud STT is faster than local; local voice ties with Azure blind; filler word in the ESPHome firmware | published 2026-10-10 (off-schedule, Raiko's call); filler snippet updated to v2 (own mixer input) the same evening |
| 2, Tue 14.10. | Moving a dead WordPress to Hugo on GitHub Pages in one evening | Pages via API, one custom domain per site, a router caching "domain does not exist" for a fresh domain | notes in CLAUDE.md |
| 2b | Private AI Services 3.0 on VMware Cloud Foundation 9.1.1: the five changes that matter | Model sharing decouples gateway and model; private does not mean no public models; tenants without GPUs; three logins; pass-through pins the VM | published 2026-10-15 (off-schedule, Raiko's call), https://raimes.ai/posts/private-ai-services-3-on-vcf-9-1-1/ ; Explore on Tour talk CLOB1084, public sources only |
| 2c | My homelab in five layers, October 2026 | One always-on node holds the context, every other layer gets one job; the architecture card is generated from a script and rendered with headless Chrome | published 2026-10-15 (off-schedule, Raiko's call), https://raimes.ai/posts/my-homelab-in-five-layers/ ; card and LinkedIn text in `../linkedin-post-homelab-architecture-2026-10.md` |
| 2c | GPU architecture for model serving on VMware Cloud Foundation: whatever you pass through pins the VM | Three server kinds, own the host / card / slice, NVLink ten times faster than the network out, letter = GPU and number = network, option C is the everyday case | draft 2026-10-15, `content/posts/gpu-architecture-for-model-serving-on-vcf.md` (second half of CLOB1084, public sources only) |
| 2d | Leaving GitHub Pages for a 2-euro web host, in one afternoon: visitor numbers without a tracker | GitHub Pages gives the owner no logs; anonymised server logs are the only reach measurement German regulators call unproblematic; Hugo deploy becomes lftp over SFTP from GitHub Actions; DNS, certificate and konsoleH clicks done by Claude in Chrome; GoAccess on the Mac mini and a Blog section in the morning report | idea (Raiko, 2026-10-17, "das werden wir auch als Blog veroeffentlichen"); facts in CLAUDE.md "Hosting" and `../reports/Blog Hosting mit Besucherstatistik.md`; wait for the first week of real numbers |
| 2e, Tue 20.10. | From 125 ms spikes to 1 ms: a Sonos and Wi-Fi tune-up with Claude Code | The soundbar on 2.4 GHz was the outlier; one cable flips the household onto SonosNet and makes six players worse; the SonosNet off switch (app 85) is the fix Sonos recommends for UniFi; automatic channels had the access points jamming each other | published 2026-10-18 (off-schedule, Raiko's call), https://raimes.ai/posts/sonos-wifi-tune-up-with-claude-code/ ; blog only, no LinkedIn (Raiko) |
| 2f | Route to Private AI Services 3.0, part 1 of 2: from a fresh ESX host to a Kubernetes API in one evening | vSphere Supervisor with VDS and the built-in Foundation Load Balancer on one host: one control plane VM, one load balancer VM, API about seven minutes after Finish; the work is DNS (forward and reverse), NTP, three port groups, a tag-based storage policy; five traps (FIPS SSH rejects ed25519, localdomain FQDN, duplicate FLB network name, DHCP on VIP VLAN, x86-only kubectl-vsphere) | draft 2026-10-19, `content/posts/kubernetes-api-on-vsphere-in-one-evening.md`; follow-up: PAIS on this Supervisor |
| 3, Tue 21.10. | Dino of the day: why image models cannot draw a Stegosaurus | Licensed Wikimedia art first, a vector drawing as the reliable layer, Flux has no anatomy, an LLM judge needs two passes | App-Development/Dino-des-Tages |
| 4, Tue 28.10. | An AI sales desk for selling old hardware | Evidence per claim before "ready", duplicate detection, fraud patterns in offers, Cloud Run with workers at home, the day bucket reads cost 2.50 EUR | SalesSupportApp (no buyer names, no serials, no order numbers) |
| 5, Tue 04.11. | A family dashboard a five-year-old reads | Kitchen tablet, dino of the day, the energy dino that shows solar surplus in five pictures, admin vs family views | home-assistant, energie-dino |
| 6, Tue 11.11. | Let Claude read your terminal | `script` plus rsync instead of screenshots, including the window-size bug and the setsid fix | shell-setup |
| 7, Tue 18.11. | A dino story every morning, written while we sleep | Prompt rules for a five-year-old (180-250 words, nothing scary, two participation lines), scheduled on the Mac mini, facts from the dino list | MacMini/dino-geschichte |
| 8, Tue 25.11. | Dino Runner: a game for a five-year-old with zero asset files | Canvas-drawn graphics, synthesized sound, PWA on the iPad, Guided Access, built in conversation with Claude | DinoGame |
| 9, Tue 02.12. | Putting my kid on a dinosaur: training a LoRA on the 4090 | 61 photos, 3000 steps, where overfitting shows, two-reference compositing, and why the profile was pulled again | Bildstudio4090 (no photos published) |
| 10, Tue 09.12. | A Mac mini as always-on control room for Claude Code | Sessions on the mini, Remote Control, SMB share | LinkedIn draft exists |
| 11, Tue 16.12. | The voice box as a household member: a product view | Reflex before reasoning, context instead of memory, parents see everything, two seconds is the target | Whisper4090/roadmap-familienalltag |
| later | One fact per file: how I run Claude Code memory | Memory folder, index, feedback rules such as "never guess click paths" | memory folder |
| later | What an RTX 4090 at home is actually for | Whisper benchmark (2,259 clips), LoRA training, solar power | benchmark README exists |
| later | Claude in Chrome: the tab group trap | Two browsers, keep the group open, verify with osascript | memory note |
| later | Cost guardrails for hobby cloud projects | Billing cap, bucket access costs, deploys stay with the human | homelab notes |
| later | Local voice for the adults' pipeline: Whisper on the mini, Piper on the Pi | Offline operation, word list fixes proper names | planned |
| later | Transferring a .de domain: AuthInfo, DENIC and the waiting game | The losing provider has to store the AuthInfo first | in progress |
| later | Skills as team rules | When a skill beats a memory note | skills folder |
