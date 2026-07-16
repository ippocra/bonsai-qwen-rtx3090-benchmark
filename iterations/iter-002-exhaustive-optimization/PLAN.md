# Iteration 002 — Exhaustive llama.cpp Optimization Sweep

> **Status:** Plan & config written, **not executed**  
> **Hardware:** RTX 3090 24GB, RTX 3090 24GB, Ubuntu 22.04, CUDA 12.8, GCC 14  
> **Models:** Ternary Bonsai 27B-Q2_0, Qwen3.6-27B-Q4_K_M, Qwen3.6-35B-A3B-UD-Q4_K_M

---

## What was tested in Iteration 001 (baseline)

| Axis | Values |
|---|---|
| **Model** | Ternary Bonsai 27B-Q2_0, Qwen3.6-27B-Q4_K_M, Qwen3.6-35B-A3B-UD-Q4_K_M |
| **Context** | 32K, 64K, 128K, 196K, 252K, 262K |
| **GPU layers (`-ngl`)** | 20, 28, 36, 44, 60, 999 |
| **KV cache quant (`-ctk/-ctv`)** | q4_0/q4_0 (fit), q8_0/q8_0, f16/f16 (boundary) |
| **Prompt tokens (`-n`)** | 1 (fit), 32–256 (quality) |
| **Flash attention** | Always `on` |
| **Threads** | 12 (fixed) |
| **Speculative decoding** | None |
| **GPU/CPU offload ratio** | None |
| **KV cache quant** | None |

**Key findings from iter-001:**
- Bonsai 27B fits 262K at q4_0/q4_0, full GPU, 34 tok/s
- Qwen3.6-35B-A3B OOMs at 252K with q4_0/q4_0, ngl=999
- q8_0/q8_0 keeps Bonsai through 262K; Qwen27/Qwen35 OOM above 131K
- f16/f16: only Bonsai reaches 262K (OOM for both Qwens at 131K)
- Quality at q4_0/q4_0: Bonsai 6/7, Qwen35-A3B 5/7 (at 131K)

---

## What's missing — optimization axes to add

### 1. Speculative Decoding (`--spec-type`)

| Technique | Flag | Draft Model | Notes |
|---|---|---|---|
| **MTP** | `--spec-type draft-mtp` | Gemma-2-2b GGUF | Parallel head, single forward pass |
| **N-gram Mod** | `--spec-type ngram-mod` | N/A (zero VRAM) | Rolling LCG hash, ~2× on repetitive text |
| **Hybrid** | `--spec-type draft-mtp,ngram-mod` | Gemma-2-2b GGUF | MTP draft + N-gram verification |
| **D-Flash** | `--spec-type draft-dflash` | Gemma-2-2b GGUF | DFlash-style speculative drafting |

**Wiki caveat:** *"MTP self-speculation is workload-dependent, and three ways your spec-decode measurement lies."* — we need to measure against the same warmup/probe method.

### 2. Batch / Uber-batch Tuning

| Value | Purpose |
|---|---|
| `batch=128, ubatch=32` | Low contention |
| `batch=256, ubatch=64` | Balanced |
| `batch=512, ubatch=128` | Default (iter-001) |
| `batch=1024, ubatch=256` | High throughput |
| `GGML_CUDA_GRAPH_OPT=0` | Baseline (no graph) |
| `GGML_CUDA_GRAPH_OPT=1` | Compiled CUDA graphs |

### 3. Mixed KV Cache Quant

| Key Cache | Value Cache | VRAM vs q4/q4 |
|---|---|---|
| q4_0 | q4_0 | 1.0× (baseline) |
| q4_0 | q8_0 | ~1.5× |
| q8_0 | q4_0 | ~1.5× |
| q8_0 | q8_0 | ~2.0× |
| f16 | q4_0 | ~4.0× |

### 4. GPU/CPU Offload Ratio (`--gpu-cpu-ratio`)

| Ratio | Purpose |
|---|---|
| 999/0 | Full GPU (iter-001) |
| 80/20 | 80% KV on GPU, 20% on RAM |
| 90/10 | Mostly GPU, small RAM tail |

### 5. Thread Count (`-t`)

| Threads | Effect |
|---|---|
| 4 | Low contention, stable tok/s |
| 8 | Good throughput |
| 12 | Default (iter-001) |
| 16 | May saturate PCIe/VRAM bandwidth |
| 24 | Aggressive, may degrade |

### 6. Temperature / Top-P Grid

| Temp | Top-P | Purpose |
|---|---|---|
| 0 | 1.0 | Deterministic baseline |
| 0.05 | 0.9 | Near-deterministic |
| 0.1 | 0.9 | Light sampling |
| 0.15 | 0.9 | Moderate |
| 0.2 | 0.9 | Aggressive |

### 7. Warm KV Cache (vs. "Say OK.")

| `n_predict` | Purpose |
|---|---|
| 1 | Probe-only (iter-001) |
| 64 | Short response |
| 128 | Medium response |
| 256 | Long response (closest to real sessions) |

---

## Proposed Config

```json
{
  "backend": "/home/fido/work/PrismML-llama.cpp/build/bin/llama-completion",
  "hardware": "RTX 3090 24GB",
  "output_dir": "runs/iter-002-exhaustive",
  "models": [
    {
      "name": "Ternary-Bonsai-27B-Q2_0",
      "path": "/home/fido/models/ternary-bonsai-27b/Ternary-Bonsai-27B-Q2_0.gguf"
    },
    {
      "name": "Qwen3.6-27B-Q4_K_M",
      "path": "/home/fido/models/qwen3.6-27b/Qwen3.6-27B-Q4_K_M.gguf"
    },
    {
      "name": "Qwen3.6-35B-A3B-UD-Q4_K_M",
      "path": "/home/fido/models/qwen3.6-35b-a3b-gguf/Qwen3.6-35B-A3B-UD-Q4_K_M.gguf"
    }
  ],
  "fit_contexts": [
    32768,
    65536,
    128000,
    196608,
    252000,
    262144
  ],
  "gpu_layers": [
    20,
    28,
    36,
    44,
    60,
    999
  ],
  "quality_contexts": [
    131072,
    252000
  ],
  "fit_cache_types": [
    ["q4_0", "q4_0"]
  ],
  "boundary_cache_types": [
    ["q8_0", "q8_0"],
    ["f16", "f16"],
    ["q4_0", "q8_0"],
    ["q8_0", "q4_0"]
  ],
  "threads_grid": [
    4,
    8,
    12,
    16,
    24
  ],
  "batch_uber_grid": [
    {"b": 128, "ub": 32},
    {"b": 256, "ub": 64},
    {"b": 512, "ub": 128},
    {"b": 1024, "ub": 256}
  ],
  "gpu_offload_ratios": [
    [999, null, null],
    [999, 80, 20],
    [999, 90, 10]
  ],
  "temp_grid": [
    0,
    0.05,
    0.1,
    0.15,
    0.2
  ],
  "spec_types": [
    {
      "enabled": true,
      "type": "draft-mtp",
      "draft_model": "/home/fido/models/gemma2-2b-Q4_K_M.gguf",
      "ngram_size": null
    },
    {
      "enabled": true,
      "type": "ngram-mod",
      "draft_model": null,
      "ngram_size": 12
    },
    {
      "enabled": true,
      "type": "draft-mtp,ngram-mod",
      "draft_model": "/home/fido/models/gemma2-2b-Q4_K_M.gguf",
      "ngram_size": 12
    }
  ],
  "timeout_seconds": {
    "fit": 180,
    "boundary": 240,
    "quality": 300
  }
}
```

---

## Execution Plan

| Phase | What | Scope | Est. Time |
|---|---|---|---|
| **Phase 0 — Baseline** | Re-run iter-001 config | All 3 models | 2-3 hours |
| **Phase 1 — KV + Thread Sweep** | `threads_grid` × `boundary_cache_types` at ctx=128K, ngl=999 | All 3 models | 2 hours |
| **Phase 2 — Speculative Decoding** | `spec_types` on fit phase, ngl=999 | All 3 models | 3 hours |
| **Phase 3 — Warm KV + Temp Grid** | Quality phase with `warm KV` + `temp_grid` | All 3 models | 4 hours |
| **Phase 4 — Partial Offload** | `gpu-cpu-ratio` on Qwen35-A3B at 131K | Qwen35-A3B only | 3 hours |
| **TOTAL** | | | **14-15 hours** |

---

## Notes

- **Gemma-2-2b** must be downloaded as GGUF for speculative decoding drafts.
- `ngram-mod` needs `--spec-size 12` (default).
- Results folder: `runs/iter-002-exhaustive/`
- TSV output: `results.tsv`
- JSON output: `results.json`
- Logs: `logs/`
- Responses: `responses/`
