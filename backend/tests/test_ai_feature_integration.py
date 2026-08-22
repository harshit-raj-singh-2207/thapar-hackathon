from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.domains.learning.schemas import TaskBreakdownRequest, TutorAskRequest
from app.domains.learning.task_service import TaskService
from app.domains.learning.tutor_service import TutorService
from app.main import app


def test_tutor_uses_smart_gateway_and_preserves_response_contract(db, monkeypatch):
    calls = []

    class FakeGateway:
        def __init__(self, gateway_db):
            assert gateway_db is db

        def explain_message(self, text, user_id=None, fallback=None, context=None):
            calls.append(
                {
                    "text": text,
                    "user_id": user_id,
                    "fallback": fallback(),
                    "context": context,
                }
            )
            return SimpleNamespace(text="A short gateway explanation.")

    monkeypatch.setattr("app.domains.learning.tutor_service.SmartAIGateway", FakeGateway)

    response = TutorService(db).ask_tutor(
        TutorAskRequest(question="Why is the sky blue?", topic="Science"),
        user_id="learner-1",
    )

    assert response.question == "Why is the sky blue?"
    assert response.reply == "A short gateway explanation."
    assert response.session_id
    assert len(calls) == 1
    assert calls[0]["text"] == "Why is the sky blue?"
    assert calls[0]["user_id"] == "learner-1"
    assert calls[0]["context"] == {"topic": "Science"}
    assert calls[0]["fallback"]


def test_tutor_provider_failure_uses_learning_fallback(db, monkeypatch):
    fallback_values = []

    class FailingGateway:
        def __init__(self, gateway_db):
            assert gateway_db is db

        def explain_message(self, text, user_id=None, fallback=None, context=None):
            del text, user_id, context
            fallback_text = fallback()
            fallback_values.append(fallback_text)
            return SimpleNamespace(text=fallback_text, source="local_fallback")

    monkeypatch.setattr("app.domains.learning.tutor_service.SmartAIGateway", FailingGateway)

    response = TutorService(db).ask_tutor(
        TutorAskRequest(question="Explain an unfamiliar concept", topic="General"),
        user_id="learner-1",
    )

    assert response.reply == fallback_values[0]
    assert response.reply
    assert response.session_id


def test_learning_tutor_route_contract_is_preserved(monkeypatch):
    class RouteGateway:
        def __init__(self, gateway_db):
            self.db = gateway_db

        def explain_message(self, text, user_id=None, fallback=None, context=None):
            del text, user_id, fallback, context
            return SimpleNamespace(text="A route-compatible explanation.")

    monkeypatch.setattr("app.domains.learning.tutor_service.SmartAIGateway", RouteGateway)

    response = TestClient(app).post(
        "/api/v1/learning/tutor/ask",
        json={"question": "Why do plants need light?", "topic": "Science"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["question"] == "Why do plants need light?"
    assert body["reply"] == "A route-compatible explanation."
    assert isinstance(body["session_id"], str)
    assert "simple_analogy" in body
    assert "follow_up_questions" in body
    assert "icon" in body


def test_learning_task_breakdown_remains_local(db):
    result = TaskService(db).breakdown_task_ai(TaskBreakdownRequest(task_title="brush teeth"))

    assert result.task_title == "brush teeth"
    assert result.steps
    assert result.total_estimated_duration_sec > 0
