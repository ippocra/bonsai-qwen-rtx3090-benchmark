#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import signal
import subprocess
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROMPTS = {
    'reasoning': 'A farmer has 17 sheep. All but 9 run away. How many sheep does the farmer have left? Answer with the final number and one concise explanation.',
    'coding': 'Write a Python function two_sum(nums: list[int], target: int) -> tuple[int, int] that returns the two numbers adding to target. Include a docstring and raise ValueError if no pair exists.',
    'json': 'Return only valid JSON with keys name, version, and description about Python. No markdown.',
    'agentic_tool_selection': 'You are Hermes running in a tool-calling environment. The user wants to inspect a file before editing it. The target file is /tmp/demo.py. The user request is: "Replace the current placeholder with a function that returns 4." You do not know the file contents yet. Output only the single next tool call in a compact JSON object with keys tool and arguments. Choose the most appropriate next tool. Do not explain.',
    'agentic_recovery': 'You are Hermes. A previous attempt failed because terminal tried to open /tmp/missing-file.txt and got ENOENT. Now recover by choosing the next best tool. You may inspect the filesystem first if that helps. Output only the next tool call in compact JSON with keys tool and arguments. Do not explain.',
    'agentic_no_tool': 'The user asks: "What is 7 * 8?" Do not use any tools. Answer directly with only the final answer.',
    'agentic_session_recall': 'You are Hermes. The user asks what we decided about the router stop order in the last session. Use session_search before answering if needed. Output only the next tool call in compact JSON with keys tool and arguments. Do not explain.',
    'fit_probe': 'Say OK.',
}

QUALITY_CASES = [
    ('reasoning', 96),
    ('coding', 256),
    ('json', 128),
    ('agentic_tool_selection', 128),
    ('agentic_recovery', 128),
    ('agentic_no_tool', 32),
    ('agentic_session_recall', 128),
]

PROMPT_RE = re.compile(r'prompt eval time\s*=\s*([0-9.]+)\s*ms\s*/\s*(\d+)\s*tokens\s*\([^)]*?([0-9.]+)\s*tokens per second\s*\)', re.I)
GEN_RE = re.compile(r'eval time\s*=\s*([0-9.]+)\s*ms\s*/\s*(\d+)\s*(?:runs|tokens)\s*\([^)]*?([0-9.]+)\s*tokens per second\s*\)', re.I)
TOTAL_RE = re.compile(r'total time\s*=\s*([0-9.]+)\s*ms\s*/\s*(\d+)\s*tokens', re.I)
LOAD_RE = re.compile(r'load time\s*=\s*([0-9.]+)\s*ms', re.I)
THINK_RE = re.compile(r'<think>.*?</think>', re.I | re.S)


@dataclass
class Result:
    phase: str
    case: str
    model: str
    ctx: int
    ngl: int
    cache_k: str
    cache_v: str
    n_predict: int
    rc: int | None
    status: str
    score: int | None
    note: str
    prompt_tokens: int | None
    generated_tokens: int | None
    prompt_tok_s: float | None
    gen_tok_s: float | None
    load_ms: float | None
    total_ms: float | None
    start_vram_mb: int | None
    peak_vram_mb: int | None
    end_vram_mb: int | None
    seconds: float
    prompt_file: str
    response_file: str
    log_file: str
    command: str


def sample_vram_mb() -> int | None:
    try:
        out = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except Exception:
        return None
    vals = [int(line.strip()) for line in out.splitlines() if line.strip().isdigit()]
    return max(vals) if vals else None


def parse_perf(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {'prompt_tokens': None, 'generated_tokens': None, 'prompt_tok_s': None, 'gen_tok_s': None, 'load_ms': None, 'total_ms': None}
    m = LOAD_RE.search(text)
    if m:
        data['load_ms'] = float(m.group(1))
    m = PROMPT_RE.search(text)
    if m:
        data['prompt_tokens'] = int(m.group(2))
        data['prompt_tok_s'] = float(m.group(3))
    matches = list(GEN_RE.finditer(text))
    if matches:
        m = matches[-1]
        data['generated_tokens'] = int(m.group(2))
        data['gen_tok_s'] = float(m.group(3))
    m = TOTAL_RE.search(text)
    if m:
        data['total_ms'] = float(m.group(1))
    return data


def classify_status(rc: int | None, output: str, timed_out: bool) -> str:
    lower = output.lower()
    if timed_out:
        return 'timeout'
    if 'prompt is too long' in lower:
        return 'prompt_too_long'
    oom_markers = ['out of memory', 'cuda error: out of memory', 'cuda error 2', 'failed to allocate', 'ggml_backend_cuda_buffer_type_alloc_buffer', 'memory allocation failed']
    if any(marker in lower for marker in oom_markers):
        return 'oom'
    if rc == 0:
        return 'ok'
    return f'rc_{rc}'


def clean_response(text: str) -> str:
    return THINK_RE.sub('', text).replace('[end of text]', '').strip()


def score_case(case: str, response: str) -> tuple[int | None, str]:
    text = clean_response(response)
    lower = text.lower()
    if case == 'reasoning':
        return (1 if re.search(r'\b9\b', text) else 0, 'expected 9 sheep left')
    if case == 'coding':
        ok = 'def two_sum' in text and 'target' in text and ('ValueError' in text or 'raise' in text)
        return (1 if ok else 0, 'expected complete two_sum implementation')
    if case == 'json':
        try:
            obj = json.loads(text)
            ok = all(key in obj for key in ['name', 'version', 'description'])
        except Exception:
            ok = False
        return (1 if ok else 0, 'expected parseable JSON with required keys')
    if case == 'agentic_no_tool':
        ok = ('56' in text or 'fifty-six' in lower) and not any(tok in lower for tok in ['read_file', 'search_files', 'session_search', 'terminal'])
        return (1 if ok else 0, 'expected direct answer 56 without tool call')
    if case == 'agentic_tool_selection':
        return (1 if 'read_file' in lower and '/tmp/demo.py' in text else 0, 'expected read_file on /tmp/demo.py')
    if case == 'agentic_recovery':
        ok = any(tok in lower for tok in ['search_files', 'read_file', 'terminal']) and 'enoent' not in lower
        return (1 if ok else 0, 'expected a recovery tool choice without repeating ENOENT')
    if case == 'agentic_session_recall':
        return (1 if 'session_search' in lower else 0, 'expected session_search')
    return (None, '')


def run_one(config: dict[str, Any], out_dir: Path, phase: str, case: str, model: dict[str, str], ctx: int, ngl: int, cache: tuple[str, str], n_predict: int, timeout_s: int) -> Result:
    backend = Path(config['backend'])
    cache_k, cache_v = cache
    prompt_dir = out_dir / 'prompts'
    log_dir = out_dir / 'logs'
    response_dir = out_dir / 'responses'
    for path in [prompt_dir, log_dir, response_dir]:
        path.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / f'{phase}__{case}.txt'
    prompt_path.write_text(PROMPTS[case], encoding='utf-8')
    stem = f'{phase}__{model["name"]}__{case}__ctx{ctx}__ngl{ngl}__{cache_k}_{cache_v}'
    log_path = log_dir / f'{stem}.log'
    response_path = response_dir / f'{stem}.txt'
    cmd = [str(backend), '-m', model['path'], '-c', str(ctx), '-n', str(n_predict), '-ngl', str(ngl), '-fit', 'off', '-fa', 'on', '--perf', '--simple-io', '--skip-chat-parsing', '--reasoning', 'off', '-no-cnv', '--no-display-prompt', '--no-warmup', '-ctk', cache_k, '-ctv', cache_v, '-b', str(config.get('batch_size', 512)), '-ub', str(config.get('ubatch_size', 128)), '-t', str(config.get('threads', 12)), '--temp', '0', '--top-p', '1', '--seed', '42', '-f', str(prompt_path)]
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = str(backend.parent)
    start_time = time.time()
    start_vram = sample_vram_mb()
    peak_vram = start_vram
    timed_out = False
    stop_event = threading.Event()

    def sampler() -> None:
        nonlocal peak_vram
        while not stop_event.is_set():
            cur = sample_vram_mb()
            if cur is not None:
                peak_vram = cur if peak_vram is None else max(peak_vram, cur)
            time.sleep(0.25)

    with log_path.open('w', encoding='utf-8') as log:
        log.write(f'COMMAND: {" ".join(cmd)}\nSTART_VRAM_MB: {start_vram}\n')
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', env=env, start_new_session=True)
        thread = threading.Thread(target=sampler, daemon=True)
        thread.start()
        try:
            stdout, stderr = proc.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                stdout, stderr = proc.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                stdout, stderr = proc.communicate()
        finally:
            stop_event.set()
            thread.join(timeout=3)
        rc = proc.returncode
        end_vram = sample_vram_mb()
        output = (stdout or '') + (stderr or '')
        log.write(output)
        log.write(f'\nEND_VRAM_MB: {end_vram}\nRETURN_CODE: {rc}\nTIMED_OUT: {timed_out}\n')
    response_path.write_text(stdout or '', encoding='utf-8')
    perf = parse_perf(output)
    status = classify_status(rc, output, timed_out)
    score, note = score_case(case, stdout or '') if phase == 'quality' and status == 'ok' else (None, '')
    return Result(phase, case, model['name'], ctx, ngl, cache_k, cache_v, n_predict, rc, status, score, note, perf['prompt_tokens'], perf['generated_tokens'], perf['prompt_tok_s'], perf['gen_tok_s'], perf['load_ms'], perf['total_ms'], start_vram, peak_vram, end_vram, round(time.time() - start_time, 3), str(prompt_path), str(response_path), str(log_path), ' '.join(cmd))


def write_results(out_dir: Path, results: list[Result]) -> None:
    if not results:
        return
    with (out_dir / 'results.tsv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(results[0]).keys()), delimiter='\t')
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))
    (out_dir / 'results.json').write_text(json.dumps([asdict(r) for r in results], indent=2), encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Bonsai vs Qwen llama.cpp hardware squeeze benchmark.')
    parser.add_argument('--config', default='configs/rtx3090-bonsai-qwen.json')
    args = parser.parse_args()
    config_path = Path(args.config)
    config = json.loads(config_path.read_text(encoding='utf-8'))
    out_dir = Path(config['output_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[Result] = []
    timeouts = config.get('timeout_seconds', {})
    for model in config['models']:
        for ctx in config['fit_contexts']:
            for ngl in config['gpu_layers']:
                for cache in config.get('fit_cache_types', [['q4_0', 'q4_0']]):
                    print(f'fit {model["name"]} ctx={ctx} ngl={ngl} cache={cache[0]}/{cache[1]}', flush=True)
                    results.append(run_one(config, out_dir, 'fit', 'fit_probe', model, ctx, ngl, tuple(cache), 1, int(timeouts.get('fit', 180))))
                    write_results(out_dir, results)
    for model in config['models']:
        for ctx in config['quality_contexts']:
            for case, n_predict in QUALITY_CASES:
                print(f'quality {model["name"]} {case} ctx={ctx} ngl=999', flush=True)
                results.append(run_one(config, out_dir, 'quality', case, model, ctx, 999, ('q4_0', 'q4_0'), n_predict, int(timeouts.get('quality', 300))))
                write_results(out_dir, results)
    for model in config['models']:
        for ctx in config['quality_contexts'] + [262144]:
            for cache in config.get('boundary_cache_types', []):
                print(f'boundary {model["name"]} ctx={ctx} ngl=999 cache={cache[0]}/{cache[1]}', flush=True)
                results.append(run_one(config, out_dir, 'boundary', 'fit_probe', model, ctx, 999, tuple(cache), 1, int(timeouts.get('boundary', 240))))
                write_results(out_dir, results)
    print(out_dir / 'results.tsv')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
