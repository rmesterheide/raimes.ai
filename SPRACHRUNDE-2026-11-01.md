# Sprachrunde 01.11.2026

Durchgang aller Artikel nur auf Sprache nach Raikos Regel vom 01.11.2026 (einfache Sätze, keine KI-Floskeln und Schlusspointen, keine US/UK-Idiome und Wortspiele, keine Gedankenstriche, Abkürzungen beim ersten Vorkommen ausgeschrieben, feste Formulierung zum Lab-Setting). Teil 4 (`one-card-three-tenants-vgpu-on-the-a5000.md`) war heute früh schon überarbeitet und diente als Maßstab; er ist unverändert.

**Nicht angefasst:** Zahlen, Messwerte, Codeblöcke, Links, Front Matter außer dem Summary-Text von Teil 1 und 2 (dort stand „on vCenter alone“), Log-Zitate, UI-Bezeichnungen, Struktur. **Nachtrag 01.11.2026 09:36:** auf Raikos Zuruf als Commit `e042cd8` gepusht, Deploy-Lauf 41289525913 erfolgreich, Stichproben live geprüft. Nicht im Commit: der Rebuild-Kasten im GPU-Sharing-Post (braucht Shortcode und Styles aus einer anderen Sitzung), die beiden Drafts, `CLAUDE.md`.

Vorschau auf dem Mini: `http://macmini01.local:1313/posts/<slug>/`, z. B. http://macmini01.local:1313/posts/kubernetes-api-on-vsphere-in-one-evening/ und http://macmini01.local:1313/posts/private-ai-services-without-a-gpu/ für die neuen Setting-Absätze. Build-Check `hugo -D`: sauber, 16 Seiten unter /posts/.

## 1. Dateien

| Datei | Datum | Status | Änderungen |
|---|---|---|---|
| `content/about.md` (Seite /about/) | – | veröffentlicht | 1 |
| `content/posts/hello-again.md` (Hello again, raimes) | 08.10.2026 | veröffentlicht | 2 |
| `content/posts/voice-assistant-for-a-five-year-old.md` (A voice assistant for a five-year-old) | 08.10.2026 | veröffentlicht | 3 |
| `content/posts/voice-box-deep-dive.md` (The voice box, measured) | 10.10.2026 | veröffentlicht | 9 |
| `content/posts/private-ai-services-3-on-vcf-9-1-1.md` (PAIS 3.0 on VCF 9.1.1: the five changes) | 15.10.2026 | veröffentlicht | 7 |
| `content/posts/my-homelab-in-five-layers.md` (My homelab in five layers) | 15.10.2026 | veröffentlicht | 8 |
| `content/posts/gpu-architecture-for-model-serving-on-vcf.md` (GPU architecture for model serving on VCF) | 16.10.2026 | veröffentlicht | 13 |
| `content/posts/sonos-wifi-tune-up-with-claude-code.md` (Sonos and Wi-Fi tune-up) | 18.10.2026 | veröffentlicht | 6 |
| `content/posts/kubernetes-api-on-vsphere-in-one-evening.md` (Route to PAIS 3.0, part 1) | 19.10.2026 | veröffentlicht | 8 |
| `content/posts/private-ai-services-without-a-gpu.md` (Route to PAIS 3.0, part 2) | 20.10.2026 | veröffentlicht | 10 |
| `content/posts/model-as-a-service-with-private-ai-services.md` (Model as a Service, the bare minimum) | 21.10.2026 | Draft, nicht in Git | 4 |
| `content/posts/rtx-a5000-behind-the-same-service-name.md` (Route to PAIS 3.0, part 3) | 27.10.2026 | veröffentlicht | 12 |
| `content/posts/sharing-one-gpu-on-the-kubernetes-layer.md` (Sharing one GPU on the Kubernetes layer) | 30.10.2026 | veröffentlicht | 9 |
| `content/posts/one-card-three-tenants-vgpu-on-the-a5000.md` (Route to PAIS 3.0, part 4) | 31.10.2026 | Draft, Maßstab, unverändert | 0 |
| **Summe** | | | **92** |

Gedankenstriche als Satzverbindung: in keiner Datei gefunden (Grep auf „ – “, „—“, „-- “).

## 2. Die wichtigsten Beispiele je Artikel

### Seite /about/ (`about.md`), 1 Änderungen

- **Idiom:** „If you want to know how the sausage is made:“ → „If you want to see how the posts are made:“

### Hello again, raimes (`hello-again.md`), 2 Änderungen

- **Idiom:** „Not demos,    the daily grind: how“ → „Not demos,    the daily work: how“
- **Idiom:** „the boring    stuff that breaks at 2 a.m.“ → „the boring    parts that break at night.“

### A voice assistant for a five-year-old (`voice-assistant-for-a-five-year-old.md`), 3 Änderungen

- **Floskel:** „Then it felt bad. Sitting sixty centimetres“ → „Then the problems started. Sitting sixty centimetres“
- **Floskel:** „The honest answer was: nowhere at home, for now.“ → „The answer was: nowhere at home, for now.“
- **Pointe:** „takes under half a second and sounds like 2015.“ → „takes under half a second and sounds dated.“

### The voice box, measured (`voice-box-deep-dive.md`), 9 Änderungen

- **Floskel:** „because it starts after you stop. So much for "local is faster".“ → „because it starts after you stop. Local is not faster here.“
- **Dreierkaskade:** „Isolated sentences say: level. Level, and nothing leaves the house, and no subscription in the loop. That is enough.“ → „Isolated sentences say: level. Level is enough when nothing leaves the house and no subscription is needed.“
- **Pointe:** „My five-year-old's verdict was one word, and it was not a complaint.“ → „My five-year-old's verdict was one word, and it was positive.“

### PAIS 3.0 on VCF 9.1.1: the five changes (`private-ai-services-3-on-vcf-9-1-1.md`), 7 Änderungen

- **Wortspiel:** „## 3. Teams keep their walls, the GPUs lose theirs“ → „## 3. Teams stay separated, the GPUs are shared“
- **Floskel:** „That is what a dedicated GPU per team looks like, at any scale.“ → „That is what a dedicated GPU per team looks like.“
- **Floskel:** „And no, this needs no special hardware.“ → „This needs no special hardware.“

### My homelab in five layers (`my-homelab-in-five-layers.md`), 8 Änderungen

- **Bild:** „**The storage lied about its speed.**“ → „**The storage was slower than it looked.**“
- **Pointe:** „It stays in the picture because the picture is supposed to show what is there, not what I am proud of.“ → „It stays in the picture because the picture should show what is there.“
- **Floskel:** „Nothing in the house depends on the cloud layer, and I like it that way.“ → „Nothing in the house depends on the cloud layer, and that is intended.“

### GPU architecture for model serving on VCF (`gpu-architecture-for-model-serving-on-vcf.md`), 13 Änderungen

- **Wortspiel, Abkürzung:** „A-1: bare metal with a vSphere badge. GPUs of two hosts exchange data directly over RDMA.“ → „A-1: bare metal behaviour on vSphere. GPUs of two hosts exchange data directly over remote direct memory access (RDMA).“
- **Idiom:** „If you ask me where this is going: here.“ → „In my view this is where the platform is heading.“
- **Idiom:** „## Enhanced DirectPath: the exception that proves the rule“ → „## Enhanced DirectPath: the one exception“

### Sonos and Wi-Fi tune-up (`sonos-wifi-tune-up-with-claude-code.md`), 6 Änderungen

- **Idiom:** „wire exactly one player, or fight your switch.“ → „wire exactly one player, or work against your switch.“
- **Floskel:** „Claude Code went reading. The answer was six weeks old.“ → „Claude Code then read the Sonos sources. The answer was six weeks old.“
- **Idiom:** „The sub rides on the soundbar's private link and inherited it:“ → „The sub uses the soundbar's private link and inherited it:“

### Route to PAIS 3.0, part 1 (`kubernetes-api-on-vsphere-in-one-evening.md`), 8 Änderungen

- **Setting-Satz:** „This is part 1 of 3 on my route to Private AI Services (PAIS) 3.0, deployed the lightweight way: vCenter and a vSphere Distributed Switch only, no NSX, no VMwar…“ → „This is part 1 of 3 on my route to Private AI Services (PAIS) 3.0 on a plain vSphere and vCenter basis: vCenter and a vSphere Distributed Switch, no NSX, no VMware Cloud Foundation (VCF) Automation. P…“
- **Idiom:** „certificates, a second appliance to babysit.“ → „certificates, a second appliance to look after.“
- **Floskel:** „Static ranges inside a DHCP pool work until the day they do not.“ → „Static ranges inside a DHCP pool work until the first conflicting lease.“

### Route to PAIS 3.0, part 2 (`private-ai-services-without-a-gpu.md`), 10 Änderungen

- **Setting-Satz:** „**To be clear about the route:** for an enterprise, the preferred way to run Private AI Services is a full VMware Cloud Foundation (VCF) deployment with VCF Aut…“ → „**About the setting:** PAIS 3.0 is fully supported on a plain vSphere and vCenter basis, and that is what this lab rebuilds. A full VMware Cloud Foundation (VCF) deployment with VCF Automation adds wh…“
- **Setting-Satz:** „For one server in my homelab, with one user, the lightweight way (vCenter, a distributed switch and the built-in load balancer) is enough, and it is the quickes…“ → „I would like to have the multi-tenancy and the NSX-based virtual private clouds as well, but the lab is small: one server, one user. For that, vCenter, a distributed switch and the built-in load balan…“
- **Bild:** „**Trap 1: the registry test that lies.**“ → „**Trap 1: a registry test that fails for the wrong reason.**“

### Model as a Service, the bare minimum (`model-as-a-service-with-private-ai-services.md`), 4 Änderungen

- **Bild:** „so in a lab without VCF Automation, the platform team is also the shop counter.“ → „so in a lab without VCF Automation, the platform team hands out the service names by hand.“
- **Floskel:** „That is the abstraction doing its job:“ → „That is what the abstraction is for:“
- **Idiom:** „and you have the audit trail for free.“ → „and you have the audit trail without extra work.“

### Route to PAIS 3.0, part 3 (`rtx-a5000-behind-the-same-service-name.md`), 12 Änderungen

- **Setting-Satz:** „The setting is unchanged from parts 1 and 2: one EPYC host with ESX 9.1.1, a vSphere Supervisor, Private AI Services (PAIS) 3.0 activated from vCenter alone, no…“ → „The setting is unchanged from parts 1 and 2: one EPYC host with ESX 9.1.1, a vSphere Supervisor, and Private AI Services (PAIS) 3.0 activated from vCenter. PAIS 3.0 is fully supported on a plain vSphe…“
- **Floskel:** „The provider does not care and delivers 700 and more. That is the honest shape of the comparison:“ → „The provider is not affected and delivers 700 and more. That is the shape of the comparison:“
- **Floskel:** „The honest result tonight is that the same client“ → „The result tonight is that the same client“

### Sharing one GPU on the Kubernetes layer (`sharing-one-gpu-on-the-kubernetes-layer.md`), 9 Änderungen

- **Setting-Satz:** „The setting is the same single-host lab as in parts 1 to 3: one EPYC host with ESX 9.1.1, a vSphere Supervisor, Private AI Services (PAIS) 3.0, no VMware Cloud …“ → „The setting is the same single-host lab as in parts 1 to 3: one EPYC host with ESX 9.1.1, a vSphere Supervisor, and Private AI Services (PAIS) 3.0 on a plain vSphere and vCenter basis, which is a full…“
- **Wortspiel:** „I read it as a good default with a loud silence:“ → „I read it as a good default that is too quiet:“
- **Floskel:** „The honest version: for a 24 GB card“ → „In short: for a 24 GB card“

## 3. Vollständige Fundlisten

### Seite /about/ (`content/about.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 39 | If you want to know how the sausage is made: | If you want to see how the posts are made: | Idiom |

### Hello again, raimes (`content/posts/hello-again.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 25 | Not demos,    the daily grind: how | Not demos,    the daily work: how | Idiom |
| 30 | the boring    stuff that breaks at 2 a.m. | the boring    parts that break at night. | Idiom |

### A voice assistant for a five-year-old (`content/posts/voice-assistant-for-a-five-year-old.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 31 | Then it felt bad. Sitting sixty centimetres | Then the problems started. Sitting sixty centimetres | Floskel |
| 77 | The honest answer was: nowhere at home, for now. | The answer was: nowhere at home, for now. | Floskel |
| 80 | takes under half a second and sounds like 2015. | takes under half a second and sounds dated. | Pointe |

### The voice box, measured (`content/posts/voice-box-deep-dive.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 11 | a 4090 that finally earns its place, | a 4090 that finally has a job, | Idiom |
| 39 | because it starts after you stop. So much for "local is faster". | because it starts after you stop. Local is not faster here. | Floskel |
| 43 | I had optimized for it anyway, and the stopwatch did not care. | I had optimized for it anyway, and it made no difference in the measurement. | Bild |
| 53 | the local voice loses its head start: 0.45 seconds to first byte, constant, because HA converts the stream | the local voice loses its advantage: 0.45 seconds to first byte, constant, because Home Assistant converts the stream | Idiom, Abkürzung |
| 57 | Isolated sentences say: level. Level, and nothing leaves the house, and no subscription in the loop. That is enough. | Isolated sentences say: level. Level is enough when nothing leaves the house and no subscription is needed. | Dreierkaskade |
| 59 | **The 4090 earns its place.** It now runs | **The 4090 has a job now.** It now runs | Idiom |
| 59 | which settled that debate. | which settled the question. | Floskel |
| 68 | For the child's wake word that is the trade I want. | For the child's wake word that is the trade-off I want. | Idiom |
| 70 | My five-year-old's verdict was one word, and it was not a complaint. | My five-year-old's verdict was one word, and it was positive. | Pointe |

### PAIS 3.0 on VCF 9.1.1: the five changes (`content/posts/private-ai-services-3-on-vcf-9-1-1.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 24 | - **Three ways to log in:** direct OIDC, OIDC via VCF Automation, local accounts. | - **Three ways to log in:** direct OpenID Connect (OIDC), OIDC via VCF Automation, local accounts. | Abkürzung |
| 26 | - **Under the hood nothing changed.** Whatever you pass through | - **At the GPU layer nothing changed.** Whatever you pass through | Idiom |
| 55 | ## 3. Teams keep their walls, the GPUs lose theirs | ## 3. Teams stay separated, the GPUs are shared | Wortspiel |
| 59 | That is what a dedicated GPU per team looks like, at any scale. | That is what a dedicated GPU per team looks like. | Floskel |
| 61 | And no, this needs no special hardware. | This needs no special hardware. | Floskel |
| 67 | Every new instance is a new IdP integration. | Every new instance is a new identity provider (IdP) integration. | Abkürzung |
| 75 | ## 5. Under the hood: the one rule | ## 5. The GPU layer: the one rule | Idiom |

### My homelab in five layers (`content/posts/my-homelab-in-five-layers.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 11 | the layer that holds the context is the one that never sleeps. | the layer that holds the context is the one that is always on. | Bild |
| 14 | where the house would hurt if a machine went away | where the house would notice if a machine went away | Bild |
| 36 | **The storage lied about its speed.** | **The storage was slower than it looked.** | Bild |
| 44 | does the heavy lifting for voice and images | does the heavy work for voice and images | Idiom |
| 44 | The third machine in that layer is the honest one: a 32-core EPYC server | The third machine in that layer is a 32-core EPYC server | Floskel |
| 44 | It stays in the picture because the picture is supposed to show what is there, not what I am proud of. | It stays in the picture because the picture should show what is there. | Pointe |
| 46 | The rest of the cloud layer is boring on purpose: | The rest of the cloud layer is kept simple on purpose: | Floskel |
| 46 | Nothing in the house depends on the cloud layer, and I like it that way. | Nothing in the house depends on the cloud layer, and that is intended. | Floskel |

### GPU architecture for model serving on VCF (`content/posts/gpu-architecture-for-model-serving-on-vcf.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 15 | This one is the part of the talk that happens under the hood. | This one covers the part of the talk below the platform: how the GPU reaches the VM. | Idiom |
| 42 | DRS chooses the seat once. After that, nobody moves. | DRS picks the host once. After that, the VM stays there. | Bild |
| 48 | Each slot brings its own KV cache. | Each slot brings its own key-value (KV) cache. | Abkürzung |
| 54 | Per GPU. Mind the units: | Per GPU. Note the units: | Idiom |
| 61 | - If you partition a GPU with MIG, NVLink is off. | - If you partition a GPU with Multi-Instance GPU (MIG), NVLink is off. | Abkürzung |
| 70 | A-1: bare metal with a vSphere badge. GPUs of two hosts exchange data directly over RDMA. | A-1: bare metal behaviour on vSphere. GPUs of two hosts exchange data directly over remote direct memory access (RDMA). | Wortspiel, Abkürzung |
| 71 | A-2: same GPUs, NIC virtualised inside a VPC. | A-2: same GPUs, NIC virtualised inside a Virtual Private Cloud (VPC). | Abkürzung |
| 71 | If you ask me where this is going: here. | In my view this is where the platform is heading. | Idiom |
| 75 | ## Enhanced DirectPath: the exception that proves the rule | ## Enhanced DirectPath: the one exception | Idiom |
| 85 | ## The details that bite when you build it | ## The details that cost time when you build it | Idiom |
| 88 | - **GPU and NIC on the same NUMA node.** | - **GPU and NIC on the same NUMA (Non-Uniform Memory Access) node.** | Abkürzung |
| 90 | - **Do not "disable ACS".** ACS stays enabled in ESX. | - **Do not "disable ACS".** ACS (PCIe Access Control Services) stays enabled in ESX. | Abkürzung |
| 96 | If yes, you are in vGPU territory, with the licence | If yes, you need vGPU, with the licence | Idiom |

### Sonos and Wi-Fi tune-up (`content/posts/sonos-wifi-tune-up-with-claude-code.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 31 | The sub rides on the soundbar's private link and inherited it: | The sub uses the soundbar's private link and inherited it: | Idiom |
| 41 | the mesh had nowhere to go. | the mesh had no free airtime. | Idiom |
| 43 | wire exactly one player, or fight your switch. | wire exactly one player, or work against your switch. | Idiom |
| 47 | Claude Code went reading. The answer was six weeks old. | Claude Code then read the Sonos sources. The answer was six weeks old. | Floskel |
| 51 | the beacons alone eat a large slice of 2.4 GHz airtime | the beacons alone take a large share of 2.4 GHz airtime | Idiom |
| 67 | Two players had parked themselves on 2.4 GHz | Two players had stayed on 2.4 GHz | Bild |

### Route to PAIS 3.0, part 1 (`content/posts/kubernetes-api-on-vsphere-in-one-evening.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 11 | summary: "Part 1 of my route to Private AI Services 3.0 on vCenter alone: one host, one vCenter, no NSX. Within a few hours the platform for a lightweight, vCenter- and distributed-switch-only deployment was in place, | summary: "Part 1 of my route to Private AI Services 3.0 on plain vSphere and vCenter: one host, one vCenter, no NSX. Within a few hours the platform for a vCenter- and distributed-switch-only deployment was in place, | Setting-Satz |
| 15 | I have installed ESX and vCenter by hand more times than I can count. | I have installed ESX and vCenter by hand many times. | Idiom |
| 15 | certificates, a second appliance to babysit. | certificates, a second appliance to look after. | Idiom |
| 15 | and the part I used to dread, the Supervisor activation, was the shortest step of all. | and the part I expected to take longest, the Supervisor activation, was the shortest step of all. | Floskel |
| 17 | This is part 1 of 3 on my route to Private AI Services (PAIS) 3.0, deployed the lightweight way: vCenter and a vSphere Distributed Switch only, no NSX, no VMware Cloud Foundation (VCF) Automation. Within a few hours | This is part 1 of 3 on my route to Private AI Services (PAIS) 3.0 on a plain vSphere and vCenter basis: vCenter and a vSphere Distributed Switch, no NSX, no VMware Cloud Foundation (VCF) Automation. PAIS 3.0 is fully supported on that basis, and that is what the lab rebuilds. I would like to have the multi-tenancy and the NSX-based Virtual Private Cloud (VPC) networking of VCF as well, but the lab is small. Within a few hours | Setting-Satz |
| 52 | Static ranges inside a DHCP pool work until the day they do not. | Static ranges inside a DHCP pool work until the first conflicting lease. | Floskel |
| 109 | On a single host they boil down to this: | On a single host they come down to this: | Idiom |
| 155 | The log tells the story: the first control plane address | The log shows the sequence: the first control plane address | Floskel |

### Route to PAIS 3.0, part 2 (`content/posts/private-ai-services-without-a-gpu.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 11 | summary: "Part 2 of my route to Private AI Services 3.0 on vCenter alone. | summary: "Part 2 of my route to Private AI Services 3.0 on plain vSphere and vCenter. | Setting-Satz |
| 19 | **To be clear about the route:** for an enterprise, the preferred way to run Private AI Services is a full VMware Cloud Foundation (VCF) deployment with VCF Automation. That is where the things live that a company needs and my lab does not: | **About the setting:** PAIS 3.0 is fully supported on a plain vSphere and vCenter basis, and that is what this lab rebuilds. A full VMware Cloud Foundation (VCF) deployment with VCF Automation adds what a company with many teams needs and my lab does not: | Setting-Satz |
| 27 | For one server in my homelab, with one user, the lightweight way (vCenter, a distributed switch and the built-in load balancer) is enough, and it is the quickest way to see how the pieces fit. Read this series as a lab route, not as an enterprise reference architecture. | I would like to have the multi-tenancy and the NSX-based virtual private clouds as well, but the lab is small: one server, one user. For that, vCenter, a distributed switch and the built-in load balancer are enough, and they are the quickest way to see how the pieces fit. | Setting-Satz |
| 50 | **Trap 1: the registry test that lies.** | **Trap 1: a registry test that fails for the wrong reason.** | Bild |
| 50 | This one-liner does the real thing, asks for the token | This one-liner does what the Supervisor does, asks for the token | Floskel |
| 140 | is not something I would bet production on; | is not something I would rely on in production; | Idiom |
| 211 | And then the best line of the morning. | Then the most interesting line of the morning. | Floskel |
| 213 | Its suggested fix was wrong as well, and honestly labelled: | Its suggested fix was wrong as well, and labelled as such: | Floskel |
| 215 | With a public model that is real money per question; | With a public model that is a noticeable cost per question; | Idiom |
| 223 | Tokens are the bill. | Tokens are what you pay for. | Floskel |

### Model as a Service, the bare minimum (`content/posts/model-as-a-service-with-private-ai-services.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 87 | so in a lab without VCF Automation, the platform team is also the shop counter. | so in a lab without VCF Automation, the platform team hands out the service names by hand. | Bild |
| 115 | That is the abstraction doing its job: | That is what the abstraction is for: | Floskel |
| 115 | and you have the audit trail for free. | and you have the audit trail without extra work. | Idiom |
| 148 | this is where the lever is: | this is where the benefit is: | Idiom |

### Route to PAIS 3.0, part 3 (`content/posts/rtx-a5000-behind-the-same-service-name.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 15 | and I could not resist a refurbished RTX A5000 for the lab instead: | and I bought a refurbished RTX A5000 for the lab instead: | Idiom |
| 15 | a sibling may follow one day. | a second card may follow one day. | Bild |
| 17 | The setting is unchanged from parts 1 and 2: one EPYC host with ESX 9.1.1, a vSphere Supervisor, Private AI Services (PAIS) 3.0 activated from vCenter alone, no VMware Cloud Foundation (VCF) Automation. Read it as a lab route, not as a reference architecture; part 2 has the list of what the full VCF stack adds. | The setting is unchanged from parts 1 and 2: one EPYC host with ESX 9.1.1, a vSphere Supervisor, and Private AI Services (PAIS) 3.0 activated from vCenter. PAIS 3.0 is fully supported on a plain vSphere and vCenter basis, and that is what the lab rebuilds. I would like to use the multi-tenancy and the NSX-based Virtual Private Cloud (VPC) features of VMware Cloud Foundation (VCF) as well, but this is a small lab; part 2 has the list of what the full VCF stack adds. | Setting-Satz |
| 31 | the Supervisor keeps resurrecting VMs you power off under it | the Supervisor keeps restarting VMs you power off under it | Bild |
| 112 | Two lines in there are traps I walked into. | Two lines in there are traps I ran into. | Idiom |
| 116 | the reasoning eats the whole budget. | the reasoning uses up the whole budget. | Idiom |
| 148 | so treat the factor as a floor, not a benchmark. | so treat the factor as a lower bound, not a benchmark. | Idiom |
| 150 | The provider does not care and delivers 700 and more. That is the honest shape of the comparison: | The provider is not affected and delivers 700 and more. That is the shape of the comparison: | Floskel |
| 156 | One more honest note on the Gemma row: | One more note on the Gemma row: | Floskel |
| 195 | Opus took the same payload without blinking, | Opus took the same payload without a problem, | Idiom |
| 195 | The honest result tonight is that the same client | The result tonight is that the same client | Floskel |
| 209 | the Supervisor and vCenter fight you if you power things off | the Supervisor and vCenter work against you if you power things off | Idiom |

### Sharing one GPU on the Kubernetes layer (`content/posts/sharing-one-gpu-on-the-kubernetes-layer.md`)

| Zeile | Original | Vorschlag (eingearbeitet) | Grund |
|---|---|---|---|
| 17 | and it uses what VKS ships today: Kubernetes 1.36 with DRA, | and it uses what VKS ships today: Kubernetes 1.36 with Dynamic Resource Allocation (DRA), | Abkürzung |
| 19 | The setting is the same single-host lab as in parts 1 to 3: one EPYC host with ESX 9.1.1, a vSphere Supervisor, Private AI Services (PAIS) 3.0, no VMware Cloud Foundation (VCF) Automation. | The setting is the same single-host lab as in parts 1 to 3: one EPYC host with ESX 9.1.1, a vSphere Supervisor, and Private AI Services (PAIS) 3.0 on a plain vSphere and vCenter basis, which is a fully supported setup. I would like to use the multi-tenancy and the NSX-based Virtual Private Cloud (VPC) features of VMware Cloud Foundation (VCF) as well, but this is a small lab. | Setting-Satz |
| 80 | the NVIDIADriver CRD on, | the NVIDIADriver custom resource definition (CRD) on, | Abkürzung |
| 84 | I read it as a good default with a loud silence: | I read it as a good default that is too quiet: | Wortspiel |
| 88 | Both traps are the kind that the person rebuilding this on Monday morning hits at 9:30. | Both traps are the kind that anyone rebuilding this hits in the first hour. | Bild |
| 106 | **Time-slicing is free until the neighbour wakes up:** | **Time-slicing is free while the neighbour is idle:** | Bild |
| 106 | the context switches bite harder, | the context switches cost more, | Idiom |
| 106 | a instance alone gets about three quarters | an instance alone gets about three quarters | Grammatik |
| 112 | The honest version: for a 24 GB card | In short: for a 24 GB card | Floskel |

## 4. Bewusst stehen gelassen, bitte entscheiden

- **Teil 4, letzter Satz:** „That is good news for everyone who wants to try it.“ Steht so im Maßstabstext von heute früh; „good news“ ist in der Regel ausdrücklich genannt. Vorschlag: „Anyone with a card from the support list can try it.“ Auf Raikos Ja um 09:50 geändert (Draft, nicht committet; Teil 4 bleibt bei der anderen Sitzung).
- **Teil 1, Zeile 17:** „This is part 1 of 3“ ist seit Teil 4 inhaltlich überholt (Titel haben das „of 3“ schon verloren). Inhalt, daher nicht angefasst.
- **Teil 2, Schluss, und Bare-Minimum-Draft, Schluss:** „Part 3 brings the RTX 3090 into the server“ bzw. „the 3090 found a new home“. Teil 3 erklärt den Wechsel selbst; Inhalt, nicht angefasst.
- **Hello again:** „That is roughly the time I used to spend per year ignoring WordPress update notifications.“ Scherz als Schlusssatz, aber konkret und nicht US/UK-gefärbt. Stehen gelassen.
- **Homelab-Post:** Schlussabsätze „Benchmark the drives before blaming the network“ usw. sind Erkenntnisse, keine Pointen. Stehen gelassen.
- **DRS, HA, NSX, VIP, HGX, GGUF, CUDA:** vSphere-Funktionen und Technik, keine Produktabkürzungen im Sinn der Regel; nicht ausgeschrieben. OIDC, IdP, MIG, RDMA, VPC, NUMA, ACS, KV, DRA, CRD habe ich dort ausgeschrieben, wo sie ohne Langform standen.
- **Wortwahl „honest“:** fünfmal gestrichen (Teil 3 dreimal, Teil 2, Sharing-Post, Voice-Assistant, Homelab). Als Floskel gewertet, weil es die Aussage nicht ändert.
- **Setting-Satz:** steht jetzt in Teil 1 (Absatz 2), Teil 2 (Block „About the setting“ mit der VCF-Liste), Teil 3 (Absatz 2) und im Sharing-Post (Absatz 3). Im PAIS-3.0-Session-Post, im GPU-Architektur-Post und im Bare-Minimum-Draft gab es keine „Lab-Weg“-Formulierung, dort nichts ergänzt.

## 5. `git diff --stat -- content/`

```
 content/about.md                                   |  2 +-
 .../gpu-architecture-for-model-serving-on-vcf.md   | 24 +++++++++++-----------
 content/posts/hello-again.md                       |  4 ++--
 .../kubernetes-api-on-vsphere-in-one-evening.md    | 12 +++++------
 content/posts/my-homelab-in-five-layers.md         | 10 ++++-----
 .../posts/private-ai-services-3-on-vcf-9-1-1.md    | 14 ++++++-------
 content/posts/private-ai-services-without-a-gpu.md | 18 ++++++++--------
 .../rtx-a5000-behind-the-same-service-name.md      | 20 +++++++++---------
 .../sharing-one-gpu-on-the-kubernetes-layer.md     | 16 ++++++++-------
 .../posts/sonos-wifi-tune-up-with-claude-code.md   | 12 +++++------
 .../posts/voice-assistant-for-a-five-year-old.md   |  6 +++---
 content/posts/voice-box-deep-dive.md               | 16 +++++++--------
 12 files changed, 78 insertions(+), 76 deletions(-)
```

Der Bare-Minimum-Draft `model-as-a-service-with-private-ai-services.md` ist noch nicht in Git (untracked) und fehlt deshalb in der Diff-Übersicht; seine 4 Änderungen stehen in Abschnitt 3.

## 6. Später, nach Raikos Blick

Push aus `raimes.ai/CLAUDE.md` (jeder Push auf `main` deployt), hier nicht ausgeführt. Vorher den Diff der veröffentlichten Artikel prüfen: `git diff -- content/posts/` im Ordner `~/claude-projects/raimes.ai` auf dem Mini.


## Runde 2 (2026-11-01 Nacht)

Zweite Runde über alle 15 Artikel, je Artikel ein lesender Sonnet-Unteragent, Ersetzungen per Skript mit exakten Zeichenketten. Aus 139 Vorschlägen wurden 120 eingearbeitet; nicht übernommen: „tenant“ in den beiden Mandanten-Artikeln (`private-ai-services-3-on-vcf-9-1-1`, `gpu-architecture-for-model-serving-on-vcf`, dort sind echte Mandanten gemeint), Ausschreibungen erlaubter Abkürzungen (GPU, VM, API, CPU, PCIe), ein Ratschlag in 4a („start it a week before you need it“) und eine Ersetzung, die eine Anweisung in eine Feststellung verwandelt hätte. Drei Ersetzungen wurden glatter formuliert als vorgeschlagen. Keine Gedankenstriche mehr in den Artikeln, Hugo baut.

Treffer je Artikel: `private-ai-services-3-on-vcf-9-1-1` 16, `sharing-one-gpu-on-the-kubernetes-layer` 14, `voice-box-deep-dive` 12, `my-homelab-in-five-layers` 11, `model-as-a-service-with-private-ai-services` 10, `rtx-a5000-behind-the-same-service-name` 10, `private-ai-services-without-a-gpu` 9, `gpu-architecture-for-model-serving-on-vcf` 6, `kubernetes-api-on-vsphere-in-one-evening` 6, `from-passthrough-to-vgpu-slices-in-one-evening` 6, `hello-again` 5, `one-card-cut-into-slices` 4, `sonos-wifi-tune-up-with-claude-code` 4, `voice-assistant-for-a-five-year-old` 4, `six-endpoints-on-one-card` 3.

### `gpu-architecture-for-model-serving-on-vcf.md`: 6 Ersetzungen
- (staccato) „That is roughly nine 400-gigabit network ports. Per GPU. Note the units:“ → „That is roughly nine 400-gigabit network ports per GPU. Note the units:“
- (punchline) „Most teams start here, and it is a good place to start.“ → „Most teams start here.“
- (punchline) „Multi-host RDMA is a network project before it is a GPU project.“ → „Multi-host RDMA needs network planning first.“
- (abbreviation) „**Physical NIC (1)**“ → „**Physical network interface card (NIC) (1)**“
- (abbreviation) „RoCE on Ethernet with priority flow control and ECN configured“ → „RDMA over Converged Ethernet (RoCE) with priority flow control and Explicit Congestion Notification (ECN) configured“
- (abbreviation) „a VM needs a virtual IOMMU, and that must be off here“ → „a VM needs a virtual input-output memory management unit (IOMMU), and that must be off here“

### `hello-again.md`: 5 Ersetzungen
- (punchline) „That is not a blog, that is a
reminder that WordPress needs attention I was never going to give it.“ → „That is not a blog. WordPress needs regular attention,
and I was never going to give it.“
- (idiom) „The homelab** that holds it together. DNS, backups, power, the boring
   parts that break at night.“ → „The homelab** that holds it together. DNS, backups and power, the parts
   that break at night.“
- (metaphor) „Mac mini as the
   always-on brain“ → „Mac mini as the
   always-on server“
- (punchline) „Publishing them forces me to tidy them
up, and maybe saves someone else a weekend.“ → „Publishing them forces me to tidy them
up.“
- (punchline) „The whole setup took one evening, including writing this post. That is
roughly the time I used to spend per year ignoring WordPress update
notifications.“ → „The whole setup took one evening, including writing this post.“

### `kubernetes-api-on-vsphere-in-one-evening.md`: 6 Ersetzungen
- (we) „Within a few hours we had every platform prerequisite“ → „Within a few hours I had every platform prerequisite“
- (punchline) „Seven minutes are short when you see the addresses come up one after another, and long when you look at a spinner.“ → „The addresses come up one after another, so the seven minutes are easy to follow.“
- (abbreviation) „DNS records, NTP, a distributed switch“ → „DNS records, Network Time Protocol (NTP), a distributed switch“
- (abbreviation) „a tag-based storage policy, HA and DRS on the cluster.“ → „a tag-based storage policy, high availability (HA) and Distributed Resource Scheduler (DRS) on the cluster.“
- (abbreviation) „runs in FIPS mode and refuses ed25519 keys.“ → „runs in Federal Information Processing Standards (FIPS) mode and refuses ed25519 keys.“
- (abbreviation) „the CLI setup for a Mac“ → „the command-line interface (CLI) setup for a Mac“

### `model-as-a-service-with-private-ai-services.md`: 10 Ersetzungen
- (punchline) „App teams get a base URL, a token and a service name. That is the whole contract.“ → „App teams get a base URL, a token and a service name.“
- (abbreviation) „or learn its SDK“ → „or learn its software development kit (SDK)“
- (abbreviation) „**mTLS to `pais-api`**“ → „**Mutual TLS (mTLS) to `pais-api`**“
- (idiom) „the only hop that leaves the house.“ → „the only hop that leaves the platform.“
- (punchline) „That is what the abstraction is for: the app knows a service, not a supplier.“ → „The app knows a service name and does not know the supplier.“
- (punchline) „So keep routes in Git, like any other resource, and you have the audit trail without extra work.“ → „Routes kept in Git, like any other resource, give you that audit trail without extra work.“
- (metaphor) „A counter that is born with the first request has no earlier value“ → „A counter that is created with the first request has no earlier value“
- (punchline) „For a platform team that is the right unit: it is what applications consume.“ → „For a platform team this is the fitting unit, because applications consume service names.“
- (punchline) „In my vCenter-only lab, I am the catalogue.“ → „In my vCenter-only lab, I hand out the service names myself.“
- (idiom) „(the 3090 found a new home)“ → „(the 3090 is sold)“

### `my-homelab-in-five-layers.md`: 11 Ersetzungen
- (staccato) „Here is the October 2026 version. Five layers, one house.“ → „Here is the October 2026 version, with five layers.“
- (abbreviation) „the Synology NAS,“ → „the Synology network-attached storage (NAS),“
- (idiom) „Large copies still crawled.“ → „Large copies were still slow.“
- (abbreviation) „within three minutes of sustained writes, the usual SLC cache cliff. The network was never the bottleneck. The drives were.“ → „within three minutes of sustained writes, which is typical once the cache of single-level cell (SLC) flash is full. The network was never the bottleneck, the drives were.“
- (abbreviation) „512 GB of ECC memory“ → „512 GB of error-correcting code (ECC) memory“
- (metaphor) „with power-loss protection and no cache cliff.“ → „with power-loss protection and no drop in write speed.“
- (punchline) „Nothing in the house depends on the cloud layer, and that is intended.“ → „I built it so that nothing in the house depends on the cloud layer.“
- (punchline) „That was a deliberate decision, not a limitation.“ → „I chose this on purpose.“
- (punchline) „The four layers above exist so this one works when I am not home.“ → „The four layers above keep this one running when I am not home.“
- (staccato) „Change the SVG, run the command again, done.“ → „To update the card, change the SVG and run the command again.“
- (punchline) „Drawn before, it would have saved the detour through two GPU machines.“ → „If I had drawn it before, I would have skipped the detour through two GPU machines.“

### `one-card-cut-into-slices.md`: 4 Ersetzungen
- (abbreviation) „Same method as part 3 and the DRA detour: Gemma 4 12B QAT in 4-bit on llama.cpp“ → „Same method as part 3 and the Dynamic Resource Allocation (DRA) detour: Gemma 4 12B QAT (quantisation-aware training) in 4-bit on llama.cpp“
- (abbreviation) „its own VKS worker VM“ → „its own vSphere Kubernetes Service (VKS) worker VM“
- (abbreviation) „ECC is on, which costs each slice“ → „ECC (error-correcting code memory) is on, which costs each slice“
- (punchline) „The charts in those pieces will come from Operations, not from a text file.“ → „The charts in those pieces will come from Operations.“

### `from-passthrough-to-vgpu-slices-in-one-evening.md`: 6 Ersetzungen
- (punchline) „The route took one evening once the three checks were done.“ → „“
- (punchline) „Nothing in that chain is mine to run. The three checks of this post sit at fixed places in it:“ → „The three checks of this post sit at fixed places in that chain:“
- (staccato) „No cluster manifest, no node pool, no driver install is mine to write.“ → „I do not write a cluster manifest, a node pool or a driver install.“
- (punchline) „Then the first VM starts on the first try.“ → „The first VM then starts without the error from Check 2.“
- (abbreviation) „so SR-IOV and ARI belong on the BIOS checklist“ → „so SR-IOV and Alternative Routing-ID Interpretation (ARI) belong on the BIOS checklist“
- (idiom) „which VM holds which profile, out of the box, through the vCenter adapter.“ → „which VM holds which profile, through the vCenter adapter.“

### `private-ai-services-3-on-vcf-9-1-1.md`: 16 Ersetzungen
- (idiom) „- **Model sharing** is the headline.“ → „- **Model sharing** is the main change.“
- (punchline) „Whatever you pass through pins the VM to the host. Choose that on purpose.“ → „Whatever you pass through pins the VM to the host.“
- (metaphor) „## 1. Model sharing: four homes for one model“ → „## 1. Model sharing: four places for one model“
- (metaphor) „1. **Next door.** A do-it-yourself VKS cluster“ → „1. **Same namespace.** A do-it-yourself VKS cluster“
- (abbreviation) „such as KV-cache-aware routing.“ → „such as routing that is aware of the key-value (KV) cache.“
- (metaphor) „2. **Far away.** A public model“ → „2. **Public.** A public model“
- (metaphor) „3. **The next team.** A model endpoint“ → „3. **Another team.** A model endpoint“
- (metaphor) „4. **At home.** The local PAIS-managed cluster, as before.“ → „4. **Local.** The local PAIS-managed cluster, as before.“
- (staccato) „one place for rate limits and logging. Where the request goes is configuration.“ → „one place for rate limits and logging. Where the request goes is a matter of configuration.“
- (punchline) „A handful of requests per week. One service had exactly one job in fourteen days. The card was powered on around the clock. That is what a dedicated GPU per team looks like.“ → „It served a handful of requests per week, one service had exactly one job in fourteen days, and the card was powered on around the clock.“
- (staccato) „Users and data stay separated. The GPUs are shared.“ → „Users and data stay separated, and the GPUs are shared.“
- (abbreviation) „No vMotion, no DRS, no HA.“ → „No vMotion, no Distributed Resource Scheduler (DRS), no high availability (HA).“
- (metaphor) „DRS picks the host once, then nobody moves.“ → „DRS picks the host once, and the VM stays there.“
- (staccato) „A 27B model on my 24 GB card lost 12 percent of its memory to another process, less than one gigabyte. Speed dropped from 99 to 56 tokens per second. No error, no warning.“ → „A 27B model on my 24 GB card lost 12 percent of its memory to another process, less than one gigabyte. Speed dropped from 99 to 56 tokens per second, with no error and no warning.“
- (idiom) „Start from what your developers ask for on Monday morning.“ → „Start from what your developers ask for.“
- (punchline) „Passthrough or vGPU. Pick it knowing what it pins.“ → „Passthrough or vGPU, depending on which vSphere features you need to keep.“

### `private-ai-services-without-a-gpu.md`: 9 Ersetzungen
- (staccato) „That is not a workaround. It is the point I made on stage at VMware Explore on Tour last week:“ → „That is not a workaround, it is the point I made on stage at VMware Explore on Tour last week:“
- (punchline) „Day zero without a single GPU is a supported start. When the GPU arrives, you repoint.“ → „Starting on day zero without a single GPU is supported. When the GPU arrives, the route points to a local model instead.“
- (punchline) „The question I had after part 1, whether the built-in L4 load balancer is enough for PAIS, has its answer: for the gateway, yes.“ → „After part 1 I wanted to know whether the built-in L4 load balancer is enough for PAIS. For the gateway, it is.“
- (punchline) „vSphere Pods. The host barely notices.*“ → „vSphere Pods. The load on the host is small.*“
- (metaphor) „A single chat answer proves the plumbing. I wanted to see“ → „A single chat answer shows that the connection works. I wanted to see“
- (punchline) „That is the behaviour I want from an assistant on a platform: look first, separate what it saw from what it guesses, and leave the change to me.“ → „It looked first, separated what it saw from what it guessed, and left the change to me.“
- (staccato) „The concierge does not change for that. Only `--model` does.“ → „The concierge stays the same, only the `--model` argument changes.“
- (punchline) „it should also cut events and status down to what matters. Tokens are what you pay for.“ → „it should also cut events and status down to what matters, because input tokens are billed.“
- (we) „and we compare answers, tokens and time.“ → „and I compare answers, tokens and time.“

### `rtx-a5000-behind-the-same-service-name.md`: 10 Ersetzungen
- (punchline) „Start on CPU, add the card later, patch three fields. I would put that sentence on the slide.“ → „Starting on CPU and adding the card later takes one patch of three fields.“
- (staccato) „so the gateway can do better. Open item.“ → „so the gateway can do better.“
- (metaphor) „That is the shape of the comparison: a local card wins on data locality and on cost per token once it is busy, the provider wins on burst and on scale.“ → „A local card wins on data locality and on cost per token once it is busy; the provider wins on burst and on scale.“
- (metaphor) „**The platform costs a second you can see.**“ → „**The platform adds about a second to the first token.**“
- (staccato) „No client changed. The concierge from part 2, the curl examples from the bare-minimum notes, the service name: all the same.“ → „No client changed: the concierge from part 2, the curl examples from the bare-minimum notes and the service name stayed the same.“
- (punchline) „answers through it anyway. The status is a hint, not a gate.“ → „answers through it anyway.“
- (punchline) „That is what vGPU is for, and that is part 4.“ → „vGPU addresses this, and part 4 covers it.“
- (punchline) „The single-request numbers hide the whole story.“ → „The single-request numbers look alike across the backends and say little about load.“
- (abbreviation) „8 vCPUs, 64 GB of memory“ → „8 virtual CPUs (vCPUs), 64 GB of memory“
- (abbreviation) „with mutual TLS. Repointing“ → „with mutual Transport Layer Security (TLS). Repointing“

### `sharing-one-gpu-on-the-kubernetes-layer.md`: 14 Ersetzungen
- (abbreviation) „while the vGPU entitlement sits in an NVIDIA support queue“ → „while the virtual GPU (vGPU) entitlement sits in an NVIDIA support queue“
- (tenant) „measured against the single-tenant baseline“ → „measured against the single-instance baseline“
- (tenant) „Time-slicing is free while the neighbour is idle and splits fairly under load; MPS caps a lone tenant at three quarters and pays it back when both are busy.“ → „Time-slicing costs nothing while the neighbour is idle and splits fairly under load; MPS caps a lone instance at three quarters and gives it back when both are busy.“
- (abbreviation) „which is what a CEL selector can match on“ → „which is what a Common Expression Language (CEL) selector can match on“
- (punchline) „and nobody upgrades anybody. Kubernetes as a service, at the version you ask for.“ → „and nobody has to upgrade because of someone else.“
- (abbreviation) „the lab registry's root CA under“ → „the lab registry's root certificate authority (CA) under“
- (punchline) „with a 7.0 kernel. Nothing on that list needed a flag.“ → „with a 7.0 kernel.“
- (tenant) „lone tenant capped at 55 / 139“ → „lone instance capped at 55 / 139“
- (idiom) „**Time-slicing is free while the neighbour is idle:**“ → „**Time-slicing costs nothing while the neighbour is idle:**“
- (tenant) „**MPS trades the lone tenant for the busy pair:** an instance alone gets“ → „**MPS caps a lone instance and gives it back when both are busy:** an instance alone gets“
- (tenant) „and each tenant keeps 36 instead of 30“ → „and each instance keeps 36 instead of 30“
- (tenant) „Both time-slicing tenants see all 24 GB“ → „Both time-slicing instances see all 24 GB“
- (metaphor) „is a real cap, and vGPU would make it a wall.“ → „is a real cap, and with vGPU the memory limit is fixed by the profile.“
- (tenant) „already gives two tenants 95 percent of the card, and the price is isolation, not throughput.“ → „already gives two instances 95 percent of the card in total. What is given up is isolation, not throughput.“

### `six-endpoints-on-one-card.md`: 3 Ersetzungen
- (punchline) „Each is one fix, once you know where to look.“ → „Each has one fix.“
- (staccato) „An unlicensed vGPU does not stop. It keeps serving at a fraction of its speed.“ → „An unlicensed vGPU does not stop, it keeps serving at a fraction of its speed.“
- (staccato) „An unlicensed slice does not fail. It runs very slowly, and the first symptom is a timeout at the gateway.“ → „An unlicensed slice does not fail, it runs very slowly, and the first symptom is a timeout at the gateway.“

### `sonos-wifi-tune-up-with-claude-code.md`: 4 Ersetzungen
- (punchline) „". A feeling is not a measurement.“ → „". I had no measurement yet.“
- (staccato) „I plugged it in. The soundbar dropped to 1 ms. Good.“ → „I plugged it in and the soundbar dropped to 1 ms.“
- (we) „We drew a plan from the floor plan:“ → „Claude Code and I drew a plan from the floor plan:“
- (metaphor) „The speakers were fine. The air was the problem: a soundbar stuck on 2.4 GHz, a mesh I never asked for, and access points jamming each other.“ → „The speakers were fine, the Wi-Fi was not: a soundbar stuck on 2.4 GHz, a mesh I never asked for, and access points that interfered with each other.“

### `voice-assistant-for-a-five-year-old.md`: 4 Ersetzungen
- (punchline) „They do nothing in this setup. That turned out to be the most useful finding.“ → „They do nothing in this setup.“
- (staccato) „Good in theory. In practice the model got 114 exposed entities“ → „That sounds sensible, but the model got 114 exposed entities“
- (idiom) „hangs off the 3.5 mm jack“ → „is connected to the 3.5 mm jack“
- (abbreviation) „**Home Assistant Voice Preview Edition** as the microphone“ → „**Home Assistant Voice Preview Edition (Voice PE)** as the microphone“

### `voice-box-deep-dive.md`: 12 Ersetzungen
- (punchline) „and a filler word in the firmware that changed nothing in the numbers and everything in the conversation.“ → „and a filler word in the firmware that changed no number but made the conversation feel natural.“
- (idiom) „Streaming saves nothing; answer length and the model's total time are the only levers.“ → „Streaming saves nothing; only the answer length and the model's total time change the delay.“
- (idiom) „The levers that actually move the number are answer length and the model's total time.“ → „Only the answer length and the model's total time change the delay.“
- (abbreviation) „Measured from inside the LAN“ → „Measured from inside the local network (LAN)“
- (abbreviation) „(5 GB of VRAM)“ → „(5 GB of video memory)“
- (punchline) „Measured latency: unchanged. Perceived latency: the pause became a conversation. My five-year-old's verdict was one word, and it was positive.“ → „Measured latency is unchanged. The pause now feels like part of a conversation. My five-year-old reacted with one word, and it was positive.“
- (idiom) „"Okay" squeezed through.“ → „"Okay" was played in full.“
- (abbreviation) „the TTS put a third of a second“ → „the text-to-speech engine put a third of a second“
- (staccato) „One removed keyword argument in the library later, Whisper ran.“ → „After I removed one keyword argument in the library, Whisper ran.“
- (punchline) „"Level and local" is a decision, not a measurement.“ → „I chose "level and local" as a decision, because the measurement could not separate the voices.“
- (staccato) „Voice, on-prem chain, filler word. Not speech recognition for the sake of it.“ → „The jobs are the voice, the on-prem chain and the filler word, not speech recognition for its own sake.“
- (punchline) „My five-year-old does not time the first token. He waits for a sign of life. A one-second "Okay" from flash memory was worth more than every model swap on this list.“ → „My five-year-old does not time the first token, he waits for a sign of life. A one-second "Okay" from flash memory helped more than every model swap on this list.“
