---
title: "Route to Private AI Services 3.0, part 2: a private AI gateway without a GPU, with Claude behind it"
date: 2026-10-20T11:11:01+02:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/private-ai-services-without-a-gpu.jpg"
  alt: "Route to Private AI Services 3.0, part 2: a private AI gateway without a GPU, with Claude behind it"
categories: ["vmware"]
tags: ["private-ai", "homelab"]
summary: "Part 2 of my route to Private AI Services 3.0 on vCenter alone. The service registered on the second try, the instance was ready four minutes after the last click, and the first model behind my own gateway was not a local one: Claude, through Anthropic's OpenAI-compatible endpoint, on day zero without a GPU. The exact YAML, the three traps, why the route says Ready False and works anyway, and a small tool-using app that lets Opus inspect the lab through the gateway."
linkedin: ""
---

Yesterday, in [part 1](/posts/kubernetes-api-on-vsphere-in-one-evening/), a single EPYC server went from a fresh ESX install to a vSphere Supervisor with a Kubernetes API in one evening. This morning's part puts Private AI Services (PAIS) 3.0 on top of it. The GPU is still in the other machine; that is part 3. So the first model behind my private gateway is a public one: Claude.

That is not a workaround. It is the point I made on stage at VMware Explore on Tour last week: private AI does not mean "no public models". It means you decide which model sees which data, behind a gateway you own. Day zero without a single GPU is a supported start. When the GPU arrives, you repoint.

**To be clear about the route:** for an enterprise, the preferred way to run Private AI Services is a full VMware Cloud Foundation (VCF) deployment with VCF Automation. That is where the things live that a company needs and my lab does not:

- **Multi-tenancy:** organizations and projects, so teams share one platform without seeing each other.
- **Self-service:** a catalog and a consumption portal, instead of an administrator in vCenter.
- **Governance:** quotas, policies and role-based access per tenant.
- **Network isolation:** NSX with virtual private clouds per tenant, instead of shared VLANs.
- **Operations at scale:** lifecycle management, fleet operations and monitoring across many hosts and clusters.

For one server in my homelab, with one user, the lightweight way (vCenter, a distributed switch and the built-in load balancer) is enough, and it is the quickest way to see how the pieces fit. Read this series as a lab route, not as an enterprise reference architecture.

A disclosure: I work at Broadcom. This is my homelab and my own reading of public documentation, not an official statement. The Anthropic endpoint I use here is their OpenAI compatibility layer, which Anthropic itself describes as intended for testing and comparing models, not as a long-term production path.

{{< tldr >}}
- PAIS 3.0 comes as a Supervisor Service. Without VCF Automation, upload the definition with **`-external`** in its file name: the other one pulls its package from a Supervisor-internal depot that only a full VCF stack fills.
- Activation from vCenter, "Model Runtime only", CPU only, local accounts: **Ready four minutes after the click**, behind the Foundation Load Balancer from part 1.
- Public models are not added in the UI. They are a Kubernetes resource, **`InferenceGatewayRoute`**, plus a Secret for the provider key. Ten lines of YAML put Claude behind the PAIS gateway.
- Three traps: a registry test that fails although the token is fine, a model check that fails although the model works, and API tokens that the UI does not switch on.
- The highlight: a 100-line Python concierge with one read-only `kubectl` tool. Opus inspects the namespace through the gateway, finds the platform healthy, and reports in bold that no model is usable, while answering through that very model.
{{< /tldr >}}

## Step 1: register the service, and pick the right file

The Private AI Services download for VCF 9.1.1 contains two service definitions, `pais-3.0.0.yml` and `pais-3.0.0-external.yml`. They differ in exactly one line, the source of the package bundle:

```diff
-          image: depot.kube-system.svc/vcf/supervisor-service-pais/ga/3.0.0/pais:3.0.0
+          image: pais-docker.packages.broadcom.com/pais-bundle-3.0.0@sha256:122ae0cc...
```

The first one expects the bundle in a depot inside the Supervisor, which VCF's content distribution fills. On a vCenter-only Supervisor that depot is empty, which is most likely why my first, quick attempt failed. The `-external` file pulls from Broadcom's registry, so the Supervisor needs credentials for it: **Supervisor → Configure → Container Registries → Add**, host `pais-docker.packages.broadcom.com`, user name your Broadcom Support Portal e-mail, password a registry token from the portal (My Downloads → Registry Tokens).

**Trap 1: the registry test that lies.** Before typing the token into vCenter I wanted to know it works. A plain `curl -u` against the package path answered 401 with a perfectly good token, because the registry wants the bearer flow that Docker and the Supervisor use. `curl -u` is only meaningful against `/v2/` itself. This one-liner does the real thing, asks for the token and keeps it out of the shell history:

```bash
# on your workstation; replace <portal-email>. Expect 200.
read -rs 'T?Registry token: '; echo
B=$(curl -s -u "<portal-email>:$T" 'https://pais-docker.packages.broadcom.com/artifactory/api/docker/pais-docker/v2/token?service=pais-docker.packages.broadcom.com&scope=repository:pais-bundle-3.0.0:pull' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin).get("token",""))')
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $B" \
  -H 'Accept: application/vnd.oci.image.manifest.v1+json' \
  https://pais-docker.packages.broadcom.com/v2/pais-bundle-3.0.0/manifests/sha256:122ae0cc0645e68e44cf42ecbfef41b9ca22a3202e0f91874d542d6dddd1944b
unset T B
```

Then **Supervisor Management → Services → Add New Service**, upload the `-external` file, and **Manage Service** on the new card to install version 3.0.0 on the Supervisor. Compatibility check and signature verification both passed. The status showed "Error" for about a minute while the service reconciled, then "Configured".

## Step 2: activate PAIS in a namespace, from vCenter

The namespace `pais` from part 1 already had the storage policy and a few VM classes. Activation lives under **Namespace → Resources → Services → Private AI → Configure Service**. The wizard shows the resulting `PAISConfiguration` as YAML on the right, which is the best documentation of what each click does. My choices:

| Step | Choice | Why |
|---|---|---|
| Service capabilities | Model Runtime only | No PostgreSQL needed; Data Indexing and Agent Builder can be added later |
| Storage | `k8s-990pro` | the tag-based policy from part 1 |
| vSphere Kubernetes Service (VKS) control plane | `best-effort-large` | the control plane needs no GPU |
| User access | local user accounts, issuer base URL `https://pais.vcf.internal` | proof of concept only, says the wizard, and it is right |
| GPU driver | Use CPUs only | the GPU comes in part 3; no NVIDIA catalog key needed |
| Observability | off | can be switched on later |

![PAIS UI with Data Indexing and Retrieval, MCP, Agent Builder and Observability locked, and the message "Data Indexing and Retrieval is not available"](/images/private-ai-services-without-a-gpu/data-indexing-not-available.jpg)
*What "Model Runtime only" looks like from the inside: everything except the gateway is locked until an administrator switches it on.*

"Create Private AI Instance" at 10:33, **Ready (paisAvailable) at 10:37**. The ingress got the next free virtual IP from the Foundation Load Balancer; vCenter shows it as "Private AI Services UI IP" together with the OpenAI-compatible base URL. One DNS record later, the PAIS UI answered on its name. The question I had after part 1, whether the built-in L4 load balancer is enough for PAIS, has its answer: for the gateway, yes.

![vCenter inventory: namespace pais with the VKS cluster pais-30695622, its control plane VM and the pods pais-api, pais-igr-monitor and pais-ingress](/images/private-ai-services-without-a-gpu/vcenter-inventory-pais.jpg)
*The instance in vCenter: one small VKS cluster for the control plane, plus the API, gateway monitor and ingress as vSphere Pods. The host barely notices.*

![Private AI Services login page](/images/private-ai-services-without-a-gpu/pais-login.jpg)
*One DNS record later: the login page on its own name.*

## Step 3: put Claude behind the gateway

PAIS 3.0 supports third-party cloud models natively: Google Gemini, Gemini Enterprise Agent Platform and any OpenAI-compatible inference service. There is no button for it in vCenter. It is a resource in the namespace, documented in Broadcom's "Connect to a Remote Model Running in the Cloud":

```yaml
# pais-route-claude.yaml
apiVersion: pais.vmware.com/v1alpha1
kind: InferenceGatewayRoute
metadata:
  name: claude-opus-5-5
  namespace: pais
spec:
  type: Completions
  engine: OpenAI                         # any OpenAI-compatible chat completions API
  matches:
    routingName: claude-opus-5-5         # the model name your clients use
  backend:
    httpBaseUrl: https://api.anthropic.com/   # no /v1, PAIS appends it
    modelId: claude-opus-5-5
    tls:
      verification: strict
    auth:
      apiTokenRef:
        name: anthropic-api-key
```

The key goes into a Secret of a PAIS-specific type. Again read from the prompt, so it never lands in the shell history or a file:

```bash
kubectl config use-context pais
read -rs 'K?Anthropic API key: '; echo
printf %s "$K" | kubectl -n pais create secret generic anthropic-api-key \
  --type=pais.vmware.com/api-token-credentials --from-file=api_token=/dev/stdin
unset K
kubectl apply -f pais-route-claude.yaml
kubectl -n pais get inferencegatewayroutes
```

```text
NAME              ROUTE             TYPE          READY
claude-opus-5-5   claude-opus-5-5   Completions   False
```

**Trap 2: Ready False, and it works anyway.** `kubectl describe` explains it:

```text
Type: Routable        Status: True   Route is the active route for this routing name
Type: Reachable       Status: True   External backend is reachable
Type: ModelAvailable  Status: False  Backend returned an HTTP error for /models. HTTP status: 400
```

PAIS checks a remote backend by listing its models. Anthropic's compatibility layer covers `chat/completions`, but `/v1/models` is Anthropic's native endpoint and answers `anthropic-version: header is required`. The chat path works with the same key. Whether a route that reports Ready False keeps routing in later versions is not something I would bet production on; for a lab it is fine, and a tiny proxy that answers `/models` in OpenAI format would turn it green.

**Trap 3: API tokens are off after a UI activation.** The PAIS 3.0 release notes list it as a known issue. Two commands fix it and give the instance its name:

```bash
kubectl -n pais patch paisconfiguration default --type json -p \
  '[{"op":"add","path":"/spec/auth/providers/0/staticCredentials/apiTokens","value":{"expirationDefault":"720h","expirationMax":"8760h"}}]'
kubectl -n pais annotate paisconfiguration default paisconfigurations.pais.vmware.com/cname=pais.vcf.internal
```

The UI still said "API token generation is not available for your sign-in method" until I logged in again in a private window. Then: user menu → API Tokens → Generate.

![PAIS UI, API tokens page with the message "API token generation is not available for your sign-in method"](/images/private-ai-services-without-a-gpu/api-tokens-not-available.webp)
*Before: the session from before the patch still says no.*

![PAIS UI, API tokens page with an "Expires in" field and the button "Generate API token"](/images/private-ai-services-without-a-gpu/api-tokens-generate.webp)
*After a fresh login in a private window. Leave "Expires in" empty for the default of 720 hours.*

## The first answer

```bash
read -rs 'T?PAIS token: '; echo
curl -sk https://pais.vcf.internal/api/v1/compatibility/openai/v1/chat/completions \
  -H "Authorization: Bearer $T" -H 'content-type: application/json' \
  -d '{"model":"claude-opus-5-5","max_tokens":2000,"messages":[{"role":"user","content":"Nenne drei Flugsaurier, je ein Satz."}]}'
unset T
```

HTTP 200, 29 tokens in, 440 out, and three pterosaurs: Pteranodon, Quetzalcoatlus and Rhamphorhynchus from the Solnhofen limestone in Bavaria. My five-year-old would have approved of the question. What matters for the architecture is the path: the client only knows `pais.vcf.internal`, a model name and a token that my platform issued. Which model answers, and where it runs, is a route in my namespace.

## The highlight: Opus explains my lab, through my own gateway

A single chat answer proves the plumbing. I wanted to see something a gateway is really for: an application with tools, written once against my platform, that does not care which model sits behind it. So I wrote a small "lab concierge": about 100 lines of Python, standard library only, OpenAI-compatible request format, pointed at `pais.vcf.internal`. The model gets exactly one tool, and it is read-only:

```python
TOOLS = [{
    "type": "function",
    "function": {
        "name": "kubectl_get",
        "description": "Read-only: list Kubernetes resources in a vSphere Supervisor namespace and return them as JSON.",
        "parameters": {
            "type": "object",
            "properties": {
                "resource": {"type": "string", "enum": ["deployments", "events", "inferencegatewayroutes",
                             "paisconfigurations", "pods", "virtualmachines", "..."]},
                "namespace": {"type": "string", "enum": ["pais"]},
            },
            "required": ["resource", "namespace"],
            "additionalProperties": False,
        },
    },
}]
```

The script runs the call with my own `kubectl` login, refuses anything outside the allowlist (no Secrets, no other namespaces), hands the JSON back and loops until the model answers. I asked, in German: how is my PAIS namespace doing, what runs there, and should I look at anything?

```text
$ python3 lab-concierge.py
PAIS token:
[tool] kubectl get pods -n pais
[tool] kubectl get inferencegatewayroutes -n pais
[tool] kubectl get events -n pais
[tool] kubectl get deployments -n pais
[tool] kubectl get virtualmachines -n pais
[tool] kubectl get paisconfigurations -n pais

[claude-opus-5-5] tokens in 98008, out 2380
```

Six tool calls, chosen by the model, then a short report. The platform is healthy, all three PAIS pods run, the deployments at zero replicas are the features I switched off, and the vSphere Kubernetes Service control plane VM is up with its two disks attached. It even found the storage warnings from the first minutes of the rollout in the event list and correctly called them resolved.

And then the best line of the morning. Opus reported, in bold, that **no model in the namespace is usable**, because the only route, `claude-opus-5-5`, is not Ready. It wrote that while being served through exactly that route. It is the Ready False from trap 2, seen from the inside: the model can only read the status, not know that the status is wrong.

Its suggested fix was wrong as well, and honestly labelled: "my assumption, not verified". It proposed adding `/v1` to the base URL; the API reference says the opposite, PAIS appends `/v1` itself. That is the behaviour I want from an assistant on a platform: look first, separate what it saw from what it guesses, and leave the change to me.

The cost side, because the gateway is the place where you see it: almost 100,000 input tokens for one question, because every tool result (pods, events, a whole `PAISConfiguration`) goes back to the model as JSON. With a public model that is real money per question; with a local model in part 3 it is only GPU time. The concierge does not change for that. Only `--model` does.


## What I would do differently

- **Test credentials the way the consumer uses them.** Both of my "failed" tests in this part were tests that could not succeed: basic auth against a bearer registry, and a model list against an API that only mirrors chat completions.
- **Read the YAML pane in the wizard.** It shows exactly which fields the UI sets, and which ones it does not (API tokens).
- **Start with a public model on purpose.** It proves the whole chain (DNS, load balancer, gateway, auth, token) before any GPU is in the box. In part 3 the only change for the client is the model name.
- **Trim tool results before they reach the model.** The concierge already drops `managedFields`; it should also cut events and status down to what matters. Tokens are the bill.

Part 3 brings the RTX 3090 into the server, a VM class with the GPU in passthrough, and a local model next to Claude behind the same gateway. Then the concierge asks the same question twice, once per model, and we compare answers, tokens and time.
