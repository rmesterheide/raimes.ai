---
title: "From Intel to AMD EPYC: one lab host, two years later"
date: 2026-11-09T22:13:51+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/from-intel-to-amd-epyc-two-years-later.jpg"
  alt: "From Intel to AMD EPYC: one lab host, two years later"
  hiddenInSingle: true
categories: ["homelab-ai"]
tags: ["homelab"]
summary: "In September 2024 I wrote on Medium why I replaced two Intel consumer servers with one AMD EPYC host. This is that post again, updated: what the reasons look like two years later, what the host does today, and the three parts that go in next: a 64-core EPYC 7713, an Optane P4800X as a memory tier and an enterprise NVMe drive with power-loss protection for vSAN."
linkedin: ""
---

In September 2024 I published a post on Medium about my move from Intel consumer CPUs to one AMD EPYC server. I no longer write on Medium, so the post moves here. The original is still there: [Why I Switched from Intel to AMD EPYC for My Homelab](https://medium.com/@rmesterheide/why-i-switched-from-intel-to-amd-epyc-for-my-homelab-9cc182dfe230). This version keeps the reasons from 2024 and adds what happened since: the host ran every VCF Holodeck release for two years, it is now a vSphere 9.1.1 lab with a GPU, and three new parts are waiting to be installed.

A disclosure, as always: I work at Broadcom as a solutions architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement.

{{< tldr >}}
- The 2024 decision still holds: **one host with local NVMe** instead of two hosts on shared NFS.
- After two years of nested Holodeck labs, the host changed its job in October 2026: a **vSphere 9.1.1 lab with an RTX A5000** for Private AI Services.
- Three parts go in next, in one go: **EPYC 7713 (64 cores), Optane P4800X 750 GB for memory tiering, Samsung PM9A3 3.84 TB for vSAN**. They are delivered or on the way, not installed yet.
{{< /tldr >}}

## Why I left Intel in 2024

For years I ran Intel consumer CPUs on Supermicro boards. The goal was many cores at a low power budget, and up to the 11th generation that worked well. The 12th generation changed the design: performance cores and efficiency cores on one chip. vSphere did not make good use of that split. The usual workaround was to disable one kind of core in the BIOS. For a lab that should run for years, that felt wrong.

So the question became Xeon or EPYC. The AMD EPYC 7513 had 32 cores, eight memory channels and a price well below a Xeon with the same core count. The workloads I had in mind were nested ESXi, VMware Cloud Foundation (VCF) and Kubernetes, all of which want cores and memory more than clock speed.

The second decision was the shape of the lab. Until then I had two physical servers with a Synology NAS as shared NFS storage over 10 Gbit/s. I replaced both with one server and local NVMe drives. The reasons from 2024:

- **One box is simpler to run** than two boxes plus shared storage.
- **VCF Holodeck needs only one ESXi host**, so a second host adds nothing for that use case.
- **Nested hypervisors are heavy on I/O.** Local NVMe keeps that traffic off the network.

Two years later I would make the same three choices again.

## The 2024 build

| Part | Model |
|---|---|
| Mainboard | Supermicro H12SSL-NT (single socket SP3, IPMI, two onboard 10 GbE ports) |
| CPU | AMD EPYC 7513, 32 cores, 2.6 GHz, 200 W |
| Memory | 8 × 64 GB Samsung RDIMM DDR4-2933 ECC, 512 GB on all eight channels |
| Cooler | Noctua NH-U14S TR4-SP3 |
| NVMe | Two Samsung 990 PRO 4 TB in the two M.2 slots |
| SATA | Samsung 870 QVO 4 TB, Samsung 870 EVO 500 GB (boot) |
| Power supply | be quiet! Straight Power 11, 750 W, 80 Plus Gold |
| Case | be quiet! Pure Base 500 |

The one lesson from the build that I still tell people: an EPYC CPU that is not seated perfectly makes memory modules disappear. I lost days to missing DIMMs. Only after I took the CPU out and put it back in did all eight modules show up.

## What the host did since

The host did what it was bought for. From the first Holodeck for VCF 5.x to Holodeck 9.0.2, every release went onto this host, and each one was used for tests: upgrades, Kubernetes on the Supervisor, NSX topologies. The [companion post](/posts/vmware-cloud-foundation-on-one-epyc-host-holodeck-and-a-single-host-fleet/) has the details. In October 2026 the host changed its job: it became a plain vSphere 9.1.1 host with a vSphere Supervisor and Private AI Services (PAIS) 3.0, and on 27 October 2026 a refurbished RTX A5000 went in. That story is in [part 1](/posts/kubernetes-api-on-vsphere-in-one-evening/) and [part 3](/posts/rtx-a5000-behind-the-same-service-name/) of the PAIS route, and the short version is on the [15-steps page](/posts/private-ai-services-on-one-host-in-15-steps/).

One number from that time shows what nested labs do to a drive. The 990 PRO that carried the Holodeck hosts had written 459 TB in 331 power-on days when I read its SMART data in November 2026, about 1.4 TB per day. The drive reports 6 percent of its rated life used, so endurance is not the problem. The problem is write latency without power-loss protection, which is the reason for the third new part below.

```
# On the ESX host, over SSH. Find the device id, then read the SMART data.
esxcli storage core device list | grep -i -B1 -A4 samsung
esxcli storage core device smart get -d <device-id>
```

Expected result: a table with `Data Units Written`, `Percentage Used` and `Unsafe Shutdowns`, among others. The data units are in 512-byte units of 1,000, so multiply by 512,000 for bytes.

## What goes in next

Three parts are new. Two are delivered, one is on its way. They go into the host in one go, with one opening of the case, as soon as the drive has arrived. Nothing is installed yet, so this section is a plan.

| Part | Model | Role |
|---|---|---|
| CPU | AMD EPYC 7713, 64 cores, 2.0 to 3.675 GHz, 225 W | replaces the EPYC 7513 |
| Memory tier | Intel Optane DC P4800X 750 GB, PCIe card, 30 drive writes per day | NVMe memory tiering |
| vSAN device | Samsung PM9A3 3.84 TB U.2 with power-loss protection, used | the single vSAN disk for a VCF fleet |
| Adapter | Delock 90081, PCIe 4.0 x4 card for one U.2 drive | carries the PM9A3 |

**The CPU.** The 7713 has twice the cores of the 7513 on the same socket, at 225 W instead of 200 W. I want a VCF 9.1.1 fleet, PAIS and nested experiments on the host at the same time, and 32 cores are tight for that. The 48-core 7643 was the budget option, and the 280 W models were out because of the cooler and the power supply. Before the swap I check the BIOS version over IPMI and the cooler rating for 225 W.

**The memory tier.** vSphere 9.1 can use an NVMe device as a second memory tier next to DRAM. With a ratio of 100 percent, 512 GB of DRAM become about 1 TB of memory for VMs. Broadcom asks for a dedicated device with high endurance, and the Optane P4800X has more of that than anything else I could buy. The ESX side is one command in maintenance mode, with no reboot in 9.1:

```
# On the ESX host, in maintenance mode. <device> is the Optane, from "vdq -q".
esxcli memtier enable -d /vmfs/devices/disks/<device> -r 100
```

What I will use the tier for is in the [companion post on Holodeck and the single-host fleet](/posts/vmware-cloud-foundation-on-one-epyc-host-holodeck-and-a-single-host-fleet/).

**The vSAN device.** The 990 PRO drives are fast, but they are consumer drives: no power-loss protection, and not on the vSAN compatibility list. Without power-loss protection every synchronous write of etcd, PostgreSQL or the vSAN log waits for the flash. On a single host with no redundancy, a power cut can also cost data. The PM9A3 is an enterprise drive with power-loss protection and it sits on the vSAN list. 3.84 TB is enough for a fleet with room left, and the freed 990 PRO stays for nested experiments. The H12SSL-NT has no U.2 port, so the drive goes on a small PCIe card.

## What stays

The board, the 512 GB of memory, the cooler, the power supply and the case stay. So does the one-host shape from 2024. The RTX A5000 keeps its x16 slot. The Optane card and the U.2 adapter take two of the free slots, and nothing uses the SlimSAS ports.

## What I would do differently

- **Buy one enterprise NVMe drive with power-loss protection from the start.** In 2024 I bought three consumer drives. The fast ones were fine for nested ESXi, but the moment the host runs a real control plane, the missing power-loss protection shows up in write latency.
- **Plan the second CPU early.** The SP3 socket on the H12SSL-NT takes the whole 7003 series. I knew that in 2024 and still bought at the low end. The 7513 was fine for Holodeck. For a fleet plus an AI platform plus nested hosts, 64 cores are the better fit, and the used 7513 will find a buyer.
- **Give the host a second job next to the nested lab.** For two years it ran Holodeck and nothing else, and between two test rounds it sat idle. Since October 2026 it also runs a platform that is used every day, and the nested labs come back on top of that.

## Official documentation and William Lam's posts

- [Memory Tiering over NVMe](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/9-1/vsphere-resource-management/memory-tiering-over-nvme.html) in the Broadcom documentation, and the VMware blog post [Advanced Memory Tiering Enhancements in VMware Cloud Foundation 9.1](https://blogs.vmware.com/cloud-foundation/2026/05/07/advanced-memory-tiering-enhancements-in-vmware-cloud-foundation-9-1/).
- William Lam: [VCF 9.1 - Are You Using the Correct ESXCLI Command to Enable NVMe Tiering?](https://williamlam.com/2026/06/vcf-9-1-are-you-using-the-correct-esxcli-command-to-enable-nvme-tiering.html) and [VCF 9.1 - Comprehensive ESX Configuration Workarounds for Lab Deployments](https://williamlam.com/2026/05/vcf-9-1-comprehensive-esx-configuration-workarounds-for-lab-deployments.html).
- The 2024 original on Medium: [Why I Switched from Intel to AMD EPYC for My Homelab](https://medium.com/@rmesterheide/why-i-switched-from-intel-to-amd-epyc-for-my-homelab-9cc182dfe230).
