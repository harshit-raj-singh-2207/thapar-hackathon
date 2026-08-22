import re
import os
from typing import Dict, Any, Optional

# Voice profile configuration — no API keys exposed
VOICE_PROFILES = {
    "friendly_child": {
        "lang": "en-US",
        "voice_name": "en-US-Standard-C",
        "rate": 0.9,
        "pitch": 1.1,
        "volume": 1.0,
        "ssml_gender": "FEMALE",
        "description": "Warm, friendly female voice for children",
    },
    "calm_female": {
        "lang": "en-US",
        "voice_name": "en-US-Standard-E",
        "rate": 0.85,
        "pitch": 1.0,
        "volume": 1.0,
        "ssml_gender": "FEMALE",
        "description": "Calm, soothing female voice",
    },
    "clear_male": {
        "lang": "en-US",
        "voice_name": "en-US-Standard-B",
        "rate": 0.9,
        "pitch": 0.95,
        "volume": 1.0,
        "ssml_gender": "MALE",
        "description": "Clear, articulate male voice",
    },
    "gentle_neutral": {
        "lang": "en-GB",
        "voice_name": "en-GB-Standard-A",
        "rate": 0.85,
        "pitch": 1.05,
        "volume": 1.0,
        "ssml_gender": "FEMALE",
        "description": "Gentle, neutral British voice",
    },
}

DEFAULT_VOICE = "friendly_child"
MAX_TEXT_LENGTH = 500  # characters — prevent abuse

# Emotion-to-prosody modulation mappings
EMOTION_PROSODY_ADAPTATIONS = {
    "excited": {"rate_mult": 1.1, "pitch_mult": 1.15},
    "happy": {"rate_mult": 1.05, "pitch_mult": 1.1},
    "calm": {"rate_mult": 0.9, "pitch_mult": 0.95},
    "sad": {"rate_mult": 0.8, "pitch_mult": 0.9},
    "angry": {"rate_mult": 1.05, "pitch_mult": 0.9},
    "anxious": {"rate_mult": 0.95, "pitch_mult": 1.05},
    "tired": {"rate_mult": 0.75, "pitch_mult": 0.9},
    "frustrated": {"rate_mult": 0.95, "pitch_mult": 0.95},
    "overwhelmed": {"rate_mult": 0.85, "pitch_mult": 1.0},
    "scared": {"rate_mult": 0.9, "pitch_mult": 1.1},
}


class SpeechService:
    """
    Backend TTS service for Nivara communication module.

    Architecture:
    - Primary: Web Speech API configuration (browser-native, zero cost, no API key needed)
    - Secondary: SSML hint for external TTS providers (Google, Azure, etc.) via env config
    - Fallback: always returns metadata with phonetic guide so UI can still function

    Security: No API keys or provider secrets are ever returned to the frontend.
    """

    @classmethod
    def _resolve_voice_profile(cls, voice: Optional[str]) -> Dict[str, Any]:
        """Resolve the requested voice profile, falling back to default."""
        key = (voice or DEFAULT_VOICE).strip().lower()
        return VOICE_PROFILES.get(key, VOICE_PROFILES[DEFAULT_VOICE])

    @classmethod
    def _clean_and_validate(cls, text: Optional[str]) -> str:
        """Clean and validate input text. Raises ValueError on failure."""
        if not text or not text.strip():
            raise ValueError("Text must not be empty.")
        cleaned = text.strip()
        # Strip excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        if len(cleaned) > MAX_TEXT_LENGTH:
            raise ValueError(
                f"Text too long ({len(cleaned)} chars). Maximum allowed is {MAX_TEXT_LENGTH}."
            )
        return cleaned

    @classmethod
    def _build_phonetic_guide(cls, text: str) -> str:
        """Build a simplified word-by-word phonetic guide."""
        words = text.split()
        phonetic_parts = []
        for word in words:
            # Strip punctuation for pronunciation
            clean_word = re.sub(r'[^\w]', '', word).lower()
            if clean_word:
                phonetic_parts.append(clean_word)
        return " ".join(phonetic_parts)

    @classmethod
    def _build_ssml(cls, text: str, profile: Dict[str, Any], speed: float, pitch: float) -> str:
        """Build SSML markup for external TTS providers."""
        # Sanitize text for SSML
        safe_text = (
            text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        rate_str = f"{int(speed * 100)}%"
        pitch_str = f"{int((pitch - 1.0) * 50):+d}%"  # Convert 1.0 → +0%, 1.2 → +10%

        ssml = (
            f'<speak>'
            f'<prosody rate="{rate_str}" pitch="{pitch_str}">'
            f'{safe_text}'
            f'</prosody>'
            f'</speak>'
        )
        return ssml

    @classmethod
    def _build_web_speech_config(
        cls, text: str, profile: Dict[str, Any], speed: float, pitch: float, language: str
    ) -> Dict[str, Any]:
        """
        Build a configuration dict for the browser Web Speech API (SpeechSynthesisUtterance).
        This is safe to send to the frontend — no credentials included.
        """
        return {
            "text": text,
            "lang": language or profile["lang"],
            "rate": round(speed * profile["rate"], 2),
            "pitch": round(pitch * profile["pitch"], 2),
            "volume": profile["volume"],
            "voice_name_hint": profile["voice_name"],
        }

    @classmethod
    def _estimate_duration(cls, text: str, speed: float) -> float:
        """Estimate speech duration in seconds based on word count and speed."""
        word_count = len(text.split())
        # Average spoken English: ~140 words/min = ~0.43 sec/word at speed=1.0
        base_duration = word_count * 0.43
        adjusted = base_duration / max(speed, 0.1)
        return max(0.5, round(adjusted, 2))

    @classmethod
    def synthesize_speech_metadata(
        cls,
        req: Any,
        child_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main TTS entry point. Returns rich speech metadata.
        Never exposes API keys or provider secrets.

        Returns is_fallback=True and a safe phonetic guide if anything fails.
        """
        try:
            # 1. Validate and clean text
            raw_text = getattr(req, "text", None) if hasattr(req, "text") else req.get("text") if isinstance(req, dict) else None
            text = cls._clean_and_validate(raw_text)

            # 2. Resolve parameters
            speed = float((getattr(req, "speed", 1.0) if hasattr(req, "speed") else (req.get("speed", 1.0) if isinstance(req, dict) else 1.0)) or 1.0)
            pitch = float((getattr(req, "pitch", 1.0) if hasattr(req, "pitch") else (req.get("pitch", 1.0) if isinstance(req, dict) else 1.0)) or 1.0)
            voice_key = (getattr(req, "voice", DEFAULT_VOICE) if hasattr(req, "voice") else (req.get("voice", DEFAULT_VOICE) if isinstance(req, dict) else DEFAULT_VOICE)) or DEFAULT_VOICE
            language = (getattr(req, "language", "en-US") if hasattr(req, "language") else (req.get("language", "en-US") if isinstance(req, dict) else "en-US")) or "en-US"
            emotion = (getattr(req, "emotion", None) if hasattr(req, "emotion") else (req.get("emotion", None) if isinstance(req, dict) else None))

            # 3. Emotion prosody modulation if specified
            if emotion and emotion.lower() in EMOTION_PROSODY_ADAPTATIONS:
                mod = EMOTION_PROSODY_ADAPTATIONS[emotion.lower()]
                speed = speed * mod["rate_mult"]
                pitch = pitch * mod["pitch_mult"]

            # 4. Clamp speed and pitch to safe ranges
            speed = max(0.5, min(2.0, speed))
            pitch = max(0.5, min(2.0, pitch))

            # 5. Resolve voice profile
            profile = cls._resolve_voice_profile(voice_key)

            # 6. Build outputs
            phonetic_guide = cls._build_phonetic_guide(text)
            ssml_hint = cls._build_ssml(text, profile, speed, pitch)
            web_speech_config = cls._build_web_speech_config(text, profile, speed, pitch, language)
            duration = cls._estimate_duration(text, speed)

            return {
                "text": text,
                "audio_url": None,  # Browser-native Web Speech API
                "phonetic_guide": phonetic_guide,
                "ssml_hint": ssml_hint,
                "web_speech_config": web_speech_config,
                "duration_estimate_sec": duration,
                "voice_used": voice_key,
                "is_fallback": False,
                "provider": "web_speech_api",
            }

        except ValueError as ve:
            # Validation errors — return safe fallback
            return {
                "text": "",
                "audio_url": None,
                "phonetic_guide": "",
                "ssml_hint": None,
                "web_speech_config": None,
                "duration_estimate_sec": 0.0,
                "voice_used": DEFAULT_VOICE,
                "is_fallback": True,
                "provider": "fallback",
                "_error": str(ve),
            }
        except Exception:
            # Provider or unexpected failure — never crash
            return {
                "text": (getattr(req, "text", "") if hasattr(req, "text") else req.get("text", "") if isinstance(req, dict) else "") or "",
                "audio_url": None,
                "phonetic_guide": "",
                "ssml_hint": None,
                "web_speech_config": None,
                "duration_estimate_sec": 1.5,
                "voice_used": DEFAULT_VOICE,
                "is_fallback": True,
                "provider": "fallback",
            }

    @classmethod
    def synthesize_aac_tokens(
        cls,
        tokens: list,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        language: str = "en-US",
        emotion: Optional[str] = None,
        child_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize speech directly from a sequence of AAC token labels.
        """
        if not tokens:
            raise ValueError("Tokens list must not be empty for AAC speech.")
        
        # Combine token labels into clean sentence
        words = [str(t).strip().capitalize() if i == 0 else str(t).strip().lower() for i, t in enumerate(tokens) if str(t).strip()]
        if not words:
            raise ValueError("No valid words in tokens.")
        sentence = " ".join(words)
        if not sentence.endswith((".", "!", "?")):
            sentence += "."

        req_dict = {
            "text": sentence,
            "voice": voice or DEFAULT_VOICE,
            "speed": speed,
            "pitch": pitch,
            "language": language,
            "emotion": emotion,
        }
        return cls.synthesize_speech_metadata(req_dict, child_id=child_id)

    @classmethod
    def synthesize_ai_sentence(
        cls,
        sentence: str,
        emotion: Optional[str] = None,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        language: str = "en-US",
        child_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize speech for an AI-generated sentence with emotional inflection.
        """
        cleaned = cls._clean_and_validate(sentence)
        req_dict = {
            "text": cleaned,
            "voice": voice or DEFAULT_VOICE,
            "speed": speed,
            "pitch": pitch,
            "language": language,
            "emotion": emotion,
        }
        return cls.synthesize_speech_metadata(req_dict, child_id=child_id)

