import re
from typing import Dict, Iterable, Optional


AAC_INTENT_TEMPLATES: Dict[str, Dict[str, object]] = {
    "need_help": {"text": "I need help, please.", "tokens": ["I", "NEED", "HELP"]},
    "need_space": {"text": "I need some space, please.", "tokens": ["I", "NEED", "SPACE"]},
    "hungry": {"text": "I am hungry and would like some food, please.", "tokens": ["I", "WANT", "FOOD"]},
    "want_water": {"text": "I would like some water, please.", "tokens": ["I", "WANT", "WATER"]},
    "scared": {"text": "I am scared. Please stay with me.", "tokens": ["I", "FEEL", "SCARED"]},
    "unsafe": {"text": "I feel unsafe. Please call my caregiver now.", "tokens": ["I", "FEEL", "UNSAFE"], "safety": True},
    "safe": {"text": "I feel safe.", "tokens": ["I", "FEEL", "SAFE"]},
    "cannot_speak": {"text": "I cannot speak right now. Please give me time.", "tokens": ["I", "CANNOT", "SPEAK"]},
    "call_caregiver": {"text": "Please call my caregiver.", "tokens": ["PLEASE", "CALL", "CAREGIVER"], "safety": True},
    "need_break": {"text": "I need a quiet break, please.", "tokens": ["I", "NEED", "BREAK"]},
    "uncomfortable": {"text": "I am uncomfortable and need help.", "tokens": ["I", "FEEL", "UNCOMFORTABLE"]},
    "tired": {"text": "I am tired and need to rest.", "tokens": ["I", "FEEL", "TIRED"]},
    "washroom": {"text": "I need to use the washroom, please.", "tokens": ["I", "NEED", "WASHROOM"]},
}

INTENT_VARIATIONS = {
    "need_help": {"i need help", "need help", "help me", "please help me", "help"},
    "need_space": {"i need space", "need space", "give me space", "space please"},
    "hungry": {"i am hungry", "im hungry", "hungry", "need food", "want food"},
    "want_water": {"i want water", "want water", "i need water", "need water", "water", "water please", "thirsty", "i am thirsty"},
    "scared": {"i am scared", "im scared", "scared", "i feel scared", "afraid"},
    "unsafe": {"i feel unsafe", "feel unsafe", "unsafe", "not safe", "i am not safe"},
    "safe": {"i feel safe", "feel safe", "i am safe", "safe now"},
    "cannot_speak": {"i cannot speak right now", "i cant speak right now", "cannot speak", "cant speak", "nonverbal right now", "no words"},
    "call_caregiver": {"please call my caregiver", "call my caregiver", "get my caregiver", "need caregiver"},
    "need_break": {"i need a break", "need a break", "need break", "break please", "quiet break"},
    "uncomfortable": {"i am uncomfortable", "im uncomfortable", "feel uncomfortable", "uncomfortable"},
    "tired": {"i am tired", "im tired", "tired", "need rest", "want to rest"},
    "washroom": {"i need the washroom", "need washroom", "need toilet", "need bathroom", "use the restroom"},
}


def normalize_input(value: str) -> str:
    """Normalize user-entered AAC text without changing its meaning."""
    if not value:
        return ""
    value = str(value).lower().replace("'", "")
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def match_template(value: str) -> Optional[str]:
    """Return the stable intent name for a normalized input, if supported."""
    normalized = normalize_input(value)
    if not normalized:
        return None
    for intent, variations in INTENT_VARIATIONS.items():
        if normalized in variations:
            return intent
    return None


def detect_template_intent(value: str) -> Optional[str]:
    """Descriptive alias for callers that only need intent detection."""
    return match_template(value)


def get_template_response(value: str) -> Dict[str, object]:
    """Return an independent offline AAC response for the matching intent."""
    intent = detect_template_intent(value)
    if intent is None:
        return {"matched": False}
    template = AAC_INTENT_TEMPLATES[intent]
    # Copy nested token lists so callers cannot mutate the shared definitions.
    result = {
        key: list(item) if isinstance(item, list) else item
        for key, item in template.items()
    }
    result.update(
        {
            "matched": True,
            "intent": intent,
            "response": result["text"],
            "source": "template",
            "safety": bool(result.get("safety", False)),
        }
    )
    return result


# Backward-compatible names used by the existing Smart AI Gateway.
normalize_message = normalize_input


def find_aac_template(message: str) -> Optional[Dict[str, object]]:
    result = get_template_response(message)
    return result if result["matched"] else None


def tokens_to_message(tokens: Optional[Iterable[str]], sentence: Optional[str] = None) -> str:
    if sentence:
        return sentence
    return " ".join(str(token) for token in (tokens or []))
