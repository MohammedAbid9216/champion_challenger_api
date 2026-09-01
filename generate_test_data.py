import random
import requests
import time


API_URL = "http://127.0.0.1:8000"

TOTAL_REQUESTS = 500


def generate_features():
    """
    Generate realistic-looking synthetic customer data.
    """

    return {
        "age": random.randint(20, 60),
        "income": random.randint(20000, 100000),
        "credit_score": random.randint(500, 800),
        "existing_loans": random.randint(0, 5),
        "employment_years": random.randint(0, 20)
    }


def generate_actual_outcome(data):
    """
    Generate the SAME ground-truth outcome
    independently of either model.

    This represents the real-world outcome.
    """

    score = 0

    # Credit score
    if data["credit_score"] >= 700:
        score += 3
    elif data["credit_score"] >= 600:
        score += 1
    else:
        score -= 2

    # Income
    if data["income"] >= 60000:
        score += 2
    elif data["income"] >= 40000:
        score += 1
    else:
        score -= 1

    # Existing loans
    if data["existing_loans"] <= 1:
        score += 2
    elif data["existing_loans"] >= 4:
        score -= 2

    # Employment
    if data["employment_years"] >= 5:
        score += 1
    elif data["employment_years"] == 0:
        score -= 1

    # Convert business rule into actual outcome
    if score >= 3:
        return 1

    return 0


def main():

    champion_count = 0
    challenger_count = 0

    print("\nGenerating fair A/B test traffic...\n")

    for i in range(TOTAL_REQUESTS):

        # -----------------------------
        # 1. Generate customer features
        # -----------------------------

        data = generate_features()

        # -----------------------------
        # 2. Generate REAL outcome
        # -----------------------------

        actual_outcome = generate_actual_outcome(data)

        # -----------------------------
        # 3. Send prediction request
        # -----------------------------

        response = requests.post(
            f"{API_URL}/predict",
            json=data
        )

        if response.status_code != 200:

            print(
                f"Prediction failed "
                f"for request {i + 1}:",
                response.text
            )

            continue

        result = response.json()

        request_id = result["request_id"]

        model_used = result["model_used"]

        # -----------------------------
        # 4. Count traffic
        # -----------------------------

        if model_used == "champion":
            champion_count += 1
        else:
            challenger_count += 1

        # -----------------------------
        # 5. Send SAME actual outcome
        # -----------------------------

        feedback_response = requests.post(
            f"{API_URL}/feedback",
            json={
                "request_id": request_id,
                "actual_outcome": actual_outcome
            }
        )

        if feedback_response.status_code != 200:

            print(
                f"Feedback failed "
                f"for request {request_id}:",
                feedback_response.text
            )

        if (i + 1) % 50 == 0:

            print(
                f"Processed {i + 1}/{TOTAL_REQUESTS}"
            )

        time.sleep(0.02)

    print("\n===================================")
    print("Fair A/B Test Completed")
    print("===================================")

    print(
        f"Total Requests : {TOTAL_REQUESTS}"
    )

    print(
        f"Champion       : {champion_count}"
    )

    print(
        f"Challenger     : {challenger_count}"
    )

    print("\nExpected approximately:")

    print("Champion       : 90%")

    print("Challenger     : 10%")


if __name__ == "__main__":
    main()