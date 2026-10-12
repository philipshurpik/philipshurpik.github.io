"""LinkedIn image for the self-hosting post: throughput (c=1 -> c=128, log) + $/MTok, one row per model/GPU."""

import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

SLUG = 'efficient-serving'

C = dict(BG='#0D1420', PANEL='#151E2E', BORDER='#27344B', TEXT='#E8EDF4', MUTED='#93A1B5',
         GEMMA='#2DD4BF', QWEN='#FFB454', API='#FF6B6B')

TITLE = 'Self-hosting at scale: \\$1.50 \u2192 \\$0.064 per 1M output tokens'
SUB1 = 'Gemma 4 vs Qwen 3.x on RTX PRO 6000 Blackwell (GCP G4 spot) - vLLM 0.31, FP8 KV cache, MTP speculative decoding.'
SUB2 = 'Left: output tok/s at 1 request and at 128 parallel requests. Right: estimated cost at ~50% average utilization.'

# (kind, label, family, c1, c128, in_price, out_price)
ROWS = [
    ('group', '\u00bd RTX PRO 6000  \u00b7  g4-standard-24  \u00b7  $683 / month spot', None, 0, 0, 0, 0),
    ('row', 'Gemma 4 26B-A4B \u00b7 Nvidia NVFP4', 'GEMMA', 178.6, 3645.4, 0.014, 0.071),
    ('row', 'Qwen3.6 35B-A3B \u00b7 Unsloth NVFP4', 'QWEN', 195.9, 1986.1, 0.026, 0.131),
    ('group', 'RTX PRO 6000  \u00b7  g4-standard-48  \u00b7  $1,189 / month spot', None, 0, 0, 0, 0),
    ('row', 'Gemma 4 26B-A4B \u00b7 Nvidia NVFP4', 'GEMMA', 264.1, 7042.1, 0.013, 0.064),
    ('row', 'Qwen3.6 35B-A3B \u00b7 Unsloth NVFP4', 'QWEN', 336.8, 4408.6, 0.021, 0.103),
    ('row', 'Gemma 4 31B \u00b7 Unsloth NVFP4', 'GEMMA', 140.0, 2982.2, 0.030, 0.152),
    ('row', 'Gemma 4 31B \u00b7 Google FP8', 'GEMMA', 117.1, 2300.9, 0.039, 0.197),
    ('row', 'Qwen3.8 27B \u00b7 Unsloth NVFP4', 'QWEN', 137.1, 2009.6, 0.045, 0.225),
    ('group', 'API  \u00b7  Google list price', None, 0, 0, 0, 0),
    ('row', 'Gemini 3.1 Flash Lite', 'API', None, None, 0.25, 1.50),
]

CARDS = [
    ('GEMMA 4 26B-A4B  vs  GEMINI 3.1 FLASH LITE', '23x', '\\$0.064 vs \\$1.50 per 1M output tokens', 'GEMMA'),
    ('NVFP4  vs  FP8  \u00b7  GEMMA 4 31B  \u00b7  c=128', '+30%', 'output tok/s  \u00b7  2,300.9 \u2192 2,982.2', 'GEMMA'),
    ('GEMMA 4  vs  QWEN 3.x  \u00b7  LIKE FOR LIKE', '32-46%', 'cheaper \\$/MTok on the same GPU', 'GEMMA'),
]

FOOT1 = ('\\$/MTok = spot price \u00f7 tokens served at 50% of peak throughput  \u00b7  5:1 input:output split  \u00b7  '
         'input priced at 1/5 of output  \u00b7  Gemini: list price')
FOOT2 = ('All tok/s measured on our production translation prompt  \u00b7  vLLM 0.31  \u00b7  FP8 KV cache  \u00b7  '
         'MTP speculative decoding  \u00b7  GCP spot prices as of Oct 2026')

GROUP_H, ROW_H = 0.72, 1.0
LABEL_X0, TP_X0, TP_X1, COST_X0, COST_X1 = 0.045, 0.335, 0.615, 0.66, 0.955
TOP_Y, ROWS_BOT, BOT_Y = 0.805, 0.40, 0.368


def row_positions() -> list[float]:
    ys, y = [], 0.0
    for kind, *_ in ROWS:
        h = GROUP_H if kind == 'group' else ROW_H
        ys.append(y + h / 2)
        y += h
    total = y
    return [TOP_Y - (TOP_Y - ROWS_BOT) * (v / total) for v in ys]


def fmt(v: float) -> str:
    return f'{v:,.1f}'


def draw_rows(fig: plt.Figure) -> None:
    ys = row_positions()
    ax_t = fig.add_axes([TP_X0, BOT_Y, TP_X1 - TP_X0, TOP_Y - BOT_Y])
    ax_c = fig.add_axes([COST_X0, BOT_Y, COST_X1 - COST_X0, TOP_Y - BOT_Y])
    for ax in (ax_t, ax_c):
        ax.set_ylim(BOT_Y, TOP_Y)
        ax.axis('off')
        ax.patch.set_alpha(0)
    ax_t.set_xscale('log')
    ax_t.set_xlim(95, 13000)
    ax_c.set_xlim(0, 0.345)

    # column headers
    fig.text(TP_X0, TOP_Y + 0.036, 'OUTPUT TOK/S', color=C['TEXT'], fontsize=12.5, fontweight='bold')
    fig.text(TP_X0, TOP_Y + 0.016, '\u25cb 1 request  \u2192  \u25cf 128 parallel   \u00b7   log scale',
             color=C['MUTED'], fontsize=11)
    fig.text(COST_X0, TOP_Y + 0.036, 'ESTIMATED COST', color=C['TEXT'], fontsize=12.5, fontweight='bold')
    fig.text(COST_X0, TOP_Y + 0.016, '\\$ per 1M tokens  \u00b7  bar = output, dark head = input', color=C['MUTED'], fontsize=11)

    # log grid
    for gx in (100, 200, 500, 1000, 2000, 5000, 10000):
        ax_t.axvline(gx, color=C['BORDER'], lw=0.9, ls=(0, (2, 5)), alpha=0.75, zorder=0)
        ax_t.text(gx, BOT_Y + 0.004, f'{gx / 1000:g}k' if gx >= 1000 else str(gx), color=C['MUTED'],
                  fontsize=9.5, ha='center', va='bottom', alpha=0.9)
    for gx in (0.05, 0.10, 0.15, 0.20, 0.25):
        ax_c.axvline(gx, color=C['BORDER'], lw=0.9, ls=(0, (2, 5)), alpha=0.75, zorder=0)
        ax_c.text(gx, BOT_Y + 0.004, f'\\${gx:.2f}', color=C['MUTED'], fontsize=9.5, ha='center', va='bottom',
                  alpha=0.9)

    bar_h = (TOP_Y - ROWS_BOT) / sum(GROUP_H if k == 'group' else ROW_H for k, *_ in ROWS) * 0.40
    for (kind, label, fam, c1, c128, pin, pout), y in zip(ROWS, ys):
        if kind == 'group':
            fig.text(LABEL_X0, y, label, color=C['MUTED'], fontsize=10.5, va='center', fontweight='bold')
            fig.add_artist(plt.Line2D([LABEL_X0, COST_X1], [y - 0.016, y - 0.016], color=C['BORDER'], lw=1))
            continue
        col = C[fam]
        fig.text(LABEL_X0, y, label, color=C['TEXT'], fontsize=12.5, va='center')

        if c1 is None:
            ax_t.text(95 * 1.15, y, 'API  \u00b7  no GPU, no throughput ceiling', color=C['MUTED'],
                      fontsize=11, va='center', style='italic')
        else:
            ax_t.plot([c1, c128], [y, y], color=col, lw=5, solid_capstyle='round', alpha=0.55, zorder=2)
            ax_t.plot([c1], [y], marker='o', ms=11, mfc=C['BG'], mec=col, mew=2.6, zorder=3)
            ax_t.plot([c128], [y], marker='o', ms=13, mfc=col, mec=C['BG'], mew=2, zorder=3)
            ax_t.text(c1 / 1.21, y, fmt(c1), color=col, fontsize=11.5, ha='right', va='center')
            ax_t.text(c128 * 1.14, y, fmt(c128), color=col, fontsize=11.5, ha='left', va='center',
                      fontweight='bold')

        if pout <= 0.345:
            ax_c.barh(y, pout, height=bar_h, color=col, alpha=0.9, zorder=2)
            ax_c.barh(y, pin, height=bar_h, color=C['BG'], alpha=0.45, zorder=3)
            ax_c.plot([pin, pin], [y - bar_h / 2, y + bar_h / 2], color=C['BG'], lw=1.6, zorder=4)
            ax_c.text(pout + 0.005, y, f'\\${pout:.3f}', color=col, fontsize=12, ha='left', va='center',
                      fontweight='bold')
            ax_c.text(0.0, y - bar_h * 0.95, f'in \\${pin:.3f}', color=C['MUTED'], fontsize=9, ha='left',
                      va='center')
        else:
            cut, gap, end = 0.20, 0.012, 0.25  # visible length 0.25 > Qwen3.8 bar (0.225) even with the break
            ax_c.barh(y, cut, height=bar_h, color=col, alpha=0.9, zorder=2)
            ax_c.barh(y, end - cut - gap, left=cut + gap, height=bar_h, color=col, alpha=0.9, zorder=2)
            head = end * pin / pout
            ax_c.barh(y, head, height=bar_h, color=C['BG'], alpha=0.45, zorder=3)
            ax_c.plot([head, head], [y - bar_h / 2, y + bar_h / 2], color=C['BG'], lw=1.6, zorder=4)
            # lightning break mark
            for dx in (0, gap):
                ax_c.plot([cut + dx - 0.004, cut + dx + 0.004], [y - bar_h * 0.8, y + bar_h * 0.8],
                          color=C['BG'], lw=5, zorder=3, solid_capstyle='butt')
                ax_c.plot([cut + dx - 0.004, cut + dx + 0.004], [y - bar_h * 0.8, y + bar_h * 0.8],
                          color=col, lw=2.2, zorder=4, solid_capstyle='round')
            ax_c.text(end + 0.006, y, '\\$1.50', color=col, fontsize=12, ha='left', va='center', fontweight='bold')
            ax_c.text(0.0, y - bar_h * 0.95, 'in \\$0.25', color=C['MUTED'], fontsize=9, ha='left', va='center')


def draw_cards(fig: plt.Figure) -> None:
    ax = fig.add_axes([0.035, 0.163, 0.93, 0.168])
    n = len(CARDS)
    ax.set_xlim(0, n)
    ax.set_ylim(0, 1)
    ax.axis('off')
    for i, (label, big, sub, fam) in enumerate(CARDS):
        ax.add_patch(FancyBboxPatch((i + 0.04, 0.05), 0.92, 0.90, boxstyle='round,pad=0.012,rounding_size=0.05',
                                    facecolor=C['PANEL'], edgecolor=C['BORDER'], lw=1.4, mutation_aspect=0.3))
        cx = i + 0.5
        ax.text(cx, 0.78, label, ha='center', va='center', color=C['MUTED'], fontsize=9.8)
        ax.text(cx, 0.46, big, ha='center', va='center', color=C[fam], fontsize=36, fontweight='bold')
        ax.text(cx, 0.15, sub, ha='center', va='center', color=C['TEXT'], fontsize=11.2)


def draw_title(fig: plt.Figure) -> None:
    parts = [('Self-hosting at scale: ', C['TEXT']), ('\\$1.50', C['API']), (' \u2192 ', C['MUTED']),
             ('\\$0.064', C['GEMMA']), (' per 1M output tokens', C['TEXT'])]
    renderer = fig.canvas.get_renderer()
    x = 0.045
    for txt, col in parts:
        t = fig.text(x, 0.962, txt, color=col, fontsize=24, fontweight='bold', va='top')
        bb = t.get_window_extent(renderer=renderer)
        x += bb.width / fig.bbox.width


def main() -> None:
    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig = plt.figure(figsize=(12, 12), dpi=100)
    fig.patch.set_facecolor(C['BG'])

    draw_title(fig)
    fig.text(0.045, 0.918, SUB1, color=C['MUTED'], fontsize=12.8, va='top')
    fig.text(0.045, 0.896, SUB2, color=C['MUTED'], fontsize=12.8, va='top')

    draw_rows(fig)
    draw_cards(fig)

    fig.text(0.5, 0.108, FOOT1, color=C['MUTED'], fontsize=10.2, ha='center')
    fig.text(0.5, 0.084, FOOT2, color=C['MUTED'], fontsize=10.2, ha='center')

    for dpi in (100, 200):
        fig.savefig(f'/mnt/user-data/outputs/{SLUG}-{dpi * 12}.png', dpi=dpi, facecolor=C['BG'])
    print('done')


if __name__ == '__main__':
    main()
