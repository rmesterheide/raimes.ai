---
title: "Route to Private AI Services 3.0, part 4c: six model endpoints on one 24 GB card, all busy at once"
date: 2026-11-03T08:30:03+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/six-endpoints-on-one-card.jpg"
  alt: "Route to Private AI Services 3.0, part 4c: six model endpoints on one 24 GB card, all busy at once"
categories: ["vmware"]
tags: ["private-ai", "homelab", "gpu", "vgpu", "benchmark", "licensing"]
summary: "Third piece of part 4. The RTX A5000 is cut into six 4 GB vGPU slices, and Private AI Services 3.0 runs six model endpoints on it: three chat and three embedding. The fifth slice only came after I switched the card out of mixed-size mode. Five of six slices ran slowly until I made the licence pool larger. vCenter shows the limit for the first problem on a page I had not opened before. With six endpoints busy at once, each keeps about a quarter of the card."
---

[Part 4a](/posts/from-passthrough-to-vgpu-slices-in-one-evening/) was the route to NVIDIA vGPU on one host and the three checks I would do first. [Part 4b](/posts/one-card-cut-into-slices/) ran one, two and three endpoints on the card and measured them. This piece puts six endpoints on the same card: six slices of 4 GB, six Private AI Services (PAIS) model endpoints, all busy at the same time. NVIDIA's table says the RTX A5000 takes six of the 4C profile. Getting there took one host reboot and one visit to the licensing portal.

The setting is the same as in parts 1 to 4b: one EPYC host with ESX 9.1.1, a vSphere Supervisor, and PAIS 3.0 activated from vCenter. PAIS 3.0 is fully supported on a plain vSphere and vCenter basis, and that is what I rebuild here. I would like to use the multi-tenancy and the NSX-based Virtual Private Cloud (VPC) features of VMware Cloud Foundation (VCF) as well, but this is a small lab. The card is a refurbished RTX A5000 with 24 GB.

A disclosure, as always: I work at Broadcom as a solutions architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement. The NVIDIA software runs on a 90-day NVIDIA AI Enterprise evaluation that I requested as a private person for this lab.

{{< rebuild repo="rmesterheide/pais-vgpu" >}}the host scripts (install, vGPU mode, scheduler, watch, housekeeping), the endpoint manifests and the runbook that creates the six endpoints one after the other, the load tool for N endpoints, and the raw results of this evening.{{< /rebuild >}}

{{< tldr >}}
- **Six 4 GB slices run six endpoints on one RTX A5000.** Three Qwen3 4B chat endpoints and three BGE-M3 embedding endpoints, all busy at once: 385 tokens per second of chat plus 454 texts per second of embeddings from one card at 100 % and 229 W.
- **Each endpoint keeps about 28 % of the card, not a sixth.** A chat slice alone does 156 tokens per second in a single stream; with five busy neighbours it does 44. The three chat endpoints land within 1 % of each other, the three embedding endpoints within 4 %.
- **Check 4, the vGPU mode of the host.** In mixed-size mode the card offers four 4C slots, not six, and vCenter says "No host is compatible" for the fifth VM. vCenter shows the limit under Monitor, DirectPath Profiles Utilization. Changing the mode needs an empty card and a host reboot before vCenter believes it.
- **Check 5, the size of the licence pool.** Every new node takes a 24-hour licence lease and deleted nodes keep theirs. My allocation of six seats ran out after a rebuild. Five slices kept serving, but very slowly, and nothing above the driver said why. Size the allocation for the nodes a rebuild creates, not for the nodes that run afterwards.
- **After a host reboot, expect four kinds of leftovers** on the Supervisor and in the PAIS cluster. Each has one fix.
{{< /tldr >}}

## The plan

The evening of part 4b ended with a 12 GB chat slice and a 4 GB embedding slice on the card and 8 GB idle. The 4C profile has 4 GB of framebuffer. With error-correcting code (ECC) switched on at the host, about 3.7 GB of the 4 GB reach the VM. That leaves room for a small chat model or an embedding model, not for the 12B model of the earlier parts. I chose two workloads that fit:

- **Qwen3 4B** in 4-bit (Q4_K_M, 2.5 GB), llama.cpp with CUDA, 4k context, reasoning switched off, for three chat endpoints.
- **BGE-M3** on the Infinity engine for three embedding endpoints, the same model as in part 4b.

Both models went into the lab's Harbor registry from the 4090 workstation in the afternoon.

One word on what the six are. All six endpoints run in the one PAIS namespace of this lab, so in VCF terms they are one tenant with six workloads. Real tenants would be separate Supervisor namespaces, or VPCs on VCF, each with its own quota and its own gateway. This piece is about sharing one card between six workloads, not about isolation between tenants. The VM class `a5000-vgpu-4c` has 4 vCPUs and 16 GB fully reserved, so six workers take 24 vCPUs and 96 GB of the host. A small runbook creates the six endpoints one after the other and waits for each node to join before it applies the next one. That is Check 3 of part 4a applied: a node that boots more than 15 minutes after its Machine was created never joins.

## The fifth slice never came

Slices two to four came up a minute apart. Slice five did not. The ModelEndpoint stayed at `waitingForVKSMachineDeployment`, the Machine at `Provisioning`, and after 20 minutes the Supervisor's event log had the reason:

```text
PlaceVmsXCluster failed: faults: [ResourcePool resgroup-57 faults: No host is compatible with the virtual machine.]
```

Nothing had reached the host. The card had 7.9 GB free, enough for two more slices, so memory was not the problem. The vGPU driver on the host shows the reason:

```text
nvidia-smi vgpu -s -i 0 -v
    NVIDIA RTXA5000-4C
        Max Instances                     : 6
        Placement Size                    : 4
        Heterogeneous Placement IDs       : 0 8 12 20
```

There are four placement IDs. The card ran in **mixed-size mode**. This mode lets a 12 GB slice and a 4 GB slice share one card, which part 4b needed. In that mode the driver reserves fixed starting points per profile size, and for 4 GB slices on a 24 GB card there are four of them. NVIDIA's table for the RTX A5000 has both columns: 4C is six per GPU in equal-size mode and four in mixed-size mode, 8C is three and two. Frank Denneman describes the theory in [his series on GPU placement](https://frankdenneman.ai/2026-02-24-mixed-size-vgpu-mode-in-practice/); this evening I ran into the practical case.

vCenter shows this more clearly than the shell does. Cluster, Monitor, **DirectPath Profiles Utilization**: one row per vGPU profile in use, with Consumed, Remaining and Maximum. With the card in mixed-size mode the maximum for `nvidia_rtxa5000-4c` is 4. I found that page only after I had solved the problem.

{{< figure src="/images/six-endpoints-on-one-card/vcenter-directpath-profiles.jpg" alt="vCenter, cluster01, Monitor, DirectPath Profiles Utilization: the profile nvidia_rtxa5000-4c with 6 instances consumed, 0 remaining, maximum 6" caption="vCenter, Monitor, DirectPath Profiles Utilization after the switch to same-size mode: six of six. In mixed-size mode the same row reads four." >}}

{{< figure src="/images/six-endpoints-on-one-card/vcenter-directpath-by-vms.jpg" alt="vCenter, DirectPath Profiles Utilization, View by VMs: the six PAIS worker VMs on esx01, each with one nvidia_rtxa5000-4c profile" caption="The same page, View by VMs: which VM holds which profile on which host. This is the list a platform team would check before it promises a seventh endpoint." >}}

Switching the mode takes one command and a long wait. `esxcli graphics device set -d <device> -m SameSize` is accepted while VMs run, but it only writes the configuration. The running driver keeps its mode until the card is empty and `nvidia-smi vgpu -shm 0` changes it. `hostd` keeps the old value until it is restarted. Even after both, vCenter kept refusing the fifth VM. What worked was a host reboot. The setting survived it, and vCenter placed slices five and six within two minutes of the Supervisor coming back.

The switch is a decision about the profile catalog, not about six against four. Mixed-size mode is for a card that serves different slice sizes at the same time; same-size mode is for a card that serves one size as densely as possible. A host runs one of the two, so the catalog of a GPU cluster decides the mode of its hosts.

## After the reboot

A single-host lab with a Supervisor does not recover from a reboot on its own. This time the list was longer than on earlier evenings, so here it is in full, each item with its fix:

1. **The Supervisor's pods on the host stayed Pending.** Spherelet, the agent on the host, had started before the Supervisor and looped on `PodNotFound`. After a restart it reported `PodVMAnnotationsMissing` for the half-created pod objects. Delete every Pending pod of the system namespaces and the Deployments recreate them. The PAIS gateway was back a minute later.
2. **The engine pods on the rebooted nodes sat in `UnexpectedAdmissionError`.** If a node reboots and a pod asks for a GPU before the device plugin has registered it, the pod ends up in that state and nothing replaces it. Delete them.
3. **One engine had loaded its model on the CPU.** Its pod had started before the driver was ready, llama.cpp fell back to the CPU without an error, and the slice held 388 MiB instead of three gigabytes. The host-side `nvidia-smi vgpu -q` shows the used framebuffer per slice, which is how I found it. Delete that pod too.
4. **The two Machines created before the reboot had expired tokens.** Check 3 from part 4a, annotate and delete, replacement VMs in a minute.

None of this is a fault of PAIS or vSphere Kubernetes Service (VKS). It is what happens to a cluster that owns its nodes when the only host under it goes away. On a cluster of three hosts the same reboot is a maintenance-mode evacuation, and none of these four problems appear.

## The licence that was not there

All six slices were on the card, all six endpoints were Ready and all six engine pods were Running, but only one endpoint answered normally. The other five needed more than 40 seconds for eight tokens. The slices held their models, the GPU sat at 0 % during a request, and the gateway timed out. Inside the driver pods, `nvidia-smi -q` showed a line I had not checked before:

```text
License Status                    : Unlicensed (Restricted)
```

It said this five times. The driver's log gives the reason: `Failed to acquire license from api.cls.licensing.nvidia.com (NVIDIA Virtual Compute Server - Error: feature limits exhausted)`. My allocation in the NVIDIA licensing portal had six licences, created for the two-slice evening of part 4b. Every new node is a new client with a 24-hour lease. A deleted node keeps its lease until it expires. That day a dozen nodes had been created and deleted. The portal lists the leases per client, with the VM name, and four of the six belonged to VMs that no longer existed.

An unlicensed vGPU does not stop, it keeps serving at a fraction of its speed. PAIS still shows the endpoint as Ready, the gateway shows a timeout, and the slice still shows its memory in use. Only the driver inside the node says "unlicensed".

The fix is in the portal: disable leasing on the allocation, edit the licence count, save, enable leasing again. Leasing has to be off to edit, so keep that window short. The driver retries every five minutes; all six slices answered within six minutes of the change. The portal also offers a Release action per lease, which I would use after every rebuild of a lab like this.

## The numbers

All six endpoints at once. I measured from the Mac mini through the PAIS gateway. Every chat endpoint got one streaming request and then four parallel requests of 400 tokens. Every embedding endpoint got four workers for 60 seconds with 16 texts per request. The host watch ran at the same time.

| Endpoint | Single stream | 4 parallel, aggregate | Embeddings |
|---|---|---|---|
| chat-4c-1, Qwen3 4B | 44.0 tok/s, first token 0.16 s | 128.0 tok/s | |
| chat-4c-2 | 44.0 tok/s, first token 0.36 s | 128.0 tok/s | |
| chat-4c-3 | 43.5 tok/s, first token 0.26 s | 129.0 tok/s | |
| bge-m3-vgpu4c, BGE-M3 | | | 148 texts/s, median 0.40 s |
| bge-m3-vgpu4c-2 | | | 154 texts/s, median 0.40 s |
| bge-m3-vgpu4c-3 | | | 152 texts/s, median 0.40 s |

Right after the run I measured one endpoint alone with the other five idle. The chat slice did 155.7 tokens per second in a single stream and 476.4 aggregate at four parallel requests, the embedding slice 523 texts per second.

| | alone | with five busy neighbours | share |
|---|---|---|---|
| Qwen3 4B, single stream | 155.7 tok/s | 44.0 tok/s | 28 % |
| Qwen3 4B, 4 parallel | 476.4 tok/s | 128.0 tok/s | 27 % |
| BGE-M3, 4 workers | 523 texts/s | 148 to 154 texts/s | 29 % |

Three readings.

First, the best-effort scheduler shares the card evenly across six VMs: the chat endpoints are within 1 % of each other, the embedding endpoints within 4 %, the same picture as with two and three endpoints in part 4b.

Second, each endpoint keeps a little more than a quarter, not a sixth. The embedding endpoints are idle between their short bursts, and that time goes to the chat endpoints.

Third, the card as a whole delivered 385 tokens per second of chat and 454 texts per second of embeddings at the same time. A single endpoint alone reaches 476 tokens per second or 523 texts per second. Running six VMs on one time-sliced card costs about a fifth of that throughput.

The host during the run: 100 % GPU utilisation, 227 to 229 W against the 230 W cap, 70 to 76 degrees Celsius. The framebuffer stayed at 22.3 of 23 GB allocated the whole evening: six slices of 3.7 GB each.

{{< figure src="/images/six-endpoints-on-one-card/ops-host-gpu-utilisation.jpg" alt="VCF Operations, GPU Equipped Clusters: host GPU utilisation of the one card over the last hour with the plateau at 100 percent during the six-endpoint run" caption="VCF Operations, GPU Equipped Clusters: the host GPU utilisation over the hour, with the six-endpoint run as the plateau at 100 %." >}}

{{< figure src="/images/six-endpoints-on-one-card/ops-gpu-consumers-summary.jpg" alt="VCF Operations, GPU Consumers summary: 6 VMs with GPU, 13 VMs in total, 1 ESXi host, 1 GPU" caption="VCF Operations, GPU Consumers: the summary strip after the evening, six VMs with GPU on one card." >}}

{{< figure src="/images/six-endpoints-on-one-card/ops-gpu-consumers-six.jpg" alt="VCF Operations, GPU Consumers: the list of six virtual machines with GPU, each with the profile nvidia_rtxa5000-4c" caption="The same dashboard, the list of VMs with a GPU: six rows, one profile. The per-VM vGPU metrics of part 4b work the same way for six." >}}

## Two more checks for the list

Part 4a ended with three checks for a platform team. This evening adds two.

- **Check 4, the vGPU mode of the host against the profile catalog.** Mixed-size mode for hosts that mix slice sizes, same-size mode for hosts that pack one size. The count per profile is in NVIDIA's table per card, and vCenter shows it live under Monitor, DirectPath Profiles Utilization. Changing the mode means an empty card and a host reboot.
- **Check 5, the licence pool against the number of nodes created.** Count the nodes a rebuild creates in a day, not the nodes that run at the end of it, and give the allocation that many seats plus headroom. An unlicensed slice does not fail, it runs very slowly, and the first symptom is a timeout at the gateway. Release the leases of deleted nodes in the portal after a rebuild.

## What comes next

The card now runs six licensed 4C slices in same-size mode. The scheduler comparison, equal share and fixed share against best effort, did not fit into this evening. It gets its own piece. Then comes the decision piece that ends the series. It compares passthrough, Dynamic Resource Allocation (DRA) and vGPU for one card, two cards and a GPU cluster. It puts the licence cost per GPU next to the utilisation each option can reach.
