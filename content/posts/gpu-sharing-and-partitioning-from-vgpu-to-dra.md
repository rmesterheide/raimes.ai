---
title: "GPU sharing and partitioning techniques: from vGPU to DRA and everything in between"
date: 2026-11-10T21:00:00+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/gpu-sharing-and-partitioning-from-vgpu-to-dra.jpg"
  alt: "GPU sharing and partitioning techniques: from vGPU to DRA and everything in between"
categories: ["vmware"]
tags: ["private-ai", "homelab", "gpu", "kubernetes"]
summary: "A short map of the ways one GPU can be shared: passthrough, flexible time-sliced vGPU and hardware-isolated MIG on the hypervisor, the device plugin, Dynamic Resource Allocation (DRA), time-slicing, the Multi-Process Service (MPS) and MIG in Kubernetes, and schedulers such as NVIDIA Run:ai on top. Where each one isolates, where each one pins, and what the same RTX A5000 delivered under each of them in my lab. Plus the gap between the two layers that platform teams on VMware Cloud Foundation have to plan around."
url: /review/gpu-sharing-480e5c31b6/
review_draft: true
build:
  list: never
  render: always
sitemap:
  disable: true
---

<div class="review-draft"><strong>Review draft, not published.</strong> This text is shared with a few readers for comments before it goes on the blog. Please do not forward the link. Comments by mail are welcome: use the "Found an error? Mail me" link at the end of the page.</div>

Three conversations in the last two weeks ended at the same question. A customer wants to run every workload on VMware Cloud Foundation (VCF), including AI. NVIDIA virtual GPU (vGPU) fits the VMware operating model well: vMotion, host maintenance without downtime, a GPU slice per VM. At the same time, the Kubernetes community builds everything around Dynamic Resource Allocation (DRA), and schedulers such as NVIDIA Run:ai expect a GPU that Kubernetes can partition itself. So which sharing technique belongs where, and what does each one cost?

This post is a map, not a series part. It sorts the techniques by layer, puts the numbers from my lab next to each other, and ends with how I position them. The lab is the same single-host setup as in the [Private AI Services route](/posts/private-ai-services-on-one-host-in-15-steps/): one EPYC host with ESX 9.1.1, a vSphere Supervisor, Private AI Services (PAIS) 3.0, and a refurbished RTX A5000 with 24 GB.


{{< tldr >}}
- **Two layers, two jobs.** The hypervisor shares a GPU between VMs: passthrough, flexible time-sliced vGPU, and hardware-isolated Multi-Instance GPU (MIG). Kubernetes shares a GPU between pods: device plugin, DRA with time-slicing, the Multi-Process Service (MPS) or MIG, and schedulers such as Run:ai on top.
- **Under moderate load the techniques are equal.** Two busy Gemma 4 12B instances on one RTX A5000 delivered 192 tokens per second with DRA time-slicing, 212 with MPS and 213 with two vGPU slices. Under heavy load, time-sliced vGPU fell to less than half of a single slice, because the card switches between VMs and neither batch fills it.
- **The two layers do not meet yet.** Run:ai's fractions work on GPUs that Kubernetes sees as whole devices. PAIS 3.0 uses vGPU and passthrough VM classes with the classic device plugin, not DRA. A Kubernetes-native AI stack on VCF therefore gets its GPU by passthrough into a vSphere Kubernetes Service (VKS) worker.
- **Passthrough is not the anti-pattern it was.** A VKS worker can be replaced at any time and is not managed one by one like a classic VM. Node replacement takes the place of vMotion, and the platform around the cluster stays.
{{< /tldr >}}

## The techniques, sorted by layer

### Hypervisor layer: GPU to VM

**DirectPath I/O (passthrough).** The whole card goes to one VM. Fixed DirectPath binds the VM to a Peripheral Component Interconnect (PCI) address, Dynamic DirectPath binds it to a device type, so vSphere can place the VM on any host with a free card of that type. No NVIDIA licence is needed, no vMotion is possible, and memory of the VM is fully reserved. This is the GPU that the Kubernetes layer later sees as a bare device.

**Flexible time-sliced vGPU.** The NVIDIA vGPU Manager on the host cuts the card into profiles with fixed framebuffer sizes, for example three 8 GB slices of a 24 GB card. Memory is isolated per slice. Compute is not: the card's scheduler switches between the VMs in time slices, best effort by default. vMotion works, host maintenance works, and the licence comes from NVIDIA AI Enterprise (NVAIE). The profile is static. Changing from six 4 GB slices to three 8 GB slices took me twenty minutes and new endpoints; mixed sizes on one card need a host setting and a reboot.

**Hardware-isolated MIG.** On cards with Multi-Instance GPU (MIG), from the A100 on, a vGPU profile can map to a hardware partition with its own memory and its own compute units. Isolation covers both. The A5000 in my lab has no MIG, so everything below is time-sliced.

### Kubernetes layer: GPU to pod

**Device plugin.** The classic path. The GPU Operator advertises `nvidia.com/gpu: 1` per device, a pod requests one, and gets the whole device. Time-slicing exists as a config map on the plugin, with no memory isolation at all. This is what PAIS 3.0 runs inside its VKS cluster today.

**DRA.** The core API is generally available (GA) since Kubernetes 1.34. The DRA driver for NVIDIA GPUs, now under `kubernetes-sigs`, publishes each device with its attributes, and a pod claims a device or a share of it. The sharing modes are time-slicing (fair, no memory limit), MPS (several processes on the streaming multiprocessors (SMs) at the same time, with a pinned memory limit per client), MIG with pre-cut or dynamic partitions, and consumable capacity, which lets claims take a slice of memory from one device. Partitionable devices and consumable capacity were still alpha in 1.34; I did not find a source that confirms a later status.

**Schedulers on top.** Run:ai, the KAI scheduler and Kueue add what DRA does not do: quotas per project, fair share between departments, over-quota borrowing, preemption. Run:ai's fractions are its own mechanism, independent of DRA, and they split a GPU that Kubernetes sees as a whole device. Broadcom's white paper of July 2026 describes how Run:ai is deployed on VCF with VKS clusters; for the supported GPU modes of a given Run:ai version, check NVIDIA's system requirements.

## What each one isolates, and what each one pins

| Technique | Memory isolation | Compute isolation | VM mobility | Decided by | Status |
|---|---|---|---|---|---|
| Passthrough (DirectPath I/O) | whole card | whole card | none; Dynamic DirectPath picks the host at power-on | vSphere admin | supported, no NVIDIA licence |
| Flexible time-sliced vGPU | fixed per slice | best-effort time slices | vMotion, maintenance | vSphere admin | NVAIE licence |
| Hardware-isolated MIG (as a vGPU profile) | hardware partition | hardware partition | vMotion, maintenance | vSphere admin | NVAIE licence, A100 and newer |
| Device plugin time-slicing | none | time slices | n/a (pod) | cluster admin | GA |
| DRA time-slicing | none | time slices | n/a (pod) | the claim | GA core, driver 0.5 |
| DRA MPS | pinned limit per client | SM share, concurrent | n/a (pod) | the claim | GA core, driver 0.5 |
| DRA MIG, dynamic MIG | hardware partition | hardware partition | n/a (pod) | the claim | dynamic MIG alpha |
| Run:ai fractions | per-fraction limit | scheduler | n/a (pod) | project quota | see NVIDIA's requirements |

The table has one pattern. Everything on the hypervisor layer is decided by the vSphere admin, in advance, as a VM class. Everything on the Kubernetes layer is decided by the workload, at request time, as a claim. That is the main difference between the two layers.

## The same card under four techniques

All runs use the same model, Gemma 4 12B in 4-bit, on llama.cpp with four slots per instance and 400 tokens per answer, on one RTX A5000. The DRA runs went straight to the llama.cpp instance through a port-forward; the vGPU runs went through the PAIS gateway. The single-request numbers of both paths match, so the rows are comparable; the four- and eight-parallel numbers carry a few percent of path difference.

| Load | One instance, whole card | Two instances, DRA time-slicing | Two instances, DRA MPS 50 % | Two VMs, two 12 GB vGPU slices |
|---|---|---|---|---|
| one stream each, sum | 72 | 59.6 | 72.1 | 59.4 |
| four parallel each, sum | 202 | 192 | 212 | 213 |
| eight parallel each, sum | 351 to 388 | not measured | not measured | 177 |
| one instance busy, the other idle | 72 | 72 | 55 | 69 |

Three readings.

**Moderate load does not separate the techniques.** At four parallel requests per instance, time-slicing in Kubernetes, MPS in Kubernetes and two vGPU slices land within ten percent of each other, and MPS even beats one instance alone because two processes fill the card better than one.

**Heavy load separates them.** At eight parallel requests per VM, two vGPU slices delivered 177 tokens per second together, while one slice alone delivered 388. The card switches between the two VMs every time slice, neither batch keeps the streaming multiprocessors busy, and time to first token rose from 0.2 to 2 to 3 seconds. The same measurement under DRA is still missing from my table; MPS is the technique that should do better here, because it runs both processes at the same time instead of switching.

**A light neighbour is free on both layers.** An embedding endpoint on a 4 GB vGPU slice next to the chat endpoint cost the chat endpoint three percent and delivered 506 texts per second itself. Under DRA time-slicing, an idle second instance cost nothing.

What the vGPU runs showed that the DRA runs could not: both time-slicing instances in Kubernetes saw the full 24 GB, because that path has no memory limit. Each vGPU slice had one.

## Where the two layers meet, and where they do not

This section covers what a platform team on VCF has to plan around.

**PAIS 3.0** supports CPU-only endpoints, passthrough and vGPU VM classes, and hardware-isolated MIG on cards that have it. The choice is a field in the VM class. In my lab the same instance went from CPU to a passthrough card to three 8 GB slices without a new activation. Inside its VKS cluster, PAIS runs the GPU Operator with the device plugin: no ResourceSlices, no DeviceClasses, no DRA driver. Each model endpoint gets its own worker VMs with a fixed GPU allocation. That is a deliberate design: the isolation lives in the hypervisor. As a consequence, sharing inside Kubernetes, such as MPS between two endpoints on one worker, is not available to PAIS endpoints.

**Run:ai, KAI, Kueue with DRA** need a GPU that Kubernetes can partition itself. On VCF that means a VKS cluster next to PAIS, with the card passed through into a worker, and the GPU Operator in DRA mode. My DRA cluster from the [sharing post](/posts/sharing-one-gpu-on-the-kubernetes-layer/) is exactly that shape.

**A combination I found no documentation for:** a full-size vGPU profile (the whole card as one vGPU) under a VKS worker, with the DRA driver on top. The VM would keep vMotion and the vGPU licence model, and Kubernetes would still do the sharing. Whether MPS and the DRA driver behave on a vGPU, and whether that is a supported shape, is the next row of my table, and it is not measured yet.

## How I position it now

Passthrough is avoided in the classic VMware operating model, for good reason: a long-lived VM with a pinned device loses vMotion, snapshots and maintenance without downtime. A VKS worker is not that VM. Cluster API replaces it at every Kubernetes upgrade anyway. Host maintenance becomes drain, replace, reschedule, and the platform around the cluster stays: namespaces as tenants, NSX, storage policies, lifecycle, VCF Operations with its GPU views, and PAIS in front for the gateway and the agents. In the lab a new GPU worker with driver, licence and model was answering nine minutes after the VM class was applied. The comparison a Kubernetes-native AI team makes is not against VCF with vGPU. It is against Kubernetes on bare metal or in a hyperscaler, where every GPU VM is pinned as well.

So the map I give customers has three rows.

| Workload | GPU technique | What VCF adds |
|---|---|---|
| Classic VMs: virtual desktop infrastructure (VDI), data science workstations, single-VM apps | vGPU | vMotion, maintenance, slices per VM |
| Managed AI platform: many small endpoints, gateway, agents | flexible time-sliced vGPU, hardware-isolated MIG where the card has it, via PAIS | the whole PAIS stack plus hypervisor isolation |
| Kubernetes-native AI: Run:ai, DRA, large models, multi-GPU | Dynamic DirectPath into VKS workers | platform instead of VM mobility: lifecycle, network, security, tenants |

Flexible time-sliced vGPU as the tool for cutting one card into AI endpoints is the one row I would retire where the hardware allows it. I base this on the result with eight parallel requests per VM above. Hardware-isolated MIG keeps the isolation and drops the switching cost, and that is the vGPU to plan for on the next generation of cards.

## Sources

Official documentation and the posts this builds on:

- Broadcom, [Deploying NVIDIA Run:ai on VMware Cloud Foundation](https://www.vmware.com/docs/vmw-private-ai-nvidia-run-ai-technical-paper), white paper VCF-Run-ai-WP100, July 2026, and the [blog summary](https://blogs.vmware.com/cloud-foundation/2026/07/31/deploying-nvidia-runai-on-vmware-cloud-foundation/).
- NVIDIA, [Run:ai self-hosted system requirements](https://run-ai-docs.nvidia.com/self-hosted/getting-started/installation/install-using-helm/system-requirements) and [GPU fractions](https://run-ai-docs.nvidia.com/self-hosted/platform-management/runai-scheduler/resource-optimization/fractions).
- Kubernetes, [DRA has graduated to GA](https://kubernetes.io/blog/2025/09/01/kubernetes-v1-34-dra-updates/) and [DRA features](https://kubernetes.io/docs/concepts/resource-management/dynamic-resource-allocation/dra-features/).
- [DRA driver for NVIDIA GPUs](https://dra-driver-nvidia-gpu.sigs.k8s.io/docs/).
- NVIDIA, [Virtual GPU Software User Guide](https://docs.nvidia.com/vgpu/latest/grid-vgpu-user-guide/index.html) (vGPU types, MIG, schedulers).
- Broadcom, [Maximizing GPU utilization for best total cost of ownership](https://blogs.vmware.com/cloud-foundation/2026/09/28/optimizing-ai-deployments-with-vmware-cloud-foundation-part-2/).
- William Lam, [Deploying model endpoint with DirectPath I/O using VMware Private AI Services](https://williamlam.com/2025/10/ms-a2-vcf-9-0-lab-deploying-model-endpoint-with-directpath-i-o-using-vmware-for-private-ai-services-pais.html) and [VCF 9.1.1: deploying your own AI models with PAIS 3.0](https://williamlam.com/2026/09/vcf-9-1-1-deploying-your-own-ai-models-with-vcf-private-ai-services-pais-3-0.html).
- My own measurements: [Sharing one GPU on the Kubernetes layer](/posts/sharing-one-gpu-on-the-kubernetes-layer/) (DRA, 30 October), [part 4b](/posts/one-card-cut-into-slices/) and [part 4c](/posts/six-endpoints-on-one-card/) (vGPU, 31 October and after), [GPU architecture for model serving on VCF](/posts/gpu-architecture-for-model-serving-on-vcf/) (the passthrough and vGPU basics).
