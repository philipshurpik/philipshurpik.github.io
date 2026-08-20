---
title: "Discovering vLLM Gemma 4 KV Cache bug"
date: 2026-07-22
slug: "discovering-vllm-gemma4-unsloth-kv-cache-bug"
draft: false
tags: ["llm", "vllm", "gemma", "kv-cache", "quantization"]
---

Two NVFP4 builds of the same Gemma 4 31B. One used 8GB less VRAM - and ran slower. That made no sense. Chasing why led me to a silent bug in vLLM's speculative decoding that quietly costs decode throughput while keeping outputs 100% correct.

![Discovering vllm Gemma 4 kv cache bug with unsloth baked scales](/images/007_vllm-kv-cache-bug.png)

Background: we serve Gemma 4 31B across a production pipeline - translation, summarization, narrative extraction, anomaly detection. I'd optimized decode from ~2,500 tok/s (the original NVIDIA NVFP4 checkpoint) up to ~3,200 while cutting memory to pack more models per box on one RTX PRO 6000.
Then Unsloth (Unsloth AI) shipped their NVFP4 checkpoint. I benchmarked it expecting a win - 8GB less VRAM than the NVIDIA build, so it should be faster.
It ran at 2,304 tok/s. Slower - on our own benchmark, a mix of the production prompts we actually run.

The thread that unraveled it: on my own NVFP4 build, I was experimenting with baking calibrated FP8 KV-cache scales into the quantization - and throughput dropped instead of improving. Backwards. So I dug into the spec-decode metrics and found MTP draft acceptance had collapsed.

🔍 The cause:
 Gemma 4's MTP drafter shares the main model's KV cache but keeps its own dequantization scales - and they stay at 1.0, because assistant checkpoints ship without them. The moment the main checkpoint has calibrated FP8 KV scales, the drafter reads keys on a completely different scale than they were written.
Draft quality craters, and rejection sampling hides it perfectly: the tokens are still correct, so nothing errors - the throughput number is just quietly lower than it should be. That's what makes it invisible.

🔧 The fix: have the drafter inherit the target's KV scales.
Applied to Unsloth's checkpoint, it went from 2,304 to 2,864 tok/s at concurrency 96 on the same benchmark - now faster than the NVIDIA build it started behind, at 8GB less VRAM. The paradox resolved.

📊 Reproducible on the public Spec-Bench mix with unsloth/gemma-4-31b-it-nvfp4:
 → mean draft acceptance: ~2.8 → ~3.4 tokens
 → decode throughput: +13-15% under load
 → up to +22% single-stream
 Every number in the chart reproduces from the public checkpoint + the patch.

⚡ Quick check if you're affected:
 Look at the "SpecDecoding metrics" lines in your vLLM logs. Mean acceptance stuck around 2.8 or below with Gemma 4 MTP means you're leaving speed on the table - after the fix it sits at ~3.4+ (higher on translation-heavy workloads).

🔗 Fix:
PR in VLLM: https://github.com/vllm-project/vllm/pull/49262
Standalone patch for vLLM 0.25.0: https://gist.github.com/philipshurpik/3278114508dfa599cac0ac27b720692b

Found it while building our own NVFP4 quantization pipeline for Gemma 4 - more on that soon.

*First published on [LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7445734767544836096/), July 22, 2026.*