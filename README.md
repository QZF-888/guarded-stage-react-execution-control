# Guarded-Stage ReAct: Execution-Time Action Control

**Guarded-Stage ReAct** is a lightweight execution-time control layer for ReAct-style language agents in ALFWorld. It sits between the LLM's proposed action and the environment transition, checks whether the action is stage-consistent, and redirects unsafe or unproductive actions when needed.

中文说明见 [README.zh-CN.md](README.zh-CN.md).

## Core Idea

Standard ReAct agents often fail in long-horizon text environments because a locally valid action can be globally wrong:

- taking the wrong object,
- carrying an object to the wrong place,
- undoing progress by taking an already placed object back,
- searching the destination again after the first object has already been placed,
- placing an object before a required heat / cool / clean operation.

Guarded-Stage ReAct keeps the LLM as the main planner, but adds a small controller at execution time:

```text
observation + admissible actions + LLM proposal
        ↓
goal parser + progress state
        ↓
wrong-object guard + stage controller
        ↓
allow / block / redirect
        ↓
environment step
```

## What This Repository Contains

- A reusable Python implementation of the action guard and stage controller.
- A compact ALFWorld-oriented runner skeleton.
- Released result summaries for full valid-unseen evaluation.
- PickTwo debugging examples.
- Editable SVG diagrams for method and failure-mode explanations.
- English and Chinese documentation.

This repository intentionally does **not** include paper PDFs, LaTeX submission folders, or camera-ready manuscript files.

## Main Results

The main full valid-unseen result uses Qwen3.5-9B through an API backend on 134 ALFWorld valid-unseen tasks with a 25-step execution budget.

| Method | Tasks | Success | Success rate | Avg. steps | Notes |
|---|---:|---:|---:|---:|---|
| ReAct baseline | 134 | 35 | 26.12% | 20.44 | Standard ReAct |
| Strong-prompt ReAct | 134 | 46 | 34.33% | 19.49 | Prompt-only strengthening |
| Guarded-Stage ReAct | 134 | 110 | 82.09% | 11.80 | Wrong-object guard + stage controller |

## Repository Layout

```text
src/guarded_stage_react/   Core action-control implementation
scripts/                   Example runner and result summarization utilities
results/                   Released compact result summaries
examples/                  Small debugging examples
figures/                   Editable SVG diagrams
docs/                      Method and result notes
tests/                     Unit tests for the controller logic
```

## Quick Start

```bash
pip install -e ".[dev]"
pytest -q
```
