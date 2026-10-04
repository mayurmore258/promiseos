"""Local ML Commitment Classification Service.

Provides cached, safe in-memory inference using the frozen local model
`backend/ml/models/commitment_classifier.joblib`.

Guarantees:
- In-memory model caching (zero redundant disk I/O).
- Fail-safe execution (missing/corrupt model never crashes discovery).
- 100% local CPU execution (zero external API calls).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import joblib

from app.core.config import settings
from app.core.logging import logger

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
V1_ROLLBACK_PATH = BACKEND_ROOT / "ml" / "models" / "commitment_classifier.joblib"


def _resolve_production_model_path() -> Path:
    """Resolves production model path from settings or defaults to calibrated V2."""
    configured = getattr(settings, "ML_MODEL_PATH", "ml/models/commitment_classifier_v2_calibrated.joblib")
    p = Path(configured)
    if not p.is_absolute():
        p = BACKEND_ROOT / p
    return p


DEFAULT_MODEL_PATH = _resolve_production_model_path()


@dataclass
class MLPredictionResult:
    """Structured result of local ML commitment inference."""
    label: str  # "COMMITMENT", "NON_COMMITMENT", "UNKNOWN", or "DISABLED"
    probability: float  # Probability of COMMITMENT class (0.0 to 1.0)
    is_available: bool  # True if model inference succeeded, False on fallback


class MLCommitmentService:
    """Service wrapper for frozen commitment classification pipeline."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = Path(model_path) if model_path else _resolve_production_model_path()
        self._model = None
        self._load_attempted = False

    def get_model(self):
        """Loads and caches the frozen joblib pipeline in memory."""
        if not settings.ML_COMMITMENT_ENABLED:
            return None

        if self._model is not None:
            return self._model

        if self._load_attempted:
            return None

        self._load_attempted = True

        if not self.model_path.exists():
            logger.warning(
                f"ML model file not found at {self.model_path}. ML classification disabled.",
                extra={"operation": "ml_service_load", "path": str(self.model_path)},
            )
            return None

        try:
            self._model = joblib.load(self.model_path)
            logger.info(
                f"Frozen ML commitment classifier loaded successfully from {self.model_path}",
                extra={"operation": "ml_service_load"},
            )
            return self._model
        except Exception as e:
            logger.warning(
                f"Failed to load ML model artifact from {self.model_path}: {e}. ML classification disabled.",
                extra={"operation": "ml_service_load", "error": str(e)},
            )
            self._model = None
            return None

    def predict(self, text: Optional[str]) -> MLPredictionResult:
        """Predicts whether the given excerpt contains a commitment.
        
        Returns:
            MLPredictionResult with predicted label, probability, and availability.
        """
        if not settings.ML_COMMITMENT_ENABLED:
            return MLPredictionResult(
                label="DISABLED",
                probability=0.0,
                is_available=False,
            )

        if not text or not text.strip():
            return MLPredictionResult(
                label="NON_COMMITMENT",
                probability=0.0,
                is_available=True,
            )

        model = self.get_model()
        if model is None:
            return MLPredictionResult(
                label="UNKNOWN",
                probability=0.5,
                is_available=False,
            )

        try:
            clean_input = text.strip()
            pred_label = str(model.predict([clean_input])[0])
            probas = model.predict_proba([clean_input])[0]

            # Compute probability specifically for "COMMITMENT" class
            classes_list = list(model.classes_)
            if "COMMITMENT" in classes_list:
                comm_idx = classes_list.index("COMMITMENT")
                commitment_prob = float(probas[comm_idx])
            else:
                commitment_prob = float(probas[0])

            return MLPredictionResult(
                label=pred_label,
                probability=round(commitment_prob, 4),
                is_available=True,
            )
        except Exception as e:
            logger.warning(
                f"ML inference error on excerpt: {e}",
                extra={"operation": "ml_predict", "error": str(e)},
            )
            return MLPredictionResult(
                label="UNKNOWN",
                probability=0.5,
                is_available=False,
            )


# Global singleton instance for backend reuse
ml_commitment_service = MLCommitmentService()
