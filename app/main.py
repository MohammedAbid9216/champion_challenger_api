from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from uuid import uuid4

from app.core.schema import (
    PredictRequest,
    PredictResponse,
    FeedbackRequest,
    FeedbackResponse
)

from app.core.router import choose_model

from app.src.predictor import predict

from app.src.logger import (
    create_table,
    log_prediction,
    update_actual_outcome
)


app = FastAPI(
    title="Champion-Challenger ML API",
    description="A/B testing API for ML models",
    version="1.0.0"
)


# Create database table when application starts
create_table()


@app.get("/")
def home():
    return {
        "message": "Champion-Challenger API is running"
    }


@app.post("/predict", response_model=PredictResponse)
def make_prediction(request: PredictRequest):

    # 1. Generate unique request ID
    request_id = str(uuid4())

    # 2. Decide Champion or Challenger
    model_used = choose_model()

    # 3. Prepare features
    features = [
        request.age,
        request.income,
        request.credit_score,
        request.existing_loans,
        request.employment_years
    ]

    # 4. Run prediction
    prediction, probability = predict(
        features,
        model_used
    )

    # 5. Create timestamp
    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    # 6. Save prediction
    log_prediction(
        request_id=request_id,
        timestamp=timestamp,
        model_used=model_used,
        input_features=features,
        prediction=prediction,
        probability=probability
    )

    # 7. Send response
    return PredictResponse(
        request_id=request_id,
        prediction=prediction,
        probability=probability,
        model_used=model_used,
        timestamp=timestamp
    )


@app.post(
    "/feedback",
    response_model=FeedbackResponse
)
def feedback(request: FeedbackRequest):

    updated_rows = update_actual_outcome(
        request.request_id,
        request.actual_outcome
    )

    if updated_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="request_id not found"
        )

    return FeedbackResponse(
        status="updated",
        request_id=request.request_id
    )