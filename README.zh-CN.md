# Guarded-Stage ReAct：推理执行期动作控制

**Guarded-Stage ReAct** 是一个用于 ALFWorld 这类长程文本交互环境的轻量级执行期控制层。它放在 LLM 生成动作之后、环境真正执行动作之前，用来检查动作是否符合当前任务阶段，并在必要时阻止或重定向动作。

English README: [README.md](README.md)

## 核心思想

标准 ReAct agent 在长程任务中经常失败，不是因为动作语法非法，而是因为动作在全局任务阶段上不合适，例如：

- 拿错物体；
- 拿着目标物体却不去目标位置；
- 把已经放好的物体又拿回来；
- PickTwo 任务中放完第一个目标后，又回到目标容器附近反复搜索；
- 需要 heat / cool / clean 的任务中，未完成操作就提前放置。

Guarded-Stage ReAct 不替代 LLM 规划，而是在执行期加入一个小控制器：

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

## 仓库内容

- 可复用的 Python action guard 和 stage controller 实现。
- 面向 ALFWorld 的紧凑运行入口示例。
- full valid-unseen 实验结果摘要。
- PickTwo 调试样例。
- 可编辑 SVG 方法图和错误类型图。
- 中英文说明文档。

本仓库**不包含**论文 PDF、LaTeX 投稿包、论文草稿或 camera-ready 文件。

## 主要结果

主结果使用 Qwen3.5-9B API 后端，在 ALFWorld valid-unseen 134 个任务上评测，最大执行步数为 25。

| 方法 | 任务数 | 成功数 | 成功率 | 平均步数 | 说明 |
|---|---:|---:|---:|---:|---|
| ReAct baseline | 134 | 35 | 26.12% | 20.44 | 标准 ReAct |
| Strong-prompt ReAct | 134 | 46 | 34.33% | 19.49 | 只增强 prompt |
| Guarded-Stage ReAct | 134 | 110 | 82.09% | 11.80 | wrong-object guard + stage controller |

按任务类型统计：

| 任务类型 | 任务数 | 成功数 | 成功率 |
|---|---:|---:|---:|
| look_at_obj_in_light | 18 | 18 | 100.00% |
| pick_and_place_simple | 24 | 20 | 83.33% |
| pick_clean_then_place_in_recep | 31 | 26 | 83.87% |
| pick_cool_then_place_in_recep | 21 | 17 | 80.95% |
| pick_heat_then_place_in_recep | 23 | 18 | 78.26% |
| pick_two_obj_and_place | 17 | 11 | 64.71% |

## 仓库结构

```text
src/guarded_stage_react/   核心动作控制实现
scripts/                   运行示例和结果汇总工具
results/                   已发布的轻量结果摘要
examples/                  小型调试样例
figures/                   可编辑 SVG 图
docs/                      方法和结果说明
tests/                     controller 单元测试
```

## 快速开始

安装：

```bash
pip install -e ".[dev]"
```

运行测试：

```bash
pytest -q
```

在其他 ALFWorld runner 中使用：

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

`safe_action` 是最终交给环境执行的动作；`reason` 记录动作是原样放行，还是被 guard / controller 重定向。

## 复现说明

- 环境：ALFWorld valid-unseen。
- 主实验预算：每个任务最多 25 个可执行动作。
- 主控制器：wrong-object guard + PickTwo stage controller + fallback ranking。
- 仓库只保留轻量结果摘要，不提交多 MB 的完整 trace 日志。
