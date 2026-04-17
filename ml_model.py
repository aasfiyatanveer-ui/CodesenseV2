"""
ml_model.py
Loads the trained Random Forest model and makes predictions.
"""

import os
import numpy as np
import joblib

# Path to saved model files
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")

FEATURE_ORDER = [
    "lines_of_code",
    "num_functions",
    "num_loops",
    "num_conditionals",
    "num_classes",
    "avg_function_length",
    "comment_ratio",
    "naming_score",
    "import_count",
    "nested_depth",
]

# Grade → numeric quality score mapping
GRADE_SCORE = {
    "Excellent": 92,
    "Good": 75,
    "Average": 55,
    "Poor": 30,
}


def load_model():
    """Loads model and scaler from disk. Raises if not found."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "model.pkl not found. Run: python train_model.py first."
        )
    clf = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return clf, scaler


def predict_quality(features: dict) -> dict:
    """
    Takes a feature dict from feature_extractor and returns:
    - grade: Excellent / Good / Average / Poor
    - quality_score: 0-100 numeric score
    - confidence: model confidence (0.0 - 1.0)
    - grade_probabilities: all class probabilities
    """
    clf, scaler = load_model()

    # Build feature vector in correct order
    vector = np.array([[features.get(f, 0) for f in FEATURE_ORDER]])

    # Scale
    vector_scaled = scaler.transform(vector)

    # Predict
    grade = clf.predict(vector_scaled)[0]
    probabilities = clf.predict_proba(vector_scaled)[0]
    classes = clf.classes_

    # Confidence = probability of predicted class
    pred_idx = list(classes).index(grade)
    confidence = round(float(probabilities[pred_idx]), 3)

    # Base score from grade + small adjustment by confidence
    base_score = GRADE_SCORE[grade]
    quality_score = min(100, int(base_score + (confidence - 0.5) * 10))

    return {
        "grade": grade,
        "quality_score": quality_score,
        "confidence": confidence,
        "grade_probabilities": {
            cls: round(float(prob), 3)
            for cls, prob in zip(classes, probabilities)
        },
    }
