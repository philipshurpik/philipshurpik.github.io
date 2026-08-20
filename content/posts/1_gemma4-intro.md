---
title: "Self hosting Gemma 4: Intro"
date: 2026-08-20
draft: false
tags: ["llm", "vllm", "gemma"]
---

How we build LLM Engine of @LetsData and process 1B+ tokens per day 10x cheaper comparing to API models with similar quality.

This journey started year and half ago, when I joined LetsData and was selecting models to power our AI processings at scale.
The first one case was simple - we needed to replace outdated old-school ML translators with LLMs.
I've done a lot of evals initially - both with open source models (e.g LLama) and API-hosted (OpenAI, Gemini).
And at that time Gemini 2.0 Flash was by far the best in quality and price.
It was better comparing to 3-5 times more expensive models from other providers.

So for the long time it started being our workhorse for translations and everything we built on top:
topic modelling, summarisation, image and video description, anomalies detection and validation, and narrative extraction.

But 6 months ago Google made an announce, that Gemini 2.0 Flash would be depricated at the beginning of the summer.

### Self hosting story

Here I will share our story of how we built an replacement pipeline that actually has comparable, and sometimes better quality, but cost less.

So what was our options:
* Gemini 2.5 Flash Lite, costed the same as 2.0 Flash, provided worse quality, was enough only for high-resource languages translations. Would be depricated soon. 
* Gemini 3.1 Flash Lite, that costed ~3 times higher, with comparable quality depending on task (sometimes worse, sometimes better vs Flash 2.0). But it hurted our unit economics at scale.
* Other providers (Haiku and GPT-5 mini costed even more, plus all our prompts that calibrated on Gemini models would require a lot of evaluations and changes)
* Go into self hosted open source world

I decided to go with 3rd option and it was quite fun. And turned to be efficient.

So what was our candidates 6 months ago?
* LLama - pretty outdated, no recent releases. Not worked well in my year ago experiments 
* Gemma 3 - promising candidate for fine-tuning on some tasks, but general quality comparing to 2.5 Flash Lite.
* Qwen 3.X - Great self hosted model for agentic tasks. But quality drops a lot with disabled thinking. With enabled thinking eats a lot of tokens. Architecture that makes harder efficient KV caching - cache only in big chunks starting at ~1600+ tokens

And then Gemma 4 was dropped, with higher availability of spot RTX 6000 Pro accelerator instances on Google Cloud that changed our quality equation and math.

...