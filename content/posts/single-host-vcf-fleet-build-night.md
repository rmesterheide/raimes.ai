---
title: "One host, one evening: a single-host VCF 9.1.1 fleet in 5 hours 14 minutes"
date: 2026-11-12T06:59:17+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/single-host-vcf-fleet-build-night.jpg"
  alt: "One host, one evening: a single-host VCF 9.1.1 fleet in 5 hours 14 minutes"
  hiddenInSingle: true
categories: ["vmware"]
tags: ["homelab", "private-ai"]
summary: "On 11 November 2026 I swapped the CPU of my lab host, added an Optane memory tier and an enterprise NVMe drive, reinstalled ESX and deployed a VMware Cloud Foundation 9.1.1 fleet on the one host. The fleet deployment took 5 hours 13 minutes 40 seconds, with no failed task. This post has the parts list, the timeline, the traps and what the fleet uses on the host."
linkedin: ""
---

On the evening of 11 November 2026 my lab host got a new CPU, a memory tier and a new vSAN drive. The same evening I reinstalled ESX and started the VMware Cloud Foundation (VCF) 9.1.1 Installer. At 01:45 the next morning the fleet was complete: vCenter, NSX, VCF Operations, VCF Automation and SDDC Manager, all on one physical host. The fleet deployment took 5 hours 13 minutes 40 seconds. No task failed, and I did not have to restart anything.

A VCF fleet on one host is not a supported deployment. Broadcom asks for at least three hosts with vSAN, or two with Network File System (NFS) or Fibre Channel ([VCF Fleet Sizing Models](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/design/vmware-cloud-foundation-concepts/vcf-fleet-sizing-models-9-x.html)). One host works with a feature flag that William Lam documents for lab use in [VCF 9.1.1 - Single ESX Host for VCF Fleet, VCF Workload Domain or VCF Cluster](https://williamlam.com/2026/09/vcf-9-1-1-single-esx-host-for-vcf-fleet-vcf-workload-domain-or-vcf-cluster.html). I followed his steps and used his repository [vcf-91-in-box](https://github.com/lamw/vcf-91-in-box).

{{< tldr >}}
- **The host** is a self-built ATX tower with a Supermicro H12SSL-NT, an AMD EPYC 7713 with 64 cores, 512 GB of DDR4, an Optane P4800X as memory tier and a Samsung PM9A3 for vSAN Express Storage Architecture (ESA). The full parts list is below.
- **The fleet deployment** from the JSON specification took 5 hours 13 minutes 40 seconds. VCF Automation alone took 1 hour 31 minutes.
- **The fleet uses 76 virtual CPUs (vCPUs) and 251 GB of memory.** The host runs at about 20 percent CPU and 26 percent memory, with the memory tier counted in.
{{< /tldr >}}

## The host: a quiet ATX build

The host is not a rack server. It is a tower that I built myself in 2024 from standard ATX parts around a server board. In November 2026 three parts went in: the EPYC 7713, the Optane and the PM9A3. Everything else is from 2024.

| Part | Model | Role in the fleet |
|---|---|---|
| Mainboard | Supermicro H12SSL-NT (socket SP3, IPMI, 2 × 10 GbE Broadcom BCM57416, 2 × M.2) | host |
| CPU | AMD EPYC 7713, 64 cores, 128 threads, 225 W | new in 2026, replaced an EPYC 7513 with 32 cores |
| Memory | 8 × 64 GB Samsung RDIMM DDR4-2933 ECC, 512 GB on all eight channels | DRAM |
| Memory tier | Intel Optane DC P4800X 750 GB, PCIe card | NVMe memory tiering at 100 percent: 512 GB DRAM plus 512 GB tier |
| vSAN device | Samsung PM9A3 3.84 TB U.2, with power-loss protection | the single vSAN Express Storage Architecture (ESA) disk |
| U.2 adapter | Delock 90081, PCIe 4.0 x4 card for one U.2 drive | carries the PM9A3 |
| GPU | NVIDIA RTX A5000 24 GB | not used by the fleet yet; for Private AI Services later |
| Boot disk | Samsung 870 EVO 500 GB (SATA) | ESX boot and a local datastore for the Installer |
| Other disks | 2 × Samsung 990 PRO 4 TB (M.2), Samsung 870 QVO 4 TB (SATA) | ISOs, the offline depot, old lab VMs; not part of vSAN |
| CPU cooler | Noctua NH-U14S TR4-SP3 | air cooling |
| Power supply | be quiet! Straight Power 11, 750 W, 80 Plus Gold | |
| Case | be quiet! Pure Base 500 | ATX tower |

{{< figure src="/images/single-host-vcf-fleet-build-night/new-parts.jpg" alt="Three parts on a table before the swap: a Samsung PM9A3 3.84 TB U.2 SSD on its box, an AMD EPYC 7713 in its carrier frame, and an Intel Optane SSD DC P4800X card in a plastic tray. Serial numbers are blurred." caption="The three new parts before the swap. I bought the SSD and the Optane used on eBay. Only the CPU is new." >}}

Why a tower and not a used rack server: the host sits in my office. With the Noctua cooler and the be quiet! case and power supply, I can hardly hear it, even under load, and it has none of the fan noise of a server room. A reboot is also fast, because the board finishes its checks and ESX starts loading after a short time. Many rack servers spend minutes on hardware initialization before the operating system starts. With a single host, every reboot takes the whole lab down, so the reboot time counts.

The 2024 reasons for this board and CPU family are in the post [From Intel to AMD EPYC: one lab host, two years later](/posts/from-intel-to-amd-epyc-two-years-later/).

## The evening in times

| Time | Step |
|---|---|
| afternoon | old lab powered off, parts installed |
| 18:00 | ESX 9.1.1 boots with 64 cores and 512 GB, after two hardware problems (next section) |
| 18:35 to 18:45 | ESX reinstalled from a USB stick with a kickstart file |
| 19:15 | VCF Installer appliance running on the host |
| 19:30 | single-host flag and the vSAN ESA settings applied on the Installer |
| 19:40 to 20:30 | validation, about 64 GB of binaries copied from the offline depot into the Installer, second validation |
| 20:32 | fleet deployment started |
| 01:45 | fleet deployment complete |

From the first boot of the new CPU to the finished fleet it was less than eight hours. Most of that time I only watched.

## Three hardware problems on the way

**Half of the memory was missing.** At the first two boots the Intelligent Platform Management Interface (IPMI) log showed "Memory Device Disabled" for four DIMMs, E1 to H1. That is one half of the socket. The DIMMs were fine, but the CPU did not have even contact pressure. I took the cooler off, seated the CPU again and tightened the screws in the order printed on the socket. After that all eight DIMMs were back. I had the same problem when I built the host in 2024.

**The board stopped at POST code B4.** B4 stands for USB, and I had a USB stick and a keyboard plugged in. I unplugged all USB devices and switched the power off and on, and the board booted.

**The clock was wrong.** The host came up with the date 28 March 2025, the date of the BIOS build. The BIOS settings were still there and only the real-time clock was reset. I set the time in the BIOS, because VCF checks time sync and the time has to be right before the install. I will check the battery on the board next.

## ESX with a kickstart file

I installed ESX 9.1.1 from a USB stick with a kickstart file, based on the one in William Lam's repository. The kickstart sets the management virtual LAN (VLAN), the Network Time Protocol (NTP) and the root password. It also turns on the memory tier on the Optane with a ratio of 100 percent. After the first boot the host showed 1 TB of memory: 512 GB DRAM and 512 GB on the Optane.

```
# In the %firstboot section of the kickstart file. The device is the Optane (find it with "vdq -q").
esxcli memtier enable -d /vmfs/devices/disks/<optane-device> -r 100
```

Expected result: after the first boot, `esxcli memtier get` shows the Optane and the ratio, and the host reports about 1 TB of memory.

The commands for 9.1 are in William Lam's post [VCF 9.1 - Are You Using the Correct ESXCLI Command to Enable NVMe Tiering?](https://williamlam.com/2026/06/vcf-9-1-are-you-using-the-correct-esxcli-command-to-enable-nvme-tiering.html) and in the Broadcom documentation [Memory Tiering over NVMe](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/9-1/vsphere-resource-management/memory-tiering-over-nvme.html).

## Four problems with the Installer

The VCF Installer is the appliance that later becomes SDDC Manager. I deployed it onto the host and applied William Lam's single-host flag and the vSAN ESA disk claim settings, as in his post [VCF 9.1 - Comprehensive VCF Installer & SDDC Manager Configuration Workarounds for Lab Deployments](https://williamlam.com/2026/05/vcf-9-1-comprehensive-vcf-installer-sddc-manager-configuration-workarounds-for-lab-deployments.html). Four things then did not work as I expected.

1. **The depot URL.** The offline depot runs on my VCF Infrastructure Services (VIS) appliance under `vis.vcf.internal`. The Installer refused that address with `VMWARE_DEPOT_OFFLINE_INVALID_URL`. Its URL check does not accept the `.internal` top-level domain, but the IP address worked. (VIS is a Fling for labs and proofs of concept, not a supported way to run a depot or Harbor in production. The supported way for Harbor is the Harbor Supervisor Service.)
2. **The API starts later than the UI.** The login page answered after the Installer booted, but the API still returned HTTP 502 for about two more minutes. A script that waits for the UI and then calls the API fails, so wait for the API itself.
3. **The binaries.** The first validation failed only at "Versions and Bundles". The Installer has to copy the binaries from the depot into itself first. In the depot settings the version list starts on 9.1.0.0. I had to switch it to 9.1.1.0, select every component and start the download. That was about 64 GB from the depot. Broadcom describes this step in [Downloading Binaries to VCF Installer](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/deployment/deploying-a-new-vmware-cloud-foundation-or-vmware-vsphere-foundation-private-cloud-/preparing-your-environment/downloading-binaries-to-the-vcf-installer-appliance.html).
4. **One validation at a time.** I started a validation over the API and then another one in the UI. The UI had to wait until the API run finished.

The validation then showed three warnings, which I acknowledged: the hardware compatibility list for vSAN, an NTP check, and the capacity check. The capacity check counts 76 vCPUs against 64 cores. That is fine in a lab, because the appliances do not use all their vCPUs at once.

## The fleet deployment

I started the deployment at 20:32 with the JSON specification, based on William Lam's `one-node-vsan-esa-tep.json` with my names, networks and passwords. The upload path is in the Broadcom documentation: [Use a JSON Specification File to Deploy VMware Cloud Foundation or vSphere Foundation](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/deployment/deploying-a-new-vmware-cloud-foundation-or-vmware-vsphere-foundation-private-cloud-/use-a-json-specification-to-deploy-vmware-cloud-foundation-or-vmware-vsphere-foundation.html). It deploys one vCenter, one NSX Manager, VCF Operations with its collector, the VCF management services, VCF Automation, and then turns the Installer into SDDC Manager. The times per step come from the Installer API:

| Step | Duration |
|---|---|
| Deploy vCenter | 15 min 53 s |
| Configure vSphere cluster | 10 min 12 s |
| Deploy and configure NSX | 23 min 16 s |
| Deploy and configure VCF Management Platform | 1 h 18 min 45 s |
| Deploy and configure the operations appliance | 43 min 8 s |
| Deploy and configure VCF Management Services | 51 min 14 s |
| Deploy and configure VCF Automation | 1 h 31 min 11 s |
| Configure the appliance as SDDC Manager | under 1 s |
| **Total** | **5 h 13 min 40 s** |

vCenter, the cluster with vSAN and NSX were ready after 49 minutes. The other four hours went to the management platform, VCF Operations and VCF Automation. Those run on a Kubernetes-based platform, and all their services need time to start.

{{< figure src="/images/single-host-vcf-fleet-build-night/installer-done.jpg" alt="VCF Installer progress page with the message 'Congratulations! Your deployment completed successfully!' and five completed milestones from NSX to VCF Automation with their durations." caption="The Installer the next morning. The milestones from NSX to VCF Automation, all completed." >}}

## What the fleet uses on one host

The next morning eleven VMs ran on the host. The table shows what each one has, read from the host:

| VM | Component | vCPU | Memory |
|---|---|---|---|
| m01-vc01 | vCenter | 4 | 21 GB |
| nsx01a | NSX Manager | 6 | 24 GB |
| sddcm01 | SDDC Manager (was the Installer) | 4 | 16 GB |
| ops01 | VCF Operations | 4 | 16 GB |
| ops-proxy01 | VCF Operations collector | 4 | 16 GB |
| lic01 | license server | 2 | 4 GB |
| msr01 (3 VMs) | VCF management platform | 28 | 58 GB |
| asr01 | VCF Automation | 24 | 96 GB |
| **Fleet total** | | **76** | **251 GB** |
| vis | VIS appliance (depot and Harbor), not part of the fleet | 2 | 4 GB |

This matches the Broadcom sizing for a simple fleet with VCF Automation: about 70 vCPUs and 250 GB of memory. On my host it means about 20 percent CPU usage and 26 percent of the memory, with the 512 GB tier counted in. vSAN uses about 1.2 TB of the 3.6 TB PM9A3. So the fleet fits on this host with DRAM alone. The memory tier leaves space for what comes next.

## What comes next

- **Virtual GPU (vGPU) for the A5000.** The NVIDIA host driver was gone with the reinstall. The cluster is now managed with a vSphere Lifecycle Manager image, so the driver goes into the image and not only onto the host.
- **Supervisor and vSphere Kubernetes Service (VKS)** with Virtual Private Cloud (VPC) networking. Without NSX Edges, the VPC needs an NSX Virtual Network Appliance for load balancing and Network Address Translation (NAT). William Lam describes the steps in [VCF 9.1 - Quick Tip: Optimized Workflow for Configuring Distributed Transit Gateway (DTGW) with NSX Virtual Network Appliance (VNA)](https://williamlam.com/2026/08/vcf-9-1-quick-tip-optimized-workflow-for-configuring-distributed-transit-gateway-dtgw-with-nsx-virtual-network-appliance-vna.html).
- **Private AI Services 3.0 activated from VCF Automation**, with a virtual GPU. This is the part that my earlier plain vSphere lab could not show.

## Thank you, William

This lab follows William Lam's work throughout: the single-host flag, the kickstart file, the JSON specification and the Installer workarounds all come from his repository and his posts. Without them I would not have tried a VCF fleet on one host. Thank you, William.

## Sources

- Broadcom: [Use a JSON Specification File to Deploy VMware Cloud Foundation or vSphere Foundation](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/deployment/deploying-a-new-vmware-cloud-foundation-or-vmware-vsphere-foundation-private-cloud-/use-a-json-specification-to-deploy-vmware-cloud-foundation-or-vmware-vsphere-foundation.html), [Downloading Binaries to VCF Installer](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/deployment/deploying-a-new-vmware-cloud-foundation-or-vmware-vsphere-foundation-private-cloud-/preparing-your-environment/downloading-binaries-to-the-vcf-installer-appliance.html), [VCF Fleet Sizing Models](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/design/vmware-cloud-foundation-concepts/vcf-fleet-sizing-models-9-x.html), [Memory Tiering over NVMe](https://techdocs.broadcom.com/us/en/vmware-cis/vsphere/vsphere/9-1/vsphere-resource-management/memory-tiering-over-nvme.html).
- William Lam: [vcf-91-in-box](https://github.com/lamw/vcf-91-in-box), [VCF 9.1.1 - Single ESX Host for VCF Fleet, VCF Workload Domain or VCF Cluster](https://williamlam.com/2026/09/vcf-9-1-1-single-esx-host-for-vcf-fleet-vcf-workload-domain-or-vcf-cluster.html), [Clarifying Minimum Required ESX Hosts for VCF Deployments](https://williamlam.com/2026/06/clarifying-minimum-required-esx-hosts-for-vcf-deployments.html), [VCF 9.1 - Comprehensive VCF Installer & SDDC Manager Configuration Workarounds for Lab Deployments](https://williamlam.com/2026/05/vcf-9-1-comprehensive-vcf-installer-sddc-manager-configuration-workarounds-for-lab-deployments.html), [VCF 9.1 - Comprehensive ESX Configuration Workarounds for Lab Deployments](https://williamlam.com/2026/05/vcf-9-1-comprehensive-esx-configuration-workarounds-for-lab-deployments.html), [VCF 9.1 - Are You Using the Correct ESXCLI Command to Enable NVMe Tiering?](https://williamlam.com/2026/06/vcf-9-1-are-you-using-the-correct-esxcli-command-to-enable-nvme-tiering.html), [VCF 9.1 - Quick Tip: Optimized Workflow for Configuring Distributed Transit Gateway (DTGW) with NSX Virtual Network Appliance (VNA)](https://williamlam.com/2026/08/vcf-9-1-quick-tip-optimized-workflow-for-configuring-distributed-transit-gateway-dtgw-with-nsx-virtual-network-appliance-vna.html).
