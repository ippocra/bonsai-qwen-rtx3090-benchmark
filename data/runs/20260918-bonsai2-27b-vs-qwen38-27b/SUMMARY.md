# Bonsai 2 27B PTQ1_0 on RTX 3090 - benchmark summary

Date: 2026-09-18
Task: t_b1328e1d
Hardware: NVIDIA RTX 3090 24 GB
Backend: PrismML llama.cpp fork, origin/prism commit 1a07bfa5f, rebuilt locally with CUDA sm_86. Stock llama.cpp was not used: its current build segfaulted on this PTQ1_0 file, while the stale Prism build rejected type 143 until updated.

## Executive result

Bonsai 2 is a viable long-context supplement, but not a drop-in quality replacement for the current Qwen3.8-27B UD-Q4_K_S router based on this local probe set. It is dramatically lighter (5.95 GB weights; 5.7-11.6 GB peak VRAM in q4_0 KV fit probes) and faster in decode at batch-1 (median 60.8 tok/s vs 44.2 tok/s at 131K fixed probes), while the Qwen baseline scored 7/7 versus Bonsai 2 at 3/7 on the seven fixed agentic/reasoning probes.

Recommended role: deploy Bonsai 2 where 262K context and VRAM headroom matter, or as a fast local worker; retain Qwen3.8 Q4 for quality-sensitive router/default-agent traffic until a broader quality evaluation is run.

## Headline numbers

| Metric | Bonsai 2 PTQ1_0 | Qwen3.8-27B UD-Q4_K_S |
|---|---:|---:|
| Model file | 5.95 GB | 15.36 GB |
| q4_0 KV at 131K, full offload | 8,758 MB peak | 14,084 MB peak |
| q4_0 KV at 262K, full offload | 11,620 MB peak | 18,872 MB peak |
| q4_0 fit generation tok/s at 131K | 27.30 (1-token fit probe) | 52.61 |
| 131K quality gen tok/s, median | 60.77 | 44.17 |
| 131K quality prompt tok/s, median | 190.04 | 455.86 |
| Quality probes at 131K | 3/7 | 7/7 |
| Quality probes at 252K | 3/7 | 7/7 |
| Maximum tested q4_0 context | 262,144 | 262,144 |

The fit probe uses a one-token generation and is not comparable to the seven quality probes for decode throughput. Prompt/gen timing is parsed separately from llama.cpp's `prompt eval time` and `eval time`; the old harness's equal prompt/gen bug is not present in the raw rows, although one-token fit probes naturally have limited timing value.

## KV boundary

Bonsai 2 completed every tested q8_0 and f16 KV row at 131,072, 252,000, and 262,144 context. At 262K it peaked at 15,714 MB with q8_0 KV and 22,270 MB with f16 KV.

Qwen3.8 completed q8_0 at all tested contexts and f16 at 131K, but OOMed at f16 for 252K and 262K. Its q8_0 262K row peaked at 14,084 MB in this harness. All rows used `-fit off`, `-ngl 999`, and batch 512 / ubatch 128.

## Quality probes

The harness's seven fixed probes are reasoning, coding, JSON, and four Hermes-style agentic tool-selection/recovery/session probes. They are short fixed prompts executed with a 131K or 252K context window; they are not synthetic 131K-token recall payloads. Scores are therefore a smoke-quality comparison at long-context configuration, not a full long-context retention benchmark.

Bonsai 2 passed reasoning, JSON, and direct no-tool arithmetic (3/7), but failed the coding and three tool/session selection heuristics. Qwen3.8 passed all seven at both contexts. This is a material local quality gap despite the vendor's broader 98.2% retention claim.

## Method and artifacts

48 rows: 8 q4_0 fit probes, 28 quality probes, and 12 KV boundary probes. Raw logs and responses are under `raw/`; the generated PNG infographics are under `infographic/`. The deterministic SVG executive card is `infographic/executive-card.svg`.

The model was downloaded from `prism-ml/Ternary-Bonsai-2-27B-gguf`. No benchmark ran while `ippocra-local-router.service` was active; after the sweep the GPU was idle and the router remained stopped pending explicit operator restart/health-check.
