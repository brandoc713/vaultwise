from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Transaction


@dataclass(frozen=True)
class TrainingResult:
    status: str
    model_version: str | None
    training_rows: int
    accuracy: float | None
    message: str


def model_path() -> Path:
    settings = get_settings()
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    return settings.models_dir / "category_classifier.joblib"


def _rows(db: Session) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(Transaction.category_id.isnot(None))
        .filter(Transaction.manual_override.is_(True))
        .all()
    )


def _features(rows: list[Transaction]) -> pd.DataFrame:
    return pd.DataFrame(
        [
        {
            "text": f"{row.merchant or ''} {row.description_redacted}",
            "amount": float(row.amount),
            "direction": row.direction.value,
        }
        for row in rows
        ]
    )


def train_classifier(db: Session) -> TrainingResult:
    settings = get_settings()
    rows = _rows(db)
    if len(rows) < settings.ml_min_training_rows:
        return TrainingResult(
            "insufficient_data",
            None,
            len(rows),
            None,
            f"Need at least {settings.ml_min_training_rows} corrected rows to train.",
        )

    labels = [str(row.category_id) for row in rows]
    if len(set(labels)) < 2:
        return TrainingResult("insufficient_data", None, len(rows), None, "Need at least two categories.")

    features = _features(rows)
    preprocessor = ColumnTransformer(
        [
            ("text", TfidfVectorizer(min_df=1), "text"),
            ("amount", StandardScaler(), ["amount"]),
            ("direction", OneHotEncoder(handle_unknown="ignore"), ["direction"]),
        ]
    )
    pipeline = Pipeline(
        [
            ("features", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )

    indices = np.arange(len(features))
    train_idx, test_idx = train_test_split(
        indices,
        test_size=0.34,
        random_state=42,
        stratify=labels if min(labels.count(label) for label in set(labels)) > 1 else None,
    )
    train_features = features.iloc[train_idx]
    test_features = features.iloc[test_idx]
    train_labels = [labels[index] for index in train_idx]
    test_labels = [labels[index] for index in test_idx]

    pipeline.fit(train_features, train_labels)
    predictions = pipeline.predict(test_features)
    accuracy = float(accuracy_score(test_labels, predictions))
    version = f"local-{uuid.uuid4().hex[:8]}"
    joblib.dump({"version": version, "pipeline": pipeline}, model_path())
    return TrainingResult("trained", version, len(rows), accuracy, "Model trained and saved locally.")


def load_model():
    path = model_path()
    if not path.exists():
        return None
    return joblib.load(path)


def predict_category(description: str, merchant: str | None, amount: float, direction: str) -> tuple[str | None, float, str | None]:
    payload = load_model()
    if not payload:
        return None, 0.0, None
    pipeline = payload["pipeline"]
    features = pd.DataFrame([{"text": f"{merchant or ''} {description}", "amount": amount, "direction": direction}])
    category_id = pipeline.predict(features)[0]
    confidence = 0.0
    if hasattr(pipeline.named_steps["classifier"], "predict_proba"):
        probabilities = pipeline.predict_proba(features)[0]
        confidence = float(max(probabilities))
    return category_id, confidence, payload["version"]
