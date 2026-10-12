---
title: "Self-hosting models: cost efficient serving"
date: 2026-10-12
slug: "efficient-serving"
draft: false
tags: ["llm", "vllm", "gemma", "qwen", "self-hosting"]
---

How we build LLM Engine of @LetsData and process 1B+ tokens per day multiple times cheaper comparing to API models with similar quality.

### How we got here

This journey started year and half ago, when I joined LetsData and was selecting models to power our AI processings at scale.
The first task was simple: replace old-school ML translators with LLMs.
I ran a lot of evals, both on open-source models such as Llama and on API models from OpenAI and Google.
Gemini 2.0 Flash won by a wide margin on quality per price - cost of $0.4/1M output tokens made it our workhorse for translation and for everything we built on top: topic modelling, summarisation, image and video description, anomaly detection and validation, narrative extraction.

But the twist with API models - they are living short life - 12/18 months.
And sometimes their replacement models cost few times more, that breaks unit economics at scale.
On February 18, 2026 Google deprecated Gemini 2.0 Flash, with a shutdown on June 1.

### The options (as of spring 2026)

* **Gemini 3.1 Flash Lite.** About three times the price. Quality comparable to 2.0 Flash, sometimes better and sometimes worse depending on the task. Other Flash models were even more expensive.
* **Other providers.** Claude Haiku and GPT-5 mini cost more still. Every prompt we run is calibrated on Gemini, so a switch meant re-evaluating and rewriting all of them.
* **Self-hosted open-source models.**

### Model selection story

I've started with Qwen 3.X models. They have decent quality for agentic tasks, with thinking enabled, but slow and eat a lot of tokens. 
And quality drops a lot with disabled thinking. And have architecture that makes harder efficient KV caching - cache only in big chunks starting at ~1600+ tokens

But everything changed on April 2, 2026, when Google released Gemma 4.
Plus at the same time Google Cloud made availiable G4 instances with the RTX PRO 6000 Blackwell, 96 GB of VRAM, including fractional GPUs.
That changed both the quality equation and the math.

### Performance output tokens/sec

Here are performance metrics in output tokens/second. 
Idea would be to show Gemma4 31B unsloth nvfp4 with 128 parallel, translation v4 prompt:
All measured with kv cache in fp8, and mtp turned on.

One graph with 7 bars, where main one is for 128 requests, and smaller one inside, as part - for 1 request tok/sec

## half instance:
# qwen 3.6 35b a3b unsloth nvfp4:   c=1: 195.9, c=128: 1986.1
# gemma4 26b a4b nvidia nvfp4:      c=1: 178.6, c=128: 3645.4

## full instance:
# qwen 3.8 27b unsloth nvfp4:       c=1: 137.1, c=128: 2009.6
# gemma4 31b google fp8:            c=1: 110.6, c=128: 2361.8
# gemma4 31b unsloth nvfp4:         c=1: 140.0, c=128: 2982.2
# qwen 3.6 35b a3b unsloth nvfp4:   c=1: 336.8, c=128: 4408.6
# gemma4 26b a4b nvidia fp8:        c=1: 264.1, c=128: 7042.1

Here is pricing, if run on spot instance autopilot kubernetes cluster: $1189 (full-g4-standard-48), $683 (half-g4-standard-24)
I price calculated for our production usage: 5 input tokens to 1 output token, 1:5 input/output price ratio, on avg 50% of max available throughput (roughly 16-32 parallel requests):

## half instance: 
# qwen 3.6 35b a3b unsloth nvfp4:   input $/Mtok: 0.026, output $/Mtok: 0.131
# gemma4 26b a4b nvidia nvfp4:      input $/Mtok: 0.014, output $/Mtok: 0.071

## full instance:
# qwen 3.8 27b unsloth nvfp4:       input $/Mtok: 0.045, output $/Mtok: 0.225
# gemma4 31b google fp8:            input $/Mtok: 0.038, output $/Mtok: 0.192
# gemma4 31b unsloth nvfp4:         input $/Mtok: 0.030, output $/Mtok: 0.152
# qwen 3.6 35b a3b unsloth nvfp4:   input $/Mtok: 0.021, output $/Mtok: 0.103
# gemma4 26b a4b nvidia fp8:        input $/Mtok: 0.013, output $/Mtok: 0.064

## API for comparison:
# gemini 3.1 flash lite:            input $/Mtok: 0.250, output $/Mtok: 1.500

So for high througput serving compatible Gemma models get 30-40% more efficient.
If you are interesting in quality comparison between Gemma 4 and Qwen on multilingual datasets, choosing between Dense and MoE models, and when to choose which.
And also stories of Gemma 4 LORA finetuning - leave a comment - I will publish them next.