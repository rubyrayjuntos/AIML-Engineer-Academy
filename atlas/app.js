const TOPICS = [
  { module: "M1", depth: "proved", name: "Async FastAPI + SSE" },
  { module: "M1", depth: "proved", name: "Multi-stage Docker" },
  { module: "M1", depth: "proved", name: "TF-IDF baseline + held-out P/R/F1" },
  { module: "M1", depth: "proved", name: "Leakage clinic" },
  { module: "M1", depth: "proved", name: "PII detect / mask" },
  { module: "M1", depth: "proved", name: "CPU RAG: chunk, hybrid retrieve, cite" },
  { module: "M1", depth: "survey", name: "gRPC / WebSocket" },
  { module: "M1", depth: "survey", name: "Neural embeddings / hosted vector DBs" },
  { module: "M2", depth: "proved", name: "Attention / KV-byte numerics" },
  { module: "M2", depth: "proved", name: "LoRA + int4 arithmetic" },
  { module: "M2", depth: "proved", name: "GRPO advantages" },
  { module: "M2", depth: "proved", name: "MoE routing numerics" },
  { module: "M2", depth: "proved", name: "Diffusion q_sample + DDIM toy" },
  { module: "M2", depth: "proved", name: "DPO loss toy" },
  { module: "M2", depth: "survey", name: "FlashAttention-3" },
  { module: "M2", depth: "survey", name: "MLA vs GQA" },
  { module: "M2", depth: "survey", name: "DualPipe / MTP" },
  { module: "M2", depth: "survey", name: "AWQ / GGUF" },
  { module: "M2", depth: "optional", name: "Live QLoRA on CUDA" },
  { module: "M3", depth: "proved", name: "Customer Success HITL ReAct" },
  { module: "M3", depth: "proved", name: "Read-only SQL firewall + MCP stdio" },
  { module: "M3", depth: "proved", name: "Dual-LLM IPI topology (CPU)" },
  { module: "M3", depth: "proved", name: "DSPy compile stub" },
  { module: "M3", depth: "survey", name: "LangGraph" },
  { module: "M3", depth: "survey", name: "Agent memory tiers" },
  { module: "M3", depth: "survey", name: "RAG vs fine-tune strategy" },
  { module: "M3", depth: "optional", name: "Live PydanticAI / Playwright / sanitizer LLM" },
  { module: "M4", depth: "proved", name: "Auth, rate limits, timeouts" },
  { module: "M4", depth: "proved", name: "CPU p50/p95/p99 budgets" },
  { module: "M4", depth: "proved", name: "Speculative-decoding teaching math" },
  { module: "M4", depth: "survey", name: "PagedAttention / continuous batching" },
  { module: "M4", depth: "survey", name: "Disaggregated prefill / FlowKV" },
  { module: "M4", depth: "optional", name: "Live vLLM adapter" },
  { module: "M5", depth: "proved", name: "Offline EDD gates" },
  { module: "M5", depth: "proved", name: "Canary reject + rollback" },
  { module: "M5", depth: "proved", name: "HF / Render / Azure / Databricks plans" },
  { module: "M5", depth: "survey", name: "G-Eval / LLM-as-judge" },
  { module: "M5", depth: "survey", name: "Ragas (no CI install)" },
  { module: "M5", depth: "survey", name: "OpenTelemetry" },
  { module: "M5", depth: "optional", name: "Live DeepEval / Promptfoo / deploy APIs" },
  { module: "—", depth: "thin", name: "Experiment tracking (W&B / MLflow)" },
  { module: "—", depth: "thin", name: "Data versioning / feature stores" },
  { module: "—", depth: "thin", name: "Token economics as a first-class topic" },
  { module: "—", depth: "thin", name: "Safety beyond Dual-LLM IPI" },
  { module: "—", depth: "thin", name: "Batch vs realtime inference" },
  { module: "—", depth: "thin", name: "Model cards / eval slices" },
];

const LABELS = {
  proved: "CPU-proved",
  survey: "Survey",
  optional: "Optional live",
  thin: "Thin",
};

const mapEl = document.getElementById("map");
const statusEl = document.getElementById("filter-status");

function render(filter) {
  const nodes = TOPICS.map((topic) => {
    const li = document.createElement("li");
    li.dataset.depth = topic.depth;
    if (filter !== "all" && topic.depth !== filter) li.classList.add("is-dim");

    const mod = document.createElement("span");
    mod.className = "map__mod";
    mod.textContent = topic.module;

    const name = document.createElement("span");
    name.textContent = topic.name;

    const depth = document.createElement("span");
    depth.className = "map__depth";
    depth.textContent = LABELS[topic.depth];

    li.append(mod, name, depth);
    return li;
  });
  mapEl.replaceChildren(...nodes);
  const n = filter === "all" ? TOPICS.length : TOPICS.filter((t) => t.depth === filter).length;
  statusEl.textContent =
    filter === "all"
      ? `Showing all ${TOPICS.length} topics. Use the legend to isolate a depth.`
      : `Showing ${n} ${LABELS[filter].toLowerCase()} topics. Others stay on the sheet, dimmed.`;
}

let active = "all";
render(active);

document.querySelectorAll(".legend button").forEach((btn) => {
  btn.addEventListener("click", () => {
    active = btn.dataset.depth;
    document.querySelectorAll(".legend button").forEach((b) => {
      b.setAttribute("aria-pressed", String(b === btn));
    });
    render(active);
  });
});

const enter = document.getElementById("enter-applet");
const note = document.getElementById("enter-note");
if (window.location.protocol === "file:") {
  enter.hidden = true;
  note.hidden = false;
}
