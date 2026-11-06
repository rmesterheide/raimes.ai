---
title: "Route to Private AI Services 3.0, the bare minimum: 15 steps on one host to a model endpoint"
date: 2026-11-06T08:39:58+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/private-ai-services-on-one-host-in-15-steps.jpg"
  alt: "Route to Private AI Services 3.0, the bare minimum: 15 steps on one host to a model endpoint"
  hiddenInSingle: true
categories: ["vmware"]
tags: ["private-ai", "homelab"]
summary: "Parts 1 to 4 of this series describe the route to Private AI Services 3.0 in the order I built it, with every detour. This page is the overview of the bare minimum, the smallest configuration that provides models and model endpoints: one diagram with the 15 configuration steps from a fresh ESX host to a local model behind a service name, all on a single host. For each step it says where it happens and which part has the details, plus the two steps that make you wait."
linkedin: ""
---

Parts 1 to 4 of this series describe the route to Private AI Services (PAIS) 3.0 in the order I built it. They include the detours and the things I got wrong first, so they are long. What they do not have is a short version: which steps are there, and where does each one happen?

This page is that overview. It has one diagram with 15 configuration steps. The first step is a fresh ESX host, and after the last one a local model answers behind a service name. Each step links to the part that has the commands and the screenshots.

**About the setting:** this is the bare minimum. It is the smallest configuration I know that provides models and model endpoints to application teams: one host, vCenter, a distributed switch, the built-in load balancer and PAIS in "Model Runtime only" mode. PAIS 3.0 is fully supported on a plain vSphere and vCenter basis, and that is what the lab rebuilds. This setup suits a proof of concept, and environments where NSX and VMware Cloud Foundation (VCF) Automation cannot be used.

It is not how I would design it for a given customer with many teams. A full VCF deployment with VCF Automation and NSX-based Virtual Private Clouds (VPC) adds a lot of value on top of this:

- **Multi-tenancy:** teams share one platform without seeing each other.
- **Self-service:** a catalogue and a portal, instead of an administrator in vCenter.
- **Governance:** quotas, policies and access rules per tenant.
- **Network isolation:** a VPC per tenant, instead of shared VLANs.

I would like to use all of that, but this is a small lab with one server and one user. [Part 2](/posts/private-ai-services-without-a-gpu/) has the longer list. The server gets a 64-core CPU and a memory tier next, and after that I plan to build the full VCF setup on the same host.

**About the licence:** "plain vSphere and vCenter" describes how the lab is built, not how it is licensed. For licence questions, please use the [official Broadcom documentation](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/requirements-for-deploying-private-ai-foundation-with-nvidia.html).

A disclosure, as always: I work at Broadcom as a solutions architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement.

{{< rebuild repo="rmesterheide/pais-route" >}}the scripts and manifests for these steps, in the folders `part1-supervisor`, `part2-gateway` and `part3-gpu`. The three folders match the three columns of the diagram.{{< /rebuild >}}

{{< tldr >}}
- This is the **bare minimum** for models and model endpoints, and it runs on **one ESX host**: vCenter, the Supervisor, PAIS, the registry, the Kubernetes cluster that PAIS creates, and every model.
- It is **15 steps in three groups**: the platform (steps 1 to 4), PAIS with remote models (steps 5 to 9), and local models (steps 10 to 15).
- After step 15 **remote and local models are available on one AI gateway**, behind service names.
- You can **stop after step 9**. At that point application teams already get a base URL, a token and a service name, and the platform needs no GPU and no registry of its own.
- **Steps 1 to 7 are done in vCenter**, once. What repeats for every new model is one push and two `kubectl apply` commands.
- **Two steps make you wait.** Changing the registry credentials or the certificate bundle replaces the control plane of the PAIS cluster. Plan 10 to 15 minutes each time.
{{< /tldr >}}

## One host

Everything in the diagram runs on this machine:

| Part | What is in the lab |
|---|---|
| Mainboard | Supermicro H12SSL-NT, one socket |
| CPU | AMD EPYC 7513, 32 cores |
| Memory | 512 GB |
| Storage | two 4 TB NVMe drives as local datastores |
| Network | two 10 GbE ports on the board |
| GPU | one refurbished RTX A5000 with 24 GB, needed from step 13 |

A single host means no high availability and no vMotion, which I accept for a lab. The configuration steps are the same on a cluster with more hosts. On a single host the Supervisor runs with one control plane VM and the load balancer with one VM.

512 GB of memory is more than this setup needs. The platform up to step 9 uses a small part of it. Local models on CPU are what take memory, because each model endpoint gets its own worker VM.

## The 15 steps

![Diagram with a band for the single ESX host on top and three columns below it: platform with steps 1 to 4, Private AI Services with steps 5 to 9, local models with steps 10 to 15. Each step names where it is done, and each column ends with what answers at that point. Step 13 is the GPU in passthrough, with a note that vGPU is the alternative and is described in part 4a. A band at the bottom shows the AI gateway of PAIS with its OpenAI-compatible URL, which remote and local models both use.](/images/private-ai-services-on-one-host-in-15-steps/pais-setup-flow.svg)
*The setup as I built it in October 2026. The coloured line in each box says where the step happens.*

### Platform: steps 1 to 4

All details are in [part 1](/posts/kubernetes-api-on-vsphere-in-one-evening/).

1. **vSphere 9.1.1.** Install ESX and vCenter. Create a cluster with Distributed Resource Scheduler (DRS) and high availability (HA) switched on, a vSphere Distributed Switch (VDS) with three port groups for management, workload and load balancer frontend, and a storage policy based on a datastore tag.
2. **Supervisor.** The wizard in vCenter activates the Kubernetes control plane. I chose VDS networking with the built-in Foundation Load Balancer (FLB), so no other load balancer is needed.
3. **Content library.** A subscribed library with the Kubernetes releases, assigned to the vSphere Kubernetes Service (VKS) of the Supervisor. PAIS needs it later to build its own cluster.
4. **Namespace.** One Supervisor namespace for PAIS with the workload network, the storage policy and the VM classes.

After step 4 the Kubernetes API answers on its own name. Before step 1 you need forward and reverse DNS records, a time server and three VLANs. Part 1 lists them.

### Private AI Services: steps 5 to 9

All details are in [part 2](/posts/private-ai-services-without-a-gpu/).

5. **Registry credentials.** The PAIS images come from a Broadcom registry that needs a token from the support portal. The token is added in vCenter as a container registry on the Supervisor.
6. **PAIS Supervisor Service.** Upload `pais-3.0.0-external.yml` in vCenter to register the service, then install it on the Supervisor.
7. **Activate in the namespace.** A wizard in vCenter. I chose "Model Runtime only", CPU only and a local user. PAIS then creates a small VKS cluster and runs it itself. I never write a cluster manifest.
8. **API tokens and DNS name.** One `kubectl patch` switches on API tokens, one annotation sets the name of the service, and one DNS record points to it. After a fresh login the PAIS UI offers "Generate API Token".
9. **First route.** An `InferenceGatewayRoute` maps a service name to a remote model. The provider key sits in a Kubernetes Secret in the namespace.

After step 9 a model answers through the gateway, and this is the first place to stop. An application team gets a base URL, a token and a service name. The platform has no GPU and no registry of its own at this point.

### Local models: steps 10 to 15

The details are in [part 3](/posts/rtx-a5000-behind-the-same-service-name/).

10. **Harbor registry.** PAIS pulls local models from a registry as Open Container Initiative (OCI) artifacts. I use the Harbor registry inside the VCF Infrastructure Services (VIS) appliance. VIS is a community Fling for labs and proofs of concept, not a supported way to run Harbor in production. For production, Broadcom documents the [Harbor Supervisor Service](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/set-up-a-harbor-registry-in-a-connected-environmnet-for-storing-models-for-private-ai-services.html). In the lab, deploy the appliance through vCenter so that its settings are applied, create its certificate authority (CA), switch on the container registry and create a project for the models.
11. **Trust the registry.** Two places need to trust that CA. The Supervisor gets a registry entry with the CA certificate in vCenter. PAIS gets the same certificate as a ConfigMap, referenced in `clientTls.caBundleRefs` of its configuration.
12. **Push models.** On a workstation, download the model files and push them with `vcf pais models push`. The command checks the content before it uploads.
13. **GPU in passthrough, optional.** Without this step a model endpoint runs on CPU. With a GPU there are three things to do: set the card to passthrough on the host, create a VM class with the device in vCenter, and add `nvidiaConfig` to the PAIS configuration with one patch. Passthrough gives the whole card to one endpoint and needs no NVIDIA licence. With virtual GPU (vGPU) several endpoints share one card. That needs an NVIDIA licence and more setup, so it is not part of the minimum. [Part 4a](/posts/from-passthrough-to-vgpu-slices-in-one-evening/) has that route.
14. **ModelEndpoint.** One YAML object names the model, the engine and the VM class. PAIS adds a worker node of that class to its cluster, pulls the model from Harbor and starts the engine.
15. **Available on the AI gateway.** One more `InferenceGatewayRoute` points the service name from step 9 to the local endpoint. No client needs a change.

After step 15 the local model is available on the AI gateway of PAIS. Remote and local models now sit behind one address with an OpenAI-compatible interface. An application needs the same three values as after step 9: the base URL, a token and a service name.

## Where the steps happen

I counted the steps by the place where I did them:

| Where | Steps | How often |
|---|---|---|
| vCenter UI | 1 to 7, and parts of 10, 11 and 13 | once |
| `kubectl` | 8, 9, 14, 15, and parts of 11 and 13 | 14 and 15 for every new model |
| Other | Broadcom portal (5), appliance UI (10), VCF command-line interface on a workstation (12), ESX host (13) | step 12 for every new model |

Most of the setup is clicks in vCenter that a vSphere administrator already knows. The daily work afterwards is small: a new model means one push, one `ModelEndpoint` and one route.

## The two steps that make you wait

Steps 5 and 11 look like small settings, but both change what the PAIS cluster needs on its nodes. PAIS reacts by replacing the control plane VM of its cluster.

In the lab I added the Harbor registry entry at 11:42 and the certificate bundle at 11:44. The control plane VM was replaced twice within a few minutes. It took 10 to 15 minutes until PAIS reported Ready again. The same happens every time the registry token from step 5 is renewed.

What this means depends on what is running:

- **Remote routes keep answering.** The gateway runs as vSphere Pods in the Supervisor namespace and does not depend on the cluster.
- **Local endpoints do not.** While the cluster was being rebuilt, the gateway answered 502 for the local models, and the endpoints showed that their prerequisites were not met.

So I do step 11 in one go before the first endpoint exists, and I renew the token in the morning of a day on which I need the local models, not shortly before I use them.

## How long it took

I built the setup in three sittings:

| When | Steps | What answered at the end |
|---|---|---|
| 19 October, one evening | 1 to 4 | the Kubernetes API, about seven minutes after the last click in the wizard |
| 20 October, one morning | 5 to 9 | a remote model through the gateway, 25 minutes after I created the PAIS instance |
| 26 and 27 October | 10 to 15 | a local model on CPU in the afternoon, the same model on the GPU in the evening |

Most of the time went into preparation and into the things described in the parts, not into the steps themselves.

## Official documentation and William Lam's posts

The steps follow the Broadcom documentation. For several of them I also used William Lam's posts and manifests, which are worth reading.

- **The whole route:** [Setup Workflows for Private AI Services](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/setup-workflow-for-private-ai-services.html) and the [requirements](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/requirements-for-deploying-private-ai-foundation-with-nvidia.html) in the Broadcom documentation. William Lam: [VCF 9.1.1 - Deploying Your Own AI Models with VCF Private AI Services (PAIS) 3.0](https://williamlam.com/2026/09/vcf-9-1-1-deploying-your-own-ai-models-with-vcf-private-ai-services-pais-3-0.html).
- **Step 2:** [Deploy a Supervisor with Foundation Load Balancer and VDS Networking](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/vsphere-supervisor-installation-and-configuration/deploying-vsphere-supervisor-with-foundation-load-balancer/deploy-a-supervisor-with-foundation-load-balancer-and-vds-networking.html).
- **Steps 6 and 7:** [Install Private AI Services on the Supervisors of the Workload Domain](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/installing-and-configuring-private-ai-services/install-private-ai-services-on-the-supervisor.html) and [Activate Private AI Services 3.0 in an Organization Namespace by Using the kubectl Command](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/installing-and-configuring-private-ai-services/Activating-Private-AI-Services-3-0/activate-private-ai-services-3-0-in-an-organization-namespace-by-using-the-kubectl-command.html).
- **Step 8:** [Generate API Tokens for VCF Automation or Local Private AI Services Accounts](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/generate-api-tokens-for-local-accounts.html).
- **Step 9:** [Connect to a Remote Model Running in the Cloud](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/connect-to-a-remote-model-running-in-the-cloud.html).
- **Step 10:** [Set Up a Local Platform Harbor Registry](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/set-up-a-harbor-registry-in-a-connected-environmnet-for-storing-models-for-private-ai-services.html), the supported way. William Lam: [VCF Infrastructure Services (VIS) Appliance for VCF 9.1 Lab/PoC](https://williamlam.com/2026/07/vcf-infrastructure-services-vis-appliance-for-vcf-9-1-lab-poc.html), the appliance I use in the lab.
- **Step 11:** [Import a CA Trust Bundle in Private AI Services](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/importing-a-ca-trust-bundle-in-private-ai-services.html).
- **Step 12:** [Storing ML Models in VMware Private AI Foundation with NVIDIA](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/storing-ml-models-in-vmware-private-ai-foundation.html).
- **Step 13:** [Configure NVIDIA vGPU or GPU Passthrough on the ESX hosts](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/configure-nvidia-vgpu-or-gpu-passthrough-on-the-esx-hosts.html), [Configure VM Classes for AI Workloads](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/configure-vgpu-based-vm-classes-for-ai-workloads.html) and [Turn on GPU for a Private AI Services 3.0 Instance by Using the UI](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/installing-and-configuring-private-ai-services/switch-from-cpu-only-to-gpu-enabled-private-ai-services.html). William Lam: [a model endpoint with DirectPath I/O in his VCF 9.0 lab](https://williamlam.com/2025/10/ms-a2-vcf-9-0-lab-deploying-model-endpoint-with-directpath-i-o-using-vmware-for-private-ai-services-pais.html).
- **Steps 14 and 15:** [Running Completion or Embedding Models by Using Model Endpoints](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/deploying-model-endpoints.html) and the [Kubernetes API reference of Private AI Services](https://developer.broadcom.com/xapis/vmware-private-ai-service-kubernetes-api/latest/api-docs.html). William Lam: [his ModelEndpoint manifests on GitHub](https://github.com/lamw/vmware-scripts/tree/master/yaml).

## What is not in the 15 steps

- **vGPU.** It needs an entitlement from NVIDIA, a licence token, a host driver and a registry key. The diagram shows it as an unnumbered branch at step 13; [part 4a](/posts/from-passthrough-to-vgpu-slices-in-one-evening/) has that route.
- **Full capabilities.** Data indexing, the Agent Builder and Model Context Protocol (MCP) servers need a PostgreSQL database. This setup is "Model Runtime only".
- **Certificates that clients trust.** The lab still uses the certificate that PAIS creates for itself.
- **Monitoring.** A VCF Operations instance next to the vCenter shows the GPU and the slices without extra setup. Part 4a and [part 4b](/posts/one-card-cut-into-slices/) show it.
- **Self-service for application teams.** In this lab I hand out service names and tokens myself. A full VCF deployment with VCF Automation adds tenants, a catalogue and quotas.

## What I would do differently

- **Do steps 10 to 12 right after step 9, even without a GPU.** A model endpoint on CPU is slow, but it proves the whole chain from the registry to the gateway before any hardware arrives.
- **Use service names from the first route.** Step 15 only works without client changes because the clients never knew the model name.
- **Write down which steps replace the control plane.** I once renewed the registry token while my local models were running, and they did not answer for 15 minutes.
