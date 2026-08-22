import re
from typing import List, Dict, Any, Optional

class CommunicationAI:
    """
    AI engine for AAC sentence generation, phrase expansion,
    simplification, and smart predictive communication for neurodivergent individuals.
    """

    DEFAULT_EXPANSIONS = {
        ("I", "WANT", "WATER"): "I want a glass of water, please.",
        ("I", "WANT", "FOOD"): "I am hungry and would like some food, please.",
        ("I", "WANT", "TOILET"): "I need to use the restroom, please.",
        ("I", "NEED", "HELP"): "I need help right now, please.",
        ("I", "FEEL", "TIRED"): "I am feeling tired and need to rest.",
        ("I", "WANT", "PLAY"): "I would like to play now.",
        ("NO", "WANT"): "I do not want this right now, thank you.",
        ("TOO", "LOUD"): "It is too loud here. I need a quiet break.",
        ("I", "FEEL", "SAD"): "I am feeling sad and would like some comfort.",
        ("I", "FEEL", "HAPPY"): "I am feeling happy and good!",
        ("I", "FEEL", "ANXIOUS"): "I am feeling anxious. Can you stay close?",
        ("I", "FEEL", "ANGRY"): "I feel angry and need space to calm down.",
        ("I", "NEED", "BREAK"): "I need a quiet break, please.",
    }

    @classmethod
    def generate_sentence_from_tokens(
        cls,
        tokens: Optional[List[str]] = None,
        sentence: Optional[str] = None,
        emotion: Optional[str] = None,
        context: Optional[str] = None,
        style: str = "natural"
    ) -> Dict[str, Any]:
        """
        Expands AAC tokens into natural, child-friendly spoken sentences with simplification
        and smart communication suggestions.
        """
        try:
            raw_tokens: List[str] = []
            if tokens:
                raw_tokens = [str(t).strip() for t in tokens if str(t).strip()]
            elif sentence:
                # Split raw sentence into tokens
                clean_s = re.sub(r'[^\w\s]', '', sentence)
                raw_tokens = [w.strip() for w in clean_s.split() if w.strip()]

            if not raw_tokens:
                return {
                    "raw_tokens": [],
                    "generated_sentence": "I want to share something with you.",
                    "simplified_sentence": "I want to share.",
                    "suggestions": ["Please help me.", "I need a moment.", "Can we talk?"],
                    "suggested_alternatives": ["Can you help me?", "I need a moment."],
                    "is_fallback": True,
                    "audio_hint": "Default communication phrase",
                }

            cleaned_upper = [t.upper() for t in raw_tokens]
            token_tuple = tuple(cleaned_upper)

            # 1. Direct dictionary match
            if token_tuple in cls.DEFAULT_EXPANSIONS:
                base_sentence = cls.DEFAULT_EXPANSIONS[token_tuple]
            else:
                # 2. Rule-based natural language builder
                words = [t.capitalize() for t in raw_tokens]
                if len(words) == 1:
                    word = words[0].lower()
                    if word in ["water", "food", "juice", "snack", "apple", "milk", "cookie"]:
                        base_sentence = f"I would like some {word}, please."
                    elif word in ["toilet", "bathroom", "restroom"]:
                        base_sentence = "I need to use the bathroom, please."
                    elif word in ["help", "assist"]:
                        base_sentence = "Please help me with this."
                    elif word in ["tired", "sleep", "rest", "break"]:
                        base_sentence = "I am feeling tired and need a break."
                    elif word in ["happy", "sad", "angry", "scared", "overwhelmed", "anxious", "frustrated"]:
                        base_sentence = f"I am feeling {word} right now."
                    else:
                        base_sentence = f"I want {word}, please."
                elif words[0].lower() in ["i", "me"]:
                    verb_part = " ".join(w.lower() for w in words[1:])
                    base_sentence = f"I {verb_part}, please."
                else:
                    base_sentence = f"I want {' '.join(w.lower() for w in words)}, please."

            # Ensure proper punctuation
            if not base_sentence.endswith((".", "!", "?")):
                base_sentence += "."

            # Apply emotion tone if provided
            if emotion:
                em = emotion.lower().strip()
                if em in ["anxious", "overwhelmed", "scared"]:
                    if not base_sentence.endswith("safe."):
                        base_sentence = f"{base_sentence[:-1]} and feel safe."
                elif em in ["tired", "exhausted"]:
                    if "tired" not in base_sentence.lower():
                        base_sentence = f"{base_sentence[:-1]} because I am tired."
                elif em in ["happy", "excited"]:
                    base_sentence = f"{base_sentence[:-1]}!"

            # Construct clean, simplified version
            simplified = " ".join(raw_tokens).capitalize()
            if not simplified.endswith((".", "!", "?")):
                simplified += "."

            # Generate child-friendly smart suggestions
            raw_combined = " ".join(raw_tokens).lower()
            suggestions = [
                f"Please give me {raw_combined}.",
                f"Can I have {raw_combined}?",
                f"I need {raw_combined} now.",
            ]

            return {
                "raw_tokens": raw_tokens,
                "generated_sentence": base_sentence,
                "simplified_sentence": simplified,
                "suggestions": suggestions,
                "suggested_alternatives": suggestions,
                "is_fallback": False,
                "audio_hint": f"Clear speech generated for {len(raw_tokens)} symbols",
            }
        except Exception:
            # Deterministic safe fallback
            fallback_text = " ".join(tokens) if tokens else (sentence or "I need assistance.")
            return {
                "raw_tokens": tokens or [],
                "generated_sentence": f"I want {fallback_text}." if fallback_text else "I need assistance.",
                "simplified_sentence": fallback_text or "I need help.",
                "suggestions": ["Please help me.", "Thank you."],
                "suggested_alternatives": ["Please help me."],
                "is_fallback": True,
                "audio_hint": "Fallback speech",
            }

    @classmethod
    def simplify_complex_text(
        cls,
        text: Optional[str] = None,
        target_level: str = "easy",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simplifies complex caregiver or educational sentences into concise, visual-friendly
        bullet points and matching AAC tokens.
        """
        try:
            if not text or not text.strip():
                return {
                    "original_text": "",
                    "simplified_text": "Please speak simply.",
                    "simplified_sentence": "Please speak simply.",
                    "key_points": ["Listen carefully", "Take one step at a time"],
                    "matching_aac_tokens": ["LISTEN", "HELP"],
                    "suggestions": ["Can you repeat simply?", "What should I do first?"],
                    "is_fallback": True,
                }

            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]

            key_points = []
            aac_tokens = []

            lower_text = text.lower()
            if "water" in lower_text or "drink" in lower_text or "thirsty" in lower_text:
                key_points.append("Drink water")
                aac_tokens.extend(["I", "WANT", "WATER"])
            if "food" in lower_text or "eat" in lower_text or "hungry" in lower_text or "lunch" in lower_text or "dinner" in lower_text:
                key_points.append("Eat food")
                aac_tokens.extend(["I", "WANT", "FOOD"])
            if "toilet" in lower_text or "bathroom" in lower_text or "restroom" in lower_text:
                key_points.append("Go to bathroom")
                aac_tokens.extend(["I", "NEED", "TOILET"])
            if "help" in lower_text or "assist" in lower_text or "stuck" in lower_text:
                key_points.append("Ask for help")
                aac_tokens.extend(["PLEASE", "HELP"])
            if "quiet" in lower_text or "loud" in lower_text or "noise" in lower_text:
                key_points.append("Too loud - need quiet")
                aac_tokens.extend(["TOO", "LOUD"])
            if "sleep" in lower_text or "bed" in lower_text or "rest" in lower_text or "tired" in lower_text:
                key_points.append("Time to rest")
                aac_tokens.extend(["I", "FEEL", "TIRED"])
            if "play" in lower_text or "game" in lower_text or "toy" in lower_text:
                key_points.append("Time to play")
                aac_tokens.extend(["I", "WANT", "PLAY"])

            if not key_points and sentences:
                first = sentences[0]
                words = first.split()
                simplified_clause = " ".join(words[:6])
                if not simplified_clause.endswith("."):
                    simplified_clause += "."
                key_points.append(simplified_clause)
                aac_tokens.extend([w.upper() for w in words[:3] if len(w) > 2])

            simplified_text = " • ".join(key_points) if key_points else "Take a breath and do one thing at a time."
            simplified_sentence = key_points[0] if key_points else "Take one step at a time."

            suggestions = [
                "Can you show me with pictures?",
                "What do I do first?",
                "I am ready.",
            ]

            return {
                "original_text": text,
                "simplified_text": simplified_text,
                "simplified_sentence": simplified_sentence,
                "key_points": key_points if key_points else ["Take a breath", "One step at a time"],
                "matching_aac_tokens": list(dict.fromkeys(aac_tokens))[:6],
                "suggestions": suggestions,
                "is_fallback": False,
            }
        except Exception:
            return {
                "original_text": text or "",
                "simplified_text": "Please take one step at a time.",
                "simplified_sentence": "Take one step at a time.",
                "key_points": ["Take one step at a time"],
                "matching_aac_tokens": ["HELP"],
                "suggestions": ["Please help me."],
                "is_fallback": True,
            }

