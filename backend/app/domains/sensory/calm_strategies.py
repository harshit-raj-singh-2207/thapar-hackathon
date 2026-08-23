from typing import Dict, List

from app.domains.sensory.schemas import SensoryState


_CALM_STRATEGIES: Dict[str, List[str]] = {
    "too_noisy": [
        "Move to a quieter place if you can.",
        "Use headphones or ear protection if available.",
        "Reduce sound exposure for a few minutes.",
    ],
    "too_bright": [
        "Reduce screen brightness if possible.",
        "Move away from strong lighting.",
        "Use a softer or shaded light source.",
    ],
    "crowded": [
        "Move toward a quieter, less crowded space.",
        "Stay near a trusted person if that feels helpful.",
        "Give yourself extra personal space.",
    ],
    "overwhelmed": [
        "Pause the current task for a moment.",
        "Try your familiar breathing or quiet routine.",
        "Let your caregiver know if you would like support.",
    ],
    "need_quiet": [
        "Choose a quiet space for a short break.",
        "Lower nearby sounds where possible.",
        "Tell others that you need quiet right now.",
    ],
    "need_space": [
        "Move to a place with more personal space.",
        "Use your 'I need space' communication phrase.",
        "Ask a trusted person to help protect your space.",
    ],
    "need_break": [
        "Pause and take a short break.",
        "Choose a familiar calming activity.",
        "Return when you feel ready.",
    ],
}


def get_calm_strategies(sensory_state: SensoryState) -> List[str]:
    """Return a fresh list of supportive, non-medical local suggestions."""
    return list(_CALM_STRATEGIES.get(sensory_state, ()))
