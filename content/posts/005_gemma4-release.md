---
title: "Gemma 4 Release"
date: 2026-04-03
slug: "gemma4-release-thoughts"
draft: false
tags: ["llm", "vllm", "gemma"]
---

Gemma 4 dropped yesterday - multimodal, open source - and I spent an hour doing math on whether it can replace our Gemini API for high-volume pipelines.

![Gemma 4 benchmark table across model sizes, compared with Gemma 3 27B](/images/005_gemma4-release.png)

Context: at LetsData we process billions of tokens/month on translation, summarization and video/image understanding. Currently using Gemini 2.0 Flash and 2.5 Flash Lite - both getting shut down this summer.

The benchmarks on directly comparable tests (GPQA Diamond, MMMU Pro, MMMLU) show Gemma 4 31B matching or beating Gemini 2.5 Flash. Hope Gemma is not as overfitted on benchmarks vs real-life performance as its Chinese counterparts like Qwen. But given even Gemma 3 was among the best open source translation models of its time, I'm hoping for better.

The 26B MoE variant is the interesting one for inference - only 3.8B active parameters per token, so it's dramatically more bandwidth-efficient on GPUs.

The cost question is trickier than it looks. Gemini 2.0 Flash at $0.10/$0.40 per 1M tokens is absurdly cheap. Running Gemma 4 26B MoE in INT4 on a single L4 roughly breaks even comparing with the Gemini 2.0 API. You need an L40 or the new GCP G4 instances (RTX PRO 6000 Blackwell, 96GB VRAM, fractional GPU support in preview at GCP) to start seeing real savings.

On a 1/2 GPU G4 fraction at Google Cloud or a cheap L40 from RunPod/Vast.ai, the math starts working - potentially 20-40% less than Gemini 2.0 Flash API pricing at our volume. And that's much better than the 3-4x price jump for what we'd get with the latest Gemini 3.1 Flash Lite.

Still just spreadsheet math though. Real questions:
- Does Gemma 4 26B match Gemini quality on our specific translation/summarization tasks?
- What's the actual throughput with vLLM/SGLang under realistic batch loads?
- How much quality do we lose going INT4 or FP4 on these tasks?
- What's the ops overhead worth in dollars?

Planning to run internal evals next week. Will share results.

Anyone already benchmarking Gemma 4 for production LLM pipelines?

*First published on [LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7445734767544836096/), April 3, 2026.*

