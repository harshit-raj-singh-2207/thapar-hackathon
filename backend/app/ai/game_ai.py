from typing import List, Dict, Any, Optional

class GameAI:
    """
    Cognitive game recommendation engine.
    Analyzes multi-modal behavioral signals (emotion distress, learning progress,
    AAC vocabulary usage, and past game accuracy) to recommend personalized skill development games.
    """

    DEFAULT_RECOMMENDATIONS = [
        {
            "game_id": "game-comm-1",
            "title": "AAC Picture Word Match",
            "category": "Communication",
            "icon": "🗣️",
            "color": "#2563EB",
            "reason": "Reinforce everyday picture vocabulary for independent home requests.",
            "recommended_focus": "Vocabulary & Word Association",
            "benefit": "Helps you communicate your needs quickly and confidently.",
        },
        {
            "game_id": "game-emotion-1",
            "title": "Emotion Detective",
            "category": "Emotion",
            "icon": "😊",
            "color": "#EC4899",
            "reason": "Explore soothing strategies for sensory self-regulation during home isolation.",
            "recommended_focus": "Emotional Regulation",
            "benefit": "Teaches calm breathing and quiet-space tools when feelings get big.",
        },
        {
            "game_id": "game-learning-1",
            "title": "Daily Routine Step Sorter",
            "category": "Learning",
            "icon": "📖",
            "color": "#3B82F6",
            "reason": "Maintain structured morning and bedtime sequences at home.",
            "recommended_focus": "Daily Living Skills",
            "benefit": "Builds confidence in completing daily tasks step by step.",
        },
    ]

    @classmethod
    def generate_recommendations(
        cls,
        child_id: Optional[str] = None,
        recent_emotions: Optional[List[str]] = None,
        struggling_skills: Optional[List[str]] = None,
        learning_topic_categories: Optional[List[str]] = None,
        is_emergency_mode: bool = False,
    ) -> List[Dict[str, Any]]:
        try:
            recs = []
            emotions_set = set([e.lower().strip() for e in (recent_emotions or [])])
            skills_set = set([s.lower().strip() for s in (struggling_skills or [])])

            # 1. Emotion distress signal
            if any(e in emotions_set for e in ["anxious", "overwhelmed", "frustrated", "angry", "scared"]):
                recs.append({
                    "game_id": "game-emotion-1",
                    "title": "Emotion Detective",
                    "category": "Emotion",
                    "icon": "😊",
                    "color": "#EC4899",
                    "reason": "You have had some intense feelings recently. Practice finding calming sensory tools.",
                    "recommended_focus": "Sensory Self-Regulation",
                    "benefit": "Helps you discover quiet-room grounding techniques.",
                })
                recs.append({
                    "game_id": "game-focus-1",
                    "title": "Quiet Focus Target Finder",
                    "category": "Focus",
                    "icon": "🎯",
                    "color": "#10B981",
                    "reason": "A quiet visual grounding game to soothe mental overload and restore calm.",
                    "recommended_focus": "Visual Calming & Focus",
                    "benefit": "Provides a low-stimulus, relaxing target search.",
                })

            # 2. Communication reinforcement
            if "communication" in skills_set or not recs:
                recs.append({
                    "game_id": "game-comm-1",
                    "title": "AAC Picture Word Match",
                    "category": "Communication",
                    "icon": "🗣️",
                    "color": "#2563EB",
                    "reason": "Practice matching everyday pictures with clear words for easy communication.",
                    "recommended_focus": "AAC Vocabulary Mastery",
                    "benefit": "Builds vocabulary for independent remote requests.",
                })

            # 3. Learning & Routine structure
            if "learning" in skills_set or is_emergency_mode:
                recs.append({
                    "game_id": "game-learning-1",
                    "title": "Daily Routine Step Sorter",
                    "category": "Learning",
                    "icon": "📖",
                    "color": "#3B82F6",
                    "reason": "Keep your home visual routines strong and predictable during 90-day isolation.",
                    "recommended_focus": "Daily Routine Steps",
                    "benefit": "Strengthens morning and evening task completion.",
                })

            # 4. Cognitive Working Memory
            if "memory" in skills_set:
                recs.append({
                    "game_id": "game-memory-1",
                    "title": "Visual Pattern & Memory Quest",
                    "category": "Memory",
                    "icon": "🧠",
                    "color": "#8B5CF6",
                    "reason": "Boost your sequence memory and pattern recognition skills.",
                    "recommended_focus": "Working Memory",
                    "benefit": "Helps with remembering multi-step directions.",
                })

            # Deduplicate by game_id
            seen_ids = set()
            unique_recs = []
            for r in recs:
                if r["game_id"] not in seen_ids:
                    unique_recs.append(r)
                    seen_ids.add(r["game_id"])

            return unique_recs[:4] if unique_recs else list(cls.DEFAULT_RECOMMENDATIONS)
        except Exception:
            return list(cls.DEFAULT_RECOMMENDATIONS)
