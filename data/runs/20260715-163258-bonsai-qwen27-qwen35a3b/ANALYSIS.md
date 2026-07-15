# Bonsai vs Qwen benchmark analysis

Results file: `data/runs/20260715-163258-bonsai-qwen27-qwen35a3b/results.tsv`
Total rows: 168
Phases: {'fit': 108, 'quality': 42, 'boundary': 18}
Status counts: {'ok': 144, 'oom': 24}

## Best exact-fit q4_0/q4_0 configs

| model | ctx | ngl | peak VRAM MB | fit gen tok/s |
|---|---:|---:|---:|---:|
| Qwen3.6-27B-Q4_K_M | 262144 | 999 | 22755 | 29.01 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 262144 | 36 | 19613 | 45.96 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 999 | 12801 | 34.14 |

## OOM boundary rows

| model | ctx | ngl | cache | status | peak VRAM MB |
|---|---:|---:|---|---|---:|
| Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | q8_0/q8_0 | ok | 12545 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | f16/f16 | ok | 16385 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | q8_0/q8_0 | ok | 17635 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | f16/f16 | ok | 23953 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 999 | q8_0/q8_0 | ok | 16897 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 999 | f16/f16 | oom | 8043 |
| Qwen3.6-27B-Q4_K_M | 131072 | 999 | q8_0/q8_0 | ok | 21389 |
| Qwen3.6-27B-Q4_K_M | 131072 | 999 | f16/f16 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 252000 | 999 | q8_0/q8_0 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 252000 | 999 | f16/f16 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 262144 | 999 | q8_0/q8_0 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 262144 | 999 | f16/f16 | oom | 16887 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 131072 | 999 | q8_0/q8_0 | ok | 22125 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 131072 | 999 | f16/f16 | oom | 22125 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 252000 | 999 | q8_0/q8_0 | oom | 22125 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 252000 | 999 | f16/f16 | oom | 22125 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 262144 | 999 | q8_0/q8_0 | oom | 22125 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 262144 | 999 | f16/f16 | oom | 22125 |

## Quality/probe summary

| model | ctx | score | avg prompt tok/s | avg gen tok/s | avg peak VRAM MB | statuses |
|---|---:|---:|---:|---:|---:|---|
| Qwen3.6-27B-Q4_K_M | 131072 | 4/7 | 297.88 | 38.30 | 19970 | ok:7 |
| Qwen3.6-27B-Q4_K_M | 252000 | 4/7 | 295.31 | 38.23 | 22602 | ok:7 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 131072 | 5/7 | 479.38 | 135.26 | 23262 | ok:7 |
| Qwen3.6-35B-A3B-UD-Q4_K_M | 252000 | 0/7 | - | - | 22954 | oom:7 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 6/7 | 353.97 | 57.67 | 11116 | ok:7 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 6/7 | 356.46 | 57.81 | 13748 | ok:7 |
