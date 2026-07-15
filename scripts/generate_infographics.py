#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BONSAI = '#48f0a4'
QWEN = '#7c83ff'
OOM = '#ff4d5f'
INK = '#e8edf2'
MUTED = '#8b96a8'
BG = '#0b1020'
PANEL = '#121a2f'
GRID = '#26324d'


def rows_from(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding='utf-8'), delimiter='\t'))


def model_color(model: str) -> str:
    return BONSAI if 'Bonsai' in model else QWEN


def short_model(model: str) -> str:
    return 'Bonsai 27B' if 'Bonsai' in model else 'Qwen3.6 27B'


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, facecolor=BG, bbox_inches='tight', pad_inches=0.18)
    plt.close(fig)
    print(path)


def style_ax(ax) -> None:
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(True, axis='y', color=GRID, alpha=0.45, linewidth=0.8)
    ax.set_axisbelow(True)


def best_fit(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out = {}
    for row in rows:
        if row['phase'] == 'fit' and row['status'] == 'ok':
            current = out.get(row['model'])
            key = (int(row['ctx']), int(row['ngl']))
            cur_key = (-1, -1) if current is None else (int(current['ctx']), int(current['ngl']))
            if key > cur_key:
                out[row['model']] = row
    return out


def quality_summary(rows: list[dict[str, str]]) -> dict[tuple[str, int], dict[str, float]]:
    out = {}
    for model in sorted({r['model'] for r in rows if r['phase'] == 'quality'}):
        for ctx in sorted({int(r['ctx']) for r in rows if r['phase'] == 'quality' and r['model'] == model}):
            subset = [r for r in rows if r['phase'] == 'quality' and r['model'] == model and int(r['ctx']) == ctx]
            out[(model, ctx)] = {
                'score': sum(int(r['score']) for r in subset if r['score'] not in ('', 'None')),
                'total': len(subset),
                'gen': sum(float(r['gen_tok_s']) for r in subset) / len(subset),
                'prompt': sum(float(r['prompt_tok_s']) for r in subset) / len(subset),
                'vram': sum(float(r['peak_vram_mb']) for r in subset) / len(subset),
            }
    return out


def draw_overview(rows: list[dict[str, str]], out_dir: Path) -> None:
    best = best_fit(rows)
    fig = plt.figure(figsize=(14, 8), facecolor=BG)
    gs = fig.add_gridspec(2, 3, height_ratios=[0.7, 1.2], wspace=0.28, hspace=0.36)
    title = fig.add_subplot(gs[0, :])
    title.axis('off')
    title.text(0.015, 0.72, 'RTX 3090 LOCAL MODEL SQUEEZE', color=INK, fontsize=26, fontweight='bold', ha='left')
    title.text(0.015, 0.38, 'Bonsai fits the full-context target with far more memory margin; Qwen reaches it only with q4 KV cache.', color=MUTED, fontsize=13, ha='left')
    title.text(0.985, 0.72, '116 runs\n108 ok / 8 OOM', color=INK, fontsize=15, ha='right', va='top')

    models = sorted(best.keys(), key=lambda m: 0 if 'Bonsai' in m else 1)
    ax1 = fig.add_subplot(gs[1, 0])
    style_ax(ax1)
    vals = [float(best[m]['peak_vram_mb']) / 1024 for m in models]
    bars = ax1.bar([short_model(m) for m in models], vals, color=[model_color(m) for m in models], width=0.58)
    ax1.axhline(24, color=OOM, linewidth=1.4, linestyle='--')
    ax1.set_title('Peak VRAM at ctx 262k / ngl 999', color=INK, fontsize=12, pad=12)
    ax1.set_ylabel('GB', color=MUTED)
    ax1.set_ylim(0, 25.5)
    for bar, val in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.5, f'{val:.1f} GB', ha='center', color=INK, fontsize=11, fontweight='bold')

    ax2 = fig.add_subplot(gs[1, 1])
    style_ax(ax2)
    vals = [float(best[m]['gen_tok_s']) for m in models]
    bars = ax2.bar([short_model(m) for m in models], vals, color=[model_color(m) for m in models], width=0.58)
    ax2.set_title('Fit-probe generation throughput', color=INK, fontsize=12, pad=12)
    ax2.set_ylabel('tok/s', color=MUTED)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.7, f'{val:.1f}', ha='center', color=INK, fontsize=11, fontweight='bold')

    ax3 = fig.add_subplot(gs[1, 2])
    ax3.set_facecolor(PANEL)
    ax3.axis('off')
    ax3.add_patch(Rectangle((0.06, 0.56), 0.88, 0.18, color=BONSAI, alpha=0.95, transform=ax3.transAxes))
    ax3.add_patch(Rectangle((0.06, 0.29), 0.88, 0.18, color=QWEN, alpha=0.95, transform=ax3.transAxes))
    ax3.text(0.08, 0.79, 'Operational call', color=INK, fontsize=15, fontweight='bold', transform=ax3.transAxes)
    ax3.text(0.09, 0.61, 'Bonsai: full context with headroom', color=BG, fontsize=12, fontweight='bold', transform=ax3.transAxes)
    ax3.text(0.09, 0.34, 'Qwen: full context only near ceiling', color=BG, fontsize=12, fontweight='bold', transform=ax3.transAxes)
    ax3.text(0.08, 0.12, 'Recommended Qwen mode: ctx=262144, ngl=999, q4_0/q4_0 KV.\nAvoid q8/f16 KV for long-context Qwen on 24GB.', color=MUTED, fontsize=10.5, transform=ax3.transAxes)
    save(fig, out_dir / 'benchmark-overview.png')


def draw_oom(rows: list[dict[str, str]], out_dir: Path) -> None:
    boundary = [r for r in rows if r['phase'] == 'boundary']
    contexts = sorted({int(r['ctx']) for r in boundary})
    combos = [('Ternary-Bonsai-27B-Q2_0', 'q8_0'), ('Ternary-Bonsai-27B-Q2_0', 'f16'), ('Qwen3.6-27B-Q4_K_M', 'q8_0'), ('Qwen3.6-27B-Q4_K_M', 'f16')]
    fig, ax = plt.subplots(figsize=(13, 7), facecolor=BG)
    ax.set_facecolor(BG)
    ax.axis('off')
    ax.text(0.02, 0.94, 'KV PRECISION BOUNDARY', color=INK, fontsize=24, fontweight='bold', transform=ax.transAxes)
    ax.text(0.02, 0.89, 'Full offload, ngl=999. Green cells fit; red cells hit OOM.', color=MUTED, fontsize=12, transform=ax.transAxes)
    left, top, cell_w, cell_h = 0.20, 0.76, 0.15, 0.13
    for i, ctx in enumerate(contexts):
        ax.text(left + i*cell_w + cell_w/2, top + 0.07, f'{ctx//1000}k', color=MUTED, ha='center', fontsize=11, transform=ax.transAxes)
    for j, (model, cache) in enumerate(combos):
        y = top - j*cell_h
        label = f'{short_model(model)}  {cache}/{cache}'
        ax.text(0.02, y + 0.035, label, color=INK, ha='left', va='center', fontsize=11, transform=ax.transAxes)
        for i, ctx in enumerate(contexts):
            row = next((r for r in boundary if r['model'] == model and int(r['ctx']) == ctx and r['cache_k'] == cache), None)
            status = row['status'] if row else 'missing'
            color = model_color(model) if status == 'ok' else OOM
            ax.add_patch(Rectangle((left + i*cell_w, y), cell_w*0.9, cell_h*0.72, color=color, alpha=0.92, transform=ax.transAxes))
            ax.text(left + i*cell_w + cell_w*0.45, y + cell_h*0.36, status.upper(), color=BG if status == 'ok' else INK, ha='center', va='center', fontsize=10, fontweight='bold', transform=ax.transAxes)
    ax.text(0.02, 0.08, 'Finding: Qwen q8_0 KV works at 131k but fails above it; Qwen f16 KV fails at every tested long context. Bonsai f16 reaches 252k but not 262k.', color=MUTED, fontsize=11, transform=ax.transAxes)
    save(fig, out_dir / 'kv-oom-boundary.png')


def draw_quality(rows: list[dict[str, str]], out_dir: Path) -> None:
    summary = quality_summary(rows)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.8), facecolor=BG)
    for ax in axes:
        style_ax(ax)
    labels = []
    scores = []
    gens = []
    colors = []
    for (model, ctx), vals in sorted(summary.items(), key=lambda item: (0 if 'Bonsai' in item[0][0] else 1, item[0][1])):
        labels.append(f'{short_model(model)}\n{ctx//1000}k')
        scores.append(vals['score'] / vals['total'] * 100)
        gens.append(vals['gen'])
        colors.append(model_color(model))
    axes[0].bar(labels, scores, color=colors, width=0.62)
    axes[0].set_ylim(0, 105)
    axes[0].set_title('Quality probe pass rate', color=INK, fontsize=13, pad=12)
    axes[0].set_ylabel('% passed', color=MUTED)
    for i, value in enumerate(scores):
        axes[0].text(i, value + 3, f'{value:.0f}%', ha='center', color=INK, fontsize=10, fontweight='bold')
    axes[1].bar(labels, gens, color=colors, width=0.62)
    axes[1].set_title('Quality probe generation speed', color=INK, fontsize=13, pad=12)
    axes[1].set_ylabel('tok/s', color=MUTED)
    for i, value in enumerate(gens):
        axes[1].text(i, value + 1, f'{value:.1f}', ha='center', color=INK, fontsize=10, fontweight='bold')
    fig.text(0.03, 0.96, 'QUALITY AND SPEED AT PRACTICAL SETTINGS', color=INK, fontsize=22, fontweight='bold')
    fig.text(0.03, 0.91, 'q4_0/q4_0 KV, ngl=999. Failures are mostly long reasoning traces consuming the answer budget.', color=MUTED, fontsize=12)
    save(fig, out_dir / 'quality-speed-score.png')


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate PNG infographics for benchmark results.')
    parser.add_argument('--results', default='data/latest/results.tsv')
    parser.add_argument('--out-dir', default='assets')
    args = parser.parse_args()
    rows = rows_from(Path(args.results))
    out_dir = Path(args.out_dir)
    draw_overview(rows, out_dir)
    draw_oom(rows, out_dir)
    draw_quality(rows, out_dir)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
