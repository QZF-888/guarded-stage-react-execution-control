# Result Notes

The released summaries are compact versions of the experiment outputs. Large raw traces are not committed because they contain multi-megabyte step-by-step interaction logs.

## Full valid-unseen comparison

| Method | Tasks | Success | Success rate | Avg. steps | Avg. time |
|---|---:|---:|---:|---:|---:|
| ReAct baseline | 134 | 35 | 0.2612 | 20.44 | 82.0s |
| Strong-prompt ReAct | 134 | 46 | 0.3433 | 19.49 | 82.1s |
| Guarded-Stage ReAct | 134 | 110 | 0.8209 | 11.80 | 24.0s |

## Guarded-Stage full valid-unseen by task type

| Task type | n | Success | Success rate |
|---|---:|---:|---:|
| look_at_obj_in_light | 18 | 18 | 1.0000 |
| pick_and_place_simple | 24 | 20 | 0.8333 |
| pick_clean_then_place_in_recep | 31 | 26 | 0.8387 |
| pick_cool_then_place_in_recep | 21 | 17 | 0.8095 |
| pick_heat_then_place_in_recep | 23 | 18 | 0.7826 |
| pick_two_obj_and_place | 17 | 11 | 0.6471 |
