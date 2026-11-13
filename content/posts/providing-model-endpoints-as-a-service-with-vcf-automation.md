---
title: "Route to Private AI Services 3.0, part 6: providing model endpoints as a service with VCF Automation"
date: 2026-11-13T08:42:36+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/providing-model-endpoints-as-a-service-with-vcf-automation.jpg"
  alt: "Route to Private AI Services 3.0, part 6: providing model endpoints as a service with VCF Automation"
categories: ["vmware"]
tags: ["private-ai", "homelab", "vcf-automation", "vgpu", "model-as-a-service"]
summary: "A question that comes up in almost every conversation about Private AI Services: how does a team get a model endpoint from a portal, without a ticket and without a pipeline? Part 6 answers it with a catalog item in VCF Automation. Four fields, one request, and seven minutes later a Gemma 4 model answers on a vGPU slice behind the gateway. With the template, the order step by step, five things that cost time, and what is still missing for a real service."
linkedin: ""
---

Parts 1 to 5 of this series ran on plain vSphere: one host, a Supervisor, Private AI Services (PAIS) activated from vCenter. For this part the lab is a different place. On the evening of 11 November it became a single-host VMware Cloud Foundation (VCF) 9.1.1 fleet, built along [William Lam's single-host guide](https://williamlam.com/2026/09/vcf-9-1-1-single-esx-host-for-vcf-fleet-vcf-workload-domain-or-vcf-cluster.html), with VCF Automation and a Supervisor on NSX Virtual Private Cloud (VPC) networking. One EPYC host now runs vCenter, NSX, VCF Operations, VCF Automation, the Supervisor and PAIS. A private cloud in a box. The [build night has its own post](/posts/single-host-vcf-fleet-build-night/).

The question this part answers comes up in almost every conversation about PAIS: **how does a team get a model endpoint from a portal, without a ticket and without writing a pipeline first?** My answer is a catalog item in VCF Automation. The team picks a model, a GPU size, a context window and a name. Seven minutes later the model answers behind the gateway.

![Flow from the request in the catalog through the template and the Supervisor namespace into Private AI Services, where the worker VM, the driver and the model come up, and back to the consumer with outputs, API token and the first call](/images/providing-model-endpoints-as-a-service-with-vcf-automation/maas-order-flow.svg)

The NVIDIA software still runs on the 90-day NVIDIA AI Enterprise evaluation from part 4, the VCF fleet on the 90-day VCF evaluation.

{{< tldr >}}
- **A model endpoint is one Kubernetes object**, a `ModelEndpoint` in the Supervisor namespace. The Model Runtime wizard in PAIS writes it for platform teams. A VCF Automation template writes the same object from four input fields.
- **The template needs two resource types:** `CCI.Supervisor.Namespace` for the existing namespace and `CCI.Supervisor.Resource` with the `ModelEndpoint` manifest and a wait condition on `Ready`. A released version shows up in the catalog by itself, in an All Apps organization too.
- **The lab example:** the order went in at 22:05 and the deployment was successful at 22:12. In between, PAIS created a worker VM with a 12 GB vGPU slice, built the driver, got a licence and pulled the model from Harbor. The first call returned 109 tokens in 1.7 seconds, 68 tokens per second.
- **Five things that cost time:** `metadata.name`, quotes around colons, strings for `cliArgs`, unique routing names, and the CPU reservation of the namespace, which let only one 12 GB worker start.
- **Still missing for a real service:** the consumer account, API tokens without a visit to the PAIS UI, quotas and rate limits per model.
{{< /tldr >}}

## Two ways to the same object

PAIS 3.0 has its own wizard for model endpoints. In the organization portal of VCF Automation it sits under Build & Deploy, Services, the namespace, Private AI, Model Runtime, **Deploy Model Endpoint**. Four steps: the model as an Open Container Initiative (OCI) path in Harbor with its pull secret, the endpoint with routing name, type and engine, the deployment with VM class and storage class, then review. The YAML of the `ModelEndpoint` runs along on the right. This is the view of the platform team or the AI team. It gives full control, and it expects you to know what an OCI path, a pull secret and `--n-gpu-layers` are.

An application team wants something else: to pick a model and a size and get a URL back. The VCF Automation catalog does that. The catalog item `llm-endpoint` creates exactly the same `ModelEndpoint` object, but the request form shows four fields, and the order has an owner, a history and outputs.

![The VCF Automation catalog of the lab organization with one item, llm-endpoint, described as Model as a Service: order an LLM endpoint in Private AI Services and get the gateway URL and model name back](/images/providing-model-endpoints-as-a-service-with-vcf-automation/catalog-card.png)

Both ways end in the same list under Model Runtime. The endpoint from the catalog order stands next to the one from the wizard, and PAIS treats them the same.

## The template

The template is a VCF Automation blueprint in format version 2, created under Content Hub, Blueprint Design, from a blank canvas. The inputs are the four fields of the form: the model as a choice of three entries from the lab's Harbor gallery, the GPU size as a choice of three VM classes with vGPU profiles of 12, 8 and 4 GB, the context window, and the model name that the application later uses in the API call.

![The request form of the catalog item: project, deployment name, model with the choices Gemma 4 12B, Qwen3 8B and Qwen3 4B, GPU size, context window and the model name in the gateway](/images/providing-model-endpoints-as-a-service-with-vcf-automation/request-form.png)

The resources part is short. The first resource points at the existing Supervisor namespace. The second one carries the `ModelEndpoint` manifest and waits until the object reports `Ready`.

```yaml
resources:
  ns:
    type: CCI.Supervisor.Namespace
    properties:
      existing: true
      name: pais-cgky3
  endpoint:
    type: CCI.Supervisor.Resource
    properties:
      context: ${resource.ns.id}
      wait:
        conditions:
          - type: Ready
            status: 'True'
      manifest:
        apiVersion: pais.vmware.com/v1alpha1
        kind: ModelEndpoint
        metadata:
          name: ${input.routingName}
          namespace: pais-cgky3
        spec:
          type: Completions
          engine: LlamaCPP
          routingName: ${input.routingName}
          replicas: 1
          virtualMachineClassName: ${input.size}
          storageClassName: <storage class of the namespace>
          model:
            ociRef: '<registry>/models/${input.model == "gemma-4-12b" ? "google/gemma-4-12b-qat-gguf:v1" : "qwen/qwen3-8b-gguf:v1"}'
            pullSecrets:
              - name: <registry secret of the PAIS instance>
          inferenceServerCustomization:
            engineImage: ghcr.io/ggml-org/llama.cpp:server-cuda-b11913
            cliArgs: ['--n-gpu-layers', '99', '--ctx-size', '${input.ctx}', '--flash-attn', 'on', '--reasoning-budget', '0', '--jinja', '--metrics']
outputs:
  gatewayBaseUrl:
    value: https://pais.example.internal/api/v1/compatibility/openai/v1
  modelName:
    value: ${input.routingName}
```

The manifest is the one the wizard would write, with the inputs in the places where the wizard has fields. The outputs give the team the gateway URL and the model name, which is all an OpenAI client needs besides a token.

To release a version, I use **Version** and then **Release**. The released version appears under Build & Deploy, Catalog without a further step. I remembered that the catalog did not work in an All Apps organization in 9.0. In 9.1.1 the catalog, the request form, the instances view and the topology all work there.

## The order, step by step

The order of the lab example was `Gemma4TeamA`: Gemma 4 12B, the 12 GB slice, a context window of 8,192 tokens and `gemma4` as the model name. The deployment API records the request at 22:05:33 and the success at 22:12:49.

1. The deployment appears under Instances with the requester, the template version, a topology of namespace and endpoint and the running tasks.
2. The `ModelEndpoint` object is created in the Supervisor namespace. PAIS picks it up and adds a machine deployment to its Kubernetes cluster, one worker VM per endpoint, in the VM class from the form.
3. The worker VM powers on with an `RTXA5000-12C` profile. On the host, `nvidia-smi vgpu` shows the new instance with its 12 GB.
4. The GPU Operator builds the vGPU guest driver on the node, about three minutes, and the driver gets its licence lease from the NVIDIA cloud licence service.
5. The engine pod pulls the 7 GB model from the lab's Harbor registry, llama.cpp loads it onto the slice, and the endpoint reports `Ready`. PAIS adds the route in the gateway.
6. The wait condition is met, the deployment finishes, and the outputs show the gateway URL and the model name.

The token is the one step that still happens outside VCF Automation. The user signs in to the PAIS UI with the same local account and generates an API token under the user menu. With it, the first call from my laptop looked like this:

```bash
curl -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  https://pais.example.internal/api/v1/compatibility/openai/v1/chat/completions \
  -d '{"model":"gemma4","messages":[{"role":"user","content":"Hallo"}]}'
```

The answer came back in 1.7 seconds, 28 tokens in, 109 tokens out, 68 tokens per second on the slice. The gateway is OpenAI-compatible, so any client that takes a base URL and a key works.

## Five things that cost time

- **The manifest needs `metadata.name`.** `generateName` fails with "missing metadata.name in manifest property". The routing name doubles as the object name in my template.
- **Quotes around colons.** A YAML value with a colon inside `${…}` has to be quoted, otherwise the blueprint does not save.
- **`cliArgs` are strings.** The context window is an input of type string with an enumeration of three values, not an integer, because the argument list of the engine takes strings only.
- **Routing names must be unique in the namespace.** Two orders with the same default name failed. The field now has no default, a pattern and a hint. A deleted deployment also keeps its name blocked for a while.
- **Capacity in the namespace.** The vGPU VM classes carry a CPU reservation of 16 GHz each. The namespace resource pool has 32 GHz of reservation and the host is almost fully reserved by the fleet, so the second 12 GB worker failed placement with "The amount of CPU resource available in the parent resource pool is insufficient". The fix on my list is a set of GPU classes that reserve the memory but not the CPU.

One more problem came from the layer below. PAIS 3.0 picks the newest vSphere Kubernetes release for its cluster, which in my lab was v1.34.11 with a 7.0 kernel, and the bundled vGPU guest driver does not build on that kernel. I pinned the cluster to v1.34.9 in the `PAISConfiguration` at creation. The wizard has no field for it, and the version cannot be lowered later.

## What is still missing

The order works. A service needs more than an order, and the lab does not show these parts yet.

- **The consumer account.** The order above was placed by the organization administrator. A real consumer is an Organization User who is a member of the project, sees the catalog and the instances and nothing else, and has a local account in PAIS for the token. That is the next step, and I want to show it from login to the first answer.
- **The token step.** VCF Automation can be the identity provider of PAIS, which would remove the visit to the PAIS UI. That needs an OAuth client in the organization, which I have not set up.
- **Quotas and rate limits.** VCF Automation limits CPU, memory and VM classes per namespace. The gateway has no quota or rate limit per model and no access list per route. Who may call which model is a question the platform team has to answer somewhere else today.
- **The pipeline path.** The same template YAML can live in Git, be released over the blueprint API and be ordered from the catalog API by a pipeline. The catalog does not replace continuous integration and delivery (CI/CD). It gives teams without a pipeline a way to order.

## Documentation

- Broadcom: [Activate Private AI Services 3.0 in an Organization Namespace by Using the UI](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/installing-and-configuring-private-ai-services/Activating-Private-AI-Services-3-0/activate-private-ai-services-30-in-an-organization-namespace-by-using-the-vcf-automation-ui.html)
- Broadcom: [Managing Blueprints in VCF Automation](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/organization-management/managing-blueprints-in-vcf-automation.html) and [Working with the catalog](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/organization-management/vcfa-overview/working-with-the-vcf-automation-catalog.html)
- Broadcom: [Understanding the VCF Automation All Apps organization multi-tenancy model](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/design/design-library/vcf-automation-deployment-models-9-x/organization-consumption-model/understanding-vcf-automation-all-apps-organization-multi-tenancy-model.html)
- VMware blog: [Activate VCF Private AI Services](https://blogs.vmware.com/cloud-foundation/2026/01/15/activate-vcf-private-ai-services/)
- William Lam: [VCF 9.1.1, deploying your own AI models with VCF Private AI Services 3.0](https://williamlam.com/2026/09/vcf-9-1-1-deploying-your-own-ai-models-with-vcf-private-ai-services-pais-3-0.html), the wizard path with kubectl and Harbor

The earlier parts: [part 5](/posts/an-agent-that-calls-tools-on-a-small-local-model/) built agents and MCP tools on the endpoints, [part 4a](/posts/from-passthrough-to-vgpu-slices-in-one-evening/) is the vGPU route, and the [overview in 15 steps](/posts/private-ai-services-on-one-host-in-15-steps/) lists every part.
