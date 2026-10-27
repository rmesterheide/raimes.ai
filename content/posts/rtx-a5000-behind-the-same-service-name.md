---
title: "Route to Private AI Services 3.0, part 3: a refurbished RTX A5000 behind the same service name"
date: 2026-10-27T20:50:03+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/rtx-a5000-behind-the-same-service-name.jpg"
  alt: "Route to Private AI Services 3.0, part 3: a refurbished RTX A5000 behind the same service name"
categories: ["vmware"]
tags: ["private-ai", "homelab", "gpu"]
summary: "Part 3 of my route to Private AI Services 3.0: a refurbished RTX A5000 goes into the single-host lab, passthrough without a reboot, the platform switches from CPU only to GPU with one kubectl patch, and the first local model is ready six minutes after apply. Then the numbers: the same model on 16 CPU cores and on the card, a 27B model, Ollama on my workstation and Claude, all through the same gateway, one request and eight at once. And what passthrough cannot do, which is where part 4 starts."
linkedin: "https://www.linkedin.com/feed/update/urn:li:activity:7520939694763872256/"
---

[Part 2](/posts/private-ai-services-without-a-gpu/) ended with a promise: the RTX 3090 moves from the Ubuntu GPU instance into the ESX server. It did not. The 3090 found a new home, and I could not resist a refurbished RTX A5000 for the lab instead: 24 GB, 230 W, one power connector, on the vSphere compatibility list for both passthrough and vGPU. The last point is the reason. The 3090 could only ever do passthrough; this card can do both, which is what parts 4 and later need. And since the A5000 has an NVLink connector, a sibling may follow one day.

So this part is the one with a GPU inside the platform. The setting is unchanged from parts 1 and 2: one EPYC host with ESX 9.1.1, a vSphere Supervisor, Private AI Services (PAIS) 3.0 activated from vCenter alone, no VMware Cloud Foundation (VCF) Automation. Read it as a lab route, not as a reference architecture; part 2 has the list of what the full VCF stack adds.

A disclosure, as always: I work at Broadcom as a solution architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement. The Anthropic numbers below come through Anthropic's OpenAI compatibility layer, which Anthropic describes as meant for testing and comparing models.

{{< tldr >}}
- **Passthrough without a reboot.** One `esxcli` line on the host switched the card to passthrough; ESX took the audio function along and reported both owned by "VM" at once.
- **From "CPU only" to GPU is one patch.** The platform was activated a week before the card existed. Adding three fields to the `PAISConfiguration` installed the NVIDIA GPU Operator in 30 seconds. No re-activation, the routes kept answering.
- **Six minutes from apply to a local model.** Worker VM with the card, driver built on the node, 16.5 GB model pulled from Harbor, llama.cpp listening. The models live in the lab's own Harbor registry: one `vcf pais models push` from the workstation, and they show up in the Model Gallery of the PAIS UI as a catalogue to deploy from. The only vSphere UI step on the way was the VM class.
- **7.6 times faster than 16 CPU cores** on the same model and the same artifact; eight clients together get five times what one client sees from one 230 W card.
- **What passthrough cannot do:** 15 GB of the card sat idle and no second endpoint could use them. That is the problem part 4 solves with vGPU.
{{< /tldr >}}

## The card goes in, the host stays up

The physical part was the easy part: shut the lab down in the right order (the Supervisor keeps resurrecting VMs you power off under it, so vCenter goes first), open the box, seat the card in the x16 slot, boot. ESX saw it right away:

```text
0000:c1:00.0 VGA compatible controller: NVIDIA Corporation GA102GL [RTX A5000]
0000:c1:00.1 Audio device: NVIDIA Corporation GA102 High Definition Audio Controller
```

The documented way to enable passthrough is the vSphere Client: host, Configure, PCI Devices, Toggle Passthrough, then reboot. I wanted to see whether the reboot is really needed, so I used the command line with the `--apply-now` flag:

```bash
esxcli hardware pci pcipassthru set --device-id 0000:c1:00.0 --enable true --apply-now
```

The second call for the audio function came back with "Device owner is already configured to passthru": ESX had switched the whole device. A moment later both functions showed `Configured Owner: VM, Current Owner: VM`. No reboot, no maintenance window. The documentation reboots unconditionally, and for a production host I would too; in the lab it was good to know that the switch itself is instant.

## From "CPU only" to GPU in one patch

Here is the part I did not expect. When I activated PAIS in part 2, the wizard asked how models would run: on CPUs only, on vGPU, or on GPU passthrough. I picked CPU only, because there was no GPU. That looked like a decision made at activation.

It is not. The API treats it as a day-two setting. The whole change was this:

```bash
kubectl -n pais patch paisconfiguration default --type merge -p '{
  "spec": {"nvidiaConfig": {
    "gpuDriverType": "OSS",
    "gpuOperatorVersion": "25.10.1",
    "driver": {"version": "580.105.8"}
  }}}'
```

`OSS` is the data-center driver type for passthrough; it needs no NVIDIA licence and no NVIDIA GPU Cloud (NGC) credentials, which is exactly what makes passthrough the natural first step. The two version numbers are the ones PAIS 3.0 ships (the alternatives are GPU Operator 26.3.1 and driver 580.126.20; the release notes have the matrix).

Thirty seconds later the GPU Operator, its node-feature-discovery pods and a job that upgrades the custom resource definitions (CRDs) were running in the vSphere Kubernetes Service (VKS) cluster behind the instance, and the `PAISConfiguration` reported `GPUOperatorReady=True`. The three public routes from part 2 answered throughout. The driver itself does not appear yet at this point: the driver daemonset only starts when a node with a GPU exists, and that comes with the first endpoint.

Start on CPU, add the card later, patch three fields. I would put that sentence on the slide.

## The VM class, the only click

The one thing that lives in the vSphere Client is the VM class that carries the GPU. Mine is called `a5000-passthrough`: 8 vCPUs, 64 GB of memory, **fully reserved**, which DirectPath I/O requires, the RTX A5000 as a Dynamic DirectPath I/O device, and two advanced parameters for memory-mapped I/O (MMIO), because the card maps more than 16 GB:

```text
pciPassthru.use64bitMMIO        = true
pciPassthru.use64bitMMIOSizeGB  = 64
```

The sizing rule from the documentation: frame buffer per GPU times number of GPUs, rounded up to the next power of two, and once more if the result was not a power of two already. 24 GB becomes 32 becomes 64. Then the class is assigned to the namespace, and from here on everything is YAML again. The Supervisor shows the device in the class as vendor `4318` and device `8753`, which is `10de:2231` in the hex the host prints.

## Harbor, the model gallery, and the endpoint

The models live in a Harbor registry on the VCF Infrastructure Services (VIS) appliance in the lab, which also does DNS. Pushing a model is one command from the VCF command line, run on my workstation where the download lands:

```bash
vcf pais models push --modelStore vis.vcf.internal:9443/models \
  --modelName google/gemma-4-12b-qat-gguf --tag v1
```

The CLI validates what it pushes (weights plus a config, or a GGUF file), and the result shows up in the PAIS UI under Model Gallery, where an endpoint can be created with a few clicks. I used YAML, because I wanted the manifest in Git. This is the whole endpoint:

```yaml
apiVersion: pais.vmware.com/v1alpha1
kind: ModelEndpoint
metadata:
  name: gemma-4-12b-a5000
  namespace: pais
spec:
  type: Completions
  engine: LlamaCPP
  model:
    ociRef: vis.vcf.internal:9443/models/google/gemma-4-12b-qat-gguf:v1
    pullSecrets:
      - name: pais-pais-reg-creds-<instance-id>
  routingName: gemma-4-12b-a5000
  replicas: 1
  virtualMachineClassName: a5000-passthrough
  storageClassName: k8s-990pro
  inferenceServerCustomization:
    engineImage: ghcr.io/ggml-org/llama.cpp:server-cuda-b11913
    cliArgs: ["--n-gpu-layers", "99", "--ctx-size", "16384", "--flash-attn", "on",
              "--reasoning-budget", "0", "--jinja", "--metrics"]
```

Two lines in there are traps I walked into.

**Trap 1: the bundled llama.cpp is CPU only.** PAIS 3.0 ships llama.cpp `b9309` without CUDA. Without the `engineImage` override the endpoint would come up on the GPU node and run on its eight vCPUs. The release notes say so, in one sentence; I read it after the fact. The public CUDA image from the llama.cpp project works as a drop-in, and PAIS pulls it from `ghcr.io` without further configuration.

**Trap 2: thinking models answer with nothing.** My CPU baseline earlier the same day returned empty answers through the gateway. Gemma 4 and Qwen3.8 both reason before they answer, and with a small `max_tokens` the reasoning eats the whole budget. `--reasoning-budget 0` on the engine, or `reasoning_effort: none` per request, fixes it. For a service name that application teams consume, I would set it on the engine: the client should not need to know which model family is behind `lab-fast`.

Then the timeline, from `kubectl apply`:

| Minute | What happened |
|---|---|
| 0 | worker VM registered from the GPU class |
| 1 | VM powered on with the card attached, no MMIO error |
| 4 | node joined the VKS cluster, driver daemonset built and loaded the 580.105.08 module, `nvidia.com/gpu: 1` allocatable |
| 5 | init container pulled the model from Harbor (the 27B model, 16.5 GB, took about two minutes) |
| 6 to 7 | llama-server loaded the model in 3.4 seconds, endpoint Ready, `AVAILABLE` in `/models` |

Seven minutes for Gemma, six for Qwen3.8 27B. `nvidia-smi` from the driver pod afterwards: driver 580.105.08, CUDA 13.0, `/app/llama-server` holding 16.7 GB for the 27B model and 8.7 GB for the 12B.

## The numbers

Everything below went through the same gateway, with the same prompt (an essay request that always hits 400 output tokens), from the same client. One request alone, then eight at once. The local models got `reasoning_effort: none`.

![Bar chart: tokens per second through the same gateway for six backends, one request and eight requests at once](/images/rtx-a5000-behind-the-same-service-name/tokens-per-second.svg)
*Same gateway, same prompt, 400 tokens per answer, 27 October 2026. Single requests on the left bar, eight concurrent requests added up on the right bar.*

| Backend through the gateway | Model | tok/s, one request | tok/s, eight at once | per request at eight | where the data goes |
|---|---|---|---|---|---|
| PAIS endpoint, 16 vCPU | Gemma 4 12B | 9.3 | not run | | lab |
| PAIS endpoint, RTX A5000 | Gemma 4 12B | 72.6 | 200 to 351 | 25 to 44 | lab |
| PAIS endpoint, RTX A5000 | Qwen3.8 27B | 31.2 | 154 | 19 | lab |
| Route to Ollama on my workstation (RTX 4090) | qwen3:14b | 70.5 | 103 | 13 | lab, outside the platform |
| Route to Anthropic | Claude Haiku 5.5 | 83.9 | 703 | 88 | provider |
| Route to Anthropic | Claude Sonnet 5.5 | 107.1 | 741 | 93 | provider |

Three things I take from the table.

**Same model, same artifact, 7.6 times faster.** The Gemma rows are the like-for-like pair: the identical GGUF file from Harbor, llama.cpp in both cases, once on 16 vCPUs of the EPYC, once on the card. 9.3 against 72.6 tokens per second, and the 250-token answer arrives in 3.5 seconds instead of 27. The CPU side was not tuned, so treat the factor as a floor, not a benchmark.

**One user cannot tell the backends apart; eight can.** For a single request the A5000, the 4090 and Haiku land within 70 to 84 tokens per second. The difference is what happens under load. Eight clients get five times the single-client throughput out of the A5000, because llama.cpp batches them across its slots. Ollama on the workstation serialises and drops to 103 in total. The provider does not care and delivers 700 and more. That is the honest shape of the comparison: a local card wins on data locality and on cost per token once it is busy, the provider wins on burst and on scale.

**The platform costs a second you can see.** The engine's own log shows the first token after 0.1 seconds; through the gateway the first token of a streamed answer took 1.1 to 1.5 seconds. Part 2 measured the gateway hops at about 30 milliseconds, so this is not the token check. My guess is buffering in the ingress or in the nginx sidecar in front of llama-server, and I have not proven it yet. Ollama behind the same gateway streams its first token after 0.14 seconds, so the gateway can do better. Open item.

**Why llama.cpp and not vLLM.** PAIS 3.0 bundles vLLM v0.20.0, and for many concurrent users that is the engine to use: continuous batching and paged attention are built for exactly the eight-client case above. I used llama.cpp because the models are GGUF files I could compare one-to-one with the CPU run and with Ollama on the 4090, and because the 27B model only fits the card as a 4-bit GGUF. So read the concurrency numbers as what llama.cpp makes of the card, not as the card's ceiling. The same models on vLLM, with an FP8 build of a smaller model, are the next measurement.

One more honest note on the Gemma row: the eight-request run gave 351 tokens per second from my MacBook and 200 from the Mac mini twenty minutes later, same endpoint, same prompt. I show the range rather than pick the number I like.

## The swap

This is the demo the whole series was building towards. In part 2, `lab-fast` was Claude Haiku. Since then it has pointed to Ollama on my workstation. Tonight it points at the card inside the platform.

PAIS creates an `InferenceGatewayRoute` for every endpoint; its backend is the endpoint's Kubernetes service, with mutual TLS. Repointing a service name means giving the `lab-fast` route that backend:

```yaml
apiVersion: pais.vmware.com/v1alpha1
kind: InferenceGatewayRoute
metadata:
  name: lab-fast
  namespace: pais
spec:
  type: Completions
  engine: LlamaCPP
  matches:
    routingName: lab-fast
  backend:
    httpBaseUrl: https://pais-modelendpoint-<id>   # copied from the endpoint's own route
    modelId: gemma-4-12b-a5000
    tls:
      verification: mutual
```

**Trap 3: the engine of a route is immutable.** My first `kubectl apply` came back with `Model engine is immutable`. The route had been created with engine `OpenAI` for Haiku and later for Ollama, and PAIS will not let it become `LlamaCPP`. Delete and recreate, which leaves the name unroutable for a few seconds. For a real platform that means: a service name that may ever move between engine types is a delete-and-create operation, so plan the second of downtime, or keep two routes and switch clients between them.

Ten seconds after the recreate, the first request to `lab-fast` with a fresh prompt answered: "I am Gemma 4, a large language model developed by Google DeepMind." No client changed. The concierge from part 2, the curl examples from the bare-minimum notes, the service name: all the same. One more quirk, the same family as the `Ready False` of part 2: the route reports `ModelAvailable=False`, because the monitor's model check does not find `gemma-4-12b-a5000` in what llama-server advertises, while every request works. `/models` lists `lab-fast` as `UNAVAILABLE` and answers through it anyway. The status is a hint, not a gate.

![Diagram: client, Foundation Load Balancer, pais-ingress, pais-api and the ModelEndpoint on the GPU node from left to right; below, what changed since part 2, the service-name table with lab-fast pointing at gemma-4-12b-a5000, and api.anthropic.com still behind lab-balanced and lab-deep; the measured numbers in a band at the bottom](/images/rtx-a5000-behind-the-same-service-name/pais-gateway-request-path-gpu.svg)
*The same request path as in the bare-minimum diagram, now with the card at the end of it. Built from the lab's configuration and the measurements of 27 October 2026.*

Then the concierge from part 2, unchanged, asked its question twice. With `--model claude-opus-5-5`: six tool calls, 124,138 tokens in, 1,740 out, 21 seconds, and a correct report (platform healthy, one control plane VM and one GPU worker, the api pod restarted once at boot). With `--model lab-fast`, now Gemma on the A5000: the first tool call went out, the first tool result came back, and the gateway answered with HTTP 400:

```text
request (46894 tokens) exceeds the available context size (16384 tokens), try increasing it
```

**Trap 4: the context window is a sizing decision, not a model property.** The deployment list of the namespace, even with `managedFields` stripped, is bigger than the 16k context I gave the endpoint. Opus took the same payload without blinking, and it costs real money per question for exactly that reason. The fix is on my side: `--ctx-size 65536` on the engine (the 12B model leaves room for it on the card), and a concierge that trims tool results to what the question needs, which part 2 already listed as a lesson. The honest result tonight is that the same client works against the public model and fails against the local one, and the gateway told me precisely why.


## What passthrough cannot do

With the 12B model loaded, `nvidia-smi` showed 8.7 GB used and 15 GB free. I could not give those 15 GB to anyone. Passthrough binds the card to one VM, the VM is one VKS node, and PAIS runs one endpoint per node. When I wanted to measure Gemma after Qwen, the Qwen endpoint had to go first; the second worker could not even power on while the first held the card. There is no vMotion for a passthrough VM either, and on my single host no high availability anyway.

For one model that fills the card this is fine, and it is the cheapest possible path: no NVIDIA licence, public driver, public operator. For two small models, for an embedding model next to a chat model, for a knowledge base and an agent on the same card, it is not. That is what vGPU is for, and that is part 4.

## What I would do differently

- **Activate on CPU, add the GPU later.** It costs nothing and it is one patch. Do not wait for the card to start the platform.
- **Pin the engine image and the thinking switch on the endpoint, not on the client.** The bundled llama.cpp is CPU only, and reasoning models return empty answers; both belong in the manifest.
- **Measure under concurrency, not alone.** The single-request numbers hide the whole story.
- **Write the shutdown order down.** On a single host the Supervisor and vCenter fight you if you power things off in the wrong order; I lost half an hour and collected eight orphaned pod VMs before I got it right.

## What comes next

- **Part 4: vGPU on the same card.** The licence chain, the host driver, VM classes with profiles, two endpoints side by side on one A5000, and the overhead against the passthrough numbers above.
- **Part 5: full capabilities.** Knowledge bases with an embedding model on CPU, and the PostgreSQL that unlocks the rest.
- **Part 6: Model Context Protocol servers and the Agent Builder** in PAIS.
- Outside the numbering: the economics. Cost per token from these measurements, the break-even utilisation at which a local card beats the API, and what the platform governs and what it does not.
