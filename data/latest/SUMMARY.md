# Finished Bonsai vs Qwen Hardware Benchmark

Hardware: RTX 3090 24GB
Backend: /home/fido/work/PrismML-llama.cpp/build/bin/llama-completion
Rows: 116

## Fit sweep

| model | ctx | ngl | status | peak VRAM MB | gen tok/s | seconds |
|---|---:|---:|---|---:|---:|---:|
| Ternary-Bonsai-27B-Q2_0 | 32768 | 20 | ok | 4135 | 0.7 | 6.501 |
| Ternary-Bonsai-27B-Q2_0 | 32768 | 28 | ok | 4999 | 0.85 | 5.713 |
| Ternary-Bonsai-27B-Q2_0 | 32768 | 36 | ok | 5863 | 1.05 | 4.888 |
| Ternary-Bonsai-27B-Q2_0 | 32768 | 44 | ok | 6725 | 1.61 | 4.061 |
| Ternary-Bonsai-27B-Q2_0 | 32768 | 60 | ok | 8433 | 6.0 | 2.685 |
| Ternary-Bonsai-27B-Q2_0 | 32768 | 999 | ok | 8927 | 33.74 | 2.145 |
| Ternary-Bonsai-27B-Q2_0 | 65536 | 20 | ok | 4473 | 0.72 | 6.504 |
| Ternary-Bonsai-27B-Q2_0 | 65536 | 28 | ok | 5409 | 0.86 | 5.504 |
| Ternary-Bonsai-27B-Q2_0 | 65536 | 36 | ok | 6375 | 1.2 | 4.588 |
| Ternary-Bonsai-27B-Q2_0 | 65536 | 44 | ok | 7279 | 1.65 | 4.043 |
| Ternary-Bonsai-27B-Q2_0 | 65536 | 60 | ok | 9147 | 4.65 | 2.687 |
| Ternary-Bonsai-27B-Q2_0 | 65536 | 999 | ok | 9639 | 34.25 | 2.139 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 20 | ok | 5191 | 0.72 | 6.227 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 28 | ok | 6271 | 0.95 | 5.393 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 36 | ok | 7351 | 1.16 | 4.875 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 44 | ok | 8431 | 1.31 | 4.593 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 60 | ok | 10587 | 5.77 | 2.683 |
| Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | ok | 10497 | 34.47 | 2.144 |
| Ternary-Bonsai-27B-Q2_0 | 196608 | 20 | ok | 5925 | 0.7 | 6.473 |
| Ternary-Bonsai-27B-Q2_0 | 196608 | 28 | ok | 7119 | 0.8 | 5.936 |
| Ternary-Bonsai-27B-Q2_0 | 196608 | 36 | ok | 8343 | 1.04 | 5.142 |
| Ternary-Bonsai-27B-Q2_0 | 196608 | 44 | ok | 9565 | 1.37 | 4.319 |
| Ternary-Bonsai-27B-Q2_0 | 196608 | 60 | ok | 12011 | 5.95 | 2.689 |
| Ternary-Bonsai-27B-Q2_0 | 196608 | 999 | ok | 12487 | 32.43 | 2.139 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 20 | ok | 6493 | 0.73 | 6.49 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 28 | ok | 7839 | 0.86 | 5.945 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 36 | ok | 9215 | 1.0 | 5.413 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 44 | ok | 10529 | 1.65 | 4.048 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 60 | ok | 13219 | 5.53 | 2.693 |
| Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | ok | 12627 | 34.21 | 2.144 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 20 | ok | 6599 | 0.7 | 6.819 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 28 | ok | 7967 | 0.86 | 5.696 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 36 | ok | 9335 | 1.21 | 4.888 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 44 | ok | 10701 | 1.62 | 4.042 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 60 | ok | 13435 | 5.43 | 2.692 |
| Ternary-Bonsai-27B-Q2_0 | 262144 | 999 | ok | 13911 | 33.89 | 2.14 |
| Qwen3.6-27B-Q4_K_M | 32768 | 20 | ok | 7307 | 5.52 | 2.95 |
| Qwen3.6-27B-Q4_K_M | 32768 | 28 | ok | 9157 | 6.43 | 2.951 |
| Qwen3.6-27B-Q4_K_M | 32768 | 36 | ok | 10971 | 7.97 | 2.949 |
| Qwen3.6-27B-Q4_K_M | 32768 | 44 | ok | 12833 | 9.96 | 2.945 |
| Qwen3.6-27B-Q4_K_M | 32768 | 60 | ok | 16553 | 19.14 | 2.932 |
| Qwen3.6-27B-Q4_K_M | 32768 | 999 | ok | 17771 | 28.92 | 2.936 |
| Qwen3.6-27B-Q4_K_M | 65536 | 20 | ok | 7681 | 5.67 | 2.947 |
| Qwen3.6-27B-Q4_K_M | 65536 | 28 | ok | 9603 | 6.71 | 2.948 |
| Qwen3.6-27B-Q4_K_M | 65536 | 36 | ok | 11489 | 7.85 | 2.949 |
| Qwen3.6-27B-Q4_K_M | 65536 | 44 | ok | 13423 | 4.41 | 3.219 |
| Qwen3.6-27B-Q4_K_M | 65536 | 60 | ok | 17275 | 18.83 | 2.939 |
| Qwen3.6-27B-Q4_K_M | 65536 | 999 | ok | 18483 | 28.7 | 2.938 |
| Qwen3.6-27B-Q4_K_M | 131072 | 20 | ok | 8449 | 5.75 | 2.954 |
| Qwen3.6-27B-Q4_K_M | 131072 | 28 | ok | 10515 | 6.52 | 2.956 |
| Qwen3.6-27B-Q4_K_M | 131072 | 36 | ok | 12545 | 7.97 | 2.963 |
| Qwen3.6-27B-Q4_K_M | 131072 | 44 | ok | 14623 | 9.76 | 2.943 |
| Qwen3.6-27B-Q4_K_M | 131072 | 60 | ok | 18715 | 18.6 | 2.935 |
| Qwen3.6-27B-Q4_K_M | 131072 | 999 | ok | 19907 | 28.86 | 2.933 |
| Qwen3.6-27B-Q4_K_M | 196608 | 20 | ok | 9189 | 5.79 | 2.955 |
| Qwen3.6-27B-Q4_K_M | 196608 | 28 | ok | 11399 | 6.74 | 2.95 |
| Qwen3.6-27B-Q4_K_M | 196608 | 36 | ok | 13603 | 4.22 | 3.222 |
| Qwen3.6-27B-Q4_K_M | 196608 | 44 | ok | 15795 | 9.8 | 2.947 |
| Qwen3.6-27B-Q4_K_M | 196608 | 60 | ok | 20139 | 18.96 | 2.946 |
| Qwen3.6-27B-Q4_K_M | 196608 | 999 | ok | 21331 | 28.79 | 2.937 |
| Qwen3.6-27B-Q4_K_M | 252000 | 20 | ok | 9817 | 5.18 | 3.252 |
| Qwen3.6-27B-Q4_K_M | 252000 | 28 | ok | 12149 | 6.73 | 2.956 |
| Qwen3.6-27B-Q4_K_M | 252000 | 36 | ok | 14445 | 7.82 | 3.213 |
| Qwen3.6-27B-Q4_K_M | 252000 | 44 | ok | 16819 | 2.62 | 4.038 |
| Qwen3.6-27B-Q4_K_M | 252000 | 60 | ok | 21379 | 15.26 | 3.203 |
| Qwen3.6-27B-Q4_K_M | 252000 | 999 | ok | 21501 | 29.12 | 2.936 |
| Qwen3.6-27B-Q4_K_M | 262144 | 20 | ok | 9929 | 5.3 | 3.247 |
| Qwen3.6-27B-Q4_K_M | 262144 | 28 | ok | 12283 | 6.26 | 3.215 |
| Qwen3.6-27B-Q4_K_M | 262144 | 36 | ok | 14601 | 3.5 | 3.497 |
| Qwen3.6-27B-Q4_K_M | 262144 | 44 | ok | 16997 | 8.47 | 2.948 |
| Qwen3.6-27B-Q4_K_M | 262144 | 60 | ok | 21563 | 19.26 | 2.934 |
| Qwen3.6-27B-Q4_K_M | 262144 | 999 | ok | 22755 | 28.57 | 2.94 |

## Best fitting exact configs

- Ternary-Bonsai-27B-Q2_0: ctx=262144, ngl=999, peak_vram_mb=13911, gen_tok_s=33.89
- Qwen3.6-27B-Q4_K_M: ctx=262144, ngl=999, peak_vram_mb=22755, gen_tok_s=28.57

## Quality runs

| case | model | ctx | ngl | status | score | prompt tok/s | gen tok/s | peak VRAM MB | note |
|---|---|---:|---:|---|---:|---:|---:|---:|---|
| reasoning | Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | ok | 1 | 289.38 | 60.5 | 11119 | expected 9 sheep left |
| coding | Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | ok | 1 | 348.07 | 61.31 | 11119 | expected complete two_sum implementation |
| json | Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | ok | 0 | 165.27 | 60.51 | 11115 | expected parseable JSON with required keys |
| agentic_tool_selection | Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | ok | 1 | 582.29 | 60.22 | 11119 | expected read_file on /tmp/demo.py |
| agentic_recovery | Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | ok | 1 | 475.14 | 60.37 | 11119 | expected a recovery tool choice without repeating ENOENT |
| agentic_no_tool | Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | ok | 1 | 238.63 | 40.23 | 11103 | expected direct answer 56 without tool call |
| agentic_session_recall | Ternary-Bonsai-27B-Q2_0 | 131072 | 999 | ok | 1 | 382.44 | 60.55 | 11119 | expected session_search |
| reasoning | Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | ok | 1 | 287.82 | 60.02 | 13751 | expected 9 sheep left |
| coding | Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | ok | 1 | 342.92 | 60.94 | 13751 | expected complete two_sum implementation |
| json | Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | ok | 0 | 163.91 | 60.41 | 13747 | expected parseable JSON with required keys |
| agentic_tool_selection | Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | ok | 1 | 579.41 | 60.38 | 13751 | expected read_file on /tmp/demo.py |
| agentic_recovery | Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | ok | 1 | 472.09 | 60.46 | 13751 | expected a recovery tool choice without repeating ENOENT |
| agentic_no_tool | Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | ok | 1 | 236.13 | 40.69 | 13735 | expected direct answer 56 without tool call |
| agentic_session_recall | Ternary-Bonsai-27B-Q2_0 | 252000 | 999 | ok | 1 | 378.86 | 60.76 | 13751 | expected session_search |
| reasoning | Qwen3.6-27B-Q4_K_M | 131072 | 999 | ok | 1 | 230.76 | 39.8 | 19973 | expected 9 sheep left |
| coding | Qwen3.6-27B-Q4_K_M | 131072 | 999 | ok | 0 | 280.9 | 39.94 | 19973 | expected complete two_sum implementation |
| json | Qwen3.6-27B-Q4_K_M | 131072 | 999 | ok | 1 | 135.83 | 38.82 | 19969 | expected parseable JSON with required keys |
| agentic_tool_selection | Qwen3.6-27B-Q4_K_M | 131072 | 999 | ok | 0 | 493.66 | 39.95 | 19973 | expected read_file on /tmp/demo.py |
| agentic_recovery | Qwen3.6-27B-Q4_K_M | 131072 | 999 | ok | 0 | 402.42 | 39.95 | 19973 | expected a recovery tool choice without repeating ENOENT |
| agentic_no_tool | Qwen3.6-27B-Q4_K_M | 131072 | 999 | ok | 1 | 196.13 | 28.83 | 19957 | expected direct answer 56 without tool call |
| agentic_session_recall | Qwen3.6-27B-Q4_K_M | 131072 | 999 | ok | 1 | 319.92 | 40.0 | 19973 | expected session_search |
| reasoning | Qwen3.6-27B-Q4_K_M | 252000 | 999 | ok | 1 | 240.3 | 39.73 | 22605 | expected 9 sheep left |
| coding | Qwen3.6-27B-Q4_K_M | 252000 | 999 | ok | 0 | 290.28 | 39.93 | 22605 | expected complete two_sum implementation |
| json | Qwen3.6-27B-Q4_K_M | 252000 | 999 | ok | 1 | 135.92 | 38.81 | 22601 | expected parseable JSON with required keys |
| agentic_tool_selection | Qwen3.6-27B-Q4_K_M | 252000 | 999 | ok | 0 | 491.98 | 39.98 | 22605 | expected read_file on /tmp/demo.py |
| agentic_recovery | Qwen3.6-27B-Q4_K_M | 252000 | 999 | ok | 0 | 402.77 | 39.93 | 22605 | expected a recovery tool choice without repeating ENOENT |
| agentic_no_tool | Qwen3.6-27B-Q4_K_M | 252000 | 999 | ok | 1 | 198.94 | 29.15 | 22589 | expected direct answer 56 without tool call |
| agentic_session_recall | Qwen3.6-27B-Q4_K_M | 252000 | 999 | ok | 1 | 323.62 | 40.03 | 22605 | expected session_search |

## Status legend

- ok: exact requested config completed with -fit off.
- oom: exact requested config failed with CUDA or allocator out-of-memory signal.
- timeout: process exceeded the per-run timeout and was terminated.
- prompt_too_long: prompt exceeded usable context.
