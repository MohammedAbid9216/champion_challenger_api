from pydantic import BaseModel


class PredictRequest(BaseModel):
    age: float
    income: float
    credit_score: float
    existing_loans: float
    employment_years: float


class PredictResponse(BaseModel):
    request_id: str
    prediction: int
    probability: float
    model_used: str
    timestamp: str


class FeedbackRequest(BaseModel):
    request_id: str
    actual_outcome: int


class FeedbackResponse(BaseModel):
    status: str
    request_id: str