Champion–Challenger ML API

A FastAPI-based machine learning system for comparing a Champion model with a Challenger model through controlled traffic, prediction logging, feedback collection, statistical evaluation, and model promotion or rollback.

Overview
This project demonstrates a practical Champion–Challenger model evaluation workflow.

The existing model is treated as the Champion, while a new model is introduced as the Challenger.

Instead of immediately replacing the Champion, a small percentage of prediction traffic is sent to the Challenger. Predictions and actual outcomes are stored and later analyzed to compare model performance.

Architecture
Client
  │
  ▼
FastAPI
  │
  ▼
Traffic Router
  │
  ├───────────────┐
  ▼               ▼
Champion      Challenger
  │               │
  └───────┬───────┘
          ▼
     Prediction
          │
          ▼
     MySQL Logging
          │
          ▼
   Actual Outcome
          │
          ▼
   Result Analysis
          │
          ▼
 Statistical Testing
          │
     ┌────┴────┐
     ▼         ▼
   Keep      Promote
 Champion   Challenger
               │
               ▼
            Rollback
Models
Champion
The Champion model uses a Scikit-learn pipeline:

Input Features
      │
      ▼
StandardScaler
      │
      ▼
LogisticRegression
      │
      ▼
Prediction + Probability
Challenger
The Challenger model uses a Random Forest classifier:

Input Features
      │
      ▼
RandomForestClassifier
      │
      ▼
Prediction + Probability
Configuration:

200 estimators

max_depth = 8

min_samples_split = 5

random_state = 42

Both models receive the same input features so their results can be compared during the experiment.

Traffic Routing
The default traffic configuration is:

Champion      90%
Challenger    10%
Traffic selection is implemented in:

app/core/router.py
The Challenger traffic percentage is configured in:

app/core/config.py
The router randomly selects the model according to the configured Challenger traffic percentage.

API Endpoints
GET /
Returns the API status.

POST /predict
Generates a prediction using either the Champion or Challenger model.

Example request:

{
  "age": 35,
  "income": 60000,
  "credit_score": 700,
  "existing_loans": 1,
  "employment_years": 8
}
The response includes:

Request ID

Prediction

Probability

Model used

Timestamp

POST /feedback
Stores the actual outcome for a previous prediction.

Example:

{
  "request_id": "request-id",
  "actual_outcome": 1
}
Feedback allows the system to compare model predictions with actual outcomes.

Database Logging
The application uses MySQL to store prediction records.

The main table is:

predictions
Stored information includes:

Request ID

Model used

Prediction

Prediction probability

Actual outcome

Timestamp

Database credentials are loaded through environment variables.

Experiment Workflow
The complete experiment follows this workflow:

Train Models
     │
     ▼
Start FastAPI
     │
     ▼
10% Challenger Traffic
     │
     ▼
Collect Predictions
     │
     ▼
Collect Actual Outcomes
     │
     ▼
Calculate Metrics
     │
     ▼
Statistical Test
     │
     ▼
Increase Challenger Traffic
     │
     ▼
Evaluate Results
     │
     ▼
Promotion / Rollback
Workflow Steps
Train Champion and Challenger models.

Start the FastAPI prediction service.

Route a percentage of requests to the Challenger.

Store predictions and model information.

Collect actual outcomes through the feedback API.

Calculate classification metrics.

Perform statistical testing.

Increase Challenger traffic when required.

Promote the Challenger or keep the Champion.

Roll back to the previous Champion when required.

Model Evaluation
The analyze_results.py script evaluates completed predictions.

Metrics include:

Sample size

Accuracy

Precision

Recall

F1 Score

Confusion Matrix

Statistical test p-value

The configured significance level is:

0.05
The minimum configured sample size is:

20
The statistical analysis uses a chi-square test on correct and incorrect prediction counts.

Local Experiment Result
A local synthetic-data experiment was performed to test the Champion–Challenger workflow.

The analysis produced:

Model	Samples	Accuracy	Precision	Recall	F1 Score
Champion	913	0.8894	0.8379	0.9722	0.9001
Challenger	91	0.9890	0.9778	1.0000	0.9888
Statistical test:

p-value = 0.004830
significance level = 0.05
The analysis script produced:

DECISION: PROMOTE CHALLENGER
These results are from a local synthetic-data experiment and should not be interpreted as production model performance.

Deployment Manager
The project includes a deployment manager for controlling experiment state and model promotion or rollback.

Check Status
python3 deployment_manager.py status
Increase Challenger Traffic to 50%
python3 deployment_manager.py 50
Promote Challenger to 100%
python3 deployment_manager.py 100
Rollback
python3 deployment_manager.py rollback
Reset Experiment
python3 deployment_manager.py reset
Before promotion, the current Champion model is backed up so that rollback can restore the previous model.

Test Data Generation
Synthetic test requests can be generated using:

python3 generate_test_data.py
The script:

Generates test input features.

Sends requests to /predict.

Records which model handled each request.

Generates the actual outcome.

Sends feedback to /feedback.

Reports the traffic distribution.

Project Structure
champion_challenger_api/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── router.py
│   │   └── schema.py
│   │
│   ├── models/
│   │   ├── champion_model.pkl
│   │   ├── challenger_model.pkl
│   │   └── backup/
│   │
│   ├── src/
│   │   ├── logger.py
│   │   └── predictor.py
│   │
│   └── main.py
│
├── analyze_results.py
├── deployment_manager.py
├── generate_test_data.py
├── train_models.py
├── requirements.txt
├── README.md
└── .gitignore
Installation
Clone Repository
git clone https://github.com/MohammedAbid9216/champion_challenger_api.git
cd champion_challenger_api
Create Virtual Environment
python3 -m venv venv
Activate Virtual Environment
source venv/bin/activate
Install Dependencies
pip install -r requirements.txt
Environment Variables
Create a .env file in the project root:

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=champion_challenger_db
The .env file is excluded from Git to prevent credentials from being committed.

Train Models
Train the Champion and Challenger models:

python3 train_models.py
The trained models are saved locally as:

app/models/champion_model.pkl
app/models/challenger_model.pkl
Model artifacts are excluded from Git.

Start the API
Start the FastAPI application:

uvicorn app.main:app --reload
The API will be available at:

http://127.0.0.1:8000
Swagger documentation:

http://127.0.0.1:8000/docs
OpenAPI specification:

http://127.0.0.1:8000/openapi.json
Run the Experiment
Start the API:

uvicorn app.main:app --reload
In another terminal, generate test traffic:

python3 generate_test_data.py
After enough feedback has been collected, analyze the results:

python3 analyze_results.py
Technologies Used
Python

FastAPI

Uvicorn

Scikit-learn

NumPy

SciPy

MySQL

mysql-connector-python

Joblib

Python-dotenv

Requests

Security
Sensitive configuration is loaded through environment variables.

The following files and directories are excluded from Git:

.env
*.pkl
*.log
logs/
deployment_state.json
app/models/backup/
Never commit:

Database passwords

API keys

Access tokens

Other sensitive credentials

Limitations
This project is designed as an ML experimentation and learning project.

Current limitations include:

Training and test data are synthetic.

Models are stored as local .pkl files.

Deployment state is managed locally.

The statistical test is a simplified implementation.

The deployment manager demonstrates promotion and rollback logic rather than a complete production deployment platform.

Traffic configuration changes made by the deployment manager are not automatically synchronized with an already-running FastAPI process.

Local experiment results should not be treated as production performance.

Learning Outcomes
This project demonstrates practical experience with:

Machine Learning model comparison

Champion–Challenger architecture

Traffic splitting

FastAPI model serving

MySQL prediction logging

Feedback collection

Classification metrics

Confusion matrix analysis

Statistical testing

Model promotion

Model rollback

Environment variable management

Git and GitHub workflow