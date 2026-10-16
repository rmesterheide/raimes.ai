---
title: "GPU architecture for model serving on VMware Cloud Foundation: whatever you pass through pins the VM"
date: 2026-10-16T09:00:04+02:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/gpu-architecture-for-model-serving-on-vcf.jpg"
  alt: "GPU architecture for model serving on VMware Cloud Foundation"
categories: ["vmware"]
tags: ["private-ai", "homelab"]
summary: "The second half of my Explore on Tour session, written down. Three ways to give a VM a GPU, how GPUs talk inside a server, and a two-letter grid for connecting GPU hosts."
---

In [the first post](/posts/private-ai-services-3-on-vcf-9-1-1/) I covered what Private AI Services 3.0 changes on VMware Cloud Foundation (VCF) 9.1.1. This one is the part of the talk that happens under the hood. A model endpoint carries two things: a model, and a VM class. Everything below is about what is inside that VM class.

As before: I work at Broadcom, this is my own reading of public material, and the lab numbers are from consumer hardware.

## TL;DR

- There are three kinds of GPU servers: normal PCIe cards, pairs joined by an NVLink bridge, and HGX systems with eight GPUs behind NVSwitch. Know which one you have before you read any option slide.
- Three ways to give a VM a GPU on one host: own the host, own the card, own a slice. More virtualisation buys more vSphere features and more driver and licence coupling.
- One rule covers all of them: whatever you pass through pins the VM to the host.
- Inside the box, NVLink is about ten times faster than any network leaving it. Fill one host before you spread a model across several.
- For several hosts there are five options, but only two decisions. The letter is the GPU, the number is the network.
- Most teams will not start with an HGX system. The everyday case is PCIe cards, GPU passed through, network virtualised, no vGPU licence.

## Three kinds of GPU servers

Before any option makes sense, look at the hardware:

1. **PCIe servers.** Normal add-in cards. Each GPU talks to the others over PCIe and the CPU.
2. **NVLink pairs.** Two cards joined by a bridge. The pair exchanges data without touching PCIe.
3. **HGX systems.** Eight GPU modules on one baseboard, fully connected through NVSwitch. NVIDIA's DGX is its own server around the same board.

The options below behave differently on each of these. Several of them do not exist on HGX at all.

## One host: own the host, own the card, own a slice

**Option A: own the host.** Full passthrough. One VM takes everything: all GPUs, the NVSwitches, the network cards if you need them. Kubernetes inside sees bare metal and runs the full NVIDIA stack in the guest. There is no driver dependency on the host. The price: no vMotion, no DRS, no HA. One cluster owns the whole host.

**Option B: own the card.** Still passthrough, but vSphere understands it. Two Kubernetes clusters can share one host, each with its own GPUs. A VM class asks for, say, two H100, and DRS finds a host that has them. DRS chooses the seat once. After that, nobody moves. Two limits: one GPU cannot be shared between VMs, and HGX systems are not supported in this mode.

**Option C: own a slice.** vGPU. The host driver cuts each GPU into profiles, and your VM class catalogue becomes a menu of GPU sizes. On HGX, device groups hand NVLink-connected GPUs to a VM as one unit: one, two, four or eight. You get vMotion and clean host maintenance, as long as you do not need unified memory. The price is coupling. Host driver and guest driver must stay on the same branch, for every tenant, and you need the NVIDIA AI Enterprise licence.

The rule that runs through all three: whatever you pass through pins the VM to the host.

One note on sizing a slice, from my own card. Parallel requests share a GPU well only if their slots fit. A 7B model with four parallel slots answered four requests at 540 tokens per second together, instead of 172 for one. The same four slots on a 27B model no longer fit on the 24 GB card. A single request fell from 101 to 56 tokens per second, and four together reached 80, less than one slot with a queue. Each slot brings its own KV cache. Size the profile for the model plus its context times its parallel slots, not for the model file. The context numbers are in [part one](/posts/private-ai-services-3-on-vcf-9-1-1/).

## Inside the box: NVLink and NVSwitch

One host is not always enough. Before connecting hosts, sixty seconds on how GPUs talk inside one.

NVLink is a private lane between GPUs. Data moves from one GPU to the next without touching PCIe or the CPU. An H100 has eighteen of these links, together about 900 gigabytes per second. That is roughly nine 400-gigabit network ports. Per GPU. Mind the units: NVLink is quoted in gigabytes, networks in gigabits.

NVSwitch is the junction. Without it, each GPU divides its links among its neighbours. With it, every GPU reaches every other at full speed. Eight cards with 80 gigabytes each then behave almost like one device with 640 gigabytes. That is how a model too large for one card still runs fast.

Three things to remember:

- Someone manages that fabric. With vGPU, the ESX host does it. With passthrough, your VM does it.
- If you partition a GPU with MIG, NVLink is off. Time-sliced profiles keep it.
- The inside of the box is about ten times faster than any network leaving it. Fill one host before you spread a model across several.

## Several hosts: the letter is the GPU, the number is the network

Five options, two decisions. Do you pass the GPU through or use vGPU? That is the letter, A or B. Do you pass the network card through or virtualise it? That is the number, 1 or 2.

| | GPU passed through (A) | vGPU (B) |
|---|---|---|
| **Physical NIC (1)** | A-1: bare metal with a vSphere badge. GPUs of two hosts exchange data directly over RDMA. No vMotion. If the host fails, the VM is gone. For one tenant doing distributed training or very large inference. | B-1: simple guest, one vGPU profile, host handles NVLink below the VM. NVIDIA AI Enterprise licence, matching drivers on host and guest. For when your NICs or your VCF version cannot do the virtualised variant yet. |
| **Virtual NIC (2)** | A-2: same GPUs, NIC virtualised inside a VPC. You keep RDMA and the workload sits in a normal tenant network. For providers who hand whole GPU hosts to tenants and re-wire the network when a host changes hands. | B-2: both virtualised. DRS places the workload. vMotion stays, as long as you do not use unified memory or NVLink between GPUs. If you ask me where this is going: here. |

And the option that does not fit the grid, which is really the everyday case. **Option C:** no HGX, no NVSwitch, normal servers with PCIe cards. Several GPU VMs per host. The GPU is passed through, the network card is virtualised. No vGPU licence. Dense, cost-efficient model serving. Most teams start here, and it is a good place to start.

## Enhanced DirectPath: the exception that proves the rule

*Added 16 October 2026, after a reader question.*

Enhanced DirectPath I/O is passthrough that vSphere understands. A vendor driver on the host presents the device as a hardware-backed virtual device, so vSphere can place it with DRS and, if the driver supports it, migrate it. Broadcom is explicit that this is a framework and not every device gets every feature.

Where it stands today, from public documentation: Intel's Flex GPUs support vMotion this way, with a short pause to move GPU state. AMD Instinct cards do not. For the MI350 on ESX 9.1, Broadcom lists Live Patch, Storage vMotion and hot-add, not vMotion. Intel Gaudi 3 uses Enhanced DirectPath for device groups of eight cards and telemetry, nothing more. NVIDIA GPUs get vMotion only through vGPU.

So for the accelerators you would buy for model serving, the rule holds. What Enhanced DirectPath buys you is the day-two work around the VM: patch the host live, move the disks, add memory. Check the Broadcom Compatibility Guide for the card you plan to buy, not the feature name.

## The details that bite when you build it

- **RDMA needs a lossless network.** Either InfiniBand, which is lossless by design, or RoCE on Ethernet with priority flow control and ECN configured. That is a job for your network team, not a vSphere setting.
- **GPU and NIC on the same NUMA node.** Direct NIC-to-GPU transfers only work when both devices sit under the same PCIe root complex. HGX boards pair them for this reason. The VM has to reproduce that pairing.
- **At most 128 vCPUs for GPUDirect VMs.** Beyond that, a VM needs a virtual IOMMU, and that must be off here.
- **Do not "disable ACS".** ACS stays enabled in ESX. Peer-to-peer is allowed per VM class, in the VM's advanced settings.
- **"No MIG" in option C is about the option, not the card.** It hands out whole cards. The RTX PRO 6000 Blackwell Server Edition does support MIG.

## What I would decide first

1. Which of the three server kinds do you have, or are you buying? That removes half the options.
2. Do you need vMotion for GPU VMs? If yes, you are in vGPU territory, with the licence and the driver coupling that comes with it.
3. Does one model fit one host? If yes, stop at NVLink. Multi-host RDMA is a network project before it is a GPU project.
4. Pass-through or vGPU, physical or virtual NIC. Pick the letter and the number knowing what each one pins.

## Watch the original

The full GPU block, with every option diagram, is in the Las Vegas recording [CLOB1084LV: Design & Architect: VMware Cloud Foundation Private AI Services](https://www.vmware.com/explore/video/6403820843112). William Lam's [vmware-explore-2026-session-urls](https://github.com/lamw/vmware-explore-2026-session-urls) lists the other sessions.

## Sources

- [Why Enhanced DirectPath wins for high-performance apps](https://blogs.vmware.com/cloud-foundation/2026/04/20/why-enhanced-directpath-wins-for-high-performance-apps/), Broadcom blog, April 2026, with the per-device feature table
- [VCF 9.1 release notes, what's new in vSphere](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/release-notes/vmware-cloud-foundation-9-1-0-0-release-notes/what-s-new/whats-new-vsphere.html), AMD MI350 and ConnectX-7 with Enhanced DirectPath
- [Intel Data Center Graphics Driver for VMware ESXi with Enhanced DirectPath I/O](https://knowledge.broadcom.com/external/article/384647/intel-data-center-graphics-driver-for-vm.html), Broadcom KB 384647
- VMware Cloud Foundation 9.1 Design Library, Private AI section, Broadcom TechDocs
- Broadcom white paper on GPUDirect RDMA on vSphere, September 2025
- Broadcom KB 313255 on virtual IOMMU and VMs with more than 128 vCPUs
- NVIDIA AI Enterprise 8 documentation, supported vGPU types
