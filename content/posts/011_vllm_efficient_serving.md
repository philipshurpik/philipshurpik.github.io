---
title: "Self-hosting models: cost-efficient serving"
date: 2026-10-12
slug: "efficient-serving"
draft: false
tags: ["llm", "vllm", "gemma", "qwen", "self-hosting"]
---

How we built the LLM engine at LetsData and process 1B+ tokens per day several times cheaper than API models of similar quality.

### How we got here

This journey started a year and a half ago, when I joined LetsData and was selecting models to power our AI processing at scale.
The first task was simple: replace old-school ML translators with LLMs.
I ran a lot of evals, both on open-source models such as Llama and on API models from OpenAI and Google.
Gemini 2.0 Flash won by a wide margin on quality per dollar - at $0.40 per 1M output tokens it became our workhorse for translation and for everything we built on top: topic modeling, summarization, image and video description, anomaly detection and validation, narrative extraction.

But there is a twist with API models - they live a short life, 12-18 months.
And sometimes the replacement costs a few times more, which breaks unit economics at scale.
On February 18, 2026, Google deprecated Gemini 2.0 Flash, with shutdown on June 1.

### The options (as of spring 2026)

* **Gemini 3.1 Flash Lite.** About three times the price. Quality comparable to 2.0 Flash. The other Flash models cost even more.
* **Other providers.** Claude Haiku and GPT-5 mini cost more still. Every prompt we run is calibrated on Gemini, so a switch meant re-evaluating and rewriting all of them.
* **Self-hosted open-source models.** The one we picked.

### Model selection story

I started with Qwen 3.x models. They have decent quality on agentic tasks with thinking enabled, but they are slow and burn a lot of tokens.
With thinking disabled, quality drops a lot.
And their hybrid architecture (Gated DeltaNet + attention) makes prefix caching less precise.
vLLM sizes the KV cache block to the recurrent state, which with FP8 KV cache and MTP is 1,600 tokens on Qwen3.8 27B.
Prompts shorter than that get zero cache hits. And that also limits max number of concurrent requests that could be efficiently served.

But everything changed on April 2, 2026, when Google released Gemma 4.
Around the same time Google Cloud made G4 instances with the RTX PRO 6000 Blackwell available - 96 GB of VRAM, including fractional GPUs.
That changed both the quality equation and the math.

### Performance: output tokens per second

When self-hosting it's important to get maximum from the model having the quality almost non-changed.
And actually there are few levers to use:
* Optimise concurrency and available KV cache
* Run KV cache in FP8 precision
* Using MTP speculative decoding with optimal parameters
* Using NVFP4 precision when possible. But here is the catch. Proper NVFP4 requires only quantisation of same layers and serving others (as attention or global pooling) as fp8.
  * Only that could give you much smaller image, more free memory headroom for KV cache and faster speed.
  * I've done that manually with google released QAT image, and it showed the same performance on most of tasks, but still some drop for low resource language translation.
  * But fortunately unsloth quantisation of Gemma4 31B arrived, and we moved to it. It showed ~25% performance increase comparing to fp8 model with some spare GPU memory to co-host embedding models. 

I've re-evaluated numbers on recent vllm 0.31, with all optimisations turned on: KV cache in FP8, MTP speculative decoding on.
All tok/sec numbers here using our production translation prompt.

| Model | GPU               | 1 request | 128 parallel |
|---|-------------------|-----------|--------------|
| Qwen3.6 35B-A3B Unsloth NVFP4 | 1/2 RTX 6000 Pro  | 195.9     | 1,986.1      |
| Gemma 4 26B-A4B NVIDIA NVFP4 | 1/2 RTX 6000 Pro  | 178.6     | 3,645.4      |
| Qwen3.8 27B Unsloth NVFP4 | RTX 6000 Pro | 137.1     | 2,009.6      |
| Gemma 4 31B Google FP8 | RTX 6000 Pro | 117.1     | 2,300.9      |
| Gemma 4 31B Unsloth NVFP4 | RTX 6000 Pro | 140.0     | 2,982.2      |
| Qwen3.6 35B-A3B Unsloth NVFP4 | RTX 6000 Pro | 336.8     | 4,408.6      |
| Gemma 4 26B-A4B NVIDIA NVFP4 | RTX 6000 Pro | 264.1     | 7,042.1      |

### Pricing

Here is the most interesting part, that defines - what load do you have, and do it fit enough with self hosting models.
Luckily enough we process social media data and have almost steady flow of requests with occasional bursts for more hungry processings - therefore queue based autoscaling on kubernetes fits our usage well.
And now let's go to pricing - with current spot values on Google Cloud it's $1,189 for a full GPU (g4-standard-48) and $683 for a half GPU.

I've converted it into $/MTok using our production profile: 1:5 input:output split, input priced at 1/5 of output, and an average load of 50% of peak throughput (roughly 16-32 parallel requests).

| Model | GPU              | input $/Mtok | output $/Mtok |
|---|------------------|---|---|
| Qwen3.6 35B-A3B Unsloth NVFP4 | 1/2 RTX 6000 Pro | 0.026 | 0.131 |
| Gemma 4 26B-A4B NVIDIA NVFP4 | 1/2 RTX 6000 Pro | 0.014 | 0.071 |
| Qwen3.8 27B Unsloth NVFP4 | RTX 6000 Pro     | 0.045 | 0.225 |
| Gemma 4 31B Google FP8 | RTX 6000 Pro     | 0.038 | 0.192 |
| Gemma 4 31B Unsloth NVFP4 | RTX 6000 Pro     | 0.030 | 0.152 |
| Qwen3.6 35B-A3B Unsloth NVFP4 | RTX 6000 Pro     | 0.021 | 0.103 |
| Gemma 4 26B-A4B NVIDIA NVFP4 | RTX 6000 Pro     | 0.013 | 0.064 |
| Gemini 3.1 Flash Lite  | API         | 0.250 | 1.500 |

So for high-throughput serving, the comparable Gemma models come out 30-45% cheaper than Qwen.
And unlike an API bill, the same g4 node could also host smaller GPU models (embedding model in our case), and CPU-heavy jobs can run on the node's spare 48 vCPUs.

Interested in the Gemma 4 vs Qwen quality comparison on multilingual data, dense vs MoE and when to pick which, or the Gemma 4 LoRA fine-tuning story? Leave a comment and I will publish them next.
