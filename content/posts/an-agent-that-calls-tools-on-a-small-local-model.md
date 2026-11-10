---
title: "Route to Private AI Services 3.0, part 5: from model endpoints to knowledge bases, agents and MCP tools"
date: 2026-11-10T07:53:27+01:00
draft: false
written_with_claude: true
cover:
  image: "/images/covers/an-agent-that-calls-tools-on-a-small-local-model.jpg"
  alt: "Route to Private AI Services 3.0, part 5: from model endpoints to knowledge bases, agents and MCP tools"
categories: ["vmware"]
tags: ["private-ai", "homelab", "agents", "mcp", "vgpu", "benchmark"]
summary: "Part 5 turns on the full set of Private AI Services 3.0 capabilities, connects a tool server over the Model Context Protocol and builds the first agent. A Qwen3 4B model on a 4 GB virtual GPU slice answered 24 of 30 questions in a usable way. One line in the agent instructions made it 30 of 30, in less than half the time. Then the agent gets the lab documentation as a knowledge base and read access to vCenter, and a small page shows every step it takes."
linkedin: "https://www.linkedin.com/feed/update/urn:li:activity:7525814884509458432/"
---

Parts 1 to 4 of this series built model endpoints: first with Claude behind the gateway, then with a local model on a GPU, then with six endpoints on one card. Since part 2 the Private AI Services (PAIS) UI has shown Data Indexing and Retrieval, Model Context Protocol (MCP) and Agent Builder as locked. This part unlocks them. It connects a small tool server over MCP, builds one agent and measures how well small local models call tools. In the last section the agent gets the lab documentation and read access to vCenter.

The setting is the same as in the earlier parts: one EPYC host with ESX 9.1.1, a vSphere Supervisor, and PAIS 3.0 activated from vCenter. PAIS 3.0 is fully supported on a plain vSphere and vCenter basis, and that is what I rebuild here. I would like to use the multi-tenancy and the NSX-based Virtual Private Cloud (VPC) features of VMware Cloud Foundation (VCF) as well, but this is a small lab. "Plain vSphere and vCenter" describes how the lab is built, not how it is licensed. For licence questions, please use the [official Broadcom documentation](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/requirements-for-deploying-private-ai-foundation-with-nvidia.html). The card is a refurbished RTX A5000 with 24 GB, shared as virtual GPU (vGPU) slices as in [part 4a](/posts/from-passthrough-to-vgpu-slices-in-one-evening/).

A disclosure, as always: I work at Broadcom as a solutions architect for infrastructure. This is my lab and my own reading of public documentation, not an official statement. The NVIDIA software runs on a 90-day NVIDIA AI Enterprise evaluation that I requested as a private person for this lab.

{{< tldr >}}
- **The full service needs a PostgreSQL database with the pgvector extension.** In the lab one vSphere Pod was enough. The activation restarted all six model endpoints for about 25 minutes, so plan it as a maintenance window.
- **An MCP server is registered with a URL, a transport and a credential header.** Its tools arrive as "Not approved", and an agent can only use approved tools.
- **The lab example: a Qwen3 4B model on a 4 GB slice gave 24 usable answers out of 30.** With `/no_think` as the first line of the agent instructions it gave 30 correct answers out of 30. The median time went from 3.1 to 1.4 seconds.
- **A larger model was not better.** Qwen3 14B on a second machine gave 22 complete answers out of 30 and needed a median of 9.9 seconds, because the agent could not switch off its thinking. Qwen3 8B on an 8 GB slice gave 30 of 30 without any switch.
- **Going further:** 70 pages of lab documentation as a knowledge base, a read-only MCP server for vCenter with 33 tools, a page that shows every tool call, search and token count of the agent, and a sketch of what twelve such servers could do for a platform team.
{{< /tldr >}}

## A PostgreSQL database for the lab

The PAIS instance of this lab was activated in "Model Runtime only" mode. Knowledge bases, MCP servers and agents need a PostgreSQL database with the pgvector extension. The Broadcom page [Enable the Full Set of Private AI Services 3.0 Capabilities by Using the UI](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/installing-and-configuring-private-ai-services/enable-the-full-set-of-private-ai-services-capabilities.html) names two ways to get one: a database from VMware Data Services Manager, created in VCF Automation, or "Bring your own PostgreSQL database". My lab has no VCF Automation, so I took the second way.

The database runs as a vSphere Pod in the same Supervisor namespace as PAIS: the public image `pgvector/pgvector:pg16`, one replica, a 20 GB persistent volume and a load balancer address. Its certificate comes from a small certificate authority (CA) that I created for this purpose, so PAIS can connect with full verification. For a platform that teams depend on I would use Data Services Manager.

In vCenter the switch is in the Service Configuration of Private AI: **Enable Full Service**. Three things happened after I clicked Enable, and I would check all three before doing this on a shared platform.

- **Check 1, the registry token.** The activation pulls two new images from the PAIS bundle. Both pods stayed in `ErrImagePull`, because the token for the Broadcom registry that the Supervisor had stored was no longer valid. I renewed it in vCenter and the job continued by itself.
- **Check 2, the rights of the database user.** The setup job creates a second, restricted database user. My user owned the database but could not create roles, and the job stopped with `permission denied to create role`. `ALTER ROLE pais CREATEROLE CREATEDB;` fixed it.
- **Check 3, the model endpoints restart.** The activation rolled the control plane of the PAIS cluster and recreated the pods of all six model endpoints. All six answered again after about 25 minutes.

## A tool server with four tools

MCP is the protocol that lets an agent call tools on another system. For the first test I wanted a server that I understand completely, so I wrote one with the official Python library for MCP. It has four tools: `add` adds two numbers, `lab_time` returns the time on the server, `lab_hosts` returns a table of the lab hosts with role and address, and `pais_models` asks the PAIS gateway which models it offers. The server runs as a vSphere Pod behind a load balancer address and expects a static token in a header.

In the PAIS UI the registration is under MCP, MCP Servers, Add server: a name, the URL, the transport "Streamable HTTP" and the header. A credential header is stored as a secret.

The tools arrive as "Not approved". An agent cannot select a tool before somebody approves it. I like this step, because it gives a platform team a place to decide which tools agents may use at all. The Broadcom page [Connect an MCP Server to Private AI Services](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/adding-mcp-servers-for-real-time-data-access-and-specialized-ai-capabilities/connect-to-an-mcp-server.html) lists what is supported: remote servers over Streamable HTTP or Server-Sent Events, optional static tokens, and tool calling.

## The first agent

An agent in the Agent Builder is a model, instructions in plain text and a list of approved tools. My first agent got all four tools and a short instruction: call the matching tool for questions about hosts, time, models or arithmetic, and answer briefly in the language of the question.

I first chose the Claude route from part 2 as the model. The playground answered with an error: "temperature is deprecated for this model". Over the API an agent on the Claude route works when the request leaves `temperature` out.

Then I chose the local Qwen3 4B endpoint on a 4 GB slice and asked for the address of one lab host. The server log showed a call of `lab_hosts`, and the agent answered with the right address. That was the first tool call from end to end. The answer had two flaws, though. The model wrote its reasoning into the answer text ("Okay, the user is asking…"), and the next question came back as a tool call written out as text.

Every agent has its own endpoint in the OpenAI format. A client uses the same PAIS token as for a model:

```bash
curl -s https://pais.vcf.internal/api/v1/compatibility/openai/v1/agents/$AGENT_ID/chat/completions \
  -H "Authorization: Bearer $PAIS_TOKEN" -H "Content-Type: application/json" \
  -d '{"model": "chat-4c-1", "max_tokens": 400,
       "messages": [{"role": "user", "content": "Which address does the host esx01 have?"}]}'
```

The `model` field has to be the model of the agent. If it names another model, the endpoint answers with HTTP 400 and `UNEXPECTED_MODEL`. A client with a fixed model name will fail on the day somebody changes the model of the agent.

## What one question does

PAIS can send traces of every agent run to an OpenTelemetry collector. I use [Arize Phoenix](https://github.com/Arize-ai/phoenix), an open-source tracing tool for large language model (LLM) applications, again as one vSphere Pod. The setting is in the Service Configuration under LLM Tracing, and the Broadcom page is [Enable Metrics Collection and LLM Traces in Private AI Services 3.0 by Using the UI](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/installing-and-configuring-private-ai-services/activate-metrics-collection-and-llm-traces-in-private-ai-services-3-0-by-using-the-ui.html). Saving the setting needed no restart.

{{< figure src="/images/an-agent-that-calls-tools-on-a-small-local-model/agent-tool-call-path.svg" alt="Diagram of one tool question in Private AI Services 3.0: the client calls the agent endpoint, the agent runtime calls the model endpoint to pick a tool, calls the tool on the MCP server and calls the model endpoint again to write the answer. Every step is sent to the tracing collector." caption="One tool question in the lab, with the medians from the traces: two model calls and one tool call." >}}

The model first picks a tool from the four descriptions, the runtime calls it, and the model then writes the answer. In the traces the model calls have a median of about 0.6 seconds each. The tool call takes 31 to 88 milliseconds, so almost all of the time goes to the model.

## The numbers: 30 questions, four setups

The load is the same in every run: 30 questions, three in parallel, from a fixed list of twelve. Eight of the twelve need a tool. The questions are a mix of German and English, `max_tokens` is 400 and `temperature` is 0. The tokens are the `usage` block of each answer, so they include every model call of the agent run. I read all answers by hand.

| Setup | Good answers | Median | 90th percentile | Tokens per question, in / out | in : out |
|---|---|---|---|---|---|
| Qwen3 4B on a 4 GB slice, first instructions | 24 of 30 | 3.1 s | 5.6 s | 1,991 / 252 | 7.9 : 1 |
| Qwen3 4B on a 4 GB slice, `/no_think` as first line | 30 of 30 | 1.4 s | 2.1 s | 896 / 91 | 9.9 : 1 |
| Qwen3 14B on the RTX 4090, external route | 22 of 30 | 9.9 s | 12.5 s | 766 / 346 | 2.2 : 1 |
| Qwen3 8B on an 8 GB slice, first instructions | 30 of 30 | 1.6 s | 3.2 s | 884 / 87 | 10.2 : 1 |

{{< figure src="/images/an-agent-that-calls-tools-on-a-small-local-model/agent-tool-calls.svg" alt="Bar chart of the four setups: median seconds per question and tokens per question, split into input and output tokens" caption="The same 30 questions against four setups. Left the median time per question, right the tokens per question." >}}

**The 4B model was large enough for these tool calls, but it put its thinking into the answer text.** With the reasoning budget at 0, llama.cpp closes the thinking block of Qwen3. The 4B model then continued its reasoning as normal answer text, and that text used up the 400 tokens. Three requests ended with HTTP 502 and "LLM exceeded max_tokens", and three more answers contained reasoning text or a tool call written as text. One question about the model list ran in a loop: 14 tool calls and 24,559 input tokens for a short list of names.

Qwen3 has a switch for this in the prompt. I put `/no_think` in the first line of the agent instructions and changed nothing else:

```text
/no_think
You are the lab assistant for a VMware Cloud Foundation lab. For questions about lab hosts, the current time, the models on the PAIS gateway or simple arithmetic, always call the matching tool from the MCP server lab-test instead of guessing. Answer briefly in the language of the question and say which tool you used.
```

All 30 answers were correct after that, and every tool question needed two model calls and one tool call. The median fell from 3.1 to 1.4 seconds. The tokens per question fell from 1,991 in and 252 out to 896 in and 91 out.

**The larger model on the second machine did worse.** All 30 requests returned HTTP 200, but the 14B model thinks before every step, and the thinking counts against `max_tokens`. Eight answers were cut off in the middle of a sentence. A normal client can switch the thinking off with `reasoning_effort` in the request. The Agent Builder has no field for it, and `/no_think` had no effect on this path. A test against the model endpoint alone would have missed this.

**The 8B model on an 8 GB slice needs no switch.** For this run I rebuilt the card from six 4 GB slices to three 8 GB slices. That needed no host reboot, because the card stays in same-size mode; only a mix of sizes needs the mode change from [part 4c](/posts/six-endpoints-on-one-card/). The 8B model gave 30 correct answers with and without `/no_think`, at 1.6 seconds.

**Most tokens go in, few come out.** A question without a tool costs about 430 input tokens. A tool question costs about 920, because it needs two model calls and each call carries the descriptions of the four tools. For sizing, this means that an agent sends much more input to a model endpoint than a chat does.

## Going crazy with PAIS and MCP

With the first agent working I added three things over the weekend: the lab documentation as a knowledge base, a second MCP server that reads vCenter, and a page that shows what the agent does. From here on the agent runs on the 8B model.

**The lab documentation as a knowledge base.** My lab handbook is a Git repository with Markdown pages. I uploaded 70 of them over the PAIS REST API. The upload took 11 seconds, and the indexing on the BGE-M3 embedding endpoint from part 4 took 111 seconds. The agent gets the knowledge base as one more tool. A knowledge-base question costs about 2,700 tokens in and 200 out and takes two to four seconds in total, of which the search is under 0.1 seconds.

Two sentences in the agent instructions decide how well this works. The first one names what the knowledge base covers. Without it the 8B model refused a question about backups as "not related to the VMware Cloud Foundation lab" and did not search at all. The second one says to answer only from the retrieved text. Without it the model answered a capacity question with a forecast that it had made up from benchmark pages.

This part is not solved. The model writes the search query, so small differences decide which pages come back. For the screenshots of this post I asked a handbook question that the agent had answered correctly on the weekend, and this time it answered from the wrong page. For this reason the agent names the page in every answer.

**Read access to vCenter.** [VMware-Monitor](https://github.com/vmware-skills/VMware-Monitor) is a community project with an MIT licence and not an official Broadcom product. It is an MCP server with read tools for vCenter: inventory, alarms, events, performance, snapshots and more. I read the code of version 2.5.0 before I installed it. It runs on my Mac mini and logs in to vCenter with an account that has only the built-in ReadOnly role, so vCenter itself enforces the limit. PAIS reaches the server over HTTPS with a token. I approved 33 read tools and gave eleven of them to an agent.

{{< figure src="/images/an-agent-that-calls-tools-on-a-small-local-model/glass-box-vcenter.jpg" alt="Screenshot of the demo page: on the left the question 'What changed overnight, and is anything red?' and the answer of the agent, on the right the agent with its eleven vCenter tools, the response time of 2.3 seconds, 8,325 tokens in and 133 out, two model calls and the tool call get_cluster_health_summary with 224 milliseconds" caption="The demo page with the vCenter agent. Left the chat, right what the agent did for this question, read from the trace." >}}

The question "What changed overnight, and is anything red?" needs one tool call of 224 milliseconds and takes 2.3 seconds in total. It costs 8,325 tokens in and 133 out, because the descriptions of the eleven tools alone are about 4,000 tokens per model call. When I asked the agent to power off a VM, it refused without a tool call. It has no tool for that, and its account could not do it either.

The limit here is the context size. My 8B endpoint has 8,192 tokens of context, and an unfiltered list of all VMs has about 12,000 tokens, so the request failed. In one answer the model also swapped two numbers, the VMs that are powered on and the VMs that are off. For tools that return long results I would plan 16,000 tokens of context as the minimum.

**A page that shows the steps.** The page in the screenshot is a small web server on the Mac mini. Next to the chat it shows the tool calls with arguments and duration, the knowledge-base hits with page and score, the model calls and the tokens for the current question. It reads all of that from the Phoenix trace of the question. I built it for talks and demos, because it shows a platform team in one view where the time and the tokens of an agent go.

{{< figure src="/images/an-agent-that-calls-tools-on-a-small-local-model/agent-paths.svg" alt="Diagram of the demo setup: browser, the page on the Mac mini, the agent runtime of Private AI Services, the model endpoints and gateway routes, the knowledge base, the two MCP servers, vCenter and the tracing collector, with eight numbered paths between them" caption="Who talks to whom in the demo: eight paths from the browser to the agent, the model endpoints, the knowledge base, the two MCP servers and the traces." >}}

## What this could mean for operations

The lab has two MCP servers. A platform team has many more systems that an agent could read. The picture below is my sketch of that idea: one working day on a large VCF platform. It shows six people with six questions, and twelve MCP servers that an agent could use to answer them.

{{< figure src="/images/an-agent-that-calls-tools-on-a-small-local-model/agents-mcp-day.svg" alt="Infographic in four rows: six people of a platform team with one question each during a working day, the Agent Builder of Private AI Services 3.0 on top of the model endpoints, twelve ideas for MCP servers from vCenter and VCF Operations to Harbor, monitoring, IT service management and team chat, and five guardrails" caption="A working day on a large VCF platform as a sketch: six questions, the agent layer of PAIS, twelve MCP server ideas and the guardrails. The two green marks are what runs in my lab." >}}

Two of the twelve run in my lab: the knowledge base and the read access to vCenter. The other ten are ideas. For monitoring, [Checkmk](https://checkmk.com/werk/22263) and [Zabbix](https://www.zabbix.com/documentation/8.0/en/manual/concepts/mcp_server) already document an MCP server of their own. The bottom row shows what I would set up first on a real platform. Each tool is approved once and each server has its own token. Every call is traced, and an agent writes only after a person has confirmed the step.

## What comes next

The next piece of this series is about the architecture: the layers of PAIS from the Supervisor up to the gateway and the agents, and what they do for a platform team.

## Official documentation and William Lam's posts

Broadcom documentation for VMware Private AI Foundation with NVIDIA 9.1:

- [Enable the Full Set of Private AI Services 3.0 Capabilities by Using the UI](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/installing-and-configuring-private-ai-services/enable-the-full-set-of-private-ai-services-capabilities.html)
- [Integrating Specialized Data and Capabilities over MCP](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/adding-mcp-servers-for-real-time-data-access-and-specialized-ai-capabilities.html)
- [Connect an MCP Server to Private AI Services](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/adding-mcp-servers-for-real-time-data-access-and-specialized-ai-capabilities/connect-to-an-mcp-server.html)
- [Explore the MCP Tools Available to Private AI Services Agents](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/adding-mcp-servers-for-real-time-data-access-and-specialized-ai-capabilities/exploring-the-mcp-tools-avaiable-in-your-namespace.html)
- [Create an Agent for a Generative AI Application](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/deploy-an-agent-for-a-rag-application.html)
- [Adding Context to Model Responses by Using Knowledge Bases](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/adding-context-to-model-responses-by-using-knowledge-bases.html)
- [Enable Metrics Collection and LLM Traces in Private AI Services 3.0 by Using the UI](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/deploying-private-ai-foundation-with-nvidia/installing-and-configuring-private-ai-services/activate-metrics-collection-and-llm-traces-in-private-ai-services-3-0-by-using-the-ui.html)
- [Tracing Agent Operation and Knowledge Base Indexing](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/tracing-agent-operation-and-knowledge-base-indexing.html)
- [Import a CA Trust Bundle in Private AI Services](https://techdocs.broadcom.com/us/en/vmware-cis/private-ai/foundation-with-nvidia/9-1/what-is-private-ai-services/importing-a-ca-trust-bundle-in-private-ai-services.html)

William Lam:

- [MS-A2 VCF 9.0 Lab: Configuring Data Services Manager (DSM) for VMware Private AI Services (PAIS)](https://williamlam.com/2025/09/ms-a2-vcf-9-0-lab-configuring-data-services-manager-dsm-for-vmware-private-ai-services-pais.html), the database route with Data Services Manager, written for VCF 9.0
- [VCF 9.1.1 - Deploying Your Own AI Models with VCF Private AI Services (PAIS) 3.0](https://williamlam.com/2026/09/vcf-9-1-1-deploying-your-own-ai-models-with-vcf-private-ai-services-pais-3-0.html)
