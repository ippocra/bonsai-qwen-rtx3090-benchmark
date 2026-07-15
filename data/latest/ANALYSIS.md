# Bonsai vs Qwen finished benchmark analysis

Results file: `/home/fido/models/benchmark-index/2026-07-15-hermes-agentic-benchmark/finished/results.tsv`
Total rows: 116
Phases: {'fit': 72, 'quality': 28, 'boundary': 16}
Status counts: {'ok': 108, 'oom': 8}

## Hardware squeeze conclusion

- With exact configs and `-fit off`, both models fit full GPU offload (`ngl=999`) at the model context limit (`ctx=262144`) when using q4_0/q4_0 KV cache.
- Qwen is close to the 24GB ceiling at full context with q4_0/q4_0 KV: peak 22755 MB, leaving roughly 1.8 GB nominal headroom on a 24576 MB RTX 3090.
- Bonsai has much more headroom at full context with q4_0/q4_0 KV: peak 13911 MB.
- The OOM boundary appears when increasing KV precision, not when increasing `ngl`: Qwen OOMs at q8_0/q8_0 above 131k context and at f16/f16 even at 131k context; Bonsai fits f16/f16 through 252k but OOMs at 262k.

## Best exact-fit q4_0/q4_0 configs

| model | ctx | ngl | peak VRAM MB | fit gen tok/s |
|---|---:|---:|---:|---:|
| Qwen3.6-27B-Q4_K_M | 262144 | 999 | 22755 | 28.57 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 999 | 13911 | 33.89 |

## OOM boundary rows

| model | ctx | ngl | cache | status | peak VRAM MB |
|---|---:|---:|---|---|---:|
| Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | q8_0/q8_0 | ok | 13111 |
| Ternary-Bonsai-27B-Q2_0 | 196608 | 999 | q8_0/q8_0 | ok | 14721 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | q8_0/q8_0 | ok | 17635 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 999 | q8_0/q8_0 | ok | 16897 |
| Qwen3.6-27B-Q4_K_M | 131072 | 999 | q8_0/q8_0 | ok | 21955 |
| Qwen3.6-27B-Q4_K_M | 196608 | 999 | q8_0/q8_0 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 252000 | 999 | q8_0/q8_0 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 262144 | 999 | q8_0/q8_0 | oom | 16887 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | f16/f16 | ok | 16385 |
| Ternary-Bonsai-27B-Q2_0 | 196608 | 999 | f16/f16 | ok | 20641 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | f16/f16 | ok | 23953 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 999 | f16/f16 | oom | 8043 |
| Qwen3.6-27B-Q4_K_M | 131072 | 999 | f16/f16 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 196608 | 999 | f16/f16 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 252000 | 999 | f16/f16 | oom | 16887 |
| Qwen3.6-27B-Q4_K_M | 262144 | 999 | f16/f16 | oom | 16887 |

## Quality/probe summary at q4_0/q4_0 ngl=999

| model | ctx | score | avg prompt tok/s | avg gen tok/s | avg peak VRAM MB |
|---|---:|---:|---:|---:|---:|
| Qwen3.6-27B-Q4_K_M | 131072 | 4/7 | 294.23 | 38.18 | 19970 |
| Qwen3.6-27B-Q4_K_M | 252000 | 4/7 | 297.69 | 38.22 | 22602 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 6/7 | 354.46 | 57.67 | 11116 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 6/7 | 351.59 | 57.67 | 13748 |

## Interpretation

- Bonsai is the better hardware-fit model on this RTX 3090: full offload plus full 262k context fits comfortably, and quality probes averaged about 57.7 gen tok/s.
- Qwen can also be squeezed into full offload plus full 262k context with q4_0/q4_0 KV, but it is near the memory ceiling and averaged about 38.2 gen tok/s on the quality probes.
- For maximum safe Qwen operation, use `ctx=262144`, `ngl=999`, `-ctk q4_0 -ctv q4_0`; avoid q8/f16 KV at long context on 24GB.
- For maximum quality KV on Bonsai, f16/f16 is possible up to 252k context, but full 262k requires dropping to q8_0/q8_0 or q4_0/q4_0.
- The remaining quality failures are mostly caused by models emitting long `<think>` traces within the token budget. They are useful operational findings: for tool/JSON/coding use, either allocate a larger generation budget or use a serving mode/template that suppresses hidden reasoning.
