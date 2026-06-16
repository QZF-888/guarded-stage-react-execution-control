#!/usr/bin/env python3
"""Minimal integration example for Guarded-Stage ReAct."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from guarded_stage_react import GuardedStageController


class Policy(Protocol):
    def propose(self, observation: str, admissible_actions: list[str], history: list[str]) -> str:
        """Return one action proposed by a ReAct language model."""


class TextWorldLikeEnv(Protocol):
    def reset(self) -> tuple[str, dict]:
        """Return initial observation and info dict with admissible actions."""

    def step(self, action: str) -> tuple[str, float, bool, dict]:
        """Execute one text action."""


@dataclass
class EpisodeResult:
    success: bool
    score: float
    steps: int
    guard_events: int
    trace: list[dict]


def extract_inventory(info: dict) -> list[str]:
    inv = info.get("inventory", [])
    if isinstance(inv, list):
        return [str(x) for x in inv]
    if isinstance(inv, str):
        return [part.strip() for part in inv.split(",") if part.strip()]
    return []


def extract_goal(observation: str, info: dict) -> str:
    if info.get("goal"):
        return str(info["goal"])
    for line in observation.splitlines():
        if "your task is to:" in line.lower():
            return line.strip()
    raise ValueError("Cannot infer ALFWorld goal from observation/info.")


def run_episode(env: TextWorldLikeEnv, policy: Policy, max_steps: int = 25) -> EpisodeResult:
    observation, info = env.reset()
    goal = extract_goal(observation, info)
    controller = GuardedStageController(goal)
    history: list[str] = []
    trace: list[dict] = []
    last_action: str | None = None
    guard_events = 0
    score = 0.0
    done = False

    for step_idx in range(max_steps):
        admissible = list(info.get("admissible_commands", info.get("admissible_actions", [])))
        inventory = extract_inventory(info)
        proposed = policy.propose(observation, admissible, history)
        action, reason = controller.control(
            proposed_action=proposed,
            admissible_actions=admissible,
            inventory=inventory,
            observation=observation,
            last_action=last_action,
        )
        if action is None:
            break
        if reason not in {"allow", "guard_pass", "controller_pass"}:
            guard_events += 1

        next_observation, score, done, info = env.step(action)
        controller.update(action, next_observation)
        trace.append({
            "step": step_idx + 1,
            "observation": observation,
            "proposed_action": proposed,
            "executed_action": action,
            "reason": reason,
            "score": score,
            "done": done,
            "controller_state": controller.state.to_dict(),
        })
        history.append(f"Thought/action proposal: {proposed}\nExecuted: {action}\nReason: {reason}")
        observation = next_observation
        last_action = action
        if done:
            break

    return EpisodeResult(
        success=bool(done and score > 0),
        score=float(score),
        steps=len(trace),
        guard_events=guard_events,
        trace=trace,
    )


if __name__ == "__main__":
    print("Connect this template to an ALFWorld env and a ReAct policy, then call run_episode(env, policy).")
