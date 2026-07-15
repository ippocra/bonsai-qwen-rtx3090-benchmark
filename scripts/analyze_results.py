#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import csv
import statistics
from pathlib import Path


def fnum(value: str | None) -> float | None:
    if value in (None, '', 'None'):
        return None
    return float(value)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build markdown analysis for a Bonsai vs Qwen benchmark results.tsv file.')
    parser.add_argument('--results', default='data/latest/results.tsv')
    parser.add_argument('--out', default='data/latest/ANALYSIS.md')
    args = parser.parse_args()
    rows = list(csv.DictReader(Path(args.results).open(encoding='utf-8'), delimiter='\t'))
    counts = collections.Counter(row['status'] for row in rows)
    phases = collections.Counter(row['phase'] for row in rows)
    lines = [
        '# Bonsai vs Qwen benchmark analysis',
        '',
        f'Results file: `{Path(args.results)}`',
        f'Total rows: {len(rows)}',
        f'Phases: {dict(phases)}',
        f'Status counts: {dict(counts)}',
        '',
        '## Best exact-fit q4_0/q4_0 configs',
        '',
        '| model | ctx | ngl | peak VRAM MB | fit gen tok/s |',
        '|---|---:|---:|---:|---:|',
    ]
    for model in sorted({row['model'] for row in rows}):
        fit = [row for row in rows if row['phase'] == 'fit' and row['model'] == model and row['status'] == 'ok']
        if not fit:
            continue
        best = max(fit, key=lambda row: (int(row['ctx']), int(row['ngl'])))
        lines.append(f"| {model} | {best['ctx']} | {best['ngl']} | {best['peak_vram_mb']} | {best['gen_tok_s']} |")
    lines += ['', '## OOM boundary rows', '', '| model | ctx | ngl | cache | status | peak VRAM MB |', '|---|---:|---:|---|---|---:|']
    for row in rows:
        if row['phase'] == 'boundary':
            lines.append(f"| {row['model']} | {row['ctx']} | {row['ngl']} | {row['cache_k']}/{row['cache_v']} | {row['status']} | {row['peak_vram_mb']} |")
    lines += ['', '## Quality/probe summary', '', '| model | ctx | score | avg prompt tok/s | avg gen tok/s | avg peak VRAM MB | statuses |', '|---|---:|---:|---:|---:|---:|---|']
    for model in sorted({row['model'] for row in rows}):
        contexts = sorted({int(row['ctx']) for row in rows if row['phase'] == 'quality' and row['model'] == model})
        for ctx in contexts:
            subset = [row for row in rows if row['phase'] == 'quality' and row['model'] == model and int(row['ctx']) == ctx]
            score = sum(int(row['score']) for row in subset if row['score'] not in ('', 'None'))
            prompt_vals = [fnum(row['prompt_tok_s']) for row in subset if fnum(row['prompt_tok_s']) is not None]
            gen_vals = [fnum(row['gen_tok_s']) for row in subset if fnum(row['gen_tok_s']) is not None]
            peak_vals = [fnum(row['peak_vram_mb']) for row in subset if fnum(row['peak_vram_mb']) is not None]
            prompt = f'{statistics.mean(prompt_vals):.2f}' if prompt_vals else '-'
            gen = f'{statistics.mean(gen_vals):.2f}' if gen_vals else '-'
            peak = f'{statistics.mean(peak_vals):.0f}' if peak_vals else '-'
            status_counts = collections.Counter(row['status'] for row in subset)
            status_note = ', '.join(f'{k}:{v}' for k, v in sorted(status_counts.items()))
            lines.append(f'| {model} | {ctx} | {score}/{len(subset)} | {prompt} | {gen} | {peak} | {status_note} |')
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
