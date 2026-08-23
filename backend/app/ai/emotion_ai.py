from typing import Dict, Any, List, Optional

class EmotionAI:
    """
    Emotion-aware recommendation engine for neurodivergent individuals.
    Provides empathetic sentence suggestions, sensory grounding tips,
    calming strategies, visual communication cues, and structured activities
    tailored to real-time emotional states and 90-day remote emergency situations.
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
            "suitable_activity": {
                "title": "Creative Joy Collage & Story Sharing",
                "category": "Creative Expression",
                "icon": "🎨",
                "duration_minutes": 15,
                "description": "Draw or color a happy moment and share the story with your caregiver.",
            },
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
            "suitable_activity": {
                "title": "Gentle Reading & Sensory Exploration",
                "category": "Quiet Focus",
                "icon": "📖",
                "duration_minutes": 20,
                "description": "Explore a picture book or tactile sensory toys in a cozy quiet corner.",
            },
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
            "suitable_activity": {
                "title": "Sensory Calm Down Jar & Box Breathing",
                "category": "Sensory Calming",
                "icon": "🫧",
                "duration_minutes": 10,
                "description": "Watch the glitter settle in a sensory bottle while taking 5 rhythmic box breaths.",
            },
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
            "suitable_activity": {
                "title": "Safe Sensory Fort / Quiet Corner Reset",
                "category": "Sensory Relief",
                "icon": "⛺",
                "duration_minutes": 15,
                "description": "Rest inside a darkened blanket fort or quiet tent with noise-canceling headphones.",
            },
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
            "suitable_activity": {
                "title": "Cozy Blanket Time & Gentle Music",
                "category": "Comfort & Soothing",
                "icon": "🧸",
                "duration_minutes": 15,
                "description": "Wrap in a favorite soft blanket and listen to soothing lullaby sounds.",
            },
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
            "suitable_activity": {
                "title": "Sensory Dough Squeeze & Lion Breaths",
                "category": "Physical Release",
                "icon": "🧱",
                "duration_minutes": 10,
                "description": "Firmly knead sensory playdough or squeeze a stress ball to safely release physical tension.",
            },
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
            "suitable_activity": {
                "title": "5-4-3-2-1 Sensory Grounding Game",
                "category": "Grounding",
                "icon": "🛡️",
                "duration_minutes": 8,
                "description": "Spot 5 colors you see, touch 4 soft textures, and listen for 3 gentle sounds.",
            },
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
            "suitable_activity": {
                "title": "Kinetic Sand Sensory Reset Break",
                "category": "Tactile Reset",
                "icon": "⏳",
                "duration_minutes": 10,
                "description": "Run hands through soft kinetic sand to reset cognitive overwhelm before trying again.",
            },
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
            "suitable_activity": {
                "title": "Restful Mat Pause & White Noise",
                "category": "Rest & Recharge",
                "icon": "🛌",
                "duration_minutes": 20,
                "description": "Lie down with dim lighting and soothing ocean soundscapes to recharge energy.",
            },
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
            "suitable_activity": {
                "title": "Star Jump & Dance Movement Break",
                "category": "Energy Channeling",
                "icon": "⭐",
                "duration_minutes": 10,
                "description": "Do 10 rhythmic star jumps or bounce on a mini-trampoline to safely release high excitement.",
            },
        },
    }

    @classmethod
    def get_emotion_recommendations(
        cls,
        emotion: str,
        intensity: int = 5,
        is_emergency_mode: bool = False
    ) -> Dict[str, Any]:
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
                    "suitable_activity": {
                        "title": "Quiet Sensory Breathing",
                        "category": "Regulation",
                        "icon": "🧘",
                        "duration_minutes": 10,
                        "description": "Take slow rhythmic breaths and rest quietly with caregiver support.",
                    },
                },
            )

            phrases = list(data["phrases"])
            calming = list(data.get("calming_strategies", []))
            activity = dict(data.get("suitable_activity", {}))
            sensory_tip = data.get("sensory_tip", "")

            # Tiered intensity handling
            if intensity <= 3:
                intensity_level = "low"
                caregiver_alert = False
                immediate_guidance = "Take a gentle breath and enjoy what you are doing."
                # Keep phrases simple and positive
                phrases = phrases[:2]
            elif 4 <= intensity <= 7:
                intensity_level = "medium"
                caregiver_alert = False
                immediate_guidance = "Let's take a calm pause and try a soothing sensory activity."
            else:  # High intensity 8-10
                intensity_level = "high"
                caregiver_alert = True
                if em_key in ["anxious", "overwhelmed", "angry", "scared", "frustrated"]:
                    immediate_guidance = "You may need a quiet place. Let's take 5 slow deep breaths together."
                    phrases.insert(0, "URGENT: I need quiet and safe space immediately.")
                    phrases.insert(1, f"I feel very {em_key}, please stay close to me.")
                    calming.insert(0, "Immediate low-stimulus sensory isolation recommended")
                    calming.insert(1, "Put on noise-canceling headphones and move to quiet fort")
                else:
                    immediate_guidance = "Your feelings are very strong right now. Let's take a gentle break."
                    phrases.insert(0, f"I am feeling very {em_key}!")

            # 90-Day Emergency Lockdown adaptations
            if is_emergency_mode:
                if em_key in ["anxious", "overwhelmed", "scared", "sad"]:
                    calming.append("Emergency Home Tip: Practice safe home routine in your dedicated quiet corner.")
                if "Home Sensory Reset" not in [calming]:
                    calming.append("Remote Caregiver Connection: Send an emotion badge to your caregiver.")

            return {
                "emotion": emotion,
                "intensity": intensity,
                "intensity_level": intensity_level,
                "icon": data["icon"],
                "immediate_calming_guidance": immediate_guidance,
                "recommended_phrases": phrases,
                "communication_suggestions": phrases,
                "calming_strategies": calming,
                "sensory_tip": sensory_tip,
                "suitable_activity": activity,
                "caregiver_alert_recommended": caregiver_alert,
                "is_emergency_mode": is_emergency_mode,
                "is_fallback": False,
            }
        except Exception:
            # Resilient fallback
            is_high = intensity >= 8
            return {
                "emotion": emotion or "calm",
                "intensity": intensity,
                "intensity_level": "high" if is_high else ("low" if intensity <= 3 else "medium"),
                "icon": "❤️",
                "immediate_calming_guidance": "Take 5 slow breaths in a quiet place.",
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
                "suitable_activity": {
                    "title": "Gentle Sensory Deep Breathing",
                    "category": "Calming",
                    "icon": "🧘",
                    "duration_minutes": 10,
                    "description": "Sit comfortably, close eyes gently, and take 5 slow box breaths.",
                },
                "caregiver_alert_recommended": is_high,
                "is_emergency_mode": is_emergency_mode,
                "is_fallback": True,
            }


