import pytest
from domain.continuous_story_plan import ContinuousStoryDraft, StoryObjectDraft
from engines.continuous_story_compiler import ContinuousStoryCompiler
from engines.continuous_story_draft_validator import validate_story_draft


@pytest.fixture
def base_timestamps():
    return [
        {"word": "Let", "start_ms": 0, "end_ms": 300},
        {"word": "us", "start_ms": 300, "end_ms": 600},
        {"word": "weigh", "start_ms": 600, "end_ms": 1100},
        {"word": "the", "start_ms": 1100, "end_ms": 1400},
        {"word": "risk", "start_ms": 1400, "end_ms": 2000},
        {"word": "versus", "start_ms": 2000, "end_ms": 2600},
        {"word": "the", "start_ms": 2600, "end_ms": 2900},
        {"word": "massive", "start_ms": 2900, "end_ms": 3500},
        {"word": "mountain", "start_ms": 3500, "end_ms": 4200},
        {"word": "of", "start_ms": 4200, "end_ms": 4500},
        {"word": "debt", "start_ms": 4500, "end_ms": 5200},
        {"word": "in", "start_ms": 5200, "end_ms": 5500},
        {"word": "this", "start_ms": 5500, "end_ms": 5900},
        {"word": "equation", "start_ms": 5900, "end_ms": 6800},
    ]


def test_scale_primitive_validation_and_compilation(base_timestamps):
    draft_dict = {
        "story_id": "scale_test_story",
        "atmosphere": "paper_clean",
        "objects": [
            {
                "id": "leverage_scale",
                "type": "scale",
                "layout": "center",
                "title": "THE DEBT RATIO SCALE",
                "left_title": "Monthly Cash Flow",
                "left_display_value": "₹1.2 Lakh",
                "left_numeric_value": 120000,
                "left_badge": "HEALTHY",
                "right_title": "Total EMI Burden",
                "right_display_value": "₹2.8 Lakh",
                "right_numeric_value": 280000,
                "right_badge": "CRITICAL",
                "tilt_direction": "right",
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "leverage_scale",
                "anchor": "weigh the risk",
            },
            {
                "action": "change_visual_state",
                "target_id": "leverage_scale",
                "state": "danger",
                "badge": "UNBALANCED",
                "anchor": "mountain of debt",
            },
            {
                "action": "exit",
                "target_id": "leverage_scale",
                "anchor": "this equation",
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(draft_dict)
    assert draft.objects[0].type == "scale"
    assert draft.objects[0].right_numeric_value == 280000

    # Validator check
    val_result = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=base_timestamps,
        total_duration_ms=7500,
    )
    assert val_result.valid, f"Validation errors: {[e.message for e in val_result.errors]}"

    # Compiler check
    compiler = ContinuousStoryCompiler()
    fixture = {
        "narration": "Let us weigh the risk versus the massive mountain of debt in this equation.",
        "word_timestamps": base_timestamps,
        "total_duration_ms": 7500,
    }
    plan = compiler.compile(draft, fixture)
    scale_obj = next(o for o in plan["objects"] if o["id"] == "leverage_scale")
    assert scale_obj["type"] == "scale"
    assert "scaleProps" in scale_obj
    assert scale_obj["scaleProps"]["rightTitle"] == "Total EMI Burden"
    assert scale_obj["scaleProps"]["tiltDirection"] == "right"


def test_money_stack_primitive_validation_and_compilation(base_timestamps):
    draft_dict = {
        "story_id": "money_stack_test_story",
        "atmosphere": "paper_clean",
        "objects": [
            {
                "id": "capital_tower",
                "type": "money_stack",
                "layout": "center",
                "title": "NATIONAL WEALTH STACK",
                "unit_label": "₹1,000 Cr",
                "unit_value": 1000,
                "total_display_value": "₹25,000 Crore",
                "total_numeric_value": 25000,
                "stack_mode": "single_tower",
                "show_human_scale": True,
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "capital_tower",
                "anchor": "massive mountain",
            },
            {
                "action": "exit",
                "target_id": "capital_tower",
                "anchor": "this equation",
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(draft_dict)
    assert draft.objects[0].type == "money_stack"
    assert draft.objects[0].total_display_value == "₹25,000 Crore"

    # Validator check
    val_result = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=base_timestamps,
        total_duration_ms=7500,
    )
    assert val_result.valid, f"Validation errors: {[e.message for e in val_result.errors]}"

    # Compiler check
    compiler = ContinuousStoryCompiler()
    fixture = {
        "narration": "Let us weigh the risk versus the massive mountain of debt in this equation.",
        "word_timestamps": base_timestamps,
        "total_duration_ms": 7500,
    }
    plan = compiler.compile(draft, fixture)
    ms_obj = next(o for o in plan["objects"] if o["id"] == "capital_tower")
    assert ms_obj["type"] == "money_stack"
    assert "moneyStackProps" in ms_obj
    assert ms_obj["moneyStackProps"]["totalDisplayValue"] == "₹25,000 Crore"
    assert ms_obj["moneyStackProps"]["showHumanScale"] is True


def test_scale_and_money_stack_field_exclusivity():
    # Card cannot specify scale fields
    with pytest.raises(ValueError, match="Card 'invalid_card' cannot specify scale fields"):
        StoryObjectDraft(
            id="invalid_card",
            type="card",
            title="Invalid",
            left_title="Leaked left title",
        )

    # Character cannot specify money_stack fields
    with pytest.raises(ValueError, match="Character 'invalid_char' cannot specify money_stack fields"):
        StoryObjectDraft(
            id="invalid_char",
            type="character",
            role="Worker",
            character_style="futuristic_stick",
            pose="idle",
            facing="right",
            unit_label="₹1,000 Cr",
        )


def test_schema_and_repair_prompt_include_new_primitives():
    from domain.continuous_story_plan import build_continuous_story_contract_schema
    from engines.continuous_story_engine import format_programmatic_repair_prompt
    from pydantic import ValidationError

    # Verify Gemini constrained decoding schema has scale, money_stack, document, waterfall, capital_flow
    schema = build_continuous_story_contract_schema()
    object_schemas = schema["properties"]["objects"]["items"]["anyOf"]
    types_in_schema = {s["properties"]["type"]["enum"][0] for s in object_schemas}
    assert "scale" in types_in_schema
    assert "money_stack" in types_in_schema
    assert "document" in types_in_schema
    assert "waterfall" in types_in_schema
    assert "capital_flow" in types_in_schema

    # Verify programmatic repair prompt provides guidance for scale and money_stack
    scale_payload = {
        "story_id": "test",
        "objects": [{"id": "s1", "type": "scale", "layout": "center"}],
        "events": [],
    }
    try:
        ContinuousStoryDraft.model_validate(scale_payload)
    except ValidationError as err:
        repair_text = format_programmatic_repair_prompt(scale_payload, validation_error=err)
        assert 'Scale requires: "type": "scale"' in repair_text

    money_payload = {
        "story_id": "test",
        "objects": [{"id": "m1", "type": "money_stack", "layout": "center"}],
        "events": [],
    }
    try:
        ContinuousStoryDraft.model_validate(money_payload)
    except ValidationError as err:
        repair_text = format_programmatic_repair_prompt(money_payload, validation_error=err)
        assert 'MoneyStack requires: "type": "money_stack"' in repair_text

    doc_payload = {
        "story_id": "test",
        "objects": [{"id": "d1", "type": "document", "layout": "center"}],
        "events": [],
    }
    try:
        ContinuousStoryDraft.model_validate(doc_payload)
    except ValidationError as err:
        repair_text = format_programmatic_repair_prompt(doc_payload, validation_error=err)
        assert 'Document requires: "type": "document"' in repair_text

    wf_payload = {
        "story_id": "test",
        "objects": [{"id": "w1", "type": "waterfall", "layout": "center"}],
        "events": [],
    }
    try:
        ContinuousStoryDraft.model_validate(wf_payload)
    except ValidationError as err:
        repair_text = format_programmatic_repair_prompt(wf_payload, validation_error=err)
        assert 'Waterfall requires: "type": "waterfall"' in repair_text

    cf_payload = {
        "story_id": "test",
        "objects": [{"id": "c1", "type": "capital_flow", "layout": "center"}],
        "events": [],
    }
    try:
        ContinuousStoryDraft.model_validate(cf_payload)
    except ValidationError as err:
        repair_text = format_programmatic_repair_prompt(cf_payload, validation_error=err)
        assert 'CapitalFlow requires: "type": "capital_flow"' in repair_text


def test_document_primitive_validation_and_compilation(base_timestamps):
    draft_dict = {
        "story_id": "doc_test_story",
        "atmosphere": "paper_clean",
        "objects": [
            {
                "id": "sebi_circular",
                "type": "document",
                "layout": "center",
                "doc_title": "SECURITIES AND EXCHANGE BOARD OF INDIA",
                "doc_reference": "CIRCULAR NO. SEBI/HO/MRD/2024/114",
                "doc_body": "Cumulative net exit exceeding ₹1,14,000 Crore from domestic equity markets.",
                "highlight_phrase": "exceeding ₹1,14,000 Crore",
                "watermark": "OFFICIAL FILING",
                "stamp_text": "REGULATORY NOTICE",
                "visual_state": "danger",
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "sebi_circular",
                "anchor": "weigh the risk",
            },
            {
                "action": "change_visual_state",
                "target_id": "sebi_circular",
                "state": "danger",
                "badge": "RESTRICTED",
                "anchor": "mountain of debt",
            },
            {
                "action": "exit",
                "target_id": "sebi_circular",
                "anchor": "this equation",
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(draft_dict)
    assert draft.objects[0].type == "document"
    assert draft.objects[0].doc_title == "SECURITIES AND EXCHANGE BOARD OF INDIA"
    assert draft.objects[0].highlight_phrase == "exceeding ₹1,14,000 Crore"

    # Validator check
    val_result = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=base_timestamps,
        total_duration_ms=7500,
    )
    assert val_result.valid, f"Validation errors: {[e.message for e in val_result.errors]}"

    # Compiler check
    compiler = ContinuousStoryCompiler()
    fixture = {
        "narration": "Let us weigh the risk versus the massive mountain of debt in this equation.",
        "word_timestamps": base_timestamps,
        "total_duration_ms": 7500,
    }
    plan = compiler.compile(draft, fixture)
    doc_obj = next(o for o in plan["objects"] if o["id"] == "sebi_circular")
    assert doc_obj["type"] == "document"
    assert "documentProps" in doc_obj
    assert doc_obj["documentProps"]["title"] == "SECURITIES AND EXCHANGE BOARD OF INDIA"
    assert doc_obj["documentProps"]["highlightPhrase"] == "exceeding ₹1,14,000 Crore"
    assert doc_obj["documentProps"]["stampText"] == "REGULATORY NOTICE"


def test_waterfall_primitive_validation_and_compilation(base_timestamps):
    draft_dict = {
        "story_id": "waterfall_test_story",
        "atmosphere": "paper_clean",
        "objects": [
            {
                "id": "profit_drain_funnel",
                "type": "waterfall",
                "layout": "center",
                "title": "WHERE CORPORATE PROFITS EVAPORATE",
                "initial_label": "Gross Revenue",
                "initial_display_value": "₹10,000 Cr",
                "initial_value": 10000,
                "steps": [
                    {
                        "label": "Raw Material Inflation",
                        "display_value": "-₹5,400 Cr",
                        "value": 5400,
                        "step_type": "deduction",
                    },
                    {
                        "label": "Rising Wage & Power Costs",
                        "display_value": "-₹2,200 Cr",
                        "value": 2200,
                        "step_type": "deduction",
                    },
                ],
                "final_label": "Net Surviving Profit",
                "final_display_value": "₹2,400 Cr",
                "final_value": 2400,
                "visual_state": "warning",
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "profit_drain_funnel",
                "anchor": "weigh the risk",
            },
            {
                "action": "transform_number",
                "target_id": "profit_drain_funnel",
                "to_display_value": "₹1,800 Cr",
                "to_numeric_value": 1800,
                "anchor": "mountain of debt",
            },
            {
                "action": "exit",
                "target_id": "profit_drain_funnel",
                "anchor": "this equation",
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(draft_dict)
    assert draft.objects[0].type == "waterfall"
    assert len(draft.objects[0].steps) == 2
    assert draft.objects[0].steps[0].label == "Raw Material Inflation"

    # Validator check
    val_result = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=base_timestamps,
        total_duration_ms=7500,
    )
    assert val_result.valid, f"Validation errors: {[e.message for e in val_result.errors]}"

    # Compiler check
    compiler = ContinuousStoryCompiler()
    fixture = {
        "narration": "Let us weigh the risk versus the massive mountain of debt in this equation.",
        "word_timestamps": base_timestamps,
        "total_duration_ms": 7500,
    }
    plan = compiler.compile(draft, fixture)
    wf_obj = next(o for o in plan["objects"] if o["id"] == "profit_drain_funnel")
    assert wf_obj["type"] == "waterfall"
    assert "waterfallProps" in wf_obj
    assert wf_obj["waterfallProps"]["initialLabel"] == "Gross Revenue"
    assert len(wf_obj["waterfallProps"]["steps"]) == 2
    assert wf_obj["waterfallProps"]["finalDisplayValue"] == "₹2,400 Cr"


def test_capital_flow_primitive_validation_and_compilation(base_timestamps):
    draft_dict = {
        "story_id": "capital_flow_test_story",
        "atmosphere": "paper_clean",
        "objects": [
            {
                "id": "fii_flight_vector",
                "type": "capital_flow",
                "layout": "center",
                "title": "GLOBAL CAPITAL FLIGHT",
                "source_label": "MUMBAI // BSE",
                "source_sublabel": "Overvalued Indian Equities",
                "target_label": "NEW YORK // WALL ST",
                "target_sublabel": "Risk-Free US Treasuries (4.5%)",
                "flow_label": "Cumulative FII Drain",
                "flow_display_value": "₹1,14,000 Crore",
                "flow_direction": "left_to_right",
                "visual_state": "danger",
            }
        ],
        "events": [
            {
                "action": "enter",
                "target_id": "fii_flight_vector",
                "anchor": "weigh the risk",
            },
            {
                "action": "change_visual_state",
                "target_id": "fii_flight_vector",
                "state": "danger",
                "badge": "RECORD DRAIN",
                "anchor": "mountain of debt",
            },
            {
                "action": "exit",
                "target_id": "fii_flight_vector",
                "anchor": "this equation",
            },
        ],
    }

    draft = ContinuousStoryDraft.model_validate(draft_dict)
    assert draft.objects[0].type == "capital_flow"
    assert draft.objects[0].source_label == "MUMBAI // BSE"
    assert draft.objects[0].flow_display_value == "₹1,14,000 Crore"

    # Validator check
    val_result = validate_story_draft(
        draft=draft,
        approved_facts={},
        word_timestamps=base_timestamps,
        total_duration_ms=7500,
    )
    assert val_result.valid, f"Validation errors: {[e.message for e in val_result.errors]}"

    # Compiler check
    compiler = ContinuousStoryCompiler()
    fixture = {
        "narration": "Let us weigh the risk versus the massive mountain of debt in this equation.",
        "word_timestamps": base_timestamps,
        "total_duration_ms": 7500,
    }
    plan = compiler.compile(draft, fixture)
    cf_obj = next(o for o in plan["objects"] if o["id"] == "fii_flight_vector")
    assert cf_obj["type"] == "capital_flow"
    assert "capitalFlowProps" in cf_obj
    assert cf_obj["capitalFlowProps"]["sourceLabel"] == "MUMBAI // BSE"
    assert cf_obj["capitalFlowProps"]["targetLabel"] == "NEW YORK // WALL ST"
    assert cf_obj["capitalFlowProps"]["flowDisplayValue"] == "₹1,14,000 Crore"


def test_field_exclusivity_for_all_primitives():
    # Card cannot specify document fields
    with pytest.raises(ValueError, match="Card 'invalid_card' cannot specify document fields"):
        StoryObjectDraft(
            id="invalid_card",
            type="card",
            title="Invalid",
            doc_body="Leak",
        )

    # Document cannot specify waterfall steps
    with pytest.raises(ValueError, match="Document 'invalid_doc' cannot specify waterfall fields"):
        StoryObjectDraft(
            id="invalid_doc",
            type="document",
            doc_title="Valid Title",
            doc_body="Leak",
            steps=[{"label": "Step 1", "display_value": "-₹100", "value": 100, "step_type": "deduction"}],
        )

    # Waterfall cannot specify capital_flow fields
    with pytest.raises(ValueError, match="Waterfall 'invalid_wf' cannot specify capital_flow fields"):
        StoryObjectDraft(
            id="invalid_wf",
            type="waterfall",
            initial_label="Gross",
            initial_display_value="₹100",
            steps=[{"label": "Step 1", "display_value": "-₹100", "value": 100, "step_type": "deduction"}],
            final_label="Net",
            final_display_value="₹10",
            source_label="Mumbai",
        )

    # Capital flow cannot specify waterfall fields
    with pytest.raises(ValueError, match="cannot specify waterfall fields"):
        StoryObjectDraft(
            id="invalid_cf",
            type="capital_flow",
            source_label="A",
            target_label="B",
            flow_display_value="₹100",
            initial_label="Gross",
        )


def test_direct_authoring_contract_validation_for_all_three_primitives():
    from engines.continuous_story_engine import _validate_direct_authoring_contract, ContinuousStoryEngineError

    # Document missing doc_body
    d1 = ContinuousStoryDraft.model_construct(
        story_id="test",
        objects=[StoryObjectDraft.model_construct(id="d1", type="document", doc_title="Title")],
        events=[],
    )
    with pytest.raises(ContinuousStoryEngineError, match="Document 'd1' requires non-empty 'doc_body' text excerpt"):
        _validate_direct_authoring_contract(d1)

    # Waterfall missing steps
    w1 = ContinuousStoryDraft.model_construct(
        story_id="test",
        objects=[
            StoryObjectDraft.model_construct(
                id="w1",
                type="waterfall",
                initial_label="Gross",
                initial_display_value="₹100",
                final_label="Net",
                final_display_value="₹10",
            )
        ],
        events=[],
    )
    with pytest.raises(ContinuousStoryEngineError, match="Waterfall 'w1' requires at least one step in 'steps'"):
        _validate_direct_authoring_contract(w1)

    # CapitalFlow missing flow_display_value
    c1 = ContinuousStoryDraft.model_construct(
        story_id="test",
        objects=[
            StoryObjectDraft.model_construct(
                id="c1",
                type="capital_flow",
                source_label="Origin",
                target_label="Destination",
            )
        ],
        events=[],
    )
    with pytest.raises(ContinuousStoryEngineError, match="CapitalFlow 'c1' requires 'flow_display_value'"):
        _validate_direct_authoring_contract(c1)


