"""Execution-time action controller for ALFWorld-style ReAct agents."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable

OBJECT_RE = r"[a-zA-Z][a-zA-Z0-9_ -]*?"


@dataclass(slots=True)
class GoalInfo:
    """Structured information parsed from an ALFWorld task goal."""

    raw_goal: str
    target_obj: str = ""
    target_dest: str = ""
    operation: str = ""
    is_pick_two: bool = False
    is_desklamp: bool = False

    @property
    def task_type(self) -> str:
        if self.is_pick_two:
            return "pick_two_obj_and_place"
        if self.is_desklamp:
            return "look_at_obj_in_light"
        if self.operation:
            return f"pick_{self.operation}_then_place"
        return "pick_and_place_simple"


@dataclass(slots=True)
class StageState:
    """Execution progress tracked outside the LLM context."""

    goal: GoalInfo
    operation_done: bool = False
    placed_count: int = 0
    target_seen_locations: set[str] = field(default_factory=set)
    placed_target_ids: set[str] = field(default_factory=set)
    last_target_source: str = ""
    banned_items: set[str] = field(default_factory=set)

    def to_dict(self) -> dict:
        return {
            "goal": {
                "raw_goal": self.goal.raw_goal,
                "target_obj": self.goal.target_obj,
                "target_dest": self.goal.target_dest,
                "operation": self.goal.operation,
                "is_pick_two": self.goal.is_pick_two,
                "is_desklamp": self.goal.is_desklamp,
                "task_type": self.goal.task_type,
            },
            "operation_done": self.operation_done,
            "placed_count": self.placed_count,
            "target_seen_locations": sorted(self.target_seen_locations),
            "placed_target_ids": sorted(self.placed_target_ids),
            "last_target_source": self.last_target_source,
            "banned_items": sorted(self.banned_items),
        }


def normalize_goal(goal: str) -> str:
    goal = goal.lower().strip()
    goal = re.sub(r"^your task is to:\s*", "", goal)
    goal = goal.replace(".", "")
    return re.sub(r"\s+", " ", goal)


def clean_object_name(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\b(?:the|a|an|some)\b", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .,")


def extract_destination_for_put(goal: str) -> str:
    patterns = [
        r"\bput (?:it|them|some [a-z0-9_ -]+|two [a-z0-9_ -]+|a [a-z0-9_ -]+|an [a-z0-9_ -]+) (?:in|on) ([a-z0-9_ -]+)",
        r"\bplace (?:it|them|some [a-z0-9_ -]+|two [a-z0-9_ -]+|a [a-z0-9_ -]+|an [a-z0-9_ -]+) (?:in|on) ([a-z0-9_ -]+)",
        r"\bfind two [a-z0-9_ -]+ and put them (?:in|on) ([a-z0-9_ -]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, goal)
        if match:
            return match.group(1).strip()
    return ""


def parse_goal_info(goal_text: str) -> GoalInfo:
    """Parse common ALFWorld goal templates into a compact schema."""

    goal = normalize_goal(goal_text)
    info = GoalInfo(raw_goal=goal_text)
    info.is_pick_two = bool(re.search(r"\btwo\b", goal))
    info.is_desklamp = "desklamp" in goal or "desk lamp" in goal

    for operation in ["heat", "cool", "clean"]:
        if re.search(rf"\b{operation}\b", goal):
            info.operation = operation
            break

    patterns = [
        r"\bfind two (" + OBJECT_RE + r") and put",
        r"\bput two (" + OBJECT_RE + r") (?:in|on)",
        r"\b(?:heat|cool|clean) (?:some |a |an )?(" + OBJECT_RE + r") and put",
        r"\bput (?:a |an |some )?(" + OBJECT_RE + r") (?:in|on)",
        r"\blook at (?:a |an |some )?(" + OBJECT_RE + r") under",
    ]
    for pattern in patterns:
        match = re.search(pattern, goal)
        if match:
            info.target_obj = clean_object_name(match.group(1))
            break

    info.target_dest = "desklamp" if info.is_desklamp else extract_destination_for_put(goal)
    info.target_dest = clean_object_name(info.target_dest)
    return info


def extract_item_from_action(action: str) -> str:
    """Extract the object phrase from an ALFWorld action string."""

    action_l = action.lower().strip()
    patterns = [
        r"^take (.+?) from ",
        r"^put (.+?) (?:in|on) ",
        r"^move (.+?) to ",
        r"^(?:heat|cool|clean) (.+?) with ",
        r"^examine (.+?) with ",
    ]
    for pattern in patterns:
        match = re.search(pattern, action_l)
        if match:
            return match.group(1).strip()
    return ""


def holding_target(inventory: Iterable[str], target_obj: str) -> bool:
    target = target_obj.lower().strip()
    return bool(target) and any(target in item.lower() for item in inventory)


def wrong_inventory_items(inventory: Iterable[str], target_obj: str) -> list[str]:
    target = target_obj.lower().strip()
    if not target:
        return []
    return [item for item in inventory if target not in item.lower()]


def is_take_from_destination(action: str, target: str, destination: str) -> bool:
    action_l = action.lower()
    return (
        action_l.startswith("take ")
        and bool(target)
        and bool(destination)
        and target in action_l
        and f"from {destination}" in action_l
    )


def find_drop_action(admissible_actions: Iterable[str], wrong_item: str, destination: str = "") -> str | None:
    wrong = wrong_item.lower()
    destination = destination.lower()
    for action in admissible_actions:
        action_l = action.lower()
        if wrong not in action_l:
            continue
        if action_l.startswith("put ") or action_l.startswith("move "):
            if not destination or destination not in action_l:
                return action
    return None


def find_open_destination(admissible_actions: Iterable[str], destination: str) -> str | None:
    destination = destination.lower()
    for action in admissible_actions:
        action_l = action.lower()
        if action_l.startswith("open ") and destination and destination in action_l:
            return action
    return None


def find_go_destination(admissible_actions: Iterable[str], destination: str, last_action: str | None = None) -> str | None:
    destination = destination.lower()
    for action in admissible_actions:
        action_l = action.lower()
        if action == last_action:
            continue
        if action_l.startswith("go to ") and destination and destination in action_l:
            return action
    return None


def find_put_or_move_target_to_destination(admissible_actions: Iterable[str], target: str, destination: str) -> str | None:
    target = target.lower()
    destination = destination.lower()
    for action in admissible_actions:
        action_l = action.lower()
        if (action_l.startswith("put ") or action_l.startswith("move ")) and target in action_l and destination in action_l:
            return action
    return None


def find_take_target(
    admissible_actions: Iterable[str],
    target: str,
    destination: str,
    placed_count: int,
    banned_items: set[str],
    last_action: str | None = None,
) -> str | None:
    target = target.lower()
    destination = destination.lower()
    for action in admissible_actions:
        action_l = action.lower()
        if action == last_action or not action_l.startswith("take "):
            continue
        item = extract_item_from_action(action_l)
        if item in banned_items:
            continue
        if target and target not in item:
            continue
        if placed_count >= 1 and destination and f"from {destination}" in action_l:
            continue
        return action
    return None


class GuardedStageController:
    """Stateful execution-time action controller."""

    def __init__(self, goal_text: str):
        self.state = StageState(goal=parse_goal_info(goal_text))

    @property
    def goal(self) -> GoalInfo:
        return self.state.goal

    def update(self, action: str, observation: str) -> None:
        """Update progress state after an environment step."""

        action_l = action.lower()
        obs_l = observation.lower()
        target = self.goal.target_obj

        if target and target in obs_l:
            if action_l.startswith("go to "):
                self.state.target_seen_locations.add(action_l.removeprefix("go to ").strip())
            elif action_l.startswith("open "):
                self.state.target_seen_locations.add(action_l.removeprefix("open ").strip())

        if action_l.startswith("take ") and target and target in action_l:
            if " from " in action_l:
                self.state.last_target_source = action_l.split(" from ", 1)[-1].strip()

        if self.goal.operation and self.goal.operation in action_l and target and target in action_l:
            self.state.operation_done = True

        if self.goal.is_pick_two and (action_l.startswith("put ") or action_l.startswith("move ")):
            if target and target in action_l:
                item = extract_item_from_action(action_l)
                if item:
                    self.state.placed_target_ids.add(item)
                    self.state.placed_count = max(self.state.placed_count, len(self.state.placed_target_ids))

    def control(
        self,
        proposed_action: str | None,
        admissible_actions: list[str],
        inventory: list[str],
        observation: str = "",
        last_action: str | None = None,
    ) -> tuple[str | None, str]:
        """Return an executable action and a reason string."""

        if not proposed_action:
            return self.fallback(admissible_actions, inventory, last_action), "fallback_none_action"

        guarded, reason = self.wrong_object_guard(proposed_action, admissible_actions, inventory)
        if guarded is None:
            return self.fallback(admissible_actions, inventory, last_action), reason
        if guarded != proposed_action:
            return guarded, reason

        if self.goal.is_pick_two:
            controlled, controller_reason = self.picktwo_stage_controller(
                proposed_action, admissible_actions, inventory, last_action
            )
            if controlled != proposed_action:
                return controlled, controller_reason

        if proposed_action in admissible_actions:
            return proposed_action, "allow"
        return self.fallback(admissible_actions, inventory, last_action), "fallback_not_admissible"

    def wrong_object_guard(
        self,
        action: str,
        admissible_actions: list[str],
        inventory: list[str],
    ) -> tuple[str | None, str]:
        """Prevent taking or moving objects unrelated to the task target."""

        target = self.goal.target_obj
        destination = self.goal.target_dest
        wrong_items = wrong_inventory_items(inventory, target)
        if wrong_items:
            wrong = wrong_items[0]
            drop = find_drop_action(admissible_actions, wrong, destination)
            self.state.banned_items.add(wrong.lower())
            if drop:
                return drop, f"guard_drop_wrong_item:{wrong}"
            return None, f"guard_holding_wrong_no_drop:{wrong}"

        action_l = action.lower()
        item = extract_item_from_action(action_l)
        if action_l.startswith("take "):
            if item in self.state.banned_items:
                return None, f"guard_block_banned_item:{item}"
            if target and target not in item:
                self.state.banned_items.add(item)
                return None, f"guard_block_take_wrong_item:{item}"
            if self.goal.is_pick_two and self.state.placed_count >= 1:
                if is_take_from_destination(action_l, target, destination):
                    return None, "guard_block_retake_target_from_destination"

        if action_l.startswith("put ") or action_l.startswith("move "):
            if item and target and target not in item:
                self.state.banned_items.add(item)
                return None, f"guard_block_move_wrong_item:{item}"

        return action, "guard_pass"

    def picktwo_stage_controller(
        self,
        action: str,
        admissible_actions: list[str],
        inventory: list[str],
        last_action: str | None = None,
    ) -> tuple[str | None, str]:
        """Force PickTwo tasks to progress through acquire -> destination -> place."""

        target = self.goal.target_obj
        destination = self.goal.target_dest
        has_target = holding_target(inventory, target)

        wrong_items = wrong_inventory_items(inventory, target)
        if wrong_items:
            wrong = wrong_items[0]
            drop = find_drop_action(admissible_actions, wrong, destination)
            self.state.banned_items.add(wrong.lower())
            if drop:
                return drop, "controller_drop_wrong_item"

        if has_target:
            put_or_move = find_put_or_move_target_to_destination(admissible_actions, target, destination)
            if put_or_move:
                return put_or_move, "controller_put_or_move_target_to_dest"
            open_dest = find_open_destination(admissible_actions, destination)
            if open_dest:
                return open_dest, "controller_open_destination"
            go_dest = find_go_destination(admissible_actions, destination, last_action)
            if go_dest:
                return go_dest, "controller_go_to_destination"
            return action, "controller_holding_target_keep_safe_action"

        take_target = find_take_target(
            admissible_actions,
            target,
            destination,
            self.state.placed_count,
            self.state.banned_items,
            last_action,
        )
        if take_target and action != take_target:
            return take_target, "controller_take_visible_target"

        if self.state.placed_count >= 1 and destination:
            action_l = action.lower()
            if destination in action_l and (action_l.startswith("go to ") or action_l.startswith("open ")):
                for candidate in admissible_actions:
                    candidate_l = candidate.lower()
                    if candidate == last_action:
                        continue
                    if candidate_l.startswith("go to ") and destination not in candidate_l:
                        return candidate, "controller_avoid_destination_search"

        return action, "controller_pass"

    def fallback(self, admissible_actions: list[str], inventory: list[str], last_action: str | None = None) -> str | None:
        """Choose a stage-aware fallback action from admissible actions."""

        if not admissible_actions:
            return None

        target = self.goal.target_obj
        destination = self.goal.target_dest

        wrong_items = wrong_inventory_items(inventory, target)
        if wrong_items:
            drop = find_drop_action(admissible_actions, wrong_items[0], destination)
            if drop:
                return drop

        if holding_target(inventory, target):
            return (
                find_put_or_move_target_to_destination(admissible_actions, target, destination)
                or find_open_destination(admissible_actions, destination)
                or find_go_destination(admissible_actions, destination, last_action)
                or admissible_actions[0]
            )

        take_target = find_take_target(
            admissible_actions,
            target,
            destination,
            self.state.placed_count,
            self.state.banned_items,
            last_action,
        )
        if take_target:
            return take_target

        for action in admissible_actions:
            action_l = action.lower()
            if action == last_action:
                continue
            if self.goal.is_pick_two and self.state.placed_count >= 1:
                if is_take_from_destination(action_l, target, destination):
                    continue
            item = extract_item_from_action(action_l)
            if action_l.startswith("take ") and item in self.state.banned_items:
                continue
            return action
        return admissible_actions[0]
