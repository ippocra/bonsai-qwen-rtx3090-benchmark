# Bonsai vs Qwen RTX 3090 Benchmark

Standalone benchmark harness and result package for comparing Ternary Bonsai 27B and Qwen3.6 27B on a single RTX 3090 24GB GPU with llama.cpp.

The benchmark answers one practical question: how much model, context, and KV precision can be squeezed out of the hardware before OOM, and what throughput/quality tradeoff results?

## Latest conclusion

Latest three-model timestamped run: `data/runs/20260715-163258-bonsai-qwen27-qwen35a3b/results.tsv`.

- Bonsai 27B fits full GPU offload at 262144 context with q4_0/q4_0 KV using about 12801 MB peak VRAM and 34.14 tok/s on the fit probe.
- Qwen3.6 27B fits full GPU offload at 262144 context with q4_0/q4_0 KV, but uses about 22755 MB peak VRAM and 29.01 tok/s.
- Qwen3.6 35B-A3B reaches 262144 context only with partial GPU offload in this sweep: best exact fit was ngl=36, about 19613 MB peak VRAM and 45.96 tok/s. Full offload, ngl=999, OOMed at 252k quality context.
- KV boundary: Bonsai keeps q8_0/q8_0 through 262k and f16/f16 through 252k; Qwen27 and Qwen35-A3B only keep q8_0/q8_0 at 131k and OOM above that; both OOM f16/f16 at 131k.
- Quality probes at q4_0/q4_0 ngl=999: Bonsai scored 6/7 at both 131k and 252k; Qwen27 scored 4/7 at both 131k and 252k; Qwen35-A3B scored 5/7 at 131k and OOMed at 252k.

Previous two-model snapshot remains available in `data/latest/`.

**You can find the infographics in `assets/`**



## Repository layout

```text
configs/rtx3090-bonsai-qwen.json  Hardware/model sweep config
configs/20260715-*.json            Timestamped run configs
scripts/run_benchmark.py           Runnable fit, boundary, and quality benchmark
scripts/analyze_results.py         Rebuilds markdown analysis from results.tsv
scripts/generate_infographics.py   Generates legacy two-model PNG infographics
scripts/generate_run_infographics.py Generates flexible multi-model PNG infographics
data/latest/                       Captured previous two-model benchmark results
data/runs/                         Timestamped benchmark result packages
assets/                            Generated two-model infographic PNGs
```

## Run the benchmark

Edit `configs/rtx3090-bonsai-qwen.json` if model or llama.cpp paths differ, then run:

```bash
python3 scripts/run_benchmark.py --config configs/rtx3090-bonsai-qwen.json
python3 scripts/analyze_results.py --results data/runs/<timestamp>/results.tsv --out data/runs/<timestamp>/ANALYSIS.md
python3 scripts/generate_run_infographics.py --results data/runs/<timestamp>/results.tsv --out-dir data/runs/<timestamp>/assets
```

The harness intentionally uses `-fit off` so exact requested configurations either run or produce a recorded failure such as `oom`, `timeout`, or `prompt_too_long`.

## Generate infographics from latest results

```bash
python3 scripts/generate_infographics.py --results data/latest/results.tsv --out-dir assets
```

## Requirements

- Python 3.10+
- llama.cpp `llama-completion`
- NVIDIA GPU with `nvidia-smi`
- Python packages for infographic generation: `matplotlib`, `Pillow`

The benchmark runner itself uses only the Python standard library.

## Day to Day use -- doom loops

_Editorial note by Michele_

I've tested this on day to day and, while I can confirm the speed and RAM usage, I've seen getting stuck into many doom loops. I've used via hermes on our instance of [ilai](https://ilai.ippocra.com) for few days, then I've switched back to my workhorse that is the Qwen 3.6 35-A3B. 
I did not have more time or more machine to dedicate to a more wider test.
