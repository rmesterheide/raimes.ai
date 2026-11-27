---
title: "GitOps for Private AI with VCF Automation, part 2: NVIDIA NIM as a catalog item, rolled out by ArgoCD and connected to Private AI Services"
date: 2026-11-24T21:55:00+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2.jpg"
  alt: "GitOps for Private AI with VCF Automation, part 2: NVIDIA NIM as a catalog item, rolled out by ArgoCD and connected to Private AI Services"
categories: ["vmware"]
tags: ["gitops", "argo-cd", "vcf-automation", "nvidia-nim", "private-ai", "homelab"]
summary: "A catalog item in VMware Cloud Foundation Automation that rolls out an NVIDIA NIM through ArgoCD: the NIM Operator runs the Nemotron model on a virtual GPU slice, and the gateway of Private AI Services makes it available under one name. Lab example: with two health checks, the catalog reports success 21 seconds after the NIM gives its first answer."
url: /review/nim-catalog-item-5e6c03d063/
review_draft: true
build:
  list: never
  render: always
sitemap:
  disable: true
---

<div class="review-draft"><strong>Review draft, not published.</strong> This text is shared with a few readers for comments before it goes on the blog. Please do not forward the link. Comments by mail are welcome: use the "Found an error? Mail me" link at the end of the page.</div>

An organization user opens the catalog of VMware Cloud Foundation (VCF) Automation, selects the item NVIDIA NIM Endpoint, picks a model, types a name and clicks Submit. Two and a half minutes later the order is done, and the model answers under that name at the gateway of Private AI Services (PAIS). The model weights were already in a cache at that point. The form does not ask for a key or a password.

![The request form of the catalog item NVIDIA NIM Endpoint with four fields: Project, Deployment Name, Model with Llama 3.1 Nemotron Nano 8B v1 selected, and Model name in the gateway](/images/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2/request-form.png)

A NIM is an inference microservice from NVIDIA. It is a container that holds an inference server with an OpenAI-compatible API, and it picks a model profile that fits the GPU it finds. I use it with a Nemotron model.

In [part 1](/posts/argo-cd-gitops-service-in-vcf-automation-part-1/) I installed the ArgoCD service of VCF Automation and attached one vSphere Kubernetes Service (VKS) cluster to an ArgoCD instance. This part uses that setup for the catalog item.

This order uses software from two vendors. NVIDIA provides the NIM, the model and two Kubernetes operators. VCF provides the virtual GPU (vGPU) slice, the Kubernetes cluster, ArgoCD, the catalog and the gateway. I did not have to change the NIM Operator or the GPU Operator to make them work with the VCF parts.

The lab is the one from part 1, the [single-host VCF 9.1.1 fleet](/posts/single-host-vcf-fleet-build-night/), with one RTX A5000 (24 GB). The NVIDIA software runs on the 90-day evaluation of NVIDIA AI Enterprise.

{{< tldr >}}
- **[One order creates two objects:](#the-blueprint-one-application-and-one-route)** an ArgoCD `Application` that rolls out the NIM on a VKS cluster, and a route in the PAIS gateway that gives the NIM a name.
- **[The NIM Operator chart needed no change for VKS.](#the-platform-side-done-once)** I installed NVIDIA's Helm chart as documented, with a Pod Security label on the namespace, and it was running after 17 seconds.
- **[The lab example:](#the-lab-example-the-catalog-waits-until-the-nim-answers)** my first order reported success after 49 seconds, and the NIM answered after about 6 minutes. With two health checks in ArgoCD, the next order reported success after 162 seconds, 21 seconds after the first answer of the NIM.
- **[A chart change is a Git commit.](#where-git-comes-in)** I committed a new context length. ArgoCD applied it 399 seconds after the push, and the NIM answered with the new value after 509 seconds.
- **[An order by the test user took 2 minutes 29 seconds,](#the-order-as-an-organization-user)** with the model weights already in the cache.
- **[Throughput on the 24 GB slice:](#throughput-with-tokens-in-and-out)** 34 tokens per second for one request, 133 tokens per second in total for four parallel requests.
- **Chart, blueprint and health checks** are in the public repository [pais-vgpu, folder nim-endpoint](https://github.com/rmesterheide/pais-vgpu/tree/main/nim-endpoint).
{{< /tldr >}}

**The ArgoCD service in VCF Automation is new, but the software behind it is older.** Broadcom released the ArgoCD Supervisor Service in July 2025 ([release notes of version 1.0.0](https://vsphere-tmm.github.io/Supervisor-Services/argocd-service/release-notes-v1.0.0.html)). It is installed through vCenter and has been available since VCF 9.0.1. A [Broadcom blog post of September 2026](https://blogs.vmware.com/cloud-foundation/2026/09/03/from-bottleneck-to-breakthrough-centralizing-gitops-at-enterprise-scale-with-vcf-9-1-1/) calls it fully supported for production use and says that enterprise customers run it in production.

The service in VCF Automation uses the same ArgoCD operator as the ArgoCD Supervisor Service. The same blog post introduced it as a Tech Preview in VCF 9.1.1. With VCF 9.1.2, released on 24 November 2026, the service in VCF Automation is generally available (GA). VCF 9.1.2 bundles it, and the [release notes of VCF Automation 9.1.2](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/release-notes/vmware-cloud-foundation-9-1-2-0-release-notes/vcf-automation-9-1-2-0-release-notes.html) list it under What's New. My lab still runs 9.1.1, so I use the Tech Preview version in this post. The catalog item creates an ArgoCD `Application`. This object is the same in the Tech Preview, in the GA version and in the ArgoCD Supervisor Service.

## Who brings what

| Part | From | What it does in this order |
|---|---|---|
| NIM container and Nemotron model | NVIDIA | the inference server with an OpenAI-compatible API and model profiles per GPU |
| NIM Operator | NVIDIA | two Kubernetes objects: `NIMCache` for the model weights, `NIMService` for the running NIM |
| GPU Operator and vGPU guest driver | NVIDIA, installed by a VCF catalog item | make the GPU of the worker node available to pods |
| vGPU and VM class | VCF | give a slice of the card to the worker VM |
| VKS cluster | VCF | the Kubernetes cluster that the NIM runs on |
| ArgoCD service | VCF Automation | rolls out the Helm chart from Git and reports the health of the NIM |
| Catalog and blueprint | VCF Automation | the form, the order with its owner, the delete action |
| Gateway | VCF, Private AI Services (PAIS) | one address and one token check for all models |

The upper three rows belong to NVIDIA AI Enterprise. The joint offering of both vendors is called VMware Private AI Foundation with NVIDIA, and its [documentation](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1.html) covers most of the lower rows.

Each vendor supports its own parts. The NVIDIA rows are part of NVIDIA AI Enterprise, and a subscription [includes NVIDIA's support services](https://docs.nvidia.com/ai-enterprise/planning-resource/licensing-guide/latest/licensing.html). The VCF rows are Broadcom products with Broadcom support. Broadcom lists the licenses that the joint offering needs on the page [Requirements for Deploying VMware Private AI Foundation with NVIDIA](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/requirements-for-deploying-private-ai-foundation-with-nvidia.html). For the support terms, please use the documentation of both vendors.

Two things in this post are not covered by vendor support. The evaluation license that my lab uses does not include NVIDIA Enterprise Support. The chart and the blueprint in my repository are lab examples, not a product.

## The platform side, done once

These steps are the work of the platform team. A consumer does not see them.

**1. A VKS cluster with a GPU worker.** I ordered it from the catalog item AI Kubernetes Cluster, which the [Private AI Foundation Quickstart](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/finalizing-the-setup-for-deep-learning-vms-and-vks-cluster-with-gpu/how-do-i-use-the-paif-quickstart-in-aria-automation.html) creates. I named the deployment `nim-cluster`. The order took under 12 minutes. It built one control plane node and one worker node with the whole card as a 24 GB slice, and it installed NVIDIA's GPU Operator and the vGPU guest driver. I did not install a driver by hand.

![The deployment nim-cluster in VCF Automation with the status Create Successful, created at 9:05:21 AM and last updated at 9:17:41 AM, from the catalog item AI Kubernetes Cluster. The page states that the cluster comes with the NVIDIA GPU operator.](/images/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2/cluster-deployment.png)

This is the cluster that I attached to the ArgoCD instance in [step 6 of part 1](/posts/argo-cd-gitops-service-in-vcf-automation-part-1/#step-6-attach-a-vks-cluster). All orders in this post deploy to it.

**2. The NIM Operator.** I followed NVIDIA's page [Installing NVIDIA NIM Operator](https://docs.nvidia.com/nim-operator/latest/install.html):

```bash
kubectl create namespace nim-operator
kubectl label namespace nim-operator pod-security.kubernetes.io/enforce=privileged
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia
helm upgrade --install nim-operator nvidia/k8s-nim-operator \
  --namespace nim-operator --version 3.1.2 --wait
```

The operator was running after 17 seconds. The Pod Security label on the namespace was the only step that I added for VKS. The chart itself needed no change.

**3. A namespace with two secrets.** The NIM needs a key for NGC, the registry of NVIDIA, once to pull the image and once to download the model. I created the namespace `nim` with the Pod Security label `privileged` and two secrets that the NIM Operator documentation names: `ngc-secret` for the image pull and `ngc-api-secret` with the key `NGC_API_KEY`. The key is typed once by the platform team. It is not in Git, and it is not in the order form.

In my lab these are two Kubernetes secrets that I created by hand. On a shared platform I would keep the key in a central secret store and let the cluster read it from there. Then the key is rotated and audited in one place. Broadcom documents the [Secret Store Service](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-secret-store-service-with-vsphere-supervisor.html) for this: a central service for secrets that pods in VKS clusters can consume. I have not installed it yet.

**4. An ArgoCD project.** The project limits what an order can do: one repository, one cluster, one namespace, and three kinds of objects (`NIMCache`, `NIMService` and `Service`). Its destination is the API address that the attached cluster shows in its status, as in the last step of part 1.

The ArgoCD interface of the instance opens from the organization portal: GitOps in the menu (1), then the instance, whose Scope tab lists the attached cluster (2), then Go to Argo CD UI (3).

![The instance on the GitOps page of the organization portal with three numbered marks: the menu entry GitOps, the Scope tab with one attached Kubernetes cluster in status Success, and the button Go to Argo CD UI](/images/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2/gitops-scope.png)

The login page of ArgoCD offers the login through VCF Automation and a local account.

![The ArgoCD login page with the button Log in via VCF Automation above the fields for a local account](/images/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2/argocd-login.png)

My instance was created with `kubectl` before I installed the ArgoCD service of VCF Automation in part 1. I have not given VCF Automation users a role in it yet, so I used the local account for the pictures in this post.

**5. The blueprint and the health checks.** Both have their own section below.

## The chart: a cache, a service and a fixed address

The Helm chart has three templates. Each order sets three values: the name, the model and the fixed address of the NIM.

The `NIMCache` downloads the model weights to a volume. The chart names it after the model, and an annotation tells ArgoCD to keep it when an order is deleted:

```yaml
apiVersion: apps.nvidia.com/v1alpha1
kind: NIMCache
metadata:
  name: cache-{{ .Values.model }}
  annotations:
    argocd.argoproj.io/sync-options: Delete=false,Prune=false
spec:
  source:
    ngc:
      modelPuller: {{ $m.repository }}:{{ $m.tag }}
      pullSecret: ngc-secret
      authSecret: ngc-api-secret
      model:
        profiles:
          - {{ $m.profile }}
  storage:
    pvc:
      create: true
      size: {{ $m.cacheSize | quote }}
```

So the weights are downloaded once per model. Every later order of the same model starts from the volume.

![The application of an order in the ArgoCD interface: Healthy and Synced, auto sync enabled, and the resource tree with the load balancer service, the NIMCache and the NIMService. The cache is 11 hours old, the other objects 10 hours](/images/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2/argocd-application.png)

The picture shows the application of one order. The cache is older than the NIM, because it was kept from an earlier order.

The `NIMService` runs the NIM with that cache and one GPU. It sets two values from my sizing runs: the profile (`NIM_MODEL_PROFILE`) and the context length (`NIM_MAX_MODEL_LEN`).

The third template is a plain Kubernetes service of type LoadBalancer with a fixed address. The gateway route points at that address, so it has to be known before the order runs. The service selects the pods by the label `app`, which the NIM Operator sets to the name of the `NIMService`. On VKS, a service with `spec.loadBalancerIP` got exactly the address I asked for after a few seconds.

NVIDIA documents both objects in [Caching NIM Models](https://docs.nvidia.com/nim-operator/latest/cache.html) and [Managing NIM Services](https://docs.nvidia.com/nim-operator/latest/service.html).

## Sizing: which Nemotron NIM fits a 24 GB card

Before I wrote the chart, I started three Nemotron NIMs in a VM with Docker, first on a 12 GB slice and then on the 24 GB slice. Each NIM lists its model profiles with the command `list-model-profiles`, and NVIDIA explains them in [Model Profiles and Selection](https://docs.nvidia.com/nim/large-language-models/latest/profiles.html). A profile names the inference engine, the precision of the weights and the GPU memory it is made for.

| NIM | Profiles for one GPU | Result on my card |
|---|---|---|
| Llama 3.1 Nemotron Nano 8B v1, version 1.8.4 | 16-bit weights (bfloat16, BF16), about 16 GB | runs on the 24 GB slice: 20.4 of 24.0 GB in use with a context of 16,384 tokens |
| Nemotron Nano 9B v2, version 1.12.2 | 16-bit weights, 17.3 GiB | needs more memory at start than the 24 GB slice offers, seen in three runs |
| Nemotron 3 Nano, version 2.1.7 | BF16 from 80 GB, 8-bit weights (FP8) from 34 GB, NVIDIA's 4-bit format (NVFP4) from 21 GB for cards of the Blackwell generation | made for larger and newer cards than an RTX A5000 |

For my card the result is one model: the 8B with 16-bit weights on the whole card. A 12 GB slice was too small for all three. These numbers describe one workstation card with 24 GB. A card with 48 GB or more should have more choices in the same list, but I have not measured that.

Three sizing notes from these runs:

- **A 24 GB vGPU slice offered about 21.4 GiB to CUDA.** I plan with that number, not with 24.
- **The context length is part of the sizing.** With this model the slice has room for about 19,000 tokens of context. A setting of 32,768 did not start, 16,384 did.
- **I pin the profile and the slice size per model.** The chart carries the profile ID, the context length and the cache size for each model that I have measured. An order can only pick from that list, so it always gets a combination that has run on this card.

My lab has one small card. For larger setups I describe hardware options on a separate page: [The Enterprise Private AI Building Block](/building-block/). It covers accelerators, servers and the open-weight models that fit, and it points to the official sources. I check it about once a month.

## The blueprint: one Application and one route

The blueprint has two inputs and two resources. This is how it looks in Blueprint Design in the organization portal:

![The blueprint NVIDIA NIM Endpoint in Blueprint Design: the canvas shows two Supervisor namespaces with the resources route and nim, the code view shows the inputs model and routingName](/images/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2/blueprint-design.png)

This is the trimmed version of the code. The names of the namespaces and the addresses are placeholders.

```yaml
formatVersion: 2
name: NVIDIA NIM Endpoint
inputs:
  model: {type: string, title: Model}                        # a list of measured models
  routingName: {type: string, title: Model name in the gateway}
resources:
  nim:
    type: CCI.Supervisor.Resource
    properties:
      context: ${resource.gitopsNs.id}
      wait:
        fields:
          - path: status.sync.status
            value: Synced
          - path: status.health.status
            value: Healthy
      manifest:
        apiVersion: argoproj.io/v1alpha1
        kind: Application
        metadata:
          name: nim-${input.routingName}
          finalizers:
            - resources-finalizer.argocd.argoproj.io
        spec:
          project: nim
          source:
            repoURL: https://github.com/rmesterheide/pais-vgpu.git
            targetRevision: HEAD
            path: nim-endpoint/chart
            helm:
              parameters:
                - {name: name, value: '${input.routingName}'}
                - {name: model, value: '${input.model}'}
                - {name: loadBalancerIP, value: '<nim-address>'}
          destination:
            server: https://<cluster-api-address>:6443
            namespace: nim
          syncPolicy:
            automated: {prune: true, selfHeal: true}
  route:
    type: CCI.Supervisor.Resource
    dependsOn:
      - nim
    properties:
      context: ${resource.paisNs.id}
      manifest:
        apiVersion: pais.vmware.com/v1alpha1
        kind: InferenceGatewayRoute
        metadata:
          name: ${input.routingName}
        spec:
          type: Completions
          engine: OpenAI
          matches:
            routingName: ${input.routingName}
          backend:
            httpBaseUrl: 'http://<nim-address>:8000/'
            modelId: nvidia/llama-3.1-nemotron-nano-8b-v1
```

After an order, the application looks like this in ArgoCD:

![The application nim-nemotron-nim as a tile in ArgoCD: project nim, status Healthy and Synced, the repository, the path nim-endpoint/chart, the attached cluster as destination and the namespace nim](/images/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2/argocd-tile.png)

Three details in this file need an explanation.

**The `wait` block.** VCF Automation keeps the order in progress until the `Application` is Synced and Healthy. The next section shows why that needs the health checks.

**The finalizer.** When a user deletes the order, ArgoCD removes the NIM and the service from the cluster before the `Application` object goes away. In my lab the NIM, the service and the gateway route were gone 70 seconds after the delete. The cache stayed, as the annotation in the chart says.

**The route.** It is the same kind of object that the PAIS documentation describes in [Connect to a Remote Model Running in the Cloud](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/connect-to-a-remote-model-running-in-the-cloud.html). Here the backend is the NIM in my own cluster. A NIM speaks the OpenAI API, so the engine is `OpenAI`, and the route needs no `auth` block. The token check happens at the gateway. The gateway is the only caller the NIM address needs, so on a shared platform I would allow only the gateway to reach it.

The full blueprint is in the repository. Broadcom documents blueprints in [Managing Blueprints in VCF Automation](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/organization-management/managing-blueprints-in-vcf-automation.html).

## Where Git comes in

The order in the portal is not a Git commit. I chose the catalog on purpose. A model endpoint is something that application teams order, and the portal gives each order an owner, a project and a delete action.

What the order rolls out comes from Git. The blueprint passes three values to a chart in a repository. ArgoCD keeps the cluster in the state that the chart describes. Each application follows the HEAD of the repository with automated sync. To change what runs, I change the chart with a commit.

I tested this with two commits. In the first one I changed the context length of the model in the chart from 16,384 to 12,288 tokens. In the second one I changed it back. I did not touch the order, the portal or the cluster.

| | Commit 1, to 12,288 | Commit 2, back to 16,384 |
|---|---|---|
| ArgoCD applied the change to the `NIMService` | 399 s after the push | 452 s after the push |
| The NIM answered with the new context length | after 509 s | after 565 s |
| The NIM was not reachable | for about 80 s | for about 80 s |

Most of that time is the wait until ArgoCD reads the repository again. I did not set up a webhook, and I did not start a refresh by hand. After ArgoCD applied the change, the NIM Operator replaced the pod, and the new NIM answered about 110 seconds later. The lab has one card, so the old NIM stops before the new one loads the model. The gateway route did not change, because it points at the fixed address.

A team that wants the order itself in Git can write the same `Application` as a file in a repository and merge it with a pull request. Both ways use the same object.

## The lab example: the catalog waits until the NIM answers

My first order ran without health checks. This is what I measured:

| | First order | Second order, with health checks |
|---|---|---|
| Model weights | downloaded, 4 minutes 50 seconds | from the cache |
| ArgoCD application Healthy | as soon as the objects existed | after 146 seconds |
| Catalog reports success | after 49 seconds | after 162 seconds |
| NIM gives its first answer | after about 6 minutes | after 141 seconds |

In the first run the catalog said the order was done about five minutes before the model could answer. ArgoCD knows the health of the built-in Kubernetes kinds. For other kinds, such as `NIMService`, it accepts a small check written in Lua. The ArgoCD documentation describes this in [Resource Health](https://argo-cd.readthedocs.io/en/stable/operator-manual/health/).

The NIM Operator writes a clear state into its objects, so the check is short:

```yaml
spec:
  resourceHealthChecks:
    - group: apps.nvidia.com
      kind: NIMService
      check: |
        hs = {}
        if obj.status ~= nil and obj.status.state ~= nil then
          if obj.status.state == "Ready" then
            hs.status = "Healthy"
            hs.message = "NIM is ready"
            return hs
          end
          if obj.status.state == "Failed" then
            hs.status = "Degraded"
            hs.message = "NIM failed"
            return hs
          end
        end
        hs.status = "Progressing"
        hs.message = "Waiting for the NIM to become ready"
        return hs
```

The same check exists for `NIMCache`. I added both to the `ArgoCD` object of the instance, as a merge patch on `spec.resourceHealthChecks`. The operator of the ArgoCD service then wrote them into the configuration of the instance. The instance stayed Ready during the change.

With the checks in place, the second order followed the state of the NIM. The application showed Synced and Progressing from second 28. The NIM answered at second 141, the application was Healthy at second 146, and the catalog reported success at second 162.

## The order as an organization user

The last test was the order as the test user of my lab organization. She has the role Organization User and is a member of the project. She logged in to the organization portal, opened the catalog, selected NVIDIA NIM Endpoint, kept the model and typed a name.

The order was successful after 2 minutes 29 seconds. The deployment shows three outputs: the address of the gateway, the model name and a `curl` line.

![The deployment NIM01 in the organization portal with the status Create Successful, created at 12:09:19 and last updated at 12:11:48, and the three outputs usage, modelName and gatewayBaseUrl](/images/nvidia-nim-as-a-catalog-item-in-vcf-automation-part-2/deployment-outputs.png)

```bash
export PAIS_TOKEN='<API token from the Private AI Services UI>'
curl -s https://<pais-gateway>/api/v1/compatibility/openai/v1/chat/completions \
  -H "Authorization: Bearer $PAIS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"model":"<name-from-the-order>","messages":[{"role":"user","content":"Hello"}]}'
```

The gateway listed the new name next to the three other routes of the lab. An application that already uses the gateway only changes the model name.

## Throughput, with tokens in and out

| Call | Tokens in | Tokens out | Time | Tokens per second |
|---|---|---|---|---|
| directly at the NIM | 47 | 87 | 2.6 s | 33 |
| through the gateway, long answer | 49 | 400 | 11.8 s | 34 |
| through the gateway, after the order by the test user | 47 | 68 | 2.1 s | 32 |
| sizing run in the VM, one request | 54 | 600 | 17.5 s | 34 |
| sizing run in the VM, four parallel requests | not recorded | 1,600 in total | 12.0 s | 133 in total |

The speed was the same on both paths: 33 tokens per second directly at the NIM, 34 through the gateway. All prompts were short, so the ratio of tokens in to tokens out is between about 1:1.4 and 1:11. I made the gateway calls with the token of my administrator account.

Four parallel requests gave almost four times the throughput of one request. For a small team that shares one endpoint, the number for parallel requests is the more useful one.

## What I build next

- **A second model in the form,** once I have a card or a NIM version that gives me a second measured combination.
- **The NGC key from the Secret Store Service.** I want to install the service and see how the NIM namespace reads the key from it.
- **A deep learning VM through ArgoCD,** as its own post.
- **A new instance as an organization user:** I want to create it on the GitOps page and check how the role assignment and the single sign-on work.
- **More than one NIM at a time.** With one card and one fixed address, the lab runs one NIM. The chart already takes the address as a value.

## Documentation and further reading

The pages for single steps are linked in the text. These are the entry points:

- Repository: [pais-vgpu, folder nim-endpoint](https://github.com/rmesterheide/pais-vgpu/tree/main/nim-endpoint) with the chart, the ArgoCD project, the blueprint and the health checks
- Hardware options for a larger setup: [The Enterprise Private AI Building Block](/building-block/), my page on accelerators, servers and models that fit, checked about once a month
- NVIDIA: [NVIDIA NIM Operator](https://docs.nvidia.com/nim-operator/latest/index.html)
- NVIDIA: [NVIDIA NIM for LLM and VLM Documentation](https://docs.nvidia.com/nim/large-language-models/latest/introduction.html)
- NVIDIA: [llama-3.1-nemotron-nano-8b-v1, model card](https://build.nvidia.com/nvidia/llama-3_1-nemotron-nano-8b-v1/modelcard)
- NVIDIA: [NVIDIA AI Enterprise documentation](https://docs.nvidia.com/ai-enterprise/index.html)
- Broadcom: [VMware Private AI Foundation with NVIDIA 9.1](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1.html)
- Broadcom: [Deploy a GPU-Accelerated VKS Cluster by Using a Self-Service Catalog Item in VCF Automation](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-ai-workloads-on-tkg-clusters/service-broker-paif-deploy-tkg-cluster.html)
- Broadcom: [Installing and Configuring the Secret Store Service](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-secret-store-service-with-vsphere-supervisor.html)
- Broadcom: [Installing and Configuring the Argo CD Service in VCF and vSphere](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-service-administration-and-development/9-1/using-argo-cd-service.html)
- William Lam: [VCF 9.1.1 - Single ESX Host for VCF Fleet, VCF Workload Domain or VCF Cluster](https://williamlam.com/2026/09/vcf-9-1-1-single-esx-host-for-vcf-fleet-vcf-workload-domain-or-vcf-cluster.html), the guide my lab is built along
- Christian Ferber: [VMware Private AI Services - a beginner's experience](https://vrealize.it/2026/11/10/9973/), an install guide for Private AI Services with VCF Automation on vrealize.it
