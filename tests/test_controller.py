from guarded_stage_react import GuardedStageController


def test_blocks_wrong_take():
    controller = GuardedStageController("Your task is to: put a mug in cabinet.")
    action, reason = controller.control(
        proposed_action="take apple 1 from countertop 1",
        admissible_actions=[
            "take apple 1 from countertop 1",
            "take mug 1 from countertop 1",
        ],
        inventory=[],
    )
    assert action == "take mug 1 from countertop 1"
    assert reason == "guard_block_take_wrong_item:apple 1"


def test_drops_wrong_inventory_item_first():
    controller = GuardedStageController("Your task is to: put a mug in cabinet.")
    action, reason = controller.control(
        proposed_action="go to cabinet 1",
        admissible_actions=[
            "put apple 1 in countertop 1",
            "go to cabinet 1",
        ],
        inventory=["apple 1"],
    )
    assert action == "put apple 1 in countertop 1"
    assert reason == "guard_drop_wrong_item:apple 1"


def test_picktwo_redirects_holding_target_to_destination():
    controller = GuardedStageController("Your task is to: find two cd and put them in safe.")
    action, reason = controller.control(
        proposed_action="go to desk 1",
        admissible_actions=[
            "go to desk 1",
            "go to safe 1",
        ],
        inventory=["cd 1"],
    )
    assert action == "go to safe 1"
    assert reason == "controller_go_to_destination"


def test_picktwo_blocks_retake_from_destination_after_progress():
    controller = GuardedStageController("Your task is to: find two cd and put them in safe.")
    controller.state.placed_count = 1
    action, reason = controller.control(
        proposed_action="take cd 1 from safe 1",
        admissible_actions=[
            "take cd 1 from safe 1",
            "go to desk 1",
        ],
        inventory=[],
    )
    assert action == "go to desk 1"
    assert reason == "guard_block_retake_target_from_destination"
