#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BG = '#0b1020'
PANEL = '#121a2f'
INK = '#e8edf2'
MUTED = '#9aa5b8'
GRID = '#26324d'
OOM = '#ff4d5f'
PALETTE = ['#48f0a4', '#7c83ff', '#ffb86b', '#66d9ef', '#c792ea']


def rows_from(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.open(encoding='utf-8'), delimiter='\t'))


def short_model(model: str) -> str:
    if 'Bonsai' in model:
        return 'Bonsai 27B'
    if '35B' in model or 'A3B' in model:
        return 'Qwen3.6 35B-A3B'
    if '27B' in model:
        return 'Qwen3.6 27B'
    return model.replace('_', ' ')


def compact_model(model: str) -> str:
    if 'Bonsai' in model:
        return 'Bonsai'
    if '35B' in model or 'A3B' in model:
        return 'Qwen35-A3B'
    if '27B' in model:
        return 'Qwen27'
    return short_model(model)


def colors_for(models: list[str]) -> dict[str, str]:
    return {model: PALETTE[i % len(PALETTE)] for i, model in enumerate(models)}


def style(ax) -> None:
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(True, axis='y', color=GRID, alpha=0.45, linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, facecolor=BG, bbox_inches='tight', pad_inches=0.18)
    plt.close(fig)
    print(path)


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def best_fit(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        if row['phase'] != 'fit' or row['status'] != 'ok':
            continue
        current = out.get(row['model'])
        key = (int(row['ctx']), int(row['ngl']), float(row['peak_vram_mb'] or 0))
        cur = (-1, -1, -1.0) if current is None else (int(current['ctx']), int(current['ngl']), float(current['peak_vram_mb'] or 0))
        if key > cur:
            out[row['model']] = row
    return out


def draw_overview(rows: list[dict[str, str]], out: Path) -> None:
    best = best_fit(rows)
    models = sorted(best, key=lambda m: (0 if 'Bonsai' in m else 1 if '27B' in m else 2, m))
    colors = colors_for(models)
    labels = [short_model(m) for m in models]
    vram = [f(best[m], 'peak_vram_mb') / 1024 for m in models]
    gen = [f(best[m], 'gen_tok_s') for m in models]

    fig = plt.figure(figsize=(14.5, 8), facecolor=BG)
    fig.text(0.04, 0.94, 'THREE-MODEL RTX 3090 SQUEEZE', color=INK, fontsize=25, fontweight='bold')
    fig.text(0.04, 0.89, 'Best exact q4_0/q4_0 fit per model. Full offload target uses ngl=999.', color=MUTED, fontsize=12)
    gs = fig.add_gridspec(1, 2, left=0.06, right=0.97, bottom=0.12, top=0.78, wspace=0.22)
    ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[0, 1])
    for ax in [ax1, ax2]:
        style(ax)
    ax1.bar(labels, vram, color=[colors[m] for m in models], width=0.58)
    ax1.axhline(24, color=OOM, linewidth=1.4, linestyle='--')
    ax1.set_title('Peak VRAM at best exact fit', color=INK, fontsize=13, pad=12)
    ax1.set_ylabel('GB', color=MUTED)
    ax1.set_ylim(0, max(25.5, max(vram) + 2))
    for i, value in enumerate(vram):
        ax1.text(i, value + 0.45, f'{value:.1f} GB', ha='center', color=INK, fontsize=10.5, fontweight='bold')
    ax2.bar(labels, gen, color=[colors[m] for m in models], width=0.58)
    ax2.set_title('Fit-probe generation speed', color=INK, fontsize=13, pad=12)
    ax2.set_ylabel('tok/s', color=MUTED)
    ax2.set_ylim(0, max(gen) * 1.22)
    for i, value in enumerate(gen):
        ax2.text(i, value + max(gen) * 0.025, f'{value:.1f}', ha='center', color=INK, fontsize=10.5, fontweight='bold')
    save(fig, out / 'three-model-overview.png')


def draw_quality(rows: list[dict[str, str]], out: Path) -> None:
    qrows = [r for r in rows if r['phase'] == 'quality']
    models = sorted({r['model'] for r in qrows}, key=lambda m: (0 if 'Bonsai' in m else 1 if '27B' in m else 2, m))
    colors = colors_for(models)
    groups = []
    for model in models:
        for ctx in sorted({int(r['ctx']) for r in qrows if r['model'] == model}):
            subset = [r for r in qrows if r['model'] == model and int(r['ctx']) == ctx]
            groups.append((model, ctx, subset))
    labels = [f'{compact_model(m)}\n{ctx//1000}k' for m, ctx, _ in groups]
    scores = [sum(int(r['score'] or 0) for r in subset) / len(subset) * 100 for _, _, subset in groups]
    gens = []
    gen_labels = []
    for _, _, subset in groups:
        ok = [r for r in subset if r['status'] == 'ok' and r['gen_tok_s'] not in ('', 'None')]
        if ok:
            value = sum(float(r['gen_tok_s']) for r in ok) / len(ok)
            gens.append(value)
            gen_labels.append(f'{value:.1f}')
        else:
            gens.append(0.0)
            gen_labels.append('OOM')
    bar_colors = [colors[m] for m, _, _ in groups]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7.6), facecolor=BG)
    fig.subplots_adjust(left=0.06, right=0.985, bottom=0.12, top=0.76, wspace=0.18)
    fig.text(0.035, 0.94, 'QUALITY PROBES AND SPEED', color=INK, fontsize=23, fontweight='bold')
    fig.text(0.035, 0.885, 'q4_0/q4_0 KV, ngl=999. Scores reflect concise correctness/tool-selection checks.', color=MUTED, fontsize=11.5)
    for ax in axes:
        style(ax)
    axes[0].bar(labels, scores, color=bar_colors, width=0.62)
    axes[0].set_ylim(0, 105)
    axes[0].set_title('Quality probe pass rate', color=INK, fontsize=13, pad=12)
    axes[0].set_ylabel('% passed', color=MUTED)
    for i, value in enumerate(scores):
        axes[0].text(i, value + 3, f'{value:.0f}%', ha='center', color=INK, fontsize=10, fontweight='bold')
    axes[1].bar(labels, gens, color=bar_colors, width=0.62)
    max_gen = max(gens) if gens else 1
    axes[1].set_ylim(0, max_gen * 1.18 if max_gen else 1)
    axes[1].set_title('Generation speed during quality probes', color=INK, fontsize=13, pad=12)
    axes[1].set_ylabel('tok/s', color=MUTED)
    for i, (value, label) in enumerate(zip(gens, gen_labels)):
        y = value + max_gen * 0.025 if value else max_gen * 0.04
        axes[1].text(i, y, label, ha='center', color=INK, fontsize=10, fontweight='bold')
    save(fig, out / 'three-model-quality-speed.png')


def draw_boundary(rows: list[dict[str, str]], out: Path) -> None:
    b = [r for r in rows if r['phase'] == 'boundary']
    contexts = sorted({int(r['ctx']) for r in b})
    models = sorted({r['model'] for r in b}, key=lambda m: (0 if 'Bonsai' in m else 1 if '27B' in m else 2, m))
    caches = sorted({r['cache_k'] for r in b}, key=lambda c: {'q8_0': 0, 'f16': 1}.get(c, 9))
    row_keys = [(m, c) for m in models for c in caches]
    colors = colors_for(models)

    fig_h = 3.3 + len(row_keys) * 0.62
    fig, ax = plt.subplots(figsize=(14, fig_h), facecolor=BG)
    ax.set_facecolor(BG); ax.axis('off')
    ax.text(0.03, 0.95, 'KV PRECISION OOM BOUNDARY', color=INK, fontsize=23, fontweight='bold', transform=ax.transAxes)
    ax.text(0.03, 0.90, 'Full offload, ngl=999. Red cells record exact OOM outcomes.', color=MUTED, fontsize=11.5, transform=ax.transAxes)
    left, top = 0.30, 0.80
    cell_w = min(0.16, 0.62 / max(1, len(contexts)))
    cell_h = min(0.09, 0.56 / max(1, len(row_keys)))
    for i, ctx in enumerate(contexts):
        ax.text(left + i * cell_w + cell_w * 0.45, top + cell_h * 0.83, f'{ctx//1000}k', color=MUTED, ha='center', fontsize=10.5, transform=ax.transAxes)
    for j, (model, cache) in enumerate(row_keys):
        y = top - j * cell_h
        ax.text(0.03, y + cell_h * 0.36, f'{short_model(model)}  {cache}/{cache}', color=INK, ha='left', va='center', fontsize=10.5, transform=ax.transAxes)
        for i, ctx in enumerate(contexts):
            row = next((r for r in b if r['model'] == model and int(r['ctx']) == ctx and r['cache_k'] == cache), None)
            status = row['status'] if row else 'missing'
            color = colors[model] if status == 'ok' else OOM
            ax.add_patch(Rectangle((left + i * cell_w, y), cell_w * 0.88, cell_h * 0.70, color=color, alpha=0.93, transform=ax.transAxes))
            ax.text(left + i * cell_w + cell_w * 0.44, y + cell_h * 0.35, status.upper(), color=BG if status == 'ok' else INK, ha='center', va='center', fontsize=9.5, fontweight='bold', transform=ax.transAxes)
    save(fig, out / 'three-model-kv-boundary.png')


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate flexible multi-model benchmark infographics.')
    parser.add_argument('--results', required=True)
    parser.add_argument('--out-dir', required=True)
    args = parser.parse_args()
    rows = rows_from(Path(args.results))
    out = Path(args.out_dir)
    draw_overview(rows, out)
    draw_quality(rows, out)
    draw_boundary(rows, out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
