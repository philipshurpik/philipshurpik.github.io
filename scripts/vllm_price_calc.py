"""Price per Mtok for self-hosted models from benchmark throughput and instance cost."""

HOURS_PER_MONTH = 730
LOAD = 0.5  # avg load as a share of max throughput (c=128)
IN_PER_OUT = 5  # usage mix: input tokens per output token
PRICE_RATIO = 5  # output price / input price

# (name, instance $/month, output tok/s at c=128)
MODELS = {
    'half': (683, [
        ('qwen 3.6 35b a3b unsloth nvfp4', 1986.1),
        ('gemma4 26b a4b nvidia nvfp4', 3645.4),
    ]),
    'full': (1189, [
        ('qwen 3.8 27b unsloth nvfp4', 2009.6),
        ('gemma4 31b google fp8', 2361.8),
        ('gemma4 31b unsloth nvfp4', 2982.2),
        ('qwen 3.6 35b a3b unsloth nvfp4', 4408.6),
        ('gemma4 26b a4b nvidia fp8', 7042.1),
    ]),
}


def prices(cost: float, tps: float) -> tuple[float, float]:
    """Return (input, output) $/Mtok so that monthly revenue at LOAD equals instance cost."""
    out_mtok = tps * LOAD * HOURS_PER_MONTH * 3600 / 1e6
    in_mtok = out_mtok * IN_PER_OUT
    # cost = p_in * in + p_out * out, with p_out = PRICE_RATIO * p_in
    p_in = cost / (in_mtok + PRICE_RATIO * out_mtok)
    return p_in, PRICE_RATIO * p_in


for size, (cost, models) in MODELS.items():
    print(f'\n## {size} instance (${cost}/month):')
    for name, tps in models:
        p_in, p_out = prices(cost, tps)
        print(f'# {name + ":":<34} input $/Mtok: {p_in:.3f}, output $/Mtok: {p_out:.3f}')

# API reference price: https://ai.google.dev/gemini-api/docs/pricing (paid tier, text)
GEMINI_FLASH_LITE = ('gemini 3.1 flash lite (API)', 0.25, 1.50)
print(f'\n## API for comparison:\n# {GEMINI_FLASH_LITE[0] + ":":<34} input $/Mtok: {GEMINI_FLASH_LITE[1]:.3f}, output $/Mtok: {GEMINI_FLASH_LITE[2]:.3f}')
