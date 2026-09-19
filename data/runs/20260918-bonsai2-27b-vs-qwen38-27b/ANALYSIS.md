# Bonsai vs Qwen benchmark analysis

Results file: `/home/fido/models/benchmark-index/2026-09-18-ternary-bonsai2-27b/raw/results.tsv`
Total rows: 48
Phases: {'fit': 8, 'quality': 28, 'boundary': 12}
Status counts: {'ok': 46, 'oom': 2}

## Best exact-fit q4_0/q4_0 configs

| model | ctx | ngl | peak VRAM MB | fit gen tok/s |
|---|---:|---:|---:|---:|
| Qwen3.8-27B-UD-Q4_K_S | 262144 | 999 | 18872 | 47.57 |
| Ternary-Bonsai-2-27B-PTQ1_0 | 262144 | 999 | 11620 | 27.25 |

## OOM boundary rows

| model | ctx | ngl | cache | status | peak VRAM MB |
|---|---:|---:|---|---|---:|
| Ternary-Bonsai-2-27B-PTQ1_0 | 131072 | 999 | q8_0/q8_0 | ok | 5698 |
| Ternary-Bonsai-2-27B-PTQ1_0 | 131072 | 999 | f16/f16 | ok | 14224 |
| Ternary-Bonsai-2-27B-PTQ1_0 | 252000 | 999 | q8_0/q8_0 | ok | 5736 |
| Ternary-Bonsai-2-27B-PTQ1_0 | 252000 | 999 | f16/f16 | ok | 21496 |
| Ternary-Bonsai-2-27B-PTQ1_0 | 262144 | 999 | q8_0/q8_0 | ok | 15714 |
| Ternary-Bonsai-2-27B-PTQ1_0 | 262144 | 999 | f16/f16 | ok | 22270 |
| Qwen3.8-27B-UD-Q4_K_S | 131072 | 999 | q8_0/q8_0 | ok | 14084 |
| Qwen3.8-27B-UD-Q4_K_S | 131072 | 999 | f16/f16 | ok | 14084 |
| Qwen3.8-27B-UD-Q4_K_S | 252000 | 999 | q8_0/q8_0 | ok | 14084 |
| Qwen3.8-27B-UD-Q4_K_S | 252000 | 999 | f16/f16 | oom | 14084 |
| Qwen3.8-27B-UD-Q4_K_S | 262144 | 999 | q8_0/q8_0 | ok | 14084 |
| Qwen3.8-27B-UD-Q4_K_S | 262144 | 999 | f16/f16 | oom | 14084 |

## Quality/probe summary

| model | ctx | score | avg prompt tok/s | avg gen tok/s | avg peak VRAM MB | statuses |
|---|---:|---:|---:|---:|---:|---|
| Qwen3.8-27B-UD-Q4_K_S | 131072 | 7/7 | 413.40 | 43.01 | 17156 | ok:7 |
| Qwen3.8-27B-UD-Q4_K_S | 252000 | 7/7 | 449.17 | 42.94 | 19790 | ok:7 |
| Ternary-Bonsai-2-27B-PTQ1_0 | 131072 | 3/7 | 222.19 | 122.32 | 8787 | ok:7 |
| Ternary-Bonsai-2-27B-PTQ1_0 | 252000 | 3/7 | 273.29 | 149.06 | 11419 | ok:7 |
