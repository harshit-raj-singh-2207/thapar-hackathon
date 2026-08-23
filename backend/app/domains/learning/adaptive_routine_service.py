from sqlalchemy.orm import Session

from app.ai.gateway import SmartAIGateway
from app.domains.learning.schemas import AdaptiveRoutineRequest, AdaptiveRoutineResponse


class AdaptiveRoutineService:
    """Optional premium adaptation; routine CRUD never depends on this service."""

    def __init__(self, db: Session, gateway=None):
        self.gateway = gateway or SmartAIGateway(db)

    @staticmethod
    def local_steps(goal: str) -> list[str]:
        clean_goal = " ".join(goal.split()).strip()
        return [
            f"Get ready for {clean_goal}.",
            f"Start one small step of {clean_goal}.",
            "Take a short transition break if needed.",
            "Finish and mark the routine complete.",
        ]

    def create_plan(self, request: AdaptiveRoutineRequest, user_id: str) -> AdaptiveRoutineResponse:
        steps = self.local_steps(request.goal)
        fallback_text = " ".join(steps)
        prompt = (
            f"Create a supportive {request.days}-day routine plan for: {request.goal}. "
            f"Change reason: {request.change_reason or 'not provided'}. "
            "Use short, predictable steps and gentle transition warnings."
        )
        result = self.gateway.generate_text(
            prompt=prompt,
            feature="routine_adaptation",
            fallback=lambda: fallback_text,
            user_id=user_id,
            context={"days": request.days, "preferences": request.preferences},
            check_aac_template=False,
            system_prompt="Return a short, supportive routine plan. Avoid medical advice.",
        )
        return AdaptiveRoutineResponse(
            recommendation=result.text,
            suggested_steps=steps,
            days=request.days,
            source=result.source,
            budget_status=result.budget_status,
            fallback_reason=result.fallback_reason,
        )
