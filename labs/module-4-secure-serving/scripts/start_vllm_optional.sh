#!/usr/bin/env bash
# Optional GPU track: start a local vLLM OpenAI-compatible server.
# Not used by CI / Cloud Agents.
set -euo pipefail

if [[ "${ACADEMY_GPU:-}" != "1" ]]; then
  echo "Refusing to start: set ACADEMY_GPU=1 to opt into the GPU track." >&2
  exit 1
fi

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi not found — CUDA host required for this script." >&2
  exit 1
fi

MODEL="${ACADEMY_VLLM_MODEL:-meta-llama/Meta-Llama-3-8B-Instruct}"
PORT="${ACADEMY_VLLM_PORT:-8001}"

echo "Starting vLLM for model=${MODEL} on port=${PORT}"
echo "Wire Module 4 with:"
echo "  export ACADEMY_GPU=1 ACADEMY_ENGINE=vllm ACADEMY_VLLM_URL=http://127.0.0.1:${PORT}"

exec python -m vllm.entrypoints.openai.api_server \
  --model "${MODEL}" \
  --port "${PORT}" \
  --gpu-memory-utilization "${ACADEMY_VLLM_GPU_MEM:-0.90}" \
  --block-size "${ACADEMY_VLLM_BLOCK_SIZE:-16}" \
  --max-num-seqs "${ACADEMY_VLLM_MAX_SEQS:-64}" \
  --enable-chunked-prefill \
  --tensor-parallel-size "${ACADEMY_VLLM_TP:-1}"
