---
title: "Route to Private AI Services 3.0, part 4b: one card cut into slices, what each endpoint gets, measured"
date: 2026-11-01T11:30:00+01:00
draft: true
written_with_claude: true
cover:
  image: "/images/covers/one-card-cut-into-slices.jpg"
  alt: "Route to Private AI Services 3.0, part 4b: one card cut into slices, what each endpoint gets, measured"
categories: ["vmware"]
tags: ["private-ai", "homelab", "gpu", "vgpu", "benchmark"]
summary: "Second of three pieces of part 4. The RTX A5000 is cut into NVIDIA vGPU slices, and Private AI Services 3.0 runs one, two and then three model endpoints on it. One 12 GB slice alone is the whole card. Two busy 12 GB slices share it exactly in half. A 4 GB embedding endpoint next to a 12 GB chat endpoint costs the chat endpoint three percent. A 12B model in 4-bit does not fit an 8 GB slice. Plus the same load as curves in VCF Operations, per card and per slice, with no management pack."
---

This is the second of three pieces of part 4, published together. [Part 4a](/posts/from-passthrough-to-vgpu-slices-in-one-evening/) is the route from passthrough to NVIDIA vGPU slices on one host and the three checks to do first. This piece has the numbers for one to three endpoints, first from `nvidia-smi` on the host, then as curves from VCF Operations. [Part 4c](/posts/six-endpoints-on-one-card/) goes on to six.

The setting in one sentence: one EPYC host with ESX 9.1.1, a vSphere Supervisor, Private AI Services (PAIS) 3.0, and a refurbished RTX A5000 with 24 GB, now in vGPU mode with the host scheduler on its default, best effort. PAIS 3.0 is fully supported on a plain vSphere and vCenter basis, and that is what I rebuild here. I would like to use the multi-tenancy and the NSX-based Virtual Private Cloud (VPC) features of VMware Cloud Foundation (VCF) as well, but this is a small lab.

A disclosure, as always: I work at Broadcom as a solutions architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement.

{{< rebuild repo="rmesterheide/pais-vgpu" >}}the benchmark tools (chat load, embedding load, the mixed run with host watch), the endpoint manifests for the three slices, and the raw result tables of this post.{{< /rebuild >}}

{{< tldr >}}
- **One 12 GB slice alone is the whole card.** 68.9 tokens per second for one request against 70.9 with passthrough in part 3. The vGPU Manager costs nothing measurable while the neighbour is idle.
- **Two busy 12 GB slices share the card exactly in half,** to the decimal across two runs. At eight parallel requests per endpoint the sum drops to less than half of what one slice delivers alone; that is the time-slice scheduler, and the equal-share and fixed-share schedulers are the next measurement.
- **Different endpoints mix well.** A 4 GB embedding slice next to a 12 GB chat slice delivered 506 texts per second and cost the chat endpoint three percent.
- **The sizing rule:** Gemma 4 12B in 4-bit needs the 12 GB slice. 8 GB is for models up to about 5 GB of weights, 4 GB is an embedding slice. Three slices on a 24 GB card is a realistic lab mix.
- **Operations shows it per card and per slice.** VCF Operations next to the vCenter drew the same load as curves: compute, power and temperature per card, utilisation per slice, with no management pack. Two of its numbers differ from `nvidia-smi`, and both are right.
{{< /tldr >}}

## The method

Same method as part 3 and the Dynamic Resource Allocation (DRA) detour: Gemma 4 12B QAT (quantisation-aware training) in 4-bit on llama.cpp, 400 tokens per answer, requests through the PAIS gateway from a machine on the network, so the numbers include the gateway. All endpoints run in the one PAIS namespace of this lab, so they are one tenant with several workloads in VCF terms; this piece is about sharing the card, not about isolation. Each endpoint is its own vSphere Kubernetes Service (VKS) worker VM with its own vGPU slice, its own guest driver and its own licence lease. For the embedding endpoint the model is BGE-M3 on the Infinity engine, 16 texts per request, four workers.

Three runs, in this order:

1. One chat endpoint on a 12 GB slice, the second slice idle.
2. Two chat endpoints on two 12 GB slices, both under load.
3. One chat endpoint on a 12 GB slice next to an embedding endpoint on a 4 GB slice, and an attempt at a second chat endpoint on an 8 GB slice.

## The numbers

![Tokens per second from one RTX A5000 as vGPU slices](/images/one-card-cut-into-slices/tokens-per-second.svg)

| Load | one 12 GB slice alone | two 12 GB slices, both busy | passthrough, whole card (part 3) |
|---|---|---|---|
| 1 request, streaming | 68.9 tok/s, first token 0.2 s | 29.0 + 30.4 tok/s, first token 2 to 3 s | 70.9 tok/s |
| 4 parallel per endpoint | 228 tok/s | 109 + 104 = 213 tok/s | 243 tok/s |
| 8 parallel per endpoint | 388 tok/s | 89 + 89 = 177 tok/s | 351 tok/s |

Three readings:

- **One slice alone is the whole card.** The vGPU Manager costs nothing measurable when the neighbour is idle; the best-effort scheduler gives the idle VM's time to the busy one. The 12 GB ceiling did not matter for this model: it used 8.7 GB.
- **Two busy endpoints split the card exactly in half,** to the decimal across two runs. At light and moderate load the sum stays within 7 to 14 percent of a single endpoint. At eight parallel requests per endpoint the sum drops to less than half of what one slice delivers alone. The card switches between the two VMs on every time slice and neither llama.cpp batch keeps the streaming multiprocessors busy; time to first token rises from 0.2 to 2 seconds. The DRA detour measured 96 + 96 tok/s for two containers in one VM under similar load, so this is the cost of VM-level isolation, not of vGPU specifically. NVIDIA's equal-share and fixed-share schedulers are made for this case; they are the first measurement of the next evening.
- **Different endpoints mix well.** For the third run I deleted the second 12 GB slice and created a 4 GB slice with the BGE-M3 embedding model. The embedding endpoint delivered 491 texts per second alone (median latency 0.11 s) and 506 next to a chat endpoint under load, while the chat endpoint lost three percent (228 to 220 tok/s at four parallel requests). Short embedding bursts fit between the time slices of the chat endpoint.

## The run that did not work, and the sizing rule

**Gemma 4 12B in 4-bit does not fit an 8 GB slice.** The GGUF is 7.2 GB, the slice filled to 7.6 GB, the engine pod crash-looped nine times in half an hour and the gateway reported the route unavailable, even with the vision projector left out and the context cut to 4k. The 12B class needs the 12 GB slice; 8 GB is for models up to about 5 GB of weights, 4 GB is an embedding slice. Three slices on a 24 GB card is a realistic lab mix: one chat model, one small chat or reranking model, one embedding model.

Two notes for the sizing table. ECC (error-correcting code memory) is on, which costs each slice a little framebuffer on the host side: the 12 GB and the 4 GB slice together hold 15.6 GB, not 16. And a VM class with a vGPU profile needs its memory fully reserved, so the three classes (8 vCPU and 32 GB, 6 and 24, 4 and 16) take 72 GB of host memory when all three run.

The host under full load: 229 W of the 230 W cap, 74 °C, 96 percent utilisation in `nvidia-smi`. Idle between runs: 89 W.

## The same evening from the host side

Every number above came from `nvidia-smi` samples in a text file on the host. A platform team does not read `nvidia-smi`, it reads a dashboard with history, so the next morning VMware Cloud Foundation (VCF) Operations 9.1.1 went next to the standalone vCenter of the lab. The deployment is routine (one OVA, the vCenter as an account) and not the topic here. The topic is what it shows: the vCenter adapter delivers a GPU metric group per host and a vGPU group per VM, and the appliance ships four Private AI dashboards, all without a management pack and without anything installed in the guests. I ran the mixed load again for 45 minutes, eight parallel chat completions against the 12 GB slice and four embedding workers against the 4 GB slice, and these are the results from the platform layer.

{{< figure src="/images/one-card-cut-into-slices/host-gpu-metrics.jpg" alt="VCF Operations, host esx01, Metrics tab: four charts for GPU 0000:c1:00.0, compute utilisation rising from 0 to 89 percent, power from 90 to 222 watts, temperature from 60 to 78 degrees, memory used flat" caption="The host view: compute, power, temperature and memory of the one card during the 45-minute run. The memory line is flat because the host counts the whole slice." >}}

{{< figure src="/images/one-card-cut-into-slices/vm-vgpu-metrics.jpg" alt="VCF Operations, the worker VM of the 12 GB slice, Metrics tab: vGPU 3D/compute utilisation 0 to 84.6 percent and vGPU memory utilisation 0 to 80.6 percent" caption="The per-VM view: the VM that holds the 12 GB slice, its own compute share and its own memory use." >}}

Two numbers differ from the `nvidia-smi` samples, and both are expected. First, utilisation: `nvidia-smi` said 93 to 96 percent for the whole run, Operations says 89 percent at the plateau. The load loop runs eight requests, waits for the slowest, then starts the next batch, so the card idles for a second or two between batches. `nvidia-smi` samples every two seconds and I read the busy ones; Operations averages five minutes and counts the gaps. For a benchmark the two-second view is the right one, for a capacity decision the five-minute view, because it is what the card delivered, gaps included. Second, memory: the host reports the memory a slice holds, 15.6 GB from the first sample to the last, because a vGPU slice holds its frame buffer from the moment the VM powers on ([Broadcom KB 439680](https://knowledge.broadcom.com/external/article/439680/gpu-utilization-metrics-are-reported-inc.html) says so). The VM reports the memory it uses, 0 to 80.6 percent. The host number is for capacity planning (how many slices fit), the VM number for right-sizing an endpoint (does it use its slice). Operations has both on different objects, and the GPU Consumers dashboard shows them one click apart.

What Operations does not show: the licence state per slice (that is in the guest's `nvidia-gridd` log or in NVIDIA's management pack), the scheduler alternation between VMs (`nvidia-smi vgpu -u` on the host), and the model metrics such as tokens per second, which live in the endpoint and in the managed Prometheus of PAIS.

## What comes next

The card now runs a chat endpoint on a 12 GB slice and an embedding endpoint on a 4 GB slice, licensed, with 8 GB free. [Part 4c](/posts/six-endpoints-on-one-card/) fills the card with six 4 GB slices the next evening and runs into two limits on the way. Still open after that: the equal-share and fixed-share schedulers against the 8 + 8 result, the licence behaviour when the Cloud License Service is unreachable, and ECC off for the full 12 GB per slice. Then the decision piece that ends the series: passthrough, DRA or vGPU for one card, two cards and a GPU cluster, with the licence cost per GPU next to the utilisation each option can reach. The charts in those pieces will come from Operations.
