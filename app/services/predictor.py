import joblib
import numpy as np


# Load models once when this file is imported
champion_model = joblib.load(
    "app/models/champion_model.pkl"
)

challenger_model = joblib.load(
    "app/models/challenger_model.pkl"
)


def predict(features, model_name):
    """
    Run prediction using the selected model.
    """

    # Convert input features into 2D array
    input_data = np.array(features).reshape(1, -1)

    # Select model
    if model_name == "challenger":
        model = challenger_model
    else:
        model = champion_model

    # Prediction
    prediction = model.predict(input_data)[0]

    # Probability
    probability = model.predict_proba(input_data)[0][1]

    return int(prediction), float(probability)