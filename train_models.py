import os
import joblib
import random

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# --------------------------------------------------
# 1. Generate customer features
# --------------------------------------------------

def generate_features():

    age = random.randint(20, 60)
    income = random.randint(20000, 100000)
    credit_score = random.randint(500, 800)
    existing_loans = random.randint(0, 5)
    employment_years = random.randint(0, 20)

    return [
        age,
        income,
        credit_score,
        existing_loans,
        employment_years
    ]


# --------------------------------------------------
# 2. Generate ground-truth outcome
# --------------------------------------------------

def generate_actual_outcome(features):

    age, income, credit_score, existing_loans, employment_years = features

    score = 0

    # Credit score
    if credit_score >= 700:
        score += 3
    elif credit_score >= 600:
        score += 1
    else:
        score -= 2

    # Income
    if income >= 60000:
        score += 2
    elif income >= 40000:
        score += 1
    else:
        score -= 1

    # Existing loans
    if existing_loans <= 1:
        score += 2
    elif existing_loans >= 4:
        score -= 2

    # Employment
    if employment_years >= 5:
        score += 1
    elif employment_years == 0:
        score -= 1

    # Age
    if age >= 25 and age <= 55:
        score += 1

    if score >= 3:
        return 1

    return 0


# --------------------------------------------------
# 3. Create training dataset
# --------------------------------------------------

X = []
y = []

for _ in range(5000):

    features = generate_features()

    outcome = generate_actual_outcome(features)

    X.append(features)
    y.append(outcome)


# --------------------------------------------------
# 4. Split dataset
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# --------------------------------------------------
# 5. Champion
# --------------------------------------------------

champion = Pipeline([
    (
        "scaler",
        StandardScaler()
    ),
    (
        "model",
        LogisticRegression(
            random_state=42,
            max_iter=1000
        )
    )
])


# --------------------------------------------------
# 6. Challenger
# --------------------------------------------------

challenger = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    min_samples_split=5,
    random_state=42
)


# --------------------------------------------------
# 7. Train models
# --------------------------------------------------

print("\nTraining Champion...")

champion.fit(
    X_train,
    y_train
)

print("Training Challenger...")

challenger.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# 8. Evaluate models
# --------------------------------------------------

champion_predictions = champion.predict(X_test)

challenger_predictions = challenger.predict(X_test)


champion_accuracy = accuracy_score(
    y_test,
    champion_predictions
)

challenger_accuracy = accuracy_score(
    y_test,
    challenger_predictions
)


print("\n===================================")
print("       MODEL TRAINING RESULTS")
print("===================================")

print(
    f"Champion Accuracy   : {champion_accuracy:.4f}"
)

print(
    f"Challenger Accuracy : {challenger_accuracy:.4f}"
)


# --------------------------------------------------
# 9. Save models
# --------------------------------------------------

os.makedirs(
    "app/models",
    exist_ok=True
)


joblib.dump(
    champion,
    "app/models/champion_model.pkl"
)


joblib.dump(
    challenger,
    "app/models/challenger_model.pkl"
)


print("\nModels saved successfully!")

print(
    "Champion   -> app/models/champion_model.pkl"
)

print(
    "Challenger -> app/models/challenger_model.pkl"
)