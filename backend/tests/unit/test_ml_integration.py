"""Unit tests for Stage 1, Stage 2, Stage 3, and Stage 4 of PromiseOS Local ML Integration.

Tests:
1. ML service successfully loads the frozen model.
2. Correct prediction is returned for a clear commitment.
3. Correct prediction is returned for a clear non-commitment.
4. CommitmentAgent invokes ML after LLM extraction when ML_COMMITMENT_ENABLED is True.
5. Existing candidate is preserved regardless of ML label (no filtering, no dropping).
6. Missing/corrupt model fails safely without crashing discovery.
7. ML_COMMITMENT_ENABLED=False disables ML inference, leaves ml_label/ml_confidence as None, and does not invoke ML.
8. ML_COMMITMENT_ENABLED=False ensures model is not loaded unnecessarily.
9. Downstream compatibility: Evidence planning works seamlessly on candidates with or without ML fields.
"""

from pathlib import Path
import pytest
from app.agents.commitment_agent import CommitmentAgent, commitment_agent
from app.agents.evidence_planner import evidence_planner
from app.core.config import settings
from app.services.ml_service import (
    MLCommitmentService,
    MLPredictionResult,
    ml_commitment_service,
)


def test_ml_service_loads_frozen_model():
    """Verify that MLCommitmentService loads and caches the frozen joblib model."""
    service = MLCommitmentService()
    model = service.get_model()
    assert model is not None, "Failed to load frozen model artifact"

    # Verify in-memory caching (same instance returned without reloading)
    model_cached = service.get_model()
    assert model is model_cached


def test_ml_service_predict_clear_commitment():
    """Verify that clear commitment statements are classified as COMMITMENT with high probability."""
    service = MLCommitmentService()
    text = "I will email the client proposal before 5 PM tomorrow."
    result = service.predict(text)

    assert result.is_available is True
    assert result.label == "COMMITMENT"
    assert result.probability >= 0.50


def test_ml_service_predict_clear_non_commitment():
    """Verify that clear questions/requests are classified as NON_COMMITMENT with low probability."""
    service = MLCommitmentService()
    text = "Can you review this document when you get a chance?"
    result = service.predict(text)

    assert result.is_available is True
    assert result.label == "NON_COMMITMENT"
    assert result.probability < 0.50


@pytest.mark.asyncio
async def test_commitment_agent_invokes_ml_after_llm_extraction():
    """Verify that CommitmentAgent populates ml_label and ml_confidence when flag is enabled."""
    assert settings.ML_COMMITMENT_ENABLED is True

    input_text = "Rahul: I'll send the quotation tonight."
    commitments = await commitment_agent.extract_commitments(input_text)

    assert len(commitments) == 1
    c = commitments[0]
    assert c.person == "Rahul"
    assert c.action == "Send"
    assert "quotation" in c.object.lower()

    # ML results must be populated on the candidate
    assert c.ml_label is not None
    assert c.ml_confidence is not None
    assert c.ml_label == "COMMITMENT"
    assert c.ml_confidence >= 0.50


@pytest.mark.asyncio
async def test_existing_candidate_preserved_regardless_of_ml_label():
    """Verify candidates are NOT discarded even if ML classifies them as NON_COMMITMENT."""
    class MockNegativeMLService:
        def predict(self, text: str) -> MLPredictionResult:
            return MLPredictionResult(
                label="NON_COMMITMENT",
                probability=0.08,
                is_available=True,
            )

    custom_agent = CommitmentAgent(ml_service=MockNegativeMLService())
    input_text = "Rahul: I'll send the quotation tonight."
    commitments = await custom_agent.extract_commitments(input_text)

    # Candidate must be strictly preserved
    assert len(commitments) == 1
    c = commitments[0]
    assert c.person == "Rahul"
    assert c.action == "Send"
    assert c.object == "quotation"
    # ML output is attached, but original LLM confidence is unchanged
    assert c.ml_label == "NON_COMMITMENT"
    assert c.ml_confidence == 0.08
    assert c.confidence == 0.94  # Original LLM confidence preserved


@pytest.mark.asyncio
async def test_missing_or_corrupt_model_fails_safely():
    """Verify that a missing or corrupt model fails gracefully without crashing discovery."""
    missing_service = MLCommitmentService(model_path=Path("non_existent_model_path.joblib"))
    res = missing_service.predict("I will complete the task.")

    assert res.is_available is False
    assert res.label == "UNKNOWN"
    assert res.probability == 0.5

    # Run agent with the missing service
    agent_fallback = CommitmentAgent(ml_service=missing_service)
    commitments = await agent_fallback.extract_commitments("Rahul: I'll send the quotation tonight.")

    assert len(commitments) == 1
    assert commitments[0].ml_label == "UNKNOWN"
    assert commitments[0].ml_confidence == 0.5
    assert commitments[0].confidence == 0.94


@pytest.mark.asyncio
async def test_feature_flag_disabled_bypasses_ml(monkeypatch):
    """Verify that when ML_COMMITMENT_ENABLED is False, ML is NOT called and fields remain None."""
    monkeypatch.setattr(settings, "ML_COMMITMENT_ENABLED", False)

    class SpyMLService:
        def __init__(self):
            self.called = False

        def predict(self, text: str) -> MLPredictionResult:
            self.called = True
            return MLPredictionResult(label="COMMITMENT", probability=0.99, is_available=True)

    spy_service = SpyMLService()
    agent = CommitmentAgent(ml_service=spy_service)

    input_text = "Rahul: I'll send the quotation tonight."
    commitments = await agent.extract_commitments(input_text)

    # Verify ML was NOT invoked
    assert spy_service.called is False

    # Verify candidate was preserved normally with None ML fields
    assert len(commitments) == 1
    c = commitments[0]
    assert c.person == "Rahul"
    assert c.action == "Send"
    assert c.ml_label is None
    assert c.ml_confidence is None
    assert c.confidence == 0.94


def test_feature_flag_disabled_prevents_unnecessary_model_loading(monkeypatch):
    """Verify that MLCommitmentService does not load model from disk when disabled."""
    monkeypatch.setattr(settings, "ML_COMMITMENT_ENABLED", False)

    fresh_service = MLCommitmentService()
    assert fresh_service._model is None

    model = fresh_service.get_model()
    assert model is None
    assert fresh_service._model is None

    res = fresh_service.predict("I'll do something.")
    assert res.label == "DISABLED"
    assert res.is_available is False
    assert fresh_service._model is None


@pytest.mark.asyncio
async def test_downstream_compatibility_evidence_planning():
    """Verify that candidates with ML fields feed into EvidencePlanner normally."""
    input_text = "Rahul: I'll send the quotation tonight."
    commitments = await commitment_agent.extract_commitments(input_text)

    assert len(commitments) == 1
    c = commitments[0]

    # Plan evidence using the extracted candidate
    c_dict = c.model_dump()
    assert "ml_label" in c_dict
    assert "ml_confidence" in c_dict

    planned_evidence = await evidence_planner.plan_evidence(c_dict)
    assert len(planned_evidence) > 0
    assert any("quotation" in req.lower() for req in planned_evidence)
