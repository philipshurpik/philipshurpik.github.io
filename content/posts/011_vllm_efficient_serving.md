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
Prompts shorter than that get zero cache hits. And that also limits the maximum number of concurrent requests that can be served efficiently.

But everything changed on April 2, 2026, when Google released Gemma 4.
Around the same time Google Cloud made G4 instances with the RTX PRO 6000 Blackwell available - 96 GB of VRAM, including fractional GPUs.
That changed both the quality equation and the math.

### Performance: output tokens per second

When self-hosting, it is important to get the maximum out of the model while keeping quality almost unchanged.
And there are a few levers to pull:
* Optimize concurrency and the available KV cache
* Run the KV cache in FP8
* Use MTP speculative decoding with tuned parameters
* Use NVFP4 weights when possible. But here is the catch: a proper NVFP4 build is mixed precision, with attention and some MLPs in FP8, while quantizing other to NVFP4.
  * That is what gives you a smaller docker image, more memory headroom for the KV cache and higher throughput than the FP8 model.
  * I did the same manually from the Google QAT checkpoint - NVFP4 MLPs, FP8 attention, calibrated on our own traffic. Same quality on most tasks, but still some drop on low-resource language translation.
  * Then the Unsloth build arrived with the more refined recipe, and we moved to it: ~30% more throughput at 128 parallel requests than the FP8 model, with spare GPU memory to co-host embedding models.

I re-measured everything on the recent vLLM 0.31 with all optimizations on: KV cache in FP8, MTP speculative decoding.
All tok/s numbers use our production translation prompt.

| Model | GPU          | 1 request | 128 parallel |
|---|--------------|-----------|--------------|
| Qwen3.6 35B-A3B Unsloth NVFP4 | 1/2 RTX PRO 6000 | 195.9     | 1,986.1      |
| Gemma 4 26B-A4B NVIDIA NVFP4 | 1/2 RTX PRO 6000 | 178.6     | 3,645.4      |
| Qwen3.8 27B Unsloth NVFP4 | RTX PRO 6000 | 137.1     | 2,009.6      |
| Gemma 4 31B Google FP8 | RTX PRO 6000 | 117.1     | 2,300.9      |
| Gemma 4 31B Unsloth NVFP4 | RTX PRO 6000 | 140.0     | 2,982.2      |
| Qwen3.6 35B-A3B Unsloth NVFP4 | RTX PRO 6000 | 336.8     | 4,408.6      |
| Gemma 4 26B-A4B NVIDIA NVFP4 | RTX PRO 6000 | 264.1     | 7,042.1      |

### Pricing

Here is the most interesting part. It comes down to what load you have, and whether it fits self-hosted models well enough.
Luckily, we process social media data and have an almost steady flow of requests, with occasional bursts for heavier processing - so queue-based autoscaling on Kubernetes fits our usage well.
Now to pricing - at current Spot prices on Google Cloud it is from $1,189 per month for a full GPU (g4-standard-48) and $683 for a half GPU (g4-standard-24).

I converted it into $/MTok using our production profile: a 5:1 input:output token split, input priced at 1/5 of output, and an average load of 50% of peak throughput (roughly 16-32 parallel requests).

| Model | GPU          | input $/Mtok | output $/Mtok |
|---|--------------|--------------|---------------|
| Qwen3.6 35B-A3B Unsloth NVFP4 | 1/2 RTX PRO 6000 | 0.026        | 0.131         |
| Gemma 4 26B-A4B NVIDIA NVFP4 | 1/2 RTX PRO 6000 | 0.014        | 0.071         |
| Qwen3.8 27B Unsloth NVFP4 | RTX PRO 6000 | 0.045        | 0.225         |
| Gemma 4 31B Google FP8 | RTX PRO 6000 | 0.039        | 0.197         |
| Gemma 4 31B Unsloth NVFP4 | RTX PRO 6000 | 0.030        | 0.152         |
| Qwen3.6 35B-A3B Unsloth NVFP4 | RTX PRO 6000 | 0.021        | 0.103         |
| Gemma 4 26B-A4B NVIDIA NVFP4 | RTX PRO 6000 | 0.013        | 0.064         |
| Gemini 3.1 Flash Lite  | API         | 0.250        | 1.500         |

So for high-throughput serving, the comparable Gemma models come out 30-45% cheaper than Qwen.
And unlike an API bill, the same G4 node can also host smaller GPU models (an embedding model, in our case), and CPU-heavy jobs can run on its spare 48 vCPUs.

Interested in the Gemma 4 vs Qwen quality comparison on multilingual data, dense vs MoE and when to pick which, or the Gemma 4 LoRA fine-tuning story? Leave a comment and I will publish them next.
