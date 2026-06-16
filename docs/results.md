# Result Notes

The released summaries are compact versions of the experiment outputs. Large raw traces and the unpublished paper PDF are intentionally not committed.

## Full valid-unseen comparison

All methods are evaluated on the same 134 ALFWorld valid-unseen tasks with a 25-step budget.

| Backbone | Method | Success | Success rate |
|---|---|---:|---:|
| Llama-3.1-8B | ReAct baseline | 35/134 | 26.1 |
| Llama-3.1-8B | Strong Prompt ReAct | 46/134 | 34.3 |
| Llama-3.1-8B | Guarded-Stage ReAct | 77/134 | 57.5 |
| Qwen3.5-9B | ReAct baseline | 100/134 | 74.6 |
| Qwen3.5-9B | Strong Prompt ReAct | 108/134 | 80.6 |
| Qwen3.5-9B | Guarded-Stage ReAct | 110/134 | 82.1 |

## Task-type success counts

| Task type | Llama R | Llama SP | Llama G | Qwen R | Qwen SP | Qwen G |
|---|---:|---:|---:|---:|---:|---:|
| Desklamp | 10/18 | 7/18 | 7/18 | 16/18 | 18/18 | 18/18 |
| PickPlace | 5/24 | 9/24 | 11/24 | 20/24 | 18/24 | 20/24 |
| Clean | 10/31 | 12/31 | 20/31 | 23/31 | 25/31 | 26/31 |
| Cool | 4/21 | 6/21 | 9/21 | 18/21 | 18/21 | 17/21 |
| Heat | 6/23 | 12/23 | 17/23 | 17/23 | 17/23 | 18/23 |
| PickTwo | 0/17 | 0/17 | 13/17 | 6/17 | 12/17 | 11/17 |
| Overall | 35/134 | 46/134 | 77/134 | 100/134 | 108/134 | 110/134 |

R, SP, and G denote ReAct, Strong Prompt ReAct, and Guarded-Stage ReAct.

## Paired comparisons

| Backbone | Comparison | Both success | Both fail | First only | Second only | p-value |
|---|---|---:|---:|---:|---:|---:|
| Llama-3.1-8B | G vs R | 27 | 49 | 50 | 8 | 1.57e-8 |
| Llama-3.1-8B | G vs SP | 41 | 52 | 36 | 5 | 7.84e-7 |
| Llama-3.1-8B | SP vs R | 24 | 77 | 22 | 11 | 0.080 |
| Qwen3.5-9B | G vs R | 96 | 20 | 14 | 4 | 0.0309 |
| Qwen3.5-9B | SP vs R | 95 | 21 | 13 | 5 | 0.096 |
| Qwen3.5-9B | G vs SP | 104 | 20 | 6 | 4 | 0.754 |

## Intervention statistics

| Backbone | Guard | Stage | Fallback | Tasks with intervention | Solved tasks with intervention |
|---|---:|---:|---:|---:|---:|
| Llama-3.1-8B | 450 | 60 | 458 | 94 | 45 |
| Qwen3.5-9B | 151 | 64 | 151 | 51 | 32 |

## Seed42 random50 ablation

| Method | Success rate |
|---|---:|
| ReAct v3 baseline | 34.0 |
| V5 baseline-patch | 36.0 |
| w/o wrong-object guard | 34.0 |
| w/o PickTwo controller | 42.0 |
| w/o PickTwo-specific prompt | 50.0 |
| Guarded-Stage ReAct | 50.0 |
