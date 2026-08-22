from typing import Dict, Any, List

class EmotionAI:
    """
    Emotion-aware recommendation engine for neurodivergent individuals.
    Provides empathetic sentence suggestions, sensory grounding tips,
    calming strategies, and visual communication cues tailored to real-time emotional states.
    """

    SUPPORTED_EMOTIONS = [
        "happy",
        "sad",
        "angry",
        "anxious",
        "calm",
        "scared",
        "frustrated",
        "overwhelmed",
        "tired",
        "excited",
    ]

    EMOTION_KNOWLEDGE_BASE = {
        "happy": {
            "icon": "😊",
            "phrases": [
                "I am happy right now!",
                "I want to share what made me smile.",
                "I'm feeling good and ready to do activities.",
                "Can we do this again tomorrow?",
            ],
            "calming_strategies": [
                "Celebrate and share the joyful moment with caregiver",
                "Draw or color a picture of what made you happy",
                "Engage in creative and interactive play",
            ],
            "sensory_tip": "Great time for active play, creative drawing, or engaging learning tasks.",
        },
        "calm": {
            "icon": "😌",
            "phrases": [
                "I feel peaceful and relaxed.",
                "Everything is okay.",
                "I am ready to listen and learn.",
                "I like this quiet space.",
            ],
            "calming_strategies": [
                "Continue steady rhythmic breathing",
                "Listen to soft melodic instrumental music",
                "Enjoy quiet reading or sensory tactile exploration",
            ],
            "sensory_tip": "Maintain this soothing rhythm with low-stimulus lighting and comfortable seating.",
        },
        "anxious": {
            "icon": "😰",
            "phrases": [
                "I am feeling worried right now.",
                "Can you stay close to me?",
                "What is going to happen next?",
                "I need a 5-minute quiet break.",
            ],
            "calming_strategies": [
                "Take 5 slow 'box breaths' (inhale 4s, hold 4s, exhale 4s)",
                "Hold and squeeze a soft sensory plush or weighted lap pad",
                "Put on noise-canceling headphones to block overwhelming sounds",
            ],
            "sensory_tip": "Try 4-7-8 deep breaths, a weighted lap pad, or noise-canceling headphones.",
        },
        "overwhelmed": {
            "icon": "🤯",
            "phrases": [
                "Too much is happening at once.",
                "It is too loud and bright here.",
                "Please stop talking for a moment.",
                "I need to go to my safe sensory corner.",
            ],
            "calming_strategies": [
                "Dim bright lights and move to a quiet corner",
                "Reduce verbal instructions and give visual space",
                "Use sensory compression or weighted blanket",
            ],
            "sensory_tip": "Dim lights immediately, remove auditory clutter, and reduce verbal instructions.",
        },
        "sad": {
            "icon": "😢",
            "phrases": [
                "I am feeling sad.",
                "Can I have a gentle hug?",
                "I miss something/someone.",
                "I just need some quiet comfort.",
            ],
            "calming_strategies": [
                "Offer a gentle hug or cozy blanket",
                "Provide favorite sensory calming item or soothing toy",
                "Allow quiet resting time without pressure to speak",
            ],
            "sensory_tip": "Offer a soft blanket, favorite sensory object, and empathetic silent presence.",
        },
        "angry": {
            "icon": "😡",
            "phrases": [
                "I feel very frustrated and angry!",
                "I do not want to do this right now.",
                "I need space to cool down safely.",
                "Please listen to what I am saying.",
            ],
            "calming_strategies": [
                "Squeeze a sensory stress ball or dough firmly",
                "Do slow 'lion breath' releases to vent tension",
                "Step into a designated cool-down sensory zone",
            ],
            "sensory_tip": "Provide deep-pressure proprioceptive squeeze, stress ball, or safe physical movement.",
        },
        "scared": {
            "icon": "😨",
            "phrases": [
                "I feel scared right now.",
                "Please hold my hand.",
                "Can you tell me I am safe?",
                "I want to go somewhere familiar.",
            ],
            "calming_strategies": [
                "Reassure safety with warm, steady physical contact",
                "Name 3 familiar safe objects in the room (5-4-3-2-1 grounding)",
                "Wrap in a comforting weighted blanket or hoodie",
            ],
            "sensory_tip": "Speak in a calm, low whisper and provide grounding tactile support.",
        },
        "frustrated": {
            "icon": "😤",
            "phrases": [
                "This is too hard for me right now.",
                "I need help with this task.",
                "Can we try a different way?",
                "I need to pause before trying again.",
            ],
            "calming_strategies": [
                "Break the current task into smaller visual micro-steps",
                "Take a 3-minute sensory reset break with kinetic sand",
                "Affirm effort: 'It is okay to find this tricky, let us do it together.'",
            ],
            "sensory_tip": "Provide immediate tactile feedback or a brief movement break to release frustration.",
        },
        "tired": {
            "icon": "😴",
            "phrases": [
                "I am very sleepy and out of energy.",
                "Can I lay down for a little bit?",
                "I need to pause this activity.",
                "My body feels heavy.",
            ],
            "calming_strategies": [
                "Dim room lights and play gentle white noise",
                "Transition to a lying down position on a soft mat",
                "Sip warm water or milk",
            ],
            "sensory_tip": "Transition to low-energy calming activities or prepare for rest with dim light.",
        },
        "excited": {
            "icon": "🤩",
            "phrases": [
                "I am so excited and have lots of energy!",
                "Look at what I did!",
                "I want to jump and celebrate!",
                "Let's go do it now!",
            ],
            "calming_strategies": [
                "Do 10 happy star jumps or mini-trampoline bounces",
                "Clap rhythmically to channel energetic excitement safely",
                "Share the accomplishment enthusiastically with caregiver",
            ],
            "sensory_tip": "Channel energy into a physical movement break like trampoline jumps or dancing.",
        },
    }

    @classmethod
    def get_emotion_recommendations(cls, emotion: str, intensity: int = 5) -> Dict[str, Any]:
        try:
            em_key = emotion.lower().strip() if emotion else "calm"
            data = cls.EMOTION_KNOWLEDGE_BASE.get(
                em_key,
                {
                    "icon": "😐",
                    "phrases": [
                        f"I am feeling {emotion}.",
                        "I want to express what I need.",
                        "Can you help me right now?",
                    ],
                    "calming_strategies": [
                        "Take 3 deep gentle breaths",
                        "Check in with a supportive caregiver",
                        "Take a brief calming sensory pause",
                    ],
                    "sensory_tip": "Check in gently and allow time for self-regulation.",
                },
            )

            phrases = list(data["phrases"])
            calming = list(data.get("calming_strategies", []))

            if intensity >= 8:
                if em_key in ["anxious", "overwhelmed", "angry", "scared", "frustrated"]:
                    phrases.insert(0, "URGENT: I need quiet and safe space immediately.")
                    calming.insert(0, "Immediate low-stimulus sensory isolation recommended")
                elif em_key in ["happy", "excited"]:
                    phrases.insert(0, "I am bursting with happy energy!")

            return {
                "emotion": emotion,
                "intensity": intensity,
                "icon": data["icon"],
                "recommended_phrases": phrases,
                "communication_suggestions": phrases,
                "calming_strategies": calming,
                "sensory_tip": data["sensory_tip"],
                "is_fallback": False,
            }
        except Exception:
            return {
                "emotion": emotion or "calm",
                "intensity": intensity,
                "icon": "❤️",
                "recommended_phrases": [
                    f"I am feeling {emotion or 'overwhelmed'}.",
                    "I need a moment to calm down.",
                    "Can you help me, please?",
                ],
                "communication_suggestions": [
                    f"I am feeling {emotion or 'overwhelmed'}.",
                    "I need a moment to calm down.",
                    "Can you help me, please?",
                ],
                "calming_strategies": [
                    "Take 5 slow deep breaths",
                    "Move to a quiet, low-light space",
                    "Hold a comforting sensory item",
                ],
                "sensory_tip": "Provide a peaceful environment and allow time for quiet regulation.",
                "is_fallback": True,
            }

