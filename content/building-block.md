---
title: "The Enterprise Private AI Building Block"
date: 2026-11-26T09:16:57+01:00
lastmod: 2026-11-26T09:32:30+01:00
draft: false
url: /building-block/
written_with_claude: true
cover:
  image: "/images/covers/building-block.jpg"
  alt: "The Enterprise Private AI Building Block"
  hiddenInSingle: true
ShowToc: true
ShowReadingTime: false
ShowBreadCrumbs: false
summary: "One building block for private AI on VMware Cloud Foundation: eight servers with four GPU cards each, in servers that can take eight. This page follows three things month by month: which accelerators and servers the Broadcom Compatibility Guide lists, what the cards cost in Germany, and what my model says such a block costs and can handle. Documented facts and model values are marked separately."
---

**Last updated:** 26 November 2026. **Data from:** 25 and 26 November 2026. **Next check:** end of December 2026.

I work as a Solutions Architect at Broadcom. This page is a service for my readers. It should help you to choose suitable hardware for private AI. It is my personal view and not an official statement from Broadcom. It is also not a sizing for your workload.

In my lab I test on a single server with one small RTX A5000. That shows how the software works. It does not show what a large installation looks like. This page adds the larger view: the same stack as a building block of eight servers with four GPU cards each, running on VMware Cloud Foundation (VCF) 9. If you need more, you fill the servers up to eight cards or add a second block.

All prices on this page are public prices from resellers in Germany that I researched myself, each with source and date. They are not vendor list prices and not quotes. They are not price information from Broadcom or from a server vendor. Real project prices differ. The calculated values come from these public sources and from my own assumptions.

I check this page about once a month. Three things change over time: the accelerators and servers that are listed, the prices of the cards, and the open-weight models that people want to run. The change log at the end says what changed in each month.

## How to read this page

Every number on this page has one of three labels.

- **Documented:** I read it in a public source, and the source and the date are named. Examples are an entry in the Broadcom Compatibility Guide or a reseller price.
- **Assumption:** I set the number myself. Examples are the power price or the price of a server without cards.
- **Model value:** I calculated it from documented numbers and assumptions. Nothing on this page is measured on this hardware. The measurements from my lab are in the posts, and they come from one RTX A5000 with 24 GB.

Use the documented parts as a starting point for your own check. Use the model values to see the order of magnitude and how it moves from month to month. For a real project, use the quote of your server vendor and a measurement with your own workload.

## The building block

| | |
|---|---|
| Servers | 8, in one cluster |
| GPU cards per server | 4, as PCIe cards, in a server that can take 8 |
| Card, variant 1 | NVIDIA RTX PRO 6000 Blackwell Server Edition, 96 GB |
| Card, variant 2 | NVIDIA H200 NVL, 141 GB |
| Platform | VCF 9.1 |
| GPU sharing | flexible time-sliced virtual GPU (vGPU) or hardware-isolated Multi-Instance GPU (MIG) |
| Host network | 2 ports of 100 Gigabit Ethernet per server, two switches. It carries management, vMotion, storage and the requests to the models. |
| Optional second network | a network with 200 or 400 Gbit/s per port for models that run across several servers, see below. Its cost is not part of the block cost. |
| Reserve | one server (7 of 8 share the load) |

Below I call the two variants the RTX block and the H200 block. "RTX PRO 6000" always means the Blackwell Server Edition on this page.

I chose servers that take standard PCIe cards. You can start such a server with two cards and add cards later.

Why four cards and not eight? A server with four of these cards draws about 3.9 kW in my model, a server with eight about 6.3 kW. Four cards per server fit the power and cooling of many existing data center racks. Most models also need only one or two cards for one copy. The four free slots leave room to grow. Systems with a fixed board of eight GPUs (NVIDIA HGX) are a different class and are not part of this page.

How one card is shared between several workloads is a topic of its own. I wrote about it in [GPU sharing and partitioning techniques](/posts/gpu-sharing-and-partitioning-from-vgpu-to-dra/) and in [GPU architecture for model serving on VMware Cloud Foundation](/posts/gpu-architecture-for-model-serving-on-vcf/).

## Accelerators from three partners

*Documented. Sources: Broadcom Compatibility Guide, programs ["DirectPath GPUs and Accelerators"](https://compatibilityguide.broadcom.com/search?program=sptg&persona=live) and ["VM Direct Path IO for General GPU"](https://compatibilityguide.broadcom.com/search?program=vmdirect&persona=live), read on 26 November 2026, and the Broadcom pages linked in the table.*

The Broadcom documentation names accelerators for private AI from three partners: AMD, Intel and NVIDIA. The table shows what I found documented for VCF 9.1 and its hypervisor ESX today. It is sorted by name.

| Partner | Accelerators in the guide for ESX 9.1 | How they are used on VCF | Read more |
|---|---|---|---|
| AMD | AMD Instinct MI350X. Listed with these servers: Dell PowerEdge R7725, Dell PowerEdge XE7745, Supermicro AS-8126GS-TNMR. The Supermicro AS-8125GS-TNMR2 is listed with the AMD Instinct MI300X. | Enhanced DirectPath. This is a passthrough mode with a driver of the card vendor on the host. PyTorch and vLLM are the frameworks. | [VCF 9.1 release notes](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/release-notes/vmware-cloud-foundation-9-1-0-0-release-notes/what-s-new/whats-new-vsphere.html), [AI with VCF 9.1 on AMD GPUs](https://blogs.vmware.com/cloud-foundation/2026/05/05/ai-with-vcf-9-1-on-amd-gpus-build-with-open-frameworks-and-simplify-management-at-a-lower-tco/) |
| Intel | Intel Gaudi 3 as a PCIe card (HL-338) and as a mezzanine card (HL-325L). | Enhanced DirectPath with a driver from Intel. Several cards can be combined into one device group. Telemetry is shown in vCenter. An operator supports Kubernetes, including vSphere Kubernetes Service (VKS). | [Accelerating AI Workloads with Intel Gaudi 3 on VMware Cloud Foundation 9.0](https://blogs.vmware.com/cloud-foundation/2025/08/07/accelerating-ai-workloads-with-intel-gaudi-3-on-vmware-cloud-foundation-9-0/) |
| NVIDIA | Data center GPUs, among them the three cards in the price table below. The program "AI Ready Node" lists them together with servers and a number of cards. | Flexible time-sliced vGPU, hardware-isolated MIG or DirectPath. | [Configure NVIDIA vGPU or GPU passthrough on the ESX hosts](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-0/private-ai-foundation-9-x/deploying-private-ai-foundation-with-nvidia/configure-nvidia-vgpu-or-gpu-passthrough-on-the-esx-hosts.html) |

Private AI Services in VCF 9.1 can also run a model on CPUs, without an accelerator. Broadcom describes this in the post [Streamline, Simplify and Protect all your AI workloads with VCF 9.1](https://blogs.vmware.com/cloud-foundation/2026/05/05/streamline-simplify-and-protect-all-your-ai-workloads-with-vcf-9-1/).

Each partner has a card in the PCIe form factor, like the cards of the building block. The MI350P is the PCIe card of the AMD Instinct MI350 series. The values come from the data sheets of the vendors.

| Partner | PCIe card | Memory | Power | In a block of 32 cards | Source |
|---|---|---:|---:|---:|---|
| AMD | AMD Instinct MI350P | 144 GB | 600 W | 4,608 GB | [AMD product page](https://www.amd.com/en/products/accelerators/instinct/mi350/mi350p.html) |
| Intel | Intel Gaudi 3 HL-338 | 128 GB | 600 W | 4,096 GB | [Intel product brief](https://cdrdv2-public.intel.com/817488/Gaudi%203%20PCIe%20Product%20Brief_RB_1_V6.pdf) |
| NVIDIA | H200 NVL | 141 GB | 600 W | 4,512 GB | see the price table below |
| NVIDIA | RTX PRO 6000 Blackwell Server Edition | 96 GB | 600 W | 3,072 GB | see the price table below |

All four cards draw up to 600 W, so the power per server in the cost model is the same for each of them. The table of open-weight models below shows all four cards.

The cost and capacity tables on this page use the two NVIDIA cards, because I started the model with them. For the AMD card I found one public offer in Germany on 26 November 2026, for the card as an option of one server vendor, made to order ([reseller page](https://www.tiefenbach-it.com/hpe-amd-instinct-mi350p-144gb-pcie-accelerator-for-s8a40c)). It does not meet the rule of my price table, so I do not calculate with it. The Intel card is sold at a price on request. Capacity numbers for the AMD and the Intel card are not part of this page.

## Servers in the compatibility guide

*Documented. Source: [Broadcom Compatibility Guide, program "AI Ready Node"](https://compatibilityguide.broadcom.com/search?program=aiserver&persona=live), read on 26 November 2026.*

The program "AI Ready Node" lists pairs of a server and a GPU. Each entry names the card, the highest number of cards and the releases of the ESX hypervisor. The guide writes "ESXi" for it.

| | November 2026 |
|---|---:|
| Entries in the program | 45 |
| Server vendors | 7 |
| Entries for ESX 9.1 | 45 |
| Entries with RTX PRO 6000 Blackwell Server Edition | 13 |
| Entries with H200 NVL | 9 |
| Entries with L40S | 24 |
| Entries with RTX PRO 4500 Blackwell Server Edition | 3 |
| Entries with an HGX board | 7 |

The next table shows the entries that fit the building block: servers that are listed with up to eight cards of one of the two variants. The numbers in the table are the highest number of cards in the entry. It is sorted by vendor name. It is not a ranking.

| Vendor | Server | CPU in the entry | H200 NVL | RTX PRO 6000 | ESX |
|---|---|---|---:|---:|---|
| Cisco | UCS C845A M8 | AMD EPYC 9005 | 8 | 8 | 9.1, 9.0 |
| Dell | PowerEdge XE7740 | Intel Xeon 6500P/6700P | 8 | 8 | 9.1, 9.0 |
| Dell | PowerEdge XE7745 | AMD EPYC 9005 | 8 | 8 | 9.1, 9.0 |
| HPE | ProLiant Compute DL380a Gen12 | Intel Xeon 6500P/6700P | 8 | 8 | 9.1, 9.0, 8.0 U3 |
| Lenovo | ThinkSystem SR675 V3 | AMD EPYC 9004 | | 8 | 9.1, 9.0, 8.0 U3 |
| Lenovo | ThinkSystem SR675 V3 | AMD EPYC 9005 | | 8 | 9.1 |

Notes on the table:

- The entries come from the certification tests of the server vendors. I have not tested any of these systems myself.
- All six entries state "NVIDIA vGPU: Yes" and "DirectPath: Yes" for the cards shown.
- An entry applies to the CPU series it names.
- An empty cell means that this pair is not in this program today. It says nothing about whether the pair works. The server vendor can tell you more.
- The program also lists servers for two to four cards, from these vendors and from Fujitsu, Hitachi Vantara and Supermicro. The full list is in the guide.
- Storage has its own program in the guide (vSAN ReadyNode). Check both programs for your configuration.

## Card prices in Germany

*Documented. Source: heise Preisvergleich, pages for [RTX PRO 6000 Blackwell Server Edition](https://preisvergleich.heise.de/nvidia-rtx-pro-6000-blackwell-server-edition-900-2g153-0000-000-a3492247.html), [H200 NVL](https://preisvergleich.heise.de/nvidia-h200-nvl-900-21010-0040-000-a3414253.html) and [L40S](https://preisvergleich.heise.de/nvidia-l40s-900-2g133-0080-000-a3127476.html). Prices read on 25 November 2026 and confirmed on 26 November 2026. Delivery status from 25 November 2026. Prices in euros. These are public reseller prices, not quotes and not project prices.*

The rule for this table: I take the lowest price of a reseller in Germany that has the card in stock. If no reseller has it in stock, I take the lowest price with a stated delivery time. Offers from other countries and offers without a delivery time are not counted.

| Card | Memory | Price incl. 19 % value added tax (VAT) | Price net | Net per GB | Delivery |
|---|---:|---:|---:|---:|---|
| RTX PRO 6000 Blackwell Server Edition | 96 GB | €19,635 | €16,500 | €172 | in stock |
| H200 NVL | 141 GB | €78,540 | €66,000 | €468 | 7 working days |
| L40S | 48 GB | €11,761 | €9,883 | €206 | in stock |

These are retail prices for a single card. A server vendor usually sells its own card option with the server, at its own price, and a project price can be very different. I use the retail price because it is public and I can read it again every month. It shows the direction, not what you will pay.

## What a block costs

*Model value. Card prices are public reseller prices, the other inputs are assumptions. All amounts in euros, net. This is not a quote.*

| Input | Value | Label |
|---|---|---|
| Card prices | as in the table above | documented |
| Server that can take 8 cards, without cards | €70,000 | assumption, servers of this class are sold at a price on request |
| Host network: adapter with 2 ports of 100 Gigabit Ethernet, one per server | €539 | documented, reseller price |
| Host network: cables, two per server | €59 each | documented, reseller price |
| Host network: switch with 32 ports of 100 Gigabit Ethernet, two per block | €15,000 each | assumption |
| Power | €0.20 per kWh, power usage effectiveness (PUE) 1.4, average load 70 % | assumption |
| Power draw | 600 W per card, 1.5 kW per server without cards | assumption |
| Hardware support | 5 % of the hardware cost per year | assumption |
| Operations | one full-time person, €120,000 per year | assumption |
| Period | 4 years | assumption |

| | RTX block | H200 block |
|---|---:|---:|
| Cards | 32 x RTX PRO 6000 | 32 x H200 NVL |
| GPU memory in total | 3,072 GB | 4,512 GB |
| Cost of the cards | €528,000 | €2,112,000 |
| Servers without cards | €560,000 | €560,000 |
| Host network | €35,000 | €35,000 |
| **Hardware in total** | **€1,123,000** | **€2,707,000** |
| Power and cooling per year | €55,000 | €55,000 |
| Hardware support per year | €56,000 | €135,000 |
| Operations per year | €120,000 | €120,000 |
| **Total over 4 years, without software** | **€2,049,000** | **€3,950,000** |
| Per card and hour, without software | €1.83 | €3.52 |

With eight cards per server (64 cards in total) the cost per card and hour falls to €1.26 and €2.95, because the same servers and the same host network hold twice as many cards.

Software is not part of this model. That includes VCF and the NVIDIA software for vGPU. For licence questions about Broadcom products, please use the [official Broadcom documentation](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/requirements-for-deploying-private-ai-foundation-with-nvidia.html). The model also leaves out the management domain, storage and data center space.

In the H200 block the cards are 78 % of the hardware cost. The card price decides the result there, so the result moves with the price table above.

## Which open-weight models fit

*Documented and model value. A number in bold is in the [list of supported models for NVIDIA NIM, the inference microservices of NVIDIA](https://docs.nvidia.com/nim/large-language-models/latest/supported-models.html) or on the model card. All other numbers are calculated.*

The rule for the calculated values: a model counts as fitting only if it fits completely into the memory of the cards. I take the size of the weights times 1.15, and that must fit into 92 % of the memory of the cards. The factor 1.15 and the 92 % are my assumptions. The table shows the smallest number of cards (1, 2, 4 or 8) for one copy of the model. One copy on the smallest number of cards serves only a few requests at the same time.

| Model | Parameters (B = billion) | Licence | Weights | AMD Instinct MI350P | Intel Gaudi 3 | NVIDIA H200 NVL | NVIDIA RTX PRO 6000 |
|---|---:|---|---|---:|---:|---:|---:|
| [gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b) | 21B | Apache 2.0 | as published | 1 | 1 | **1** | 1 |
| [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) | 27.8B | Apache 2.0 | 8-bit, 31 GB | 1 | 1 | **1** | 1 |
| [Gemma 4 31B](https://huggingface.co/google/gemma-4-31b-it) | 30.7B | Apache 2.0 | 4-bit, 18 GB | 1 | 1 | 1 | **1** |
| [Llama 3.3 70B](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) | 70.6B | Llama 3.3 Community | 8-bit, 78 GB | 1 | 1 | **2** | 2 |
| [gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) | 117B | Apache 2.0 | as published | 1 | 1 | **1** | 1 |
| [Qwen3.5-122B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B) | 125B | Apache 2.0 | 8-bit, 138 GB | 2 | 2 | **2** | 2 |
| [Mistral Medium 3.5 128B](https://huggingface.co/mistralai/Mistral-Medium-3.5-128B) | 128B | Modified MIT | 8-bit, 141 GB | 2 | 2 | 2 | 2 |
| [Qwen3.5-397B](https://huggingface.co/Qwen/Qwen3.5-397B-A17B) | 403B | Apache 2.0 | 8-bit, 443 GB | 4 | 8 | **4** | 8 |
| [GLM-5.2](https://huggingface.co/zai-org/GLM-5.2) | 753B | MIT | 8-bit, 756 GB | 8 | 8 | **8** | more than 8 |

The rule looks only at memory. Whether an inference server supports a model and a weight format on a card is a separate check with the documentation of the card vendor. For Llama 3.3 70B the NVIDIA list names two H200 NVL cards, and I show that number. By memory alone one card would be enough.

I only name the licences. I do not assess them. Please read the licence of a model before you use it.

Models up to about 130 billion parameters fit on one or two cards of each of the four types. A model that needs eight cards has two ways to run. One way is a server with all eight slots in use, which is the last expansion stage. The other way is to spread the model over two servers of the block. That uses the optional second network, which has its own section below. A model that needs more than eight cards has to run across servers and therefore uses that network.

## What a block can handle

*Model value, not measured. When I compared the model with published measurements, it was off by up to about one third, mostly too low. In one case with a very long input it was more than twice as high.*

The model answers one question: how many people can work on one block at the same time, if the answers stay fast? Fast means about 25 to 30 output tokens per second for each user, and less than one second until the first token in a chat. For an agent call with 60,000 tokens of input the model gives one to three seconds until the first token.

I look at two kinds of use:

| Use | Tokens in per call | Tokens out per call | In : out | Calls |
|---|---:|---:|---:|---|
| Chat with an assistant | 10,000, of which 70 % from the cache | 500 | 20 : 1 | one call per active user every 2 minutes |
| Coding agents | 60,000, of which 85 % from the cache | 500 | 120 : 1 | one call per running agent session every minute |

All values in this table are assumptions, and I chose round numbers on purpose. Replace them with your own.

Both use a model of the 27B class. "Healthy operation" means: one of the eight servers is a reserve, and the other seven run at 70 % of what the model says they can do.

| Healthy operation | RTX block | H200 block |
|---|---:|---:|
| Cards that share the load | 28 | 28 |
| Chat: users active at the same time | about 1,800 | about 3,300 |
| Chat: tokens in per second | about 150,000 | about 270,000 |
| Chat: tokens out per second | about 7,400 | about 14,000 |
| Agents: sessions running at the same time | about 210 | about 410 |
| Agents: tokens in per second | about 210,000 | about 410,000 |
| Agents: tokens out per second | about 1,800 | about 3,500 |

How to read these numbers:

- Each row assumes that the whole block serves only this one use. The rows do not add up.
- "Active at the same time" means people who are in a chat right now. The number of people with an account is several times higher.
- The input tokens include the part that comes from the cache. Without a cache the block can handle much less input.
- A chat with long documents needs more input per call. With 30,000 tokens per call instead of 10,000, the number of users falls to about one third in my model.
- A larger model changes the numbers. With a model of the 120B class the RTX block can handle about 20 % fewer agent calls.
- An agent session is one developer who has an agent working. How many developers that covers depends on how often they use agents.

## From proof of concept to eight cards per server

*Model value. Hardware cost in euros, net, cumulative, without software. It is based on public reseller prices and assumptions, not on a quote. The host network is included from the first stage. The second network is not included.*

You do not have to buy the block at once. You buy servers that can take eight cards and fill them step by step, so no hardware is replaced on the way. The last stage fills all eight servers completely.

| Stage | Servers x cards | Cards | Reserve | Hardware, RTX | Hardware, H200 | Chat users, RTX | Chat users, H200 |
|---|---|---:|---|---:|---:|---:|---:|
| Proof of concept | 2 x 2 | 4 | none | €237,000 | €435,000 | about 250 | about 470 |
| Pilot | 3 x 4 | 12 | one server | €440,000 | €1,034,000 | about 510 | about 940 |
| Production, one block | 8 x 4 | 32 | one server | €1,123,000 | €2,707,000 | about 1,800 | about 3,300 |
| Expansion, eight cards per server | 8 x 8 | 64 | one server | €1,651,000 | €4,819,000 | about 3,600 | about 6,600 |

Four things to check before you plan the stages:

- The table counts only the GPU servers. Check the minimum number of hosts for your cluster in the Broadcom documentation.
- A server with two or four cards instead of eight must be a configuration that the server vendor offers.
- A server with eight cards draws about 6.3 kW in my model. Check power and cooling of the rack before the last stage.
- The pilot is the stage to measure. Record tokens in and out per call and the share that comes from the cache, and replace my assumptions with your numbers.

## Optional: a second network for models across servers

*Documented and model value. The design is from public Broadcom sources, the cost is a model value. The adapter price is a public reseller price in Germany, read on 26 November 2026, in euros, net. The prices of switches and cables are assumptions. This is not a quote.*

The host network is all a block needs as long as every model runs inside one server. A model that needs more cards than one server holds can be spread over several servers. This is called distributed inference. The GPUs then exchange data directly from server to server, and a second, faster network carries this traffic. It uses Remote Direct Memory Access (RDMA) over Converged Ethernet (RoCE) in version 2, written RoCE v2 below.

Broadcom describes such a design with its own Ethernet parts in the post [Deploy VMware Private AI on HGX servers with Broadcom Ethernet Networking](https://blogs.vmware.com/cloud-foundation/2025/09/09/deploy-vmware-private-ai-on-hgx-servers-with-broadcom-ethernet-networking/) and in the [white paper](https://www.vmware.com/docs/paif-hgx-brcm-eth) behind it:

- Broadcom adapters of the type BCM57608 with 400 Gbit/s in the servers.
- Switches with the Broadcom Tomahawk 5 chip.
- The GPUs and the adapters are given to the virtual machine with DirectPath I/O.
- Inference across several servers with NVIDIA NIM and with vLLM.

The paper uses servers with an HGX board. On this page I apply the same design to the PCIe servers of the building block. That step is my assumption.

| Part | What is documented | Source |
|---|---|---|
| Adapter | Broadcom BCM57608 with 2 x 200 Gbit/s or 1 x 400 Gbit/s, listed for ESX 9.1 with the drivers bnxtnet and bnxtroce | [Broadcom Compatibility Guide, program "IO Devices"](https://compatibilityguide.broadcom.com/detail?program=io&productId=61222&persona=live), read on 26 November 2026 |
| Switch chip | Broadcom Tomahawk 5 with 51.2 Tbit/s in total. That equals 64 ports with 800 Gbit/s or 128 ports with 400 Gbit/s. The cost table below assumes a smaller switch with 32 ports of 400 Gbit/s. | [Broadcom product page](https://www.broadcom.com/products/ethernet-connectivity/switching/strataxgs/bcm78900-series) |
| Network settings | RoCE v2 needs a network without packet loss. Priority Flow Control (PFC) is one way to get it. | [Network requirements for RDMA over Converged Ethernet](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/9-1/vsphere-networking/managing-network-resources/rdma/network-requirements-for-rdma-over-converged-ethernet.html) |
| Software | Distributed inference on vSphere Kubernetes Service | [Broadcom paper on distributed inference](https://www.vmware.com/docs/vcf-distributed-infer) |

What this second network adds to the cost of one block if every server is connected. It is not part of the block cost, the stages or the capacity numbers above.

| | 8 servers x 4 cards | 8 servers x 8 cards | Label |
|---|---:|---:|---|
| Adapters, each with 2 ports of 200 Gbit/s | 16 | 32 | assumption: one port per card, so one adapter serves two cards |
| Cost of the adapters, €1,347 each | €22,000 | €43,000 | documented, [reseller price](https://www.senetic.de/product/BCM957608-P2200GQF00) |
| Cables, one per adapter port (32 or 64), €310 each | €10,000 | €20,000 | assumption |
| Two switches with 32 ports of 400 Gbit/s, €45,000 each | €90,000 | €90,000 | assumption |
| **Second network in total** | **€121,000** | **€153,000** | model value, calculated from unrounded amounts |

With 8 cards per server the 64 adapter ports use all ports of both switches. Links between the switches and to other networks are not in this cost.

Three things to plan if you want this network:

- The servers that use it give whole cards to one virtual machine. Plan them as their own group of servers, next to the servers that share cards.
- Check with the server vendor that the server has free slots for the adapters next to the GPU cards: two adapters per server with 4 cards, four adapters with 8 cards.
- Measure one model on two servers against the same model on one server before you decide. I have no numbers for that.

## What this page leaves out

Servers that can take eight cards are sold by quote. I do not compare server prices of the vendors here. I also do not compare adapters or switches of different vendors.

## Method and sources

- The compatibility guide is read through its public web interface. A small script saves all entries of the program and compares them with the month before.
- Card prices come from three pages of one price comparison site. I read them once a month.
- The capacity model describes a GPU by three data sheet values (memory, memory bandwidth, compute) and a model by the size of its weights and its cache per token. The load profiles are my own assumptions.
- NVIDIA sources: [vGPU support matrix for vSphere](https://docs.nvidia.com/vgpu/latest/product-support-matrix/vmware-vsphere.html), [cards that support MIG](https://docs.nvidia.com/datacenter/tesla/mig-user-guide/supported-gpus.html), [supported models for NIM](https://docs.nvidia.com/nim/large-language-models/latest/supported-models.html).
- Broadcom source for the GPU modes on the hosts: [Configure NVIDIA vGPU or GPU passthrough on the ESX hosts](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-0/private-ai-foundation-9-x/deploying-private-ai-foundation-with-nvidia/configure-nvidia-vgpu-or-gpu-passthrough-on-the-esx-hosts.html).

If you find an error, please [mail me](/imprint/).

## Change log

**November 2026, first edition**

- Compatibility guide: 45 entries in the program "AI Ready Node". This is the baseline for the next comparison.
- Accelerators: AMD Instinct MI350X and Intel Gaudi 3 are listed for ESX 9.1, next to the NVIDIA cards. The model table shows a PCIe card of each partner.
- Card prices: first reading, see the table.
- Model: first version with two card variants, four cards per server and four stages.
- Added on the same day: the 100 Gigabit Ethernet network is called the host network, and a new section describes an optional second network for models across servers, with its cost.
