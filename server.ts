import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const XAI_API_URL = 'https://api.x.ai/v1/chat/completions';
const XAI_MODEL = process.env.XAI_MODEL || 'grok-4.6';

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json({ limit: '10mb' }));

  // API Routes
  app.get('/api/health', (req, res) => {
    res.json({
      status: 'ok',
      hasXaiKey: Boolean(process.env.XAI_API_KEY),
      model: XAI_MODEL,
      timestamp: new Date().toISOString()
    });
  });

  // xAI Grok AI Tutor Endpoint
  app.post('/api/ai/chat', async (req, res) => {
    try {
      const { prompt, context, conversationHistory } = req.body;

      if (!prompt) {
        return res.status(400).json({ error: 'Prompt is required' });
      }

      const apiKey = process.env.XAI_API_KEY;

      if (!apiKey) {
        // High quality fallback responses for learning concepts when key is absent
        const fallbackText = generateFallbackAiResponse(prompt, context);
        return res.json({
          reply: fallbackText,
          source: 'simulated_mentor'
        });
      }

      const systemInstruction = `You are the Principal AI Engineer Mentor for the "AI/ML Engineer Command Center". 
Your goal is to provide authoritative, mathematically precise, code-backed, and architecture-focused explanations for engineering students.
You specialize in:
1. Transformer internals (FlashAttention-3, Multi-Head Latent Attention/MLA, Rotary Embeddings/RoPE)
2. Post-training & RL (DPO, GRPO, Ra-DPO, Cold-start reasoning traces)
3. MoE Architectures (DeepSeek-V3 load-balancing, DualPipe pipeline parallelism, Multi-Token Prediction)
4. PEFT & Quantization (LoRA, QLoRA, AWQ, GGUF, FP8 block quantization)
5. Agent Orchestration (ReAct loops, DSPy, Model Context Protocol / MCP, PydanticAI, LangGraph)
6. Systems Optimization (vLLM, PagedAttention, Continuous Batching block_size tuning, Disaggregated Prefill/Decode, Speculative Decoding)
7. Production Security (Indirect Prompt Injection, Dual-LLM firewalls)
8. Evaluation & CI/CD (EDD, DeepEval, Ragas, Promptfoo, OpenTelemetry)

Keep answers structured with Markdown headings, code blocks (Python/TypeScript/Bash), clear tradeoffs, and bullet points.
Context module: ${context || 'General AI Engineering'}`;

      const messages: Array<{ role: 'system' | 'user' | 'assistant'; content: string }> = [
        { role: 'system', content: systemInstruction }
      ];

      for (const msg of conversationHistory || []) {
        const role = msg.role === 'assistant' ? 'assistant' : 'user';
        if (msg.content) {
          messages.push({ role, content: String(msg.content) });
        }
      }

      messages.push({ role: 'user', content: prompt });

      const xaiResponse = await fetch(XAI_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: XAI_MODEL,
          messages,
          temperature: 0.7
        })
      });

      if (!xaiResponse.ok) {
        const errorBody = await xaiResponse.text();
        throw new Error(`xAI API ${xaiResponse.status}: ${errorBody.slice(0, 300)}`);
      }

      const data = (await xaiResponse.json()) as {
        choices?: Array<{ message?: { content?: string } }>;
      };
      const reply = data.choices?.[0]?.message?.content?.trim();

      return res.json({
        reply: reply || 'No output generated from Grok.',
        source: XAI_MODEL
      });
    } catch (err: any) {
      console.error('xAI Grok API Error:', err);
      // Fallback response on error so user experience remains flawless
      const fallbackText = generateFallbackAiResponse(req.body.prompt, req.body.context);
      return res.json({
        reply: `${fallbackText}\n\n*(Note: Powered by Curriculum Knowledge Engine; xAI Grok API encountered an issue: ${err.message || 'Service temporarily unreachable'})*`,
        source: 'curriculum_engine'
      });
    }
  });

  // Code Simulation Runner Route
  app.post('/api/simulate-code', (req, res) => {
    const { code, language, title } = req.body;
    
    // Simulate execution output
    let output = '';
    if (language === 'python') {
      if (code.includes('StreamingResponse') || title?.includes('Streaming Service')) {
        output = `[INFO] Creating FastAPI app instance...
[INFO] Validating PromptRequest schema constraints...
[INFO] Exercising /api/v1/generate/stream over text/event-stream
[INFO] SSE frames emitted: data: Processing | data: prompt | data: [DONE]
[SUCCESS] FastAPI server running on port 3000. Streaming tokens verified via SSE event loop.`;
      } else if (code.includes('vllm') || title?.includes('vLLM')) {
        output = `[INFO] Initializing vLLM Engine v0.6.2...
[INFO] GPU Memory Utilization target: 0.95
[INFO] PagedAttention Block Size: 16 tokens | Total blocks: 40,960
[INFO] Loading base model weights: llama-3-8b-instruct
[INFO] Prefill batch processed: 128 prompts in 142ms (TTFT: 142ms)
[INFO] Decode loop running: 450 tokens/sec total throughput
[SUCCESS] Execution complete. No OOM errors detected. Memory fragmentation: 0.82%`;
      } else if (code.includes('pydantic') || code.includes('agent')) {
        output = `[INFO] Initializing PydanticAI Agent with result_type=SQLQueryResult
[INFO] Step 1: User prompt received -> "Find top 5 customers by revenue"
[INFO] Step 2: LLM invoked -> Generating SQL query
[INFO] Step 3: Tool called -> execute_sql_query(sql='SELECT name, revenue FROM customers ORDER BY revenue DESC LIMIT 5')
[INFO] Step 4: Validation PASSED -> 5 records matched schema
[SUCCESS] Agent Execution Result:
[
  {"name": "Enterprise Corp", "revenue": "$1,250,000"},
  {"name": "TechGlobal Inc", "revenue": "$980,000"},
  {"name": "Apex AI Systems", "revenue": "$840,000"}
]`;
      } else if (code.includes('LoraConfig') || code.includes('QLoRA')) {
        output = `[INFO] Loading base model in 4-bit NF4 precision (BitsAndBytes)...
[INFO] Injecting LoRA adapter matrices into target_modules=['q_proj', 'v_proj']
[INFO] Trainable parameters: 4,194,304 / 8,030,000,000 (0.052% of total weights)
[INFO] Epoch 1/3 | Loss: 1.428 | VRAM Allocated: 5.2 GB
[INFO] Epoch 2/3 | Loss: 0.892 | VRAM Allocated: 5.2 GB
[INFO] Epoch 3/3 | Loss: 0.611 | VRAM Allocated: 5.2 GB
[SUCCESS] Fine-tuning completed successfully! Adapter weights saved to ./adapter_model.bin`;
      } else {
        output = `[INFO] Executing script in sandbox environment...
[INFO] Imports verified: scikit-learn, numpy, pandas, torch
[SUCCESS] Output generated successfully: 
Accuracy: 0.964 | F1-Score: 0.958 | Loss: 0.042`;
      }
    } else if (language === 'docker' || language === 'bash') {
      output = `[DOCKER] Building stage 1: builder (python:3.11-slim)...
[DOCKER] Installing dependencies with pip --user...
[DOCKER] Building stage 2: final production container...
[DOCKER] Copying clean binaries from builder stage...
[SUCCESS] Image built successfully: ai-engine-service:v3.1 (Size: 184MB - 82% smaller than non-multi-stage image!)`;
    } else {
      output = `[SIMULATION] Executed ${language || 'code'} block successfully.\nResponse Status: 200 OK\nTimestamp: ${new Date().toISOString()}`;
    }

    res.json({ output, executionTimeMs: Math.floor(Math.random() * 80) + 120 });
  });

  // Vite middleware in dev, static files in prod
  if (process.env.NODE_ENV !== 'production') {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa'
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`AI Engineer Academy server running at http://0.0.0.0:${PORT}`);
  });
}

function generateFallbackAiResponse(prompt: string, context?: string): string {
  const p = prompt.toLowerCase();
  
  if (p.includes('flashattention') || p.includes('attention')) {
    return `### FlashAttention-3 & Memory Tiling Mechanics

FlashAttention-3 optimizes the standard $O(N^2)$ self-attention mechanism by avoiding slow High Bandwidth Memory (HBM) writes for intermediate $N \\times N$ attention matrices ($S = Q K^T / \\sqrt{d}$).

**Key Architectural Innovations:**
1. **Asynchronous Producer-Consumer Pipeline:** Interleaves Tensor Memory Accelerator (TMA) data loading with Tensor Core GEMM operations on Hopper GPUs (H100/H200).
2. **FP8 Low-Precision Computation:** Utilizes block-wise quantization with incoherent processing to mitigate outlier activation spikes.
3. **On-Chip SRAM Tiling:** Computes Softmax incrementally using online softmax normalization without ever instantiating full attention matrices in HBM.

**Code Impact:**
\`\`\`python
# Utilizing FlashAttention-3 in PyTorch via Flash-Attn package
from flash_attn import flash_attn_func

# q, k, v shapes: [batch_size, seq_len, num_heads, head_dim]
out = flash_attn_func(q, k, v, dropout_p=0.0, softmax_scale=1.0 / (head_dim**0.5), causal=True)
\`\`\``;
  }

  if (p.includes('mcp') || p.includes('model context protocol')) {
    return `### Model Context Protocol (MCP) Standard

The **Model Context Protocol (MCP)** by Anthropic is an open JSON-RPC 2.0 protocol standardizing how LLM agents interact with tools, resources, and prompt templates.

**Transport Topology:**
- **stdio (Standard Input/Output):** Local process subprocess execution with sub-millisecond JSON-RPC line delimited messages. Ideal for local filesystem, IDE, and terminal tools.
- **SSE (Server-Sent Events over HTTP):** Asynchronous streaming over HTTP POST (client -> server commands) and SSE (server -> client event stream) for remote distributed tool servers.

**Primitives:**
- \`Tools\`: Invokable functions with JSON schemas.
- \`Resources\`: Static or dynamic context files/URIs.
- \`Prompts\`: Reusable prompt templates.`;
  }

  if (p.includes('dpo') || p.includes('grpo') || p.includes('rlhf')) {
    return `### GRPO (Group Relative Policy Optimization) vs DPO vs PPO

**Group Relative Policy Optimization (GRPO):**
Pioneered in DeepSeekMath & DeepSeek-R1, GRPO completely **removes the Critic (Value) neural network** required by PPO.

**How GRPO Works:**
1. For a prompt $q$, the policy $\\pi_\\theta$ generates a group of $G$ outputs $\\{o_1, o_2, \\dots, o_G\\}$.
2. A deterministic reward function or judge evaluates each output $r_i$.
3. Normalized advantages are computed relative to the group mean and std:
   $$A_i = \\frac{r_i - \\text{mean}(R)}{\\text{std}(R)}$$
4. This reduces GPU VRAM consumption by ~50% compared to PPO, enabling massive RL scaling for complex reasoning.`;
  }

  return `### AI Engineering Architecture Insight

To achieve production reliability with non-deterministic LLMs:

1. **Type Safety & Schema Validation:** Always wrap tool calls in validation frameworks (like **PydanticAI** or Zod) to catch malformed JSON at the boundary and automatically trigger reflection retries.
2. **Inference Optimization:** Deploy models via **vLLM** using **PagedAttention** to eliminate KV cache memory fragmentation.
3. **Security Boundaries:** Enforce a **Dual-LLM Security Topology** (Minimizer + Sanitizer firewalls) to protect agents against Indirect Prompt Injection attacks when fetching untrusted web or database data.

*Question subject:* **${context || 'General AI System Design'}**`;
}

startServer();
