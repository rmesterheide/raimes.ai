---
title: "Model as a Service, the bare minimum: AI models as a platform service with Private AI Services 3.0"
date: 2026-10-21T17:40:00+02:00
draft: true
written_with_claude: true
cover:
  image: "/images/covers/model-as-a-service-with-private-ai-services.jpg"
  alt: "Model as a Service, the bare minimum: AI models as a platform service with Private AI Services 3.0"
  hiddenInSingle: true
categories: ["vmware"]
tags: ["private-ai", "homelab"]
summary: "The smallest useful Private AI Services setup for a platform team: no agents, no knowledge bases, only model endpoints that application teams on the VMware stack consume like any other platform service. Three service names instead of model names, one request traced through every hop, metrics per service name, and what this bare minimum does not give you yet."
linkedin: ""
---

In [part 2](/posts/private-ai-services-without-a-gpu/) Claude went behind my private gateway, on a server without a GPU. Part 3 puts a local GPU behind that gateway. Before that, I wanted to look at the use case most customers actually start with, and which needs the least of Private AI Services (PAIS): **Model as a Service, the bare minimum.**

The setting is simple. A platform engineering team runs vSphere or VMware Cloud Foundation (VCF). Application teams deploy their apps on it, in virtual machines or on Kubernetes, and want AI model functions in those apps: summarise a ticket, classify a document, draft a reply. They should not have to sign their own contract with a model provider, store its key in their app, or learn its software development kit (SDK). They should consume models from the platform, the way they consume storage or a load balancer.

So this post leaves out everything else PAIS can do. No Agent Builder, no knowledge bases, no data indexing, no Model Context Protocol (MCP) servers, no PostgreSQL. Only the model runtime and its gateway, and the question every developer asks first: why not just `pip install` the provider's SDK?

A disclosure, as always: I work at Broadcom as a solutions architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement. And as in part 2, the Anthropic endpoint behind my routes is their OpenAI compatibility layer, which Anthropic describes as meant for testing and comparing models.

{{< tldr >}}
- The bare minimum is **"Model Runtime only"**: three small vSphere Pods, no database. App teams get a base URL, a token and a service name.
- Apps ask for **service names** (`lab-fast`, `lab-balanced`, `lab-deep`), not model names. Which model answers is one line in an `InferenceGatewayRoute`; in part 3 one name moves to a local GPU without an app noticing.
- One request crosses **four hops**. The app's token ends at the ingress, the provider key never leaves the namespace. The platform adds about **30 ms** to a two-second answer.
- The answer does not say which model answered: the `model` field echoes the service name. Metrics count per service name too.
- Not in the bare minimum, and not in PAIS 3.0 at all: quotas, rate limits, access per model.
{{< /tldr >}}

## What the bare minimum is

In part 2 I activated PAIS in the mode the wizard calls "Model Runtime only". That turned out to be exactly this use case. What runs:

- **`pais-ingress`**: the entry point behind the load balancer, with the token check.
- **`pais-api`**: the gateway that routes requests to a model.
- **`pais-igr-monitor`**: checks the backends of the routes.

All three are vSphere Pods in one Supervisor namespace. The components for indexing, metrics and the like exist as deployments with zero replicas; they cost nothing until someone switches them on. The vSphere Kubernetes Service (VKS) cluster of the instance has one control plane node and no workers. It only gets work once local model endpoints arrive.

What an application team receives from the platform team is three values:

```bash
export OPENAI_BASE_URL=https://pais.vcf.internal/api/v1/compatibility/openai/v1
export OPENAI_API_KEY=<PAIS API token for this app>
MODEL=lab-fast

curl -sk "$OPENAI_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" -H 'Content-Type: application/json' \
  -d "{\"model\":\"$MODEL\",\"max_tokens\":200,\"messages\":[{\"role\":\"user\",\"content\":\"Name one dinosaur that could fly, in one short sentence.\"}]}"
```

Any client that speaks the OpenAI chat completions format works with that, which covers most libraries and frameworks app teams already use. (`-k` because my lab certificate is not trusted by clients yet; in a real setup the ingress gets a proper certificate.)

## Three service names instead of model names

Part 2 ended with one route, `claude-opus-5-5`, whose routing name was the model name. That works, but it hard-wires every app to a model. For a catalogue I added two direct routes for Sonnet and Haiku, and then three neutral names on top:

| Service name | Model behind it today |
|---|---|
| `lab-fast` | `claude-haiku-5-5` |
| `lab-balanced` | `claude-sonnet-5-5` |
| `lab-deep` | `claude-opus-5-5` |

Each is a small Kubernetes resource. The interesting part is that `routingName` and `modelId` are two separate fields:

```yaml
apiVersion: pais.vmware.com/v1alpha1
kind: InferenceGatewayRoute
metadata:
  name: lab-fast
  namespace: pais
spec:
  type: Completions
  engine: OpenAI
  matches:
    routingName: lab-fast              # what apps ask for
  backend:
    httpBaseUrl: https://api.anthropic.com/
    modelId: claude-haiku-5-5          # what answers, today
    auth:
      apiTokenRef:
        name: anthropic-api-key       # same Secret for all routes
```

All six routes share one Secret. All six show `Ready False` for the reason from part 2 (Anthropic's `/models` endpoint wants a header PAIS does not send), and all six answer. One more thing I had not expected: in "Model Runtime only" mode the PAIS UI shows neither routes nor models. The catalogue exists only in `kubectl`, so in a lab without VCF Automation, the platform team hands out the service names by hand.

## One request, four hops

I wanted to know what actually happens between an app and Anthropic, without guessing. A read-only inventory script, the nginx configuration of the ingress, the role-based access control (RBAC) rules of each component and the logs of one test minute gave this picture:

![Diagram: client, Foundation Load Balancer, pais-ingress, pais-api and api.anthropic.com from left to right, below them the two keys, the service-name table and the route monitor](/images/model-as-a-service-with-private-ai-services/pais-gateway-request-path.svg)
*One request through the gateway, built from the lab's configuration and logs on 21 October 2026.*

1. **Foundation Load Balancer.** The virtual IP from part 1. Plain layer 4.
2. **`pais-ingress`**, nginx with an `auth` sidecar. Every request under `/api/v1/compatibility/openai/` first goes to `auth_request /auth/validate`, which the sidecar answers on localhost. A wrong token gets its 401 here, in about 20 ms, before anything else is touched.
3. **Mutual TLS (mTLS) to `pais-api`**: nginx in front of a Python service. Its role may read routes and Secrets. This is the actual gateway: it looks up the route by name, takes the provider key from the Secret and calls the backend.
4. **`api.anthropic.com`**, the only hop that leaves the platform.

Off the path, `pais-igr-monitor` asks every backend for `/models` and writes the route status. That is where the `Ready False` comes from.

The cost of the extra hops is small. For the `lab-fast` request, `pais-api` logged the request in and out 2.08 seconds apart; the client measured 2.11 seconds to the first byte. Load balancer, ingress, token check and mTLS together: about 30 ms. The rest is the model. One request per name, not streamed, so treat the numbers as an order of magnitude:

| Service name | Time to first byte |
|---|---|
| `lab-fast` | 2.1 s |
| `lab-balanced` | 1.6 s |
| `lab-deep` | 1.7 s |

## The answer does not say who answered

This was the result I liked best. Every answer comes back with token usage, and with a `model` field. I expected `claude-haiku-5-5` in it. It says `lab-fast`.

The app knows a service name and does not know the supplier. It also means the app cannot tell which model wrote the answer, which matters the day someone asks why an answer got worse. The answer to that question lives in the platform, in the route and its history. Routes kept in Git, like any other resource, give you that audit trail without extra work.

## Metrics per service name

Part 2 activated PAIS with metrics off. Switching them on later is one field in the `PAISConfiguration`; vCenter shows the same switch under the instance's Service Configuration. It still needs no database:

```bash
kubectl -n pais patch paisconfiguration default --type merge \
  -p '{"spec":{"observability":{"prometheusRuntime":{"storageClassName":"k8s-990pro","metricsRetention":"30d"}}}}'
```

A managed Prometheus came up within minutes. The Metrics page in the PAIS UI stayed locked anyway. **Trap 1:** the UI reads its feature switches from `/env.json`, and that file comes from the ingress pod, which the patch did not restart. One `kubectl -n pais rollout restart deployment pais-ingress-<id>` later, the page was open.

It then showed zero requests. **Trap 2:** the charts ask Prometheus for `increase(inference_gateway_inference_request_total{routing_name="lab-fast"}[300s])`. A counter that is created with the first request has no earlier value, so that first request never shows. A dozen short requests later:

![PAIS metrics page, Model Metrics for all models over one hour: about six requests per five-minute step and up to about 1,200 tokens, the model list open with lab-balanced, lab-deep and lab-fast](/images/model-as-a-service-with-private-ai-services/pais-metrics-by-service-name.jpg)
*The model list in the metrics page knows the service names, not the models behind them.*

Note the drop-down. The gateway counts requests and tokens per service name. For a platform team this is the fitting unit, because applications consume service names.

## Why broker models at all

Here is my answer for the customer conversation, with what the lab showed:

| Topic | Every app team connects the provider directly | Through the platform |
|---|---|---|
| Keys | The provider key sits in every app; rotating it touches all of them | One Secret in the namespace; apps get PAIS tokens with an expiry date (30 days by default) |
| Change | Provider, SDK and model ID are hard-wired | `lab-fast` changes its backend with one `kubectl apply` |
| Interface | One SDK per provider | One OpenAI-compatible endpoint for cloud and, later, local models |
| Visibility | One total on the provider's invoice | Usage in every answer, metrics per service name |

And what the bare minimum does not do, in PAIS 3.0 and as far as I can see in the documentation: no quotas, no rate limits, no access rules per model. A token is valid for every route of the instance. So the hard cost guardrail for now is a spend limit on the provider's side, not in PAIS. The gateway also adds a hop, which costs 30 ms, and in my lab every component runs once, without high availability.

If the application stack already runs on vSphere or VCF, this is where the benefit is: models become one more platform service next to storage and network, declared and versioned like everything else, and app teams consume them without leaving the platform. The developer benefit really shows once the platform offers it as self-service, which is what VCF Automation adds with tenants, a catalogue and quotas. In my vCenter-only lab, I hand out the service names myself.

## What I would do differently

- **Name services, not models, from day one.** Renaming a route later means touching every app.
- **Hand out three values, not a provider account.** Base URL, token, service name. Everything else stays on the platform side.
- **Give every app its own user and token.** Tokens belong to users, and that is the only "per consumer" handle PAIS gives you today.
- **Restart the ingress after changing observability, and send a little traffic before judging the charts.** Both traps cost me half an hour.

Since I wrote this, `lab-fast` has already moved once: to a model on a GPU outside the platform, Ollama on my workstation, with one `kubectl apply` and no change on any client. In part 3 a refurbished RTX A5000 goes into the server itself (the 3090 is sold), `lab-fast` moves again, this time to a local model inside Private AI Services, and the apps from this post still do not change a single line.
