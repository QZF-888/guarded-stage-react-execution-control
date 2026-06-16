# 方法说明

Guarded-Stage ReAct 在 ReAct agent 外面增加一个确定性的动作控制层。它不替代 LLM 规划，而是在动作真正交给环境执行之前，检查这个动作是否符合当前任务进度。

## 组成部分

1. **目标解析器**：将 ALFWorld 常见任务模板解析为结构化 schema：目标物体、目标位置、所需操作、是否为 PickTwo 任务、是否为 desklamp 检查任务。

2. **进度状态**：记录 LLM 在长历史中容易遗忘的信息：目标是否已经放置、heat/cool/clean 是否完成、哪些错误物体已经被拦截、目标曾经在哪些位置出现过。

3. **Wrong-object guard**：阻止拿取或移动与任务目标无关的物体。如果 agent 已经拿错物体，controller 会优先把动作重定向为安全放下/放回动作。

4. **PickTwo stage controller**：强制双目标任务按照稳定阶段推进：寻找并拿第一个目标、去目标位置、必要时打开容器、放置第一个目标、再寻找第二个独立目标。

5. **Fallback ranking**：如果 LLM 提出的动作不安全或不在 admissible actions 中，controller 会从当前可执行动作里选一个更符合阶段的 fallback 动作。

## 设计原则

这个 controller 刻意保持小而透明。LLM 仍然是主要规划器；controller 只负责那些容易明确检查、容易审计的执行期一致性约束。
