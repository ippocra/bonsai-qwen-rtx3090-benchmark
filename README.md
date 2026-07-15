# Bonsai vs Qwen RTX 3090 Benchmark

Standalone benchmark harness and result package for comparing Ternary Bonsai 27B and Qwen3.6 27B on a single RTX 3090 24GB GPU with llama.cpp.

The benchmark answers one practical question: how much model, context, and KV precision can be squeezed out of the hardware before OOM, and what throughput/quality tradeoff results?

## Latest conclusion

Latest captured run: `data/latest/results.tsv`.

- Bonsai fits full GPU offload at full 262144 context with q4_0/q4_0 KV using about 13911 MB peak VRAM.
- Qwen also fits full GPU offload at full 262144 context with q4_0/q4_0 KV, but uses about 22755 MB peak VRAM.
- Qwen crosses the OOM boundary when increasing KV precision: q8_0/q8_0 OOMs above 131k context; f16/f16 OOMs even at 131k.
- Bonsai can run f16/f16 KV up to 252k context, but OOMs at 262k.
- Quality probes at q4_0/q4_0 ngl=999: Bonsai scored 6/7 at both 131k and 252k; Qwen scored 4/7 at both 131k and 252k.

## Repository layout

```text
configs/rtx3090-bonsai-qwen.json  Hardware/model sweep config
scripts/run_benchmark.py           Runnable fit, boundary, and quality benchmark
scripts/analyze_results.py         Rebuilds markdown analysis from results.tsv
scripts/generate_infographics.py   Generates PNG infographics from results.tsv
data/latest/                       Captured latest benchmark results
assets/                            Generated infographic PNGs
```

## Run the benchmark

Edit `configs/rtx3090-bonsai-qwen.json` if model or llama.cpp paths differ, then run:

```bash
python3 scripts/run_benchmark.py --config configs/rtx3090-bonsai-qwen.json
python3 scripts/analyze_results.py --results runs/rtx3090-bonsai-qwen/results.tsv --out runs/rtx3090-bonsai-qwen/ANALYSIS.md
python3 scripts/generate_infographics.py --results runs/rtx3090-bonsai-qwen/results.tsv --out-dir runs/rtx3090-bonsai-qwen/assets
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
