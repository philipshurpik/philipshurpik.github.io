---
title: "Self hosting Gemma 4: Intro"
date: 2026-08-20
slug: "gemma4-intro"
draft: false
tags: ["llm", "vllm", "gemma"]
---

How we build LLM Engine of @LetsData and process 1B+ tokens per day multiple times cheaper comparing to API models with similar quality. 

This journey started year and half ago, when I joined LetsData and was selecting models to power our AI processings at scale.
The first one case was simple - we needed to replace outdated old-school ML translators with LLMs.
I've done a lot of evals initially - both with open source models (e.g LLama) and API-hosted (OpenAI, Gemini).
And at that time Gemini 2.0 Flash was by far the best in quality and price.
It was better comparing to 3-5 times more expensive models from other providers.

So for the long time it started being our workhorse for translations and everything we built on top:
topic modelling, summarisation, image and video description, anomalies detection and validation, and narrative extraction.

On February 18, 2026 Google deprecated Gemini 2.0 Flash, with a shutdown on June 1.
We had three and a half months to replace the model under every pipeline we run. 

### Self hosting story

Here I will share our story of how we built an replacement pipeline that actually has comparable, and sometimes better quality, but cost less.

So what was our options:
* Gemini 2.5 Flash Lite, costed the same as 2.0 Flash, provided worse quality, was enough only for high-resource languages translations. Would be depricated soon. 
* Gemini 3.1 Flash Lite, that costed ~3 times higher, with comparable quality depending on task (sometimes worse, sometimes better vs Flash 2.0). But it hurted our unit economics at scale.
* Other providers (Haiku and GPT-5 mini costed even more, plus all our prompts that calibrated on Gemini models would require a lot of evaluations and changes)
* Go into self hosted open source world

We decided to go with 3rd option and it was quite fun. And turned to be efficient.

So what was our candidates 6 months ago?
* LLama - pretty outdated, no recent releases. Not worked well in my year ago experiments 
* Gemma 3 - promising candidate for fine-tuning on some tasks, but general quality comparing to 2.5 Flash Lite.
* Qwen 3.X - Great self hosted model for agentic tasks. But quality drops a lot with disabled thinking. With enabled thinking eats a lot of tokens. Architecture that makes harder efficient KV caching - cache only in big chunks starting at ~1600+ tokens

And then Gemma 4 was dropped, with higher availability of spot RTX 6000 Pro accelerator instances on Google Cloud that changed our quality equation and math.

### Part 1 - Model selection story

So here is our try and adopt story.
Here I need to have 3 graphs:
Qwen3.8 27B vs Gemma 4 26B vs Gemma 4 31B

1) Speed [regular, non nvfp4 model, kv cache 8, max available 96/128/256 parallel, real translation load] - full instance
2) Speed [regular, non nvfp4 model, kv cache 8, max available 96/128/256 parallel, real translation load] - half instance
3) Quality translations high resource language (german?)
4) Quality translations medium resource (ukrainian) + LoRA teaser with unsloth of eu model :)

Translation benchmark selected because it's more representative, and translation tokens are ~40% of our pipeline as of now.
So any model we select as workhorse should work well enough and consistently enough across multiple different languages, including low resource.

Gemma 4 26B works good with high resource languages, but fails with low/medium resource
Plus our testing showed it a bit more inconsistent with task execution and prompt following for other tasks (e.g anomaly extraction).
So roughly Gemini 2.5 Flash Lite level of intelligence

It could be sufficient to adopt it for limited amount of tasks, that require high througput, or cost efficient serving with "half" instances.
But it's not good enough for unified cost efficient workhorse model 

### Part 2 - Performance improvement and optimisation

As we selected Gemma 4 31B - what are the options to optimize it.
What we want:
* Maximize throughput for parallel processing
* Minimize amount of memory consumed - increase amount available for
  * KV cache
  * co-hosting of embedding models (Qwen3-VL-8B) on same 96GB of RAM

What are the options:
* Original model deployed in fp8 + fp8 kv cache
* Nvidia NVFP4 quantization
* Unsloth NVFP4 quantization
* Self - created NVFP4 full quantization, baked kv cache calibration

During this work I've discovered vLLM bug with KV cache loading, but that's different story [link here to 007_vllm-cache...]

What are the results:
Show 3 graphs:
1) Memory footprint of the VRAM usage [regular 40?gb nvidia 31gb? unsloth 23gb? self quantized from qat - 21gb?]
2) Quality for high resource language (german)
3) Quality for low resource language (armenian) + LoRA teaser with unsloth of hy model :) 

### Part 3 - LoRA finetuning

Here is separate story of finetuning.
My initial goal was to develop finetuning solution for low resource language.
We have bunch of projects in Armenia and Armenian language support in gemma 4 was quite "not good" too be honest.
1) So it started with first adapter for Armenian language with achieving quality similar to Gemini 3.1 Flash Lite 
2) and continued with unified adapter for 11 other European languages that we support for different projects.
Idea here was to achieve same or better quality comparing to Gemini Flash Lite 3.1, 
but with better understanding and alignment of abbreviations, named entities and slang including the most recent ones.


