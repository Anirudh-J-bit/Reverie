## AI²<br>
Sustainable AI for AI<br>
 Environmental Pre-Flight System

Team Name: Reverie

Team Members

* Anirudh J Nair
* Amal S
* Akhil E H
* Dhruvan S S

## An Intelligent Resource-Aware AI Orchestration Platform for Sustainable Artificial Intelligence

### 1. Project Overview

Artificial Intelligence requires massive computational power, but not every task demands the same resources. **GreenAI Optimizer** dynamically analyzes task complexity and routes requests to the most efficient suitable model.

> "Use only the amount of AI computation that is actually required to achieve the desired quality."

---

### 2. Problem Statement

* **Unnecessary Resource Consumption:** Defaulting to large models for simple queries wastes energy and compute.
* **Environmental Impact:** Higher energy usage drives up carbon footprints and hardware wear.
* **Cost Inefficiency:** Operating massive models for trivial tasks increases operational overhead.

---

### 3. Proposed Solution

An intelligent middleware layer that sits between users and AI models to:

* Classify task complexity (**Low**, **Medium**, **High**).
* Route requests to the smallest capable model.
* Monitor resource utilization and estimate energy savings.

---

### 4. Core Concept & Workflow

```text
User Request → Task Complexity Analysis → Model Selection → Execution → Resource Monitoring → Response + Dashboard

```

---

### 5. Intelligent Model Routing & Task Classification

* **Low Complexity:** Basic explanations $\rightarrow$ **Small Models** (Low energy).
* **Medium Complexity:** Multi-step reasoning $\rightarrow$ **Medium Models** (Balanced).
* **High Complexity:** Long-context analysis/coding $\rightarrow$ **Large Models** (Maximum capability).

---

### 6. Resource Monitoring & Energy Estimation

* **Metrics:** CPU/GPU usage, VRAM, latency, and token count.
* **Energy Formula:** $\text{Energy} = \text{Power} \times \text{Time}$
* **Carbon Footprint:** $\text{CO}_2\text{e} = \text{Energy Consumed} \times \text{Carbon Intensity}$

---

### 7. Sustainability Dashboard & Green Score

Provides real-time feedback and a custom Green Score (out of 100) per request.

| Metric | Conventional Approach | GreenAI Optimizer |
| --- | --- | --- |
| **Compute** | 100% | ~58% |
| **Energy** | 100% | ~64% |
| **Latency** | 100% | ~70% |
| **Quality** | 95% | ~93% |

---

### 8. Technology Stack

* **Frontend:** React.js / Vite (`greenai-optimizer-jungle-react`)
* **Backend:** Python, FastAPI (`ai-squared-backend`)
* **AI / Inference:** Hugging Face, Ollama, open-source models
* **Data & Visualization:** PostgreSQL / MongoDB, Recharts

---

### 9. Implementation Plan

1. Build core chat interface and connect multi-model backend.
2. Implement task complexity classifier.
3. Deploy intelligent model router.
4. Integrate resource monitoring and energy estimation.
5. Launch sustainability dashboard and benchmarking suite.
