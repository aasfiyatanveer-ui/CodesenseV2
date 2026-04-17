"""
train_model.py
Trains a Random Forest Classifier on synthetic code quality data.
Run this once: python train_model.py
Saves: model.pkl and scaler.pkl
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ── Reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)
N = 600  # number of synthetic training samples

# ── Feature columns (must match feature_extractor.py output order) ───────────
FEATURE_NAMES = [
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

GRADES = ["Excellent", "Good", "Average", "Poor"]


def generate_synthetic_data():
    """
    Creates realistic synthetic training samples per grade.
    Rules mirror what good/bad student code actually looks like.
    """
    samples, labels = [], []

    # ── Excellent code ────────────────────────────────────────────────────────
    for _ in range(N // 4):
        samples.append([
            np.random.randint(30, 120),     # lines_of_code
            np.random.randint(3, 10),       # num_functions
            np.random.randint(1, 5),        # num_loops
            np.random.randint(1, 6),        # num_conditionals
            np.random.randint(0, 3),        # num_classes
            np.random.uniform(8, 20),       # avg_function_length
            np.random.uniform(0.15, 0.35),  # comment_ratio  (well commented)
            np.random.uniform(0.85, 1.0),   # naming_score   (snake_case)
            np.random.randint(1, 5),        # import_count
            np.random.randint(0, 2),        # nested_depth   (shallow)
        ])
        labels.append("Excellent")

    # ── Good code ─────────────────────────────────────────────────────────────
    for _ in range(N // 4):
        samples.append([
            np.random.randint(20, 100),
            np.random.randint(2, 8),
            np.random.randint(1, 6),
            np.random.randint(1, 8),
            np.random.randint(0, 2),
            np.random.uniform(10, 25),
            np.random.uniform(0.08, 0.20),
            np.random.uniform(0.70, 0.90),
            np.random.randint(1, 6),
            np.random.randint(1, 3),
        ])
        labels.append("Good")

    # ── Average code ─────────────────────────────────────────────────────────
    for _ in range(N // 4):
        samples.append([
            np.random.randint(10, 80),
            np.random.randint(0, 5),
            np.random.randint(2, 8),
            np.random.randint(2, 10),
            np.random.randint(0, 2),
            np.random.uniform(15, 40),
            np.random.uniform(0.02, 0.10),  # low comments
            np.random.uniform(0.50, 0.75),
            np.random.randint(0, 4),
            np.random.randint(2, 4),
        ])
        labels.append("Average")

    # ── Poor code ─────────────────────────────────────────────────────────────
    for _ in range(N // 4):
        samples.append([
            np.random.randint(5, 50),
            np.random.randint(0, 2),        # almost no functions
            np.random.randint(3, 10),
            np.random.randint(3, 12),
            np.random.randint(0, 1),
            np.random.uniform(20, 60),      # very long functions
            np.random.uniform(0.0, 0.05),   # no comments
            np.random.uniform(0.2, 0.55),   # bad naming
            np.random.randint(0, 3),
            np.random.randint(3, 6),        # deeply nested
        ])
        labels.append("Poor")

    return np.array(samples), np.array(labels)


def train():
    print("🔧 Generating synthetic training data...")
    X, y = generate_synthetic_data()

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train Random Forest
    print("🌲 Training Random Forest Classifier...")
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred))

    # Save model and scaler
    joblib.dump(clf, "model.pkl")
    joblib.dump(scaler, "scaler.pkl")
    print("✅ Saved: model.pkl and scaler.pkl")


if __name__ == "__main__":
    train()
