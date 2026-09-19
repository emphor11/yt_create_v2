from domain.script_visual_strategy import ScriptVisualStrategy, VideoIdea
from domain.validators.script_visual_strategy_validator import ScriptVisualStrategyValidator


def test_validator_accepts_valid_strategy() -> None:
    strategy = ScriptVisualStrategy(
        thesis="Renting is superior.",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="The Cost Equation",
                focus_concept="Opportunity Cost",
                core_teaching_point="Show unrecoverable costs comparison",
                narration="Renting has unrecoverable costs but buying has higher ones.",
            ),
            VideoIdea(
                idea_id="idea_02",
                title="Liquidity Factor",
                focus_concept="Liquidity",
                core_teaching_point="Show liquidity advantage",
                narration="Renting allows you to invest down payment capital into index funds.",
            ),
        ],
    )
    result = ScriptVisualStrategyValidator().validate(strategy)
    assert result.status == "valid"
    assert not result.errors


def test_validator_rejects_empty_thesis() -> None:
    strategy = ScriptVisualStrategy(
        thesis="   ",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="The Cost Equation",
                focus_concept="Opportunity Cost",
                core_teaching_point="Show unrecoverable costs comparison",
                narration="Renting has unrecoverable costs.",
            )
        ],
    )
    result = ScriptVisualStrategyValidator().validate(strategy)
    assert result.status == "blocked"
    assert "core thesis is required" in result.errors[0]


def test_validator_rejects_empty_ideas() -> None:
    strategy = ScriptVisualStrategy(
        thesis="Valid thesis",
        ideas=[],
    )
    result = ScriptVisualStrategyValidator().validate(strategy)
    assert result.status == "blocked"
    assert "must contain at least 1 video idea" in result.errors[0]


def test_validator_rejects_missing_idea_fields() -> None:
    # 1. Missing idea_id
    strategy_no_id = ScriptVisualStrategy(
        thesis="Valid thesis",
        ideas=[
            VideoIdea(
                idea_id="",
                title="Title",
                focus_concept="Concept",
                core_teaching_point="Point",
                narration="Narration",
            )
        ],
    )
    res_no_id = ScriptVisualStrategyValidator().validate(strategy_no_id)
    assert res_no_id.status == "blocked"
    assert "requires an idea_id" in res_no_id.errors[0]

    # 2. Missing title
    strategy_no_title = ScriptVisualStrategy(
        thesis="Valid thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="",
                focus_concept="Concept",
                core_teaching_point="Point",
                narration="Narration",
            )
        ],
    )
    res_no_title = ScriptVisualStrategyValidator().validate(strategy_no_title)
    assert res_no_title.status == "blocked"
    assert "requires a title" in res_no_title.errors[0]

    # 3. Missing focus_concept
    strategy_no_concept = ScriptVisualStrategy(
        thesis="Valid thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Title",
                focus_concept="",
                core_teaching_point="Point",
                narration="Narration",
            )
        ],
    )
    res_no_concept = ScriptVisualStrategyValidator().validate(strategy_no_concept)
    assert res_no_concept.status == "blocked"
    assert "requires a focus concept" in res_no_concept.errors[0]

    # 4. Missing core_teaching_point
    strategy_no_point = ScriptVisualStrategy(
        thesis="Valid thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Title",
                focus_concept="Concept",
                core_teaching_point="",
                narration="Narration",
            )
        ],
    )
    res_no_point = ScriptVisualStrategyValidator().validate(strategy_no_point)
    assert res_no_point.status == "blocked"
    assert "requires a core teaching point" in res_no_point.errors[0]

    # 5. Missing narration
    strategy_no_narration = ScriptVisualStrategy(
        thesis="Valid thesis",
        ideas=[
            VideoIdea(
                idea_id="idea_01",
                title="Title",
                focus_concept="Concept",
                core_teaching_point="Point",
                narration="",
            )
        ],
    )
    res_no_narration = ScriptVisualStrategyValidator().validate(strategy_no_narration)
    assert res_no_narration.status == "blocked"
    assert "requires narration text" in res_no_narration.errors[0]
