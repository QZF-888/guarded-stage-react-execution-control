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

![Method overview](figures/guarded_stage_react_flowchart.svg)

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

By task type, Guarded-Stage ReAct reaches:

| Task type | Tasks | Success | Success rate |
|---|---:|---:|---:|
| look_at_obj_in_light | 18 | 18 | 100.00% |
| pick_and_place_simple | 24 | 20 | 83.33% |
| pick_clean_then_place_in_recep | 31 | 26 | 83.87% |
| pick_cool_then_place_in_recep | 21 | 17 | 80.95% |
| pick_heat_then_place_in_recep | 23 | 18 | 78.26% |
| pick_two_obj_and_place | 17 | 11 | 64.71% |

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

Install the lightweight package:

```bash
pip install -e ".[dev]"
```

Run unit tests:

```bash
pytest -q
```

Use the controller in another ALFWorld runner:

```python
from guarded_stage_react import GuardedStageController

controller = GuardedStageController(goal_text)
safe_action, reason = controller.control(
    proposed_action=llm_action,
    admissible_actions=admissible_actions,
    inventory=inventory,
    observation=observation,
    last_action=last_action,
)
```

The returned `safe_action` can be executed in the environment. `reason` records whether the original action was allowed or redirected by a guard/controller rule.

## Reproduction Notes

- Environment: ALFWorld valid-unseen.
- Main budget: 25 executable steps per task.
- Main controller: wrong-object guard + PickTwo stage controller + fallback ranking.
- The released summaries are compact artifacts. Large raw traces are not committed because they are multi-megabyte logs.

## Citation

If you use this repository, cite the project as:

```bibtex
@software{guarded_stage_react_2026,
  title = {Guarded-Stage ReAct: Execution-Time Action Control for Reliable Language Agents},
  year = {2026},
  url = {https://github.com/QZF-888/guarded-stage-react-execution-control}
}
```
