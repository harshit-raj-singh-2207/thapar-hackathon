import pytest

from app.ai.templates import (
    AAC_INTENT_TEMPLATES,
    detect_template_intent,
    get_template_response,
    match_template,
    normalize_input,
)


@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("I need help", "need_help"),
        ("I need space", "need_space"),
        ("I am hungry", "hungry"),
        ("I want water", "want_water"),
        ("I am scared", "scared"),
        ("I feel unsafe", "unsafe"),
        ("I feel safe", "safe"),
        ("I cannot speak right now", "cannot_speak"),
        ("Please call my caregiver", "call_caregiver"),
        ("I need a break", "need_break"),
        ("I am uncomfortable", "uncomfortable"),
        ("I am tired", "tired"),
        ("I need the washroom", "washroom"),
    ],
)
def test_all_required_template_intents(message, expected_intent):
    response = get_template_response(message)
    assert response is not None
    assert response["intent"] == expected_intent
    assert response["matched"] is True
    assert response["response"] == response["text"]
    assert response["source"] == "template"
    assert response["text"]
    assert response["tokens"]


@pytest.mark.parametrize("variation", ["help me", "need help", "I need help", "PLEASE HELP ME!"])
def test_help_variations_resolve_to_same_intent(variation):
    assert detect_template_intent(variation) == "need_help"


@pytest.mark.parametrize("variation", ["water", "want water", "I need water"])
def test_water_variations_resolve_to_same_intent(variation):
    assert detect_template_intent(variation) == "want_water"


def test_normalization_handles_case_punctuation_apostrophes_and_spaces():
    assert normalize_input("  I CAN'T   speak, right now! ") == "i cant speak right now"
    assert match_template("  I CAN'T   speak, right now! ") == "cannot_speak"


def test_unknown_or_empty_input_has_no_template():
    assert match_template("") is None
    assert match_template("tell me about quantum physics") is None
    assert get_template_response("unknown request") == {"matched": False}


def test_template_response_does_not_mutate_shared_definition():
    response = get_template_response("need water")
    response["tokens"].append("CHANGED")
    assert "CHANGED" not in AAC_INTENT_TEMPLATES["want_water"]["tokens"]


def test_safety_related_templates_are_marked_deterministically():
    assert get_template_response("I feel unsafe")["safety"] is True
    assert get_template_response("call my caregiver")["safety"] is True


def test_non_safety_template_is_explicitly_marked_false():
    assert get_template_response("need help")["safety"] is False
