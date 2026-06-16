# Method Notes

Guarded-Stage ReAct adds a deterministic action-control layer to a ReAct agent. It does not replace the LLM. Instead, it checks the LLM's proposed action against task progress before the action is sent to the environment.

## Components

1. **Goal parser** parses common ALFWorld task templates into a compact schema: target object, destination, required operation, whether the task is PickTwo, and whether it is a desklamp inspection task.

2. **Progress state** tracks facts that the LLM often fails to preserve over long histories: whether the target has been placed, whether an operation is complete, which wrong items were already blocked, and where the target was last seen.

3. **Wrong-object guard** blocks actions that take or move objects unrelated to the task target. If the agent is already holding a wrong object, the controller redirects to a safe drop/place-back action when available.

4. **PickTwo stage controller** forces two-object tasks to proceed through a stable stage sequence: find/take target, move to destination, open if needed, place target, then search for a second separate target.

5. **Fallback ranking** chooses a stage-aware fallback from the current admissible action list if the proposed action is unsafe or not admissible.

## Design Principle

The controller is intentionally small and transparent. The LLM remains the main planner, while the controller handles execution-time consistency checks that are easy to specify and audit.
