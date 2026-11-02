---
title: "Route to Private AI Services 3.0, part 4a: one evening to vGPU, three checks first"
date: 2026-11-01T12:00:00+01:00
draft: true
written_with_claude: true
cover:
  image: "/images/covers/one-evening-to-vgpu-three-checks-first.jpg"
  alt: "Route to Private AI Services 3.0, part 4a: one evening to vGPU, three checks first"
categories: ["vmware"]
tags: ["private-ai", "homelab", "gpu", "vgpu"]
summary: "Part 4 of my route to Private AI Services 3.0 comes in three pieces, published together. This first piece is the route from a passthrough card to NVIDIA vGPU slices on one host in one evening: the licence side, the version chain, and three checks that would have saved me two hours. For each step I note the log line I used to check it, and a VCF Operations instance next to the vCenter shows the result without extra setup. Part 4b has the numbers for one to three endpoints, part 4c pushes the card to six."
---

[Part 3](/posts/rtx-a5000-behind-the-same-service-name/) ended with 15 GB of the RTX A5000 sitting idle because passthrough gives the whole card to one VM. While NVIDIA sorted out my licence entitlement, I took an unplanned [detour on the Kubernetes layer](/posts/sharing-one-gpu-on-the-kubernetes-layer/): Dynamic Resource Allocation (DRA) on a vSphere Kubernetes Service (VKS) cluster, two model instances sharing the card with time-slicing and MPS, no licence and no host driver involved. That detour gave me numbers to compare against, and it raised the question: what does vGPU add on top? Part 4 answers it, in three pieces published together:

- **4a, this piece:** the route from passthrough to vGPU slices on one host, and the three checks I would do first.
- **[4b, the numbers](/posts/one-card-three-endpoints-the-numbers/):** one endpoint, two endpoints, three endpoints on one card, with the curves from the host.
- **[4c, six endpoints on one card](/posts/six-endpoints-on-one-card/):** six 4 GB slices, the two limits I hit on the way (the host's vGPU mode and the licence pool), and two more checks for the list.

NVIDIA vGPU splits the card into slices, each slice goes into its own VKS worker, and Private AI Services (PAIS) 3.0 runs a model endpoint per slice. In the vSphere community this is seen as the Königsdisziplin, the supreme discipline: NVIDIA, Broadcom, Kubernetes and the model engine all have to fit together before the first slice works. In my lab that took one evening on one host. This piece describes the route and names three things I would check before starting, because they would have saved me two hours.

The setting is the same as in parts 1 to 3: one EPYC host with ESX 9.1.1, a vSphere Supervisor, and PAIS 3.0 activated from vCenter. PAIS 3.0 is fully supported on a plain vSphere and vCenter basis, and that is what I rebuild here. I would like to use the multi-tenancy and the NSX-based Virtual Private Cloud (VPC) features of VMware Cloud Foundation (VCF) as well, but this is a small lab. The card is a refurbished RTX A5000 with 24 GB, which NVIDIA's support matrix lists for vGPU on VCF 9.1.

A disclosure, as always: I work at Broadcom as a solutions architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement. The NVIDIA software runs on a 90-day NVIDIA AI Enterprise evaluation that I requested as a private person for this lab.

{{< rebuild repo="rmesterheide/pais-vgpu" >}}the host scripts (install, Shared Direct, scheduler, watch), the licence and endpoint manifests, the settings of the Display Mode Selector VM, and the benchmark tools and raw results of parts 4b and 4c.{{< /rebuild >}}

{{< tldr >}}
- **vGPU on a single host is five pieces that must agree:** a licence token from NVIDIA's cloud licence service, the host driver on ESX, a VM class with a vGPU profile, the guest driver that PAIS pulls from NVIDIA's registry with your own key, and the GPU scheduler on the host. Once they fit, a new endpoint is nine minutes from `kubectl apply` to a licensed, answering model.
- **PAIS runs the Kubernetes cluster itself.** It created a VKS cluster at activation and lifecycles it. Every ModelEndpoint is a node pool in that cluster, sized by its VM class. I do not write a cluster manifest, a node pool or a driver install.
- **Check 1, the card's mode.** Workstation cards like the RTX A5000 ship in display mode and run vGPU in display-off mode. Switch it once with NVIDIA's Display Mode Selector, then the host driver installs without problems. The support matrix says so in a footnote.
- **Check 2, the BIOS.** Ampere cards do vGPU over Single Root I/O Virtualization (SR-IOV) on vSphere, so SR-IOV and Alternative Routing-ID Interpretation (ARI) belong on the BIOS checklist next to Above 4G Decoding. One line in `vmkwarning.log` at boot confirms the virtual functions are there.
- **Check 3, the clock.** Create the endpoint once the host is ready: a VKS worker that boots more than 15 minutes after it was created has an expired bootstrap token. If it happens, one annotation and one delete replace the node in five minutes.
- **The platform team sees it without extra work.** A VCF Operations instance next to the vCenter shows the card, the slices and which VM holds which profile, through the vCenter adapter.
{{< /tldr >}}

## What NVIDIA needs before the first slice starts

vGPU is licensed software. Nothing on the card or in vSphere changes that: without a licence the guest driver throttles after a grace period, so the licence side comes first. For the lab I requested the 90-day evaluation of NVIDIA AI Enterprise. The request itself was a web form and was approved within hours. Getting the entitlement to show up in NVIDIA's portals took two days and a support case; the backend fault was on NVIDIA's side and they fixed it overnight. This is the one step you cannot automate, so start it a week before you need it.

Once the entitlement was visible, the portal part took twenty minutes and has four results you need later:

1. **A licence allocation on the Cloud License Service (CLS).** In the licensing portal a "license allocation" (the portal says "License Servers are now License Allocations") gets some of your licences and is deployed to CLS. No appliance to run; the guests talk to `api.cls.licensing.nvidia.com` directly. The alternative is a Delegated License Service appliance in the lab, which I did not need.
2. **A client configuration token.** One button on the allocation. It is a file; it goes into the guest driver's licence folder, and every VM with that file leases a licence from your allocation for 24 hours at a time.
3. **An NVIDIA NGC API key.** PAIS pulls the vGPU guest driver image from NVIDIA's registry, `nvcr.io/nvaie`, which needs your personal key. Note: the NGC left navigation offers "Service Keys" first, which are organisation automation keys; the personal key you want lives under the account settings.
4. **The host package.** The download page lists NVIDIA AI Enterprise releases, not vGPU releases. I took "NVIDIA AI Enterprise 7.8 for VMware vSphere 9.0", which contains vGPU Manager 580.178.05 for the host and a 580.178.04 guest driver.

Why 7.8 and not the newest 8.x? PAIS 3.0 pins the guest driver it installs through the GPU Operator to 580.105. NVIDIA's rule is that host and guest must be on the same major branch, so a 580 host driver is the safe choice, and 7.8 is the long-term branch of that family. The 8.x releases are a 595 host driver and would have meant overriding the driver image that PAIS ships. That is an experiment for later, not for the first run.

## The version chain, written down once

This is the chain. Each vendor documents its own part of it:

| Layer | What | Who picks it |
|---|---|---|
| ESX host | vGPU Manager 580.178.05 (NVIDIA AI Enterprise 7.8), two vSphere Installation Bundles (VIBs): the driver and the GPU management daemon | you, from the licensing portal |
| GPU mode | card in display-off mode, host graphics type Shared Direct, vGPU mode Mixed Size | you, on the host |
| VM class | vCPU, memory fully reserved, one PCI device of type "NVIDIA GRID vGPU" with profile `nvidia_rtxa5000-12c` | you, in vCenter |
| VKS node | Ubuntu node image, GPU Operator 25.10.1 | PAIS |
| Guest driver | `nvidia-vgpu-driver-ubuntu24.04`, driver 580.105.08 from `nvcr.io/nvaie`, pulled with your NGC key | PAIS, driver type `NVAIE` |
| Licence | `nvidia-gridd` in the driver pod, token from a ConfigMap, lease from CLS | you provide the token, PAIS mounts it |

On the PAIS side the whole thing is three objects in the Supervisor namespace: a ConfigMap with the token, a Secret with the NGC key, and five fields on the `PAISConfiguration`:

```json
{"gpuDriverType": "NVAIE",
 "gpuOperatorVersion": "25.10.1",
 "driver": {"version": "580.105.8"},
 "licenseConfigRef": {"name": "nvaie-license"},
 "imagePullSecretRef": {"name": "ngc-pull"}}
```

Part 3 switched the platform from CPU only to GPU with one patch of this block; this is the same patch with the driver type changed from `OSS` to `NVAIE` and the two references added. The GPU Operator reported ready within a minute. The VKS control plane rolled once, which it does on every change to the node configuration, and the platform was back after about fifteen minutes.

## Check 1: a workstation card needs one firmware switch first

The host install is one command per VIB from a datastore path, in maintenance mode, followed by a reboot. The first attempt ended like this:

```text
#PF Exception 14 in world 2327861:nvidia-smi IP 0x42001bb4987d addr 0x50
Module(s) involved in panic: [nvidia 580.178.05 (External)]
... rm_init_adapter@(nvidia) ... nvidia_open@(nvidia)
```

The VIB's post-install script loads the module live and calls `nvidia-smi`. The first thing the driver does with the card is `rm_init_adapter`, and that is where it dereferenced a null pointer. I assumed a stale passthrough state (the card had been a passthrough device minutes earlier), rebooted cleanly and tried again. The stack and the offset were the same. The kernel log, pulled out of the dump with `esxcfg-dumppart -L`, had no complaint from the driver before the fault: the module loaded, attached the device, set the scheduler, and crashed 0.4 seconds later.

The reason is in NVIDIA's support matrix for vSphere. The RTX A5000 is listed for VCF 9.1 with footnote 7: supported only in displayless mode. The quick-start guide has a table of cards that ship in display-enabled mode and must be switched with the Display Mode Selector tool before vGPU: the RTX A5000, A5500, A6000 and the RTX 5000 and 6000 Ada. Data-centre cards like the A40 and L40 ship display-off and do not need this step. My card is an HP workstation board, so it was in display mode, and the vGPU host driver does not support that. Others on the NVIDIA forum report a cleaner failure, a VM that refuses to start, with the same cause; on ESX 9.1.1 with the 580.178 driver it is a purple screen.

The tool is a download behind an approval form on the developer site (approved immediately in my case) and it does not run on ESX. The documented way is a Linux VM with the card in passthrough, so I built a throw-away VM on the host: EFI, Secure Boot off, 8 GB reserved, the card and a second ISO with the tool attached, booted from an Ubuntu 24.04 desktop ISO. Two things to know before you do the same:

- Boot the live system with `modprobe.blacklist=nouveau` on the kernel line. With the open-source driver bound to the card, unbinding it hangs the session, and `nomodeset` leaves the VM's screen black.
- The VM needs PCIe root ports (`pciBridge4` to `pciBridge7` with `pcieRootPort` in the VMX) or the power-on fails with "No PCIe slot available".

Then it is two commands:

```text
# displaymodeselector --listgpumodes
GPU Mode: Graphics
# displaymodeselector --gpumode compute
Successfully updated GPU mode to "physical_display_disabled" ( Mode 4 ).
A reboot is required for the update to take effect.
```

Version 1.77 of the tool calls the modes `graphics` and `compute`; older guides say `physical_display_disabled`, which is the same thing and reversible. After a host reboot the card's HDMI audio function was gone from the PCI bus, BAR1 had grown from 256 MB to 32 GB, and the third install of the same two VIBs went through without an error. The host then showed the card as `SharedPassthru`, I switched it to `MixedSize`, and `nvidia-smi vgpu -s` listed all 24 profiles from 1B to 24C.

For a platform team this means: the compatibility list says the card works, the footnote says under which condition. A workstation card from the vGPU list works once it is in the right mode. The mode is a firmware setting, changed once, with a tool you request on the same day as the licence.

## Check 2: SR-IOV belongs on the BIOS checklist

With the host driver up I created three VM classes in vCenter, 12 GB, 8 GB and 4 GB slices (the "Device Selection" dialog lists the profiles as `nvidia_rtxa5000-12c` and so on, with access type "NVIDIA GRID vGPU"), assigned them to the namespace and applied the first ModelEndpoint with the 12 GB class. The worker VM was created and did not power on:

```text
vmiop_log: (0x0): Initialization: Failed to alloc kernel host vgpu device handle error 1
[msg.vmx.plugin.vmiop.vgpu.failed] Could not initialize plugin 'libnvidia-vgx.so' for vGPU 'nvidia_rtxa5000-12c'.
```

The VM operator retried every two minutes and the VM folder filled with log files. The explanation was on the host: `nvidia-smi -q` said `Host VGPU Mode: SR-IOV`, and `vmkwarning.log` had said at every boot since the driver install:

```text
PCI: 1645: Enable VFs failed for device @0000:c1:00.0, Please make sure the system has proper BIOS installed and enabled for SR-IOV
```

Ampere cards do vGPU on vSphere through SR-IOV virtual functions, one per slice, and the board's BIOS still had SR-IOV disabled. Passthrough never needed it, which is why five weeks of passthrough and a DRA experiment did not show it. The fix is one change in the BIOS (Advanced, PCIe/PCI/PnP Configuration, SR-IOV Support from Disabled to Enabled; I also set PCIe ARI Support (Alternative Routing-ID Interpretation) from Auto to Enabled because the card creates up to 24 functions), and a boot. Afterwards the host listed 25 PCI functions on the card's bus, the physical function and 24 virtual ones, and the next power-on of the same VM worked: `vGPU manager is running in SRIOV mode`, `display_init successful`.

## One YAML object, and PAIS runs the rest

Check 3 only makes sense with one thing about PAIS in view. When I activated PAIS in the Supervisor namespace, it created a VKS cluster of its own, `pais-30695622` in my lab. I never wrote a cluster manifest for it, and I do not upgrade or scale it. PAIS does. Every ModelEndpoint I apply becomes a node pool in that cluster: one MachineDeployment with one replica, and the VM class of the endpoint is the node size. Cluster API asks the Supervisor for a VM of that class, vCenter places it on a host with a free vGPU slot, the VM boots the node image and joins the cluster with a kubeadm token. On the node, the GPU Operator installs the guest driver and gets the licence, the engine pod pulls the model from Harbor, and the gateway routes the model name to that pod. Delete the endpoint and the node pool goes with it. The VM is gone within a minute.

The three checks of this post sit at fixed places in that chain: Check 1 and Check 2 on the host, before any VM boots; Check 3 at the join.

{{< figure src="/images/one-evening-to-vgpu-three-checks-first/pais-modelendpoint-flow.svg" alt="Diagram in three lanes: the Supervisor namespace with ModelEndpoint, PAIS operator and MachineDeployment; vCenter and the ESX host with VirtualMachine, placement and power-on; the VKS cluster run by PAIS with node join, engine pod and Ready=True. Nine numbered steps, the three checks marked at steps 6 and 7." caption="From one ModelEndpoint to a running model. Lane one is what I apply, lanes two and three are what PAIS, Cluster API and vCenter do with it. The three checks of this post sit at steps 6 and 7." >}}

## Check 3: create the endpoint when the host is ready

The VM that had waited through the BIOS change powered on, got an address, ran cloud-init, and never appeared as a Kubernetes node. Twelve minutes later the kubelet port was still silent and the ModelEndpoint said:

```text
NodeHealthy: Waiting for a Node with spec.providerID vsphere://... to exist
```

The Machine had been created at 20:36 and booted at 21:08. Its kubeadm bootstrap token had been generated with the Machine and is valid for 15 minutes; cloud-init runs once; the join failed without an error and nothing retries it. The fix is to replace the Machine, and VKS protects that step with a webhook:

```bash
kubectl -n pais delete machine <name>
# Error from server (Forbidden): ... Machine deletion is only allowed when the
# 'cluster.x-k8s.io/remediate-machine' annotation is present
kubectl -n pais annotate machine <name> cluster.x-k8s.io/remediate-machine=""
kubectl -n pais delete machine <name>
```

The MachineDeployment created a new VM within a minute, the new node joined after five, and the rest of the chain ran on its own: the GPU Operator's `nvidia-vgpu-driver-ubuntu24.04` pod came from `nvcr.io/nvaie` with my key, the CUDA validator completed, and the licence daemon wrote the two lines that confirm the licence:

```text
nvidia-gridd: Acquiring license. (Info: api.cls.licensing.nvidia.com; NVIDIA Virtual Compute Server)
nvidia-gridd: License acquired successfully. (Info: api.cls.licensing.nvidia.com, NVIDIA Virtual Compute Server; Expiry: ...)
```

Five seconds from request to lease. Inside the pod, `nvidia-smi` showed `NVIDIA RTXA5000-12C`, 12,288 MiB, driver 580.105.08 next to the host's 580.178.05, and no complaint about the mismatch within the branch. The endpoint went Ready at 21:39, and the second one on the second 12 GB slice took nine minutes from apply to a licensed, answering model with nothing cached on the new node.

## What the platform team sees

All of the above is host and `kubectl` work. The platform team does not read `nvidia-smi` on the host, it reads a dashboard, so the next morning I put VMware Cloud Foundation (VCF) Operations 9.1.1 next to the standalone vCenter. Deploying it is routine for anyone who has run vSphere: one OVA, the vCenter as an account, done. The point here is what it shows about the shared card without a management pack and without anything installed in the guests. The vCenter adapter delivers a GPU metric group per host (compute utilisation, power, temperature, memory held) and a vGPU group per VM (the compute and memory utilisation of its own slice), and the 9.1.1 appliance ships four Private AI dashboards: GPU Overview, GPU Consumers, GPU Equipped Clusters, GPU Providers.

{{< figure src="/images/one-evening-to-vgpu-three-checks-first/gpu-heatmaps.jpg" alt="VCF Operations dashboard GPU Overview: three heat maps for the one RTX A5000, temperature in orange at the 70 degree band, memory usage and compute utilisation in green" caption="GPU Overview in VCF Operations, the heat-map row: temperature, memory usage and compute utilisation of the one card, with the colour bands below each map. One card is one tile; a GPU cluster fills the row." >}}

The GPU Consumers dashboard is the one I would show an endpoint: it lists the VM classes from Check 2 as `nvidia_rtxa5000-12c` and `nvidia_rtxa5000-4c` per VM, and it is the first place where a slice is visible without `kubectl`. Part 4b has the curves from the same instance under load.

## The checklist I would hand to a platform team

- **Read the footnotes of the support matrix** for your card, and request the Display Mode Selector on the same day as the licence if it is a workstation model. Switching the mode is a ten-minute job once the tool is there.
- **Check the BIOS for SR-IOV, ARI and Above 4G Decoding before the driver install**, and grep `vmkwarning.log` for `Enable VFs` right after the first boot with the driver. The first VM then starts without the error from Check 2.
- **Create the first ModelEndpoint once the host shows the profiles** in `nvidia-smi vgpu -c`. Then the bootstrap token is fresh when the VM boots and the node joins within five minutes.
- **Keep the host scripts on a datastore.** `/tmp` on ESX is wiped on every reboot.
- **Renew the Broadcom registry token the same day.** Every new VKS node pulls the PAIS bundle, and with a fresh token the first endpoint starts without a delay.

## What comes next

With the chain in place, the card ran a chat endpoint on a 12 GB slice, then two chat endpoints, then a chat endpoint next to an embedding endpoint. [Part 4b](/posts/one-card-three-endpoints-the-numbers/) has the tokens per second for each of these, the sizing rule that came out of the one run that did not work, and the same evening as curves in VCF Operations. [Part 4c](/posts/six-endpoints-on-one-card/) takes the same card to six slices and adds two checks to the three above. The scripts and manifests are in the repository, and the checklist is above.
