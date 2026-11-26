---
title: "The Enterprise Private AI Building Block"
date: 2026-11-26T09:16:57+01:00
lastmod: 2026-11-26T23:46:38+01:00
draft: false
url: /building-block/
written_with_claude: true
cover:
  image: "/images/covers/building-block-technical.jpg"
  alt: "The Enterprise Private AI Building Block"
  hiddenInSingle: true
ShowToc: true
ShowReadingTime: false
ShowBreadCrumbs: false
summary: "This page describes hardware options for Private AI on VMware Cloud Foundation in building blocks. For two example sizes it shows what can run on the hardware, from a single model to agents, and which accelerators and servers are behind it. It covers technical aspects only. Documented values, assumptions and model values are marked separately. I check it about once a month."
---

<style>.post-content table{font-size:.9em}.post-content table th,.post-content table td{padding:6px 9px}</style>

**Last updated:** 26 November 2026. **Data from:** 25 and 26 November 2026. **Next check:** end of December 2026.

In most Private AI projects today, hardware is the first question. There are many ways to build such a platform, and discussions at work keep showing me new options.

On this page I think in building blocks. I describe the technical options I see and what each of them means for the architecture. For the hardware on this page I ask the same question: what can run on it, and how much, from a single model to agents. The market changes fast: new accelerators and servers appear in the Broadcom Compatibility Guide, and new open-weight models are published. So I check the page about once a month, and the change log at the end says what changed.

I work as a Solutions Architect at Broadcom. This page is my personal view and not an official statement from Broadcom. It is not a sizing for your workload and not a recommendation to buy.

In my lab I test on a single server with one small RTX A5000. That shows how the software works. It does not show what a large installation looks like. This page adds the larger view: the same stack in two sizes, based on VMware Cloud Foundation (VCF) 9. The starter block has three servers with two GPU cards each. The building block has eight servers with four GPU cards each. The sizes are examples to calculate with. With servers that can take eight cards, the first size can grow into the second, and beyond it.

This page covers technical aspects only: which open-weight models fit, what my model says the two sizes can handle, and which kinds of accelerators and servers there are. It has no prices and no cost calculation. The calculated values come from public data sheets and from my own assumptions.

## The official source

Support for hardware on VMware Cloud Foundation is documented in the [Broadcom Compatibility Guide](https://compatibilityguide.broadcom.com/) and in the Broadcom documentation, not on this page. I do not copy the guide here, because a copy gets old. Where this page mentions the guide, it links to it, and the guide has the current state.

## How to read this page

Every number on this page has one of three labels.

- **Documented:** I read it in a public source, and the source and the date are named. Examples are a value from a data sheet or a statement in the Broadcom documentation. The source stays the authority, and it can change after the date I name.
- **Assumption:** I set the number myself. Examples are the power draw of a server without cards or the number of calls per user.
- **Model value:** I calculated it from documented numbers and assumptions. Nothing on this page is measured on this hardware. The measurements from my lab are in the posts, and they come from one RTX A5000 with 24 GB.

The documented parts can be checked in the public sources named next to them. The model values show the order of magnitude and how it moves from month to month. The supported configuration of a server comes from the server vendor, and numbers for a specific workload come from a measurement with that workload.

## Two sizes: the starter block and the building block

| | Starter block | Building block |
|---|---|---|
| Servers | 3, in one cluster | 8, in one cluster |
| GPU cards per server | 2, as PCIe cards | 4, as PCIe cards, in a server that can take 8 |
| Cards in total | 6 | 32 |
| Reserve | one server (2 of 3 share the load) | one server (7 of 8 share the load) |
| Power | about 2.7 kW per server, about 9 kW in total | about 3.9 kW per server, about 32 kW in total |

Both sizes use the same parts:

| | |
|---|---|
| Card, variant 1 | NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GB |
| Card, variant 2 | NVIDIA H200 NVL, 141 GB |
| Platform | VCF 9.1 |
| GPU sharing | flexible time-sliced virtual GPU (vGPU) or hardware-isolated Multi-Instance GPU (MIG) |
| Host network | 2 ports of 100 Gigabit Ethernet per server, two switches. It carries management, vMotion, storage and the requests to the models. |
| Optional second network | a network with 200 or 400 Gbit/s per port for models that run across several servers, see below. |

The power values are model values from the section on power and memory below. The next three sections show what each size can run. The sections after them describe the hardware.

Below I call the two card variants RTX and H200. "RTX PRO 6000" always means the Blackwell Server Edition on this page.

Both sizes use servers that take standard PCIe cards.

The starter block is an example of a small, complete setup: three servers, so that one of them can be the reserve, and two cards in each. I see two options to build it:

- **Option 1: small servers.** These are servers with room for two to four of these cards, often of the usual 2U size (two rack units high). The compatibility guide has the current entries. They need less space and power. They do not grow to eight cards, and a model that needs four cards for one copy may not fit into one server.
- **Option 2: servers that can take eight cards, with two cards each.** The server is larger at the start. The same servers then grow to the building block and to eight cards each, so no hardware is replaced on the way.

The building block in my example has four cards per server. Eight cards per server is the other option. This is what each option means:

- **Power.** A server with four of these cards draws about 3.9 kW in my model, a server with eight about 6.3 kW. That is the power the rack supplies and cools.
- **Failure of a server.** For the same 32 cards, eight servers with four cards each lose one eighth of the cards when one server fails. Four servers with eight cards each lose one quarter. With one server as reserve, the reserve is one eighth of the cards in the first case and one quarter in the second.
- **Large models.** Most models in the next section need one or two cards for one copy. A model that needs eight cards fits into one server only with eight cards per server.
- **Growth.** With four cards per server, four slots stay free for more cards. With eight cards per server, all slots are in use.

Systems with a fixed board of eight GPUs (NVIDIA HGX) are a different class and are not part of this page.

How one card is shared between several workloads is a topic of its own. I wrote about it in [GPU sharing and partitioning techniques](/posts/gpu-sharing-and-partitioning-from-vgpu-to-dra/) and in [GPU architecture for model serving on VMware Cloud Foundation](/posts/gpu-architecture-for-model-serving-on-vcf/).

## Which open-weight models fit

*Documented and model value. A number in bold is in the [list of supported models for NVIDIA NIM, the inference microservices of NVIDIA](https://docs.nvidia.com/nim/large-language-models/latest/supported-models.html) or on the model card, as read on 26 November 2026. All other numbers are calculated.*

The rule for the calculated values: a model counts as fitting only if it fits completely into the memory of the cards. I take the size of the weights times 1.15, and that must fit into 92 % of the memory of the cards. The factor 1.15 and the 92 % are my assumptions. The table shows the smallest number of cards (1, 2, 4 or 8) for one copy of the model. It has one column for each of four PCIe cards: the AMD Instinct MI350P, the Intel Gaudi 3, and the two NVIDIA cards of both sizes, the H200 NVL and the RTX PRO 6000. The section on accelerators below describes these cards. One copy on the smallest number of cards serves only a few requests at the same time.

| Model | Weights | AMD MI350P | Intel Gaudi 3 | NVIDIA H200 NVL | NVIDIA RTX PRO 6000 |
|---|---|---:|---:|---:|---:|
| gpt-oss-20b | as published | 1 | 1 | **1** | 1 |
| Qwen3.8-27B | 8-bit, 31 GB | 1 | 1 | **1** | 1 |
| Gemma 4 31B | 4-bit, 18 GB | 1 | 1 | 1 | **1** |
| Llama 3.3 70B | 8-bit, 78 GB | 1 | 1 | **2** | 2 |
| gpt-oss-120b | as published | 1 | 1 | **1** | 1 |
| Qwen3.5-122B | 8-bit, 138 GB | 2 | 2 | **2** | 2 |
| Mistral Medium 3.5 128B | 8-bit, 141 GB | 2 | 2 | 2 | 2 |
| Qwen3.5-397B | 8-bit, 443 GB | 4 | 8 | **4** | 8 |
| GLM-5.2 | 8-bit, 756 GB | 8 | 8 | **8** | more than 8 |

The rule looks only at memory. Whether an inference server supports a model and a weight format on a card is a separate check with the documentation of the card vendor. For Llama 3.3 70B the NVIDIA list names two H200 NVL cards, and I show that number. By memory alone one card would be enough.

The models with their size and licence (B = billion parameters):

| Model | Parameters | Licence |
|---|---:|---|
| [gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b) | 21B | Apache 2.0 |
| [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) | 27.8B | Apache 2.0 |
| [Gemma 4 31B](https://huggingface.co/google/gemma-4-31b-it) | 30.7B | Apache 2.0 |
| [Llama 3.3 70B](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) | 70.6B | Llama 3.3 Community |
| [gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) | 117B | Apache 2.0 |
| [Qwen3.5-122B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B) | 125B | Apache 2.0 |
| [Mistral Medium 3.5 128B](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B) | 128B | Modified MIT |
| [Qwen3.5-397B](https://huggingface.co/Qwen/Qwen3.5-397B-A17B) | 403B | Apache 2.0 |
| [GLM-5.2](https://huggingface.co/zai-org/GLM-5.2) | 753B | MIT |

I only name the licences. I do not assess them. Please read the licence of a model before you use it.

Models up to about 130 billion parameters fit on one or two cards of each of the four types. A model that needs eight cards has two options. One option is a server with all eight slots in use, which is the stage called Expansion below. The other option is to spread the model over two servers of the building block. That uses the optional second network, which has its own section below. The starter block has only 6 cards, so a model that needs 8 cards does not fit into it. A model that needs more than eight cards has to run across servers and therefore uses that network.

## What the two sizes can handle

*Model value, not measured. I compared the model with published measurements for short prompts. There the model values differed by up to about one third, mostly lower than measured, and in one case with a long input they were more than twice as high. For calls with 60,000 tokens of input I found no public measurement on these cards. The agent values are not checked against a measurement.*

The model answers one question: how many people can work on a block of each size at the same time, if the answers stay fast? Fast means about 25 to 30 output tokens per second for each user, and less than one second until the first token in a chat. For an agent call with 60,000 tokens of input the model gives two to three seconds until the first token.

I look at two kinds of use:

| Use | Tokens in per call | Tokens out per call | In : out | Calls |
|---|---:|---:|---:|---|
| Chat with an assistant | 10,000, of which 70 % from the cache | 500 | 20 : 1 | one call per active user every 2 minutes |
| Coding agents | 60,000, of which 85 % from the cache | 500 | 120 : 1 | open session: one call every one to two minutes. Working agent: one call every 30 seconds |

The values for coding agents are not my own measurements. They are rounded from a public study of GitHub Copilot traces and from its public dataset. Both are named under "Method and sources". The study reports a median prompt of 61,000 tokens for one call. In the dataset a call has 528 completion tokens on average (the study's median is 179), and 85.7 % of all prompt tokens come from the cache. The mean session in the study has 55.4 calls in 52.5 minutes, which is about one call per minute. The median session is much shorter and denser: it has 20 calls in 3.8 minutes, which is about five calls per minute.

I count agents in two ways. An open session is one developer who has an agent session open. The calls are averaged over the time the agent works and the time the developer reads and thinks. For open sessions I show one call per minute and one call every two minutes. A working agent is an agent that is running a task right now and calls the model without waiting for a person. For working agents I assume one call every 30 seconds.

The chat values are my assumptions, and I chose round numbers on purpose. Your own values will differ.

Both kinds of use run on a model of the 27B class. "Healthy operation" means: one server is a reserve, and the other servers run at 70 % of what the model says they can do. The cards in those other servers are the cards that share the load.

| Healthy operation | Starter, RTX | Starter, H200 | Building block, RTX | Building block, H200 |
|---|---:|---:|---:|---:|
| Cards that share the load | 4 | 4 | 28 | 28 |
| Chat: users active at the same time | 160 | 470 | 1,100 | 3,300 |
| Chat: tokens in per second | 13,000 | 39,000 | 91,000 | 270,000 |
| Chat: tokens out per second | 650 | 2,000 | 4,600 | 14,000 |
| Agents: open sessions, one call every 2 minutes | 38 | 120 | 270 | 830 |
| Agents: open sessions, one call per minute | 19 | 59 | 130 | 410 |
| Agents: working agents, one call every 30 seconds | 10 | 30 | 67 | 210 |
| Agents: tokens in per second | 19,000 | 59,000 | 130,000 | 410,000 |
| Agents: tokens out per second | 160 | 490 | 1,100 | 3,500 |

All numbers in this table are rounded. The three agent rows describe the same load of calls, so they give the same tokens per second.

How to read these numbers:

- Each row assumes that the whole block serves only this one use. The rows do not add up.
- One RTX PRO 6000 card is enough to hold the 27B model. In my model one copy still runs across two of these cards, because that handles more calls per card.
- The values for the H200 NVL are an upper limit of my model. I have not checked the speed my model assumes for reading a prompt of 60,000 tokens against a measurement on this card. A measurement of a similar model on an older card gave a lower speed than my model assumes.
- My model needs a compute value for each card, in TFLOPS (trillions of floating-point operations per second) for dense 16-bit calculations, which means without sparsity. For the RTX PRO 6000 I took 500 TFLOPS as my own assumption, so the values for this card depend on that choice.
- "Active at the same time" means people who are in a chat right now. The number of people with an account is several times higher.
- The input tokens include the part that comes from the cache. Without a cache the block can handle much less input.
- A chat with long documents needs more input per call. With 30,000 tokens per call instead of 10,000, the number of users falls to about one third in my model.
- A larger model changes the numbers. The model table above shows how many cards one copy of a larger model needs.
- The call rate changes the agent numbers by a factor of up to four, between one call every two minutes and one call every 30 seconds. The choice between the two cards changes them by about a factor of three. Agents that run in the background without a person count as working agents.

## From the starter block to eight cards per server

*Model value. Power is the highest value for the servers and the host network. The second network is not included.*

The building block can be reached in stages. If the starter block uses servers that can take eight cards, they can be filled step by step and more servers can be added. The last stage fills all eight servers completely.

| Stage | Servers x cards | Cards | Cards that share the load | Power |
|---|---|---:|---:|---:|
| Starter block | 3 x 2 | 6 | 4 | 9.1 kW |
| Pilot | 3 x 4 | 12 | 8 | 12.7 kW |
| Building block | 8 x 4 | 32 | 28 | 32.2 kW |
| Expansion | 8 x 8 | 64 | 56 | 51.4 kW |

One server is the reserve in every stage. The next table shows what each stage can handle in healthy operation. Users and sessions grow in proportion to the cards that share the load. The numbers are rounded.

| Stage | Chat users, RTX | Chat users, H200 | Open agent sessions, RTX | Open agent sessions, H200 |
|---|---:|---:|---:|---:|
| Starter block | 160 | 470 | 19 | 59 |
| Pilot | 310 | 940 | 38 | 120 |
| Building block | 1,100 | 3,300 | 130 | 410 |
| Expansion | 2,200 | 6,600 | 270 | 830 |

The agent columns count open sessions at one call per minute. At one call every two minutes the numbers are twice as high. Working agents, at one call every 30 seconds, are half of the numbers shown.

Four things that the stages depend on:

- The tables count only the GPU servers. The Broadcom documentation states the minimum number of hosts for a cluster.
- Whether a server is offered with two or four cards instead of eight is something the server vendor can confirm.
- The power values come from the model in the section on power and memory further below.
- The starter block is the first stage where real load can be measured: tokens in and out per call and the share that comes from the cache. Measured values can then replace my assumptions.

## Accelerators from three partners

*Pointers to official sources, read on 26 November 2026. The sources have the current state.*

The Broadcom documentation names accelerators for Private AI from three partners: AMD, Intel and NVIDIA. The table lists the accelerator families, how the linked sources describe their use on VCF, and where the compatibility guide has the current entries. It is sorted by name.

| Partner | Accelerators | What the linked sources describe | Read more | Program in the guide |
|---|---|---|---|---|
| AMD | AMD Instinct MI350 series | Enhanced DirectPath. This is a passthrough mode with a driver of the card vendor on the host. PyTorch and vLLM are the frameworks. | [VCF 9.1 release notes](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/release-notes/vmware-cloud-foundation-9-1-0-0-release-notes/what-s-new/whats-new-vsphere.html), [AI with VCF 9.1 on AMD GPUs](https://blogs.vmware.com/cloud-foundation/2026/05/05/ai-with-vcf-9-1-on-amd-gpus-build-with-open-frameworks-and-simplify-management-at-a-lower-tco/) | ["DirectPath GPUs and Accelerators"](https://compatibilityguide.broadcom.com/search?program=sptg&persona=live) |
| Intel | Intel Gaudi 3 | Enhanced DirectPath with a driver from Intel. Several cards can be combined into one device group. Telemetry is shown in vCenter. The post also describes an operator for Kubernetes, including vSphere Kubernetes Service (VKS). | [Accelerating AI Workloads with Intel Gaudi 3 on VMware Cloud Foundation 9.0](https://blogs.vmware.com/cloud-foundation/2025/08/07/accelerating-ai-workloads-with-intel-gaudi-3-on-vmware-cloud-foundation-9-0/) | ["DirectPath GPUs and Accelerators"](https://compatibilityguide.broadcom.com/search?program=sptg&persona=live) |
| NVIDIA | Data center GPUs, among them the two cards of both sizes | Flexible time-sliced vGPU, hardware-isolated MIG or DirectPath. | [Configure NVIDIA vGPU or GPU passthrough on the ESX hosts](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-0/private-ai-foundation-9-x/deploying-private-ai-foundation-with-nvidia/configure-nvidia-vgpu-or-gpu-passthrough-on-the-esx-hosts.html) | ["AI Ready Node"](https://compatibilityguide.broadcom.com/search?program=aiserver&persona=live) |

The guide also has the program "VM Direct Path IO for General GPU" for pairs of a server and a card with passthrough: [open the program](https://compatibilityguide.broadcom.com/search?program=vmdirect&persona=live).

Private AI Services in VCF 9.1 can also run a model on CPUs, without an accelerator. The post [Streamline, Simplify and Protect all your AI workloads with VCF 9.1](https://blogs.vmware.com/cloud-foundation/2026/05/05/streamline-simplify-and-protect-all-your-ai-workloads-with-vcf-9-1/) describes this.

Each partner has a card in the PCIe form factor, like the cards of both sizes. The MI350P is the PCIe card of the AMD Instinct MI350 series. The values come from the data sheets of the vendors.

| Partner | PCIe card | Memory | Power | In the building block (32 cards) | Source |
|---|---|---:|---:|---:|---|
| AMD | AMD Instinct MI350P | 144 GB | 600 W | 4,608 GB | [AMD product page](https://www.amd.com/en/products/accelerators/instinct/mi350/mi350p.html) |
| Intel | Intel Gaudi 3 HL-338 | 128 GB | 600 W | 4,096 GB | [Intel product brief](https://cdrdv2-public.intel.com/817488/Gaudi%203%20PCIe%20Product%20Brief_RB_1_V6.pdf) |
| NVIDIA | H200 NVL | 141 GB | 600 W | 4,512 GB | [NVIDIA product page](https://www.nvidia.com/en-us/data-center/h200/) |
| NVIDIA | RTX PRO 6000 Blackwell Server Edition | 96 GB | 600 W | 3,072 GB | [NVIDIA product page](https://www.nvidia.com/en-us/data-center/rtx-pro-6000-blackwell-server-edition/) |

All four cards draw up to 600 W, so in my model the power per server is the same for each of them. More memory per card means that the same model fits on fewer cards. The table of open-weight models above shows that for all four cards.

The capacity numbers on this page use the two NVIDIA cards, because I started the model with them. Capacity numbers for the AMD and the Intel card are not part of this page.

## Servers: where the official list is

*Pointer to the official source: [Broadcom Compatibility Guide, program "AI Ready Node"](https://compatibilityguide.broadcom.com/search?program=aiserver&persona=live).*

The program "AI Ready Node" lists pairs of a server and a GPU. Each entry names the card, the highest number of cards, the releases of the ESX hypervisor and what it says about NVIDIA vGPU and DirectPath. The guide writes "ESXi" for the hypervisor. I would like to test each of these servers thoroughly and run it at its limits. I cannot do that, so the values on this page are modelled at most, not measured.

I do not repeat the entries here. The two sizes on this page need servers with two to four cards (option 1) or with up to eight cards (option 2 and the building block). Which servers the guide lists for them today is in the guide. The number of cards in one server and the memory of each card set the largest model that fits into one server.

As examples, and not as a full list: when I read the program on 26 November 2026, it had entries with up to eight of these cards for the Cisco UCS C845A M8, the Dell PowerEdge XE7740 and XE7745, the HPE ProLiant Compute DL380a Gen12 and the Lenovo ThinkSystem SR675 V3. The order is alphabetical. The guide has the current list.

Three things about an entry in the guide:

- An entry applies to the CPU series it names.
- If a pair of server and card is not in the program, that says nothing about whether the pair works. The server vendor can say more.
- Storage has its own program in the guide (vSAN ReadyNode). A configuration with vSAN involves both programs.

## Power and memory of both sizes

*Model value. The power per card is the highest value from the data sheets. The other inputs are assumptions.*

| Input | Value | Label |
|---|---|---|
| Power per card | 600 W | documented, data sheets of the four cards |
| Server without cards | 1.5 kW | assumption |
| Two switches of the host network | 1.0 kW | assumption |

| | Starter block, 3 x 2 | Building block, 8 x 4 | Expansion, 8 x 8 |
|---|---:|---:|---:|
| Power per server | 2.7 kW | 3.9 kW | 6.3 kW |
| Power of all servers and the host network | 9.1 kW | 32.2 kW | 51.4 kW |
| GPU memory with RTX PRO 6000 | 576 GB | 3,072 GB | 6,144 GB |
| GPU memory with H200 NVL | 846 GB | 4,512 GB | 9,024 GB |

The model uses the same 1.5 kW for every server without cards. A small server may draw less.

These are the highest values, not an average over the day. Cooling and the optional second network are not included. The cooling you need depends on the data center.

Power and GPU memory grow with the number of cards. The number of users and agent sessions a size can handle grows with the cards that share the load, as the stage tables above show.

## Optional: a second network for models across servers

*Documented and assumption. The design is from public Broadcom sources. The numbers of adapters and switches for the building block are my assumptions.*

The host network is all a block needs as long as every model runs inside one server. A model that needs more cards than one server holds can be spread over several servers. This is called distributed inference. The GPUs then exchange data directly from server to server, and a second, faster network carries this traffic. It uses Remote Direct Memory Access (RDMA) over Converged Ethernet (RoCE) in version 2, written RoCE v2 below.

The post [Deploy VMware Private AI on HGX servers with Broadcom Ethernet Networking](https://blogs.vmware.com/cloud-foundation/2025/09/09/deploy-vmware-private-ai-on-hgx-servers-with-broadcom-ethernet-networking/) and the [white paper](https://www.vmware.com/docs/paif-hgx-brcm-eth) behind it describe such a design with Broadcom Ethernet parts:

- Broadcom adapters of the type BCM57608 with 400 Gbit/s in the servers.
- Switches with the Broadcom Tomahawk 5 chip.
- The GPUs and the adapters are given to the virtual machine with DirectPath I/O.
- Inference across several servers with NVIDIA NIM and with vLLM.

The paper uses servers with an HGX board. On this page I apply the same design to the PCIe servers of the building block. That step is my assumption.

| Part | What is documented | Source |
|---|---|---|
| Adapter | Broadcom BCM57608 with 2 x 200 Gbit/s or 1 x 400 Gbit/s. The guide has the current entries and drivers. | [Broadcom Compatibility Guide, program "IO Devices"](https://compatibilityguide.broadcom.com/search?program=io&persona=live) |
| Switch chip | Broadcom Tomahawk 5 with 51.2 Tbit/s in total. That equals 64 ports with 800 Gbit/s or 128 ports with 400 Gbit/s. The table below assumes a smaller switch with 32 ports of 400 Gbit/s. | [Broadcom product page](https://www.broadcom.com/products/ethernet-connectivity/switching/strataxgs/bcm78900-series) |
| Network settings | RoCE v2 needs a network without packet loss. Priority Flow Control (PFC) is one way to get it. | [Network requirements for RDMA over Converged Ethernet](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/9-1/vsphere-networking/managing-network-resources/rdma/network-requirements-for-rdma-over-converged-ethernet.html) |
| Software | Distributed inference on vSphere Kubernetes Service | [Broadcom paper on distributed inference](https://www.vmware.com/docs/vcf-distributed-infer) |

What this second network needs for the building block (8 x 4) and for the expansion (8 x 8) if every server is connected:

| | 8 servers x 4 cards | 8 servers x 8 cards | Label |
|---|---:|---:|---|
| Adapters, each with 2 ports of 200 Gbit/s | 16 | 32 | assumption: one port per card, so one adapter serves two cards |
| Adapter ports and cables | 32 | 64 | follows from the row above |
| Switches with 32 ports of 400 Gbit/s | 2 | 2 | assumption: one switch port per adapter port |

With 8 cards per server the 64 adapter ports use all ports of both switches. Links between the switches and to other networks need more ports.

### What this means for the virtual machine

*From my preparation for the session CLOB1084 at VMware Explore on Tour Frankfurt in October 2026, and from my lab. The linked posts name the sources.*

A model across servers runs in one virtual machine per server. In the design above, this virtual machine gets the GPUs and the adapters with DirectPath I/O. These settings shape it:

- **Card and adapter on the same side of the server.** Direct transfers between an adapter and a GPU work when both sit under the same PCIe root complex, on the same Non-Uniform Memory Access (NUMA) node. The virtual machine shows the same pairing to the guest operating system.
- **At most 128 virtual CPUs in this design.** A larger virtual machine would need a virtual input-output memory management unit (IOMMU), and this design runs without one.
- **Access Control Services stay on in the ESX hypervisor.** Direct traffic between two devices is allowed for the single virtual machine, in its advanced settings. It is not switched off for the whole host.
- **Memory is fully reserved.** DirectPath I/O requires that.
- **Large cards use 64-bit memory-mapped I/O.** In my lab one card with 24 GB already needed two extra settings for it. The value grows with the memory of all cards in the virtual machine.
- **The devices bind the virtual machine to its server.** There is no vMotion for it. A model that runs across two servers stops when one of them fails.

The details are in [GPU architecture for model serving on VMware Cloud Foundation](/posts/gpu-architecture-for-model-serving-on-vcf/) and in [part 3 of my lab series](/posts/rtx-a5000-behind-the-same-service-name/). The first post also shows other options that are not part of this design: vGPU instead of passthrough for the GPU, and a virtual function instead of passthrough for the adapter.

Three consequences of this network:

- The servers that use it give whole cards to one virtual machine, as described above. They form their own group of servers, next to the servers that share cards.
- The server needs free slots for the adapters next to the GPU cards: two adapters per server with 4 cards, four adapters with 8 cards. The server vendor can confirm that.
- I have no numbers that compare one model on two servers with the same model on one server. A measurement would show the difference.

## What this page leaves out

This page has no prices and no cost calculation. I also do not compare adapters, switches or servers of different vendors.

## Method and sources

- I read the Broadcom Compatibility Guide on 26 November 2026 to see which programs apply. I do not copy entries from it, and the guide has the current state.
- The values of the cards come from the data sheets and product pages of AMD, Intel and NVIDIA.
- The capacity model describes a GPU by three values (memory, memory bandwidth, compute) and a model by the size of its weights and the memory its cache needs per token. The card values come from the data sheets. The exception is the compute value of the RTX PRO 6000, which is my own assumption, as described under the capacity table. The chat profile is my own assumption.
- The profile for coding agents is rounded from Liu et al., [Agentic Coding in the Wild: Characterizing GitHub Copilot Traces at Production Scale](https://arxiv.org/abs/2608.00101), arXiv 2608.00101, version 2 of 20 November 2026, and from the public dataset [GitHub Copilot Coding Agent Traces 2026](https://github.com/Azure/AzurePublicDataset/blob/master/GitHubCopilotCodingAgentDataset2026.md) with traces from 1 to 7 June 2026. I read both on 26 November 2026. The prompt size in the table is rounded from a median of the study. The output size is rounded from a mean of the dataset. The traces come from the coding agents of one cloud service and, in the dataset, from its non-enterprise users. Other agents and other users have other values.
- NVIDIA sources: [vGPU support matrix for vSphere](https://docs.nvidia.com/vgpu/latest/product-support-matrix/vmware-vsphere.html), [cards that support MIG](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html), [supported models for NIM](https://docs.nvidia.com/nim/large-language-models/latest/supported-models.html).
- Broadcom source for the GPU modes on the hosts: [Configure NVIDIA vGPU or GPU passthrough on the ESX hosts](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-0/private-ai-foundation-9-x/deploying-private-ai-foundation-with-nvidia/configure-nvidia-vgpu-or-gpu-passthrough-on-the-esx-hosts.html).

If you find an error, please [mail me](/imprint/).

## Change log

**November 2026, first edition**

- First edition with two card variants, two sizes (starter block and building block), open-weight models, a capacity model, four stages and power values.
- Accelerators from AMD, Intel and NVIDIA, with a PCIe card of each partner in the model table.
- Second network: a section describes an optional second network for models across servers.
- The page covers technical aspects only.
- Correction: the capacity values for the RTX PRO 6000 are lower than in the first version. The compute value I used for this card was not on the same basis as the value for the H200 NVL, so I replaced it. The agent values are now shown as a range, and the values for the H200 NVL are described as an upper limit.
