---
title: "Private AI Services 3.0 on VMware Cloud Foundation 9.1.1: the five changes that matter"
date: 2026-10-15T09:00:00+02:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/private-ai-services-3-on-vcf-9-1-1.jpg"
  alt: "Private AI Services 3.0 on VMware Cloud Foundation 9.1.1"
categories: ["vmware"]
tags: ["private-ai", "homelab"]
summary: "Notes from preparing a VMware Explore on Tour session. Model sharing, public models behind a private gateway, tenants without GPUs, three ways to log in, and the one rule that still decides your GPU design."
---

Yesterday I co-presented "Design & Architect: VMware Cloud Foundation Private AI Services" at VMware Explore on Tour in Frankfurt. Four weeks of preparation went into thirty minutes on stage. This post is the condensed version: what Private AI Services (PAIS) 3.0 changes on VMware Cloud Foundation (VCF) 9.1.1, and what I would decide first.

A disclosure: I work at Broadcom. This is my own reading of public documentation and the session. Nothing here is an official statement, and the home-lab numbers are mine.

{{< tldr >}}
- VCF 9.1.1 and PAIS 3.0 have been generally available since 3 September 2026. Everything below is released, not a preview.
- **Model sharing** is the headline. The gateway and the model no longer have to live in the same namespace. One PAIS instance can expose a local model, a self-managed endpoint, a model borrowed from another instance and a public cloud model side by side.
- **Public models are first-class endpoints.** Google Gemini, Gemini Enterprise Agent Platform and any OpenAI-compatible API, with token usage tracking per consumer.
- **Tenants without GPUs.** Each team keeps its own PAIS instance as the security and data boundary. The GPUs sit in one provider instance and are shared.
- **Three ways to log in:** direct OIDC, OIDC via VCF Automation, local accounts. Two are for production, one is for the first afternoon.
- **Less friction:** the agent layer is optional, and activation works from the vCenter UI without VCF Automation.
- **Under the hood nothing changed.** Whatever you pass through pins the VM to the host. Choose that on purpose.
{{< /tldr >}}

## PAIS in one paragraph

PAIS is a supervisor service in VCF. You enable it per vSphere namespace, one instance per namespace. An instance consists of an inference gateway, a PAIS-managed vSphere Kubernetes Service (VKS) cluster that runs the models, and an optional agent layer with Agent Builder and Data Indexing. A model endpoint is defined by two things: the model URI, pulled from Harbor or another OCI registry, and a VM class that encapsulates the GPU configuration. Developers get an OpenAI-compatible API. They never see the Kubernetes underneath.

## 1. Model sharing: four homes for one model

Until 3.0, a model had to run inside the PAIS instance that served it. With model sharing, the gateway in the middle keeps one list of models, but the models can live in four places:

1. **Next door.** A do-it-yourself VKS cluster in the same namespace. Useful when you need something PAIS does not do natively yet, such as KV-cache-aware routing. The gateway only routes there.
2. **Far away.** A public model behind an OpenAI-compatible API, or Gemini.
3. **The next team.** A model endpoint of another PAIS instance.
4. **At home.** The local PAIS-managed cluster, as before.

The application sees one endpoint, one login, one place for rate limits and logging. Where the request goes is configuration.

## 2. Private does not mean no public models

This is the point most people get wrong about private AI. Private AI does not mean "no public models". It means you decide which model sees which data, behind a gateway you own.

I run the same split at home. Some jobs go to a local model on my own GPU. Other jobs go to a public model, because it is simply better at them. One morning I moved a service from the local model to a public endpoint. I did not touch the application. I changed where the request goes, and the local path stayed as a fallback.

PAIS 3.0 makes this a platform feature. Two consequences I find useful:

- **Day zero without a GPU.** Start with a public endpoint. When your GPUs arrive, repoint the model. The application does not change.
- **Token usage tracking for cloud models.** You see what the public model costs you, per consumer, in the same place as your local models.

## 3. Teams keep their walls, the GPUs lose theirs

A PAIS instance is the security and data boundary. Whoever can log in sees all models and all data sources of that instance. Separating teams therefore means separate instances. Until now, separate instances meant separate GPUs.

I checked the logs of my own GPU box before the talk. A handful of requests per week. One service had exactly one job in fourteen days. The card was powered on around the clock. That is what a dedicated GPU per team looks like, at any scale.

With 3.0, two organisations run PAIS without GPUs: only the lightweight gateway pods, their own vector database, their own tools and agents. Both point at one provider instance that runs the models. Users and data stay separated. The GPUs are shared. And no, this needs no special hardware. All of it lives on the same vSphere cluster, in different namespaces.

## 4. Three ways to log in

| Option | Fit | Cost |
|---|---|---|
| Direct OIDC | One company, production | Every new instance is a new IdP integration. Scripts fetch and refresh their own tokens. Shared instances need all users in one directory. |
| VCF Automation OIDC | Many tenants, production | VCF Automation is the issuer and federates to each tenant's IdP. Long-lived API tokens for scripts. You declare which organisations may use an instance. |
| Local accounts | Proof of concept | Embedded issuer, personal access tokens, no IdP, no VCF Automation. Not for production. |

The second option is the one that fits the shared-GPU pattern above. VCF Automation is still not required for PAIS. Once you have more than one tenant, it is the path.

Two known issues from the 3.0 release notes if you demo this: API tokens are not enabled when PAIS is activated through the UI, and the default base URL for local accounts cannot be set in the UI.

## 5. Under the hood: the one rule

The model endpoint carries a VM class, and the VM class decides how the GPU reaches the VM. Three options on a single host:

- **Own the host.** Full passthrough of all GPUs and NVSwitches. Kubernetes sees bare metal. No vMotion, no DRS, no HA.
- **Own the card.** DirectPath with DRS placement. DRS picks the host once, then nobody moves. No sharing of one GPU, no HGX systems.
- **Own a slice.** vGPU profiles from the host driver. You keep vMotion and clean host maintenance, as long as you do not need unified memory. The price is coupling: host and guest driver stay on the same branch, for every tenant, plus the NVIDIA AI Enterprise licence.

The rule that runs through all of them: whatever you pass through pins the VM to the host. More virtualisation buys more vSphere features and more driver and licence coupling.

One lesson from home on sizing a vGPU profile. A 27B model on my 24 GB card lost 12 percent of its memory to another process, less than one gigabyte. Speed dropped from 99 to 56 tokens per second. No error, no warning. Then I doubled the context window from 64k to 128k. The KV cache grew from four to eight gigabytes and no longer fit. Speed dropped from 98 to 27. Consumer hardware and Ollama, so the numbers do not carry over. The rule does: size the profile for the model plus its context, not for the model file.

## What I would decide first

In this order, before anyone buys a GPU:

1. **What do you offer?** Model endpoints or agents on top. Start from what your developers ask for on Monday morning. If the answer is "give me an endpoint", ship endpoints first.
2. **Where does each model run?** Local, self-managed, borrowed, public. Decide per model which one may see which data.
3. **How many tenants?** One instance per security boundary. Share the GPUs behind a provider instance.
4. **How does the GPU reach the VM?** Passthrough or vGPU. Pick it knowing what it pins.

## Watch the original

The Frankfurt talk was a shortened version of the Las Vegas session. The full recording is [CLOB1084LV: Design & Architect: VMware Cloud Foundation Private AI Services](https://www.vmware.com/explore/video/6403820843112), presented by Luca Camarda and Agustin Malanco. If you want the whole GPU architecture block with every option slide, watch that one.

William Lam keeps a curated, searchable list of all VMware Explore 2026 on-demand sessions with video links in his GitHub repository [vmware-explore-2026-session-urls](https://github.com/lamw/vmware-explore-2026-session-urls). It is the fastest way to find the other private AI sessions from the event.

## Sources

- [Announcing general availability of VMware Cloud Foundation 9.1.1](https://blogs.vmware.com/cloud-foundation/2026/09/03/announcing-general-availability-of-vmware-cloud-foundation-9-1-1/), Broadcom, 3 September 2026
- Private AI Services 3.0 release notes and the VCF 9.1 Design Library on Broadcom TechDocs
- [Deploying your own AI models with VCF Private AI Services 3.0](https://williamlam.com/2026/09/vcf-9-1-1-deploying-your-own-ai-models-with-vcf-private-ai-services-pais-3-0.html), William Lam
