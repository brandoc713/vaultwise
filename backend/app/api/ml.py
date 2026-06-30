from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import MLPredictRequest, MLPredictResult, MLStatus, MLTrainResult
from app.services.ml_classifier import load_model, model_path, predict_category, train_classifier

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.post("/train", response_model=MLTrainResult)
def train(db: Session = Depends(get_db)) -> MLTrainResult:
    result = train_classifier(db)
    return MLTrainResult(**result.__dict__)


@router.post("/predict", response_model=MLPredictResult)
def predict(payload: MLPredictRequest) -> MLPredictResult:
    category_id, confidence, version = predict_category(
        payload.description,
        payload.merchant,
        payload.amount,
        payload.direction.value,
    )
    return MLPredictResult(
        category_id=UUID(category_id) if category_id else None,
        confidence=confidence,
        model_version=version,
        source="scikit-learn" if version else "none",
    )


@router.get("/status", response_model=MLStatus)
def status() -> MLStatus:
    settings = get_settings()
    payload = load_model()
    return MLStatus(
        model_exists=model_path().exists(),
        model_version=payload["version"] if payload else None,
        min_training_rows=settings.ml_min_training_rows,
    )
