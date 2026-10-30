---
title: "Sharing one GPU on the Kubernetes layer"
date: 2026-10-30T22:54:25+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/sharing-one-gpu-on-the-kubernetes-layer.jpg"
  alt: "Sharing one GPU on the Kubernetes layer"
categories: ["vmware"]
tags: ["private-ai", "homelab", "gpu", "kubernetes"]
summary: "A detour on the route to Private AI Services 3.0: while the vGPU entitlement sits in an NVIDIA support queue, the RTX A5000 and a fresh vSphere Kubernetes Service cluster answer the question every platform team gets, how many models fit on one card. Dynamic Resource Allocation (DRA) on Kubernetes 1.36, NVIDIA's new operator mode with the DRA driver built in, two llama.cpp instances on one GPU with time-slicing and then with the Multi-Process Service (MPS), measured against the single-tenant baseline. Plus the two traps that cost the evening, and a companion repository to rebuild it from zero."
---

[Part 3](/posts/rtx-a5000-behind-the-same-service-name/) ended with the plan for part 4: NVIDIA vGPU on the same card, so that several vSphere Kubernetes Service (VKS) workers share the A5000 and the platform can hand out slices instead of whole GPUs. The 90-day NVIDIA AI Enterprise (NVAIE) evaluation was approved within hours. Then NVIDIA's own portal could not attach it to my account. Their support answered quickly and confirmed a known issue on their side; the fix is in the works, and the card has time until then. The card was ready, the weekend was free, and the question behind part 4 does not need vGPU to be asked: **how do you share one GPU between several workloads, and what does each way cost?**

So this is a detour, on purpose. It stays one layer up, in Kubernetes, and it uses what VKS ships today: Kubernetes 1.36 with DRA, the NVIDIA GPU Operator in its new mode that brings the DRA driver along, and one RTX A5000 in passthrough. No licence server, no entitlement, nothing that waits in a queue. When vGPU arrives, it becomes the third row of the same table.

The setting is the same single-host lab as in parts 1 to 3: one EPYC host with ESX 9.1.1, a vSphere Supervisor, Private AI Services (PAIS) 3.0, no VMware Cloud Foundation (VCF) Automation. The post keeps the story and the numbers; every manifest and script is in the [companion repository](https://github.com/rmesterheide/vks-gpu-sharing) so that you can rebuild it from zero.

A disclosure, as always: I work at Broadcom as a solutions architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement.

{{< tldr >}}
- **VKS brings DRA with it, and the Kubernetes version is a field in a manifest.** The PAIS cluster runs 1.34; next to it, on the same Supervisor, a 1.36.4 cluster was available eight minutes after `kubectl apply`, with the `resource.k8s.io/v1` API on and containerd 2.3 with the Container Device Interface (CDI) enabled. Nothing to switch on. The catalogue offered every release from 1.33 to 1.36, with 1.37 already announced.
- **NVIDIA's operator-managed DRA driver works on vSphere.** GPU Operator 26.7.2 in `GPUCluster` mode built the 595 driver on the Ubuntu 24.04 node in three minutes and published the A5000 as a DRA device with its attributes (product name, architecture, compute capability, PCI address).
- **Two traps cost the evening, both VKS defaults worth knowing.** New namespaces enforce Pod Security `restricted`, which silently rejects every GPU Operator pod; and the node's root disk is too small for GPU images. One label and one volume override fix both.
- **The numbers:** one Gemma 4 12B instance alone delivers 202 tokens per second at four parallel requests; two instances on the same card with time-slicing get 96 each (192 together), with MPS 106 each (212 together, more than one instance alone). Time-slicing is free while the neighbour is idle and splits fairly under load; MPS caps a lone tenant at three quarters and pays it back when both are busy.
- **What it means for PAIS:** PAIS owns its GPU Operator and still uses the device plugin, so DRA is not a weekend job there. The sharing model that PAIS endpoints get today is one card per worker; this post shows what the next step looks like.
{{< /tldr >}}

## Why share a card at all

A 24 GB card runs a 12B model with room to spare, 8.7 GB in part 3. The rest of the card idles unless a second model moves in. In a platform that hands out "a model behind a service name", that is the normal case: several small models, few of them busy at the same time. Three answers exist, and they live on different layers:

- **vGPU** cuts the card on the hypervisor into profiles with fixed memory, each VM sees its own GPU. Isolation at the VM boundary, needs the NVIDIA host driver and a licence. That is part 4.
- **Time-slicing** on the Kubernetes layer lets several containers use the whole card in turns. No isolation, no memory limit, zero setup beyond a claim.
- **Multi-Process Service (MPS)** runs several CUDA processes concurrently on one card with a thread share and a pinned memory limit per client. More isolation than time-slicing, less than vGPU, and the card switches to exclusive process mode.

Until now the Kubernetes answers were configured on the node, in the device plugin's config, for everyone at once. DRA moves the decision into the workload's claim.

## What DRA changes

With the device plugin a pod asks for `nvidia.com/gpu: 1` and gets whatever the node has. With DRA a pod references a `ResourceClaimTemplate`, and the template says what kind of device, selected by attributes, and how it should be configured. The sharing strategy is part of that configuration:

```yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaimTemplate
metadata:
  name: shared-gpu
spec:
  spec:
    devices:
      requests:
      - name: gpu
        exactly:
          deviceClassName: gpu.nvidia.com
      config:
      - requests: ["gpu"]
        opaque:
          driver: gpu.nvidia.com
          parameters:
            apiVersion: resource.nvidia.com/v1beta1
            kind: GpuConfig
            sharing:
              strategy: TimeSlicing
```

Change `TimeSlicing` to `MPS` and add thread and memory limits, and the same two containers share the card the other way. The pod references the claim once and every container that should see the GPU names the same request. That is the whole API surface this post needs. The driver publishes what it has as a `ResourceSlice`; on the A5000 that is one device with product name, architecture Ampere, CUDA compute capability 8.6, the PCI address and the UUID, which is what a CEL selector can match on.

## The cluster: eight minutes, nothing to switch on

The part that deserves a sentence before the manifest: on this Supervisor the PAIS cluster keeps running on Kubernetes 1.34.9, and the new cluster came up on 1.36.4 next to it, from the same content library, with the same VM classes and storage. The cluster is a plain Cluster API object (`cluster.x-k8s.io`, a ClusterClass with variables for storage class, VM class, trusted CAs and node volumes), so everything a Cluster API user knows applies: the Kubernetes version is one field in the manifest, a worker pool is a machine deployment with its own VM class and rollout strategy, and the replacement of the GPU worker later in this post was a rolling update of that machine deployment, not a ticket. `kubectl get tkr` listed every release from 1.33.1 to 1.36.4 as ready and 1.37.1 as announced. That is the design that makes a detour like this one cheap: a team that needs the newest scheduler feature gets its own cluster on the newest release, the team next door stays on the version its platform was certified for, and nobody upgrades anybody. Kubernetes as a service, at the version you ask for.

The manifest is thirty lines: ClusterClass `builtin-generic-v3.7.0`, version `v1.36.4+vmware.2-vkr.3`, one control plane on a small VM class, one worker pool with the passthrough VM class from part 3, the storage class, pod and service ranges away from the home network, and the lab registry's root CA under `osConfiguration.trust` so that the nodes pull from Harbor. `kubectl apply`, eight minutes, `Available=True`. `kubectl api-resources` then lists `deviceclasses`, `resourceclaims`, `resourceclaimtemplates` and `resourceslices` in `resource.k8s.io/v1`; the nodes run containerd 2.3.4, where CDI is on by default, on Ubuntu 24.04.5 with a 7.0 kernel. Nothing on that list needed a flag.

## The operator: one Helm install, one `GPUCluster`

One Helm install of the GPU Operator 26.7.2 in its new `GPUCluster` mode: `clusterPolicy.deployCR=false`, `gpuCluster.deployCR=true`, the NVIDIADriver CRD on, the device plugin off, ComputeDomains off (that is for NVLink fabrics), and the two feature gates `TimeSlicingSettings` and `MPSSupport` for the sharing settings. The operator then does what it did in part 3 plus one thing: it builds the 595 driver on the node in about three minutes, starts the container toolkit and node feature discovery, and additionally runs the DRA kubelet plugin and a validator. The result shows up as three DeviceClasses, `gpu.nvidia.com`, `mig.nvidia.com` and `vfio.gpu.nvidia.com`, and one ResourceSlice. The first claim test was a plain CUDA pod that asked for one `gpu.nvidia.com` device and ran `nvidia-smi`: the A5000 with 24 GB, and `NVIDIA_VISIBLE_DEVICES=void` in its environment, which is how you can tell that the device arrived through CDI and not through the old environment variable path. Ten seconds from apply to output, image pull included.

## Two traps, both VKS defaults

**Pod Security.** Helm said "deployed". `kubectl get pods -n gpu-operator` stayed empty for seventeen minutes. VKS 1.36 enforces Pod Security Admission `restricted:latest` on new namespaces, and the GPU Operator needs privileged pods for the driver and the toolkit. The ReplicaSet controller logged the rejection in events, helm and kubectl did not. One label per namespace, `pod-security.kubernetes.io/enforce=privileged`, and a rollout restart so that the controllers do not wait out their backoff. PAIS sets exactly this label on its own operator namespace, which is why part 3 never met the problem. I read it as a good default with a loud silence: a cluster that is secure by default should tell you in `helm status` that nothing is running.

**Ephemeral storage.** The first llama.cpp pod was evicted while its image was still downloading: "The node was low on resource: ephemeral-storage". The default VKS node disk has room for the system images and not much more; driver and operator images had filled it. The fix is a `volumes` override on the worker in the Cluster manifest, a dedicated disk for `/var/lib/containerd`. PAIS does this for its nodes too. One re-apply, the worker VM was replaced, the model volume survived.

Both traps are the kind that the person rebuilding this on Monday morning hits at 9:30. They are in the repository as defaults now.

## The numbers

Same model as part 3, Gemma 4 12B QAT, same llama.cpp build and arguments, pulled from the lab's Harbor with oras in 36 seconds onto a volume both containers mount. The load goes straight to llama-server through a port-forward, not through the PAIS gateway, so the gateway's time to first token from part 3 is out of the picture (here it is 0.1 to 0.2 seconds everywhere). 400 tokens per answer, one request and four parallel requests per instance, and for the sharing rows the same load on both instances at the same time.

![One RTX A5000, Gemma 4 12B: tokens per second with four requests per instance](/images/sharing-one-gpu-on-the-kubernetes-layer/tokens-per-second.svg)

| Setup | 1 request tok/s | 4 parallel, per instance | 4 parallel, card total | Note |
|---|---|---|---|---|
| Part 3 baseline, device plugin, through the gateway | 70.9 | 242.7 | 242.7 | gateway path, from part 3 |
| DRA claim, one instance | 72.0 | 201.6 | 201.6 | control |
| Time-slicing, two instances, one busy | 72.2 | 202.9 | 202.9 | the idle neighbour costs nothing |
| Time-slicing, two instances, both busy | 29.8 + 29.8 | 96.0 + 96.0 | 192.0 | fair split, 5 percent lost |
| Time-slicing "Long" interval, both busy | 29.6 + 29.6 | 95.1 + 95.1 | 190.1 | no measurable difference |
| MPS 50/50, two instances, both busy | 36.1 + 36.1 | 106.1 + 106.1 | 212.2 | lone tenant capped at 55 / 139 |
| vGPU, two VMs with 12 GB each | | | | part 4 |

Four things the table says. **DRA itself costs nothing:** 72 tokens per second for one request through a claim, the same as through the device plugin in part 3. **Time-slicing is free until the neighbour wakes up:** with the second instance loaded but idle, the first one sees the whole card; once both are busy the card splits exactly in half and loses about five percent in total. With only one request per instance the context switches bite harder, 60 tokens per second together instead of 72 for one instance alone. **The time-slice interval did not matter** for this workload; "Long" and "Default" are within two percent. **MPS trades the lone tenant for the busy pair:** a instance alone gets about three quarters of the card because of the 50 percent thread share, but with both busy the card delivers more than one instance alone did, 212 against 202, and each tenant keeps 36 instead of 30 tokens per second on single requests. The MPS control daemon appeared with the claim and vanished with it; the card ran in exclusive process mode in between.

What the table does not show: memory. Both time-slicing tenants see all 24 GB and one can starve the other; the MPS pinned limit of 10 GiB each is a real cap, and vGPU would make it a wall. That is the row the next part adds.

## What it means for Private AI Services

PAIS 3.0 manages its own GPU Operator and talks to the device plugin; a ModelEndpoint asks for a whole GPU on a worker of its own. Switching that cluster to DRA is not a label away, it is a product decision, and until then one card means one endpoint. What this detour shows is the shape of the next step: the sharing policy travels with the workload, the platform decides per claim who shares with whom, and vGPU stays the answer when the boundary has to be a VM. The honest version: for a 24 GB card and 12B models, time-slicing on the Kubernetes layer already gives two tenants 95 percent of the card, and the price is isolation, not throughput.

## What I would do differently

- Put the containerd volume and the namespace label into the cluster template from the start; both are one line each.
- Read `kubectl get events -A` before reading `helm status`.
- Kill `kubectl port-forward` by name, not by the shell job: a stale forward cost me one full measurement round.

## What comes next

The vGPU row of the table, as soon as NVIDIA's portal lets the entitlement through. Same model, same prompts, two VKS workers with a 12 GB profile each, and then the question that part 4 was always about: what the version chain from host driver to GPU Operator to VKS to PAIS looks like when all of it has to line up.

Everything from this post, manifests, scripts and the raw numbers, is in [rmesterheide/vks-gpu-sharing](https://github.com/rmesterheide/vks-gpu-sharing).
