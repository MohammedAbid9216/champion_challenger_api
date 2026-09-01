import mysql.connector

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from scipy.stats import chi2_contingency


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Abid@9216",
    "database": "champion_challenger_db"
}


SIGNIFICANCE_LEVEL = 0.05
MINIMUM_SAMPLE_SIZE = 20


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def get_results():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            model_used,
            prediction,
            actual_outcome
        FROM predictions
        WHERE actual_outcome IS NOT NULL
    """)

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results


def calculate_metrics(rows):
    y_true = [row["actual_outcome"] for row in rows]
    y_pred = [row["prediction"] for row in rows]

    return {
        "samples": len(rows),
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(
            y_true,
            y_pred,
            zero_division=0
        ),
        "recall": recall_score(
            y_true,
            y_pred,
            zero_division=0
        ),
        "f1": f1_score(
            y_true,
            y_pred,
            zero_division=0
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            y_pred
        )
    }


def statistical_test(champion_rows, challenger_rows):

    champion_correct = sum(
        row["prediction"] == row["actual_outcome"]
        for row in champion_rows
    )

    champion_wrong = (
        len(champion_rows) - champion_correct
    )

    challenger_correct = sum(
        row["prediction"] == row["actual_outcome"]
        for row in challenger_rows
    )

    challenger_wrong = (
        len(challenger_rows) - challenger_correct
    )

    contingency_table = [
        [champion_correct, champion_wrong],
        [challenger_correct, challenger_wrong]
    ]

    _, p_value, _, _ = chi2_contingency(
        contingency_table
    )

    return p_value


def print_metrics(name, metrics):

    print(f"\n{name}")
    print("-----------------------------------")

    print(f"Samples        : {metrics['samples']}")
    print(f"Accuracy       : {metrics['accuracy']:.4f}")
    print(f"Precision      : {metrics['precision']:.4f}")
    print(f"Recall         : {metrics['recall']:.4f}")
    print(f"F1 Score       : {metrics['f1']:.4f}")

    print("\nConfusion Matrix")
    print(metrics["confusion_matrix"])


def main():

    print("""
======================================
 Champion vs Challenger Experiment
======================================
""")

    results = get_results()

    champion_rows = [
        row for row in results
        if row["model_used"] == "champion"
    ]

    challenger_rows = [
        row for row in results
        if row["model_used"] == "challenger"
    ]

    print("Sample Size Check")
    print(f"Required minimum : {MINIMUM_SAMPLE_SIZE}")
    print(f"Champion         : {len(champion_rows)}")
    print(f"Challenger       : {len(challenger_rows)}")

    if len(champion_rows) < MINIMUM_SAMPLE_SIZE:
        print("\nWARNING: Champion sample size is too small.")

    if len(challenger_rows) < MINIMUM_SAMPLE_SIZE:
        print("\nWARNING: Challenger sample size is too small.")

    if not champion_rows or not challenger_rows:
        print("\nNot enough data for comparison.")
        return

    champion_metrics = calculate_metrics(
        champion_rows
    )

    challenger_metrics = calculate_metrics(
        challenger_rows
    )

    print_metrics(
        "Champion",
        champion_metrics
    )

    print_metrics(
        "Challenger",
        challenger_metrics
    )

    p_value = statistical_test(
        champion_rows,
        challenger_rows
    )

    print("""
Statistical Significance
""")

    print(f"p-value        : {p_value:.6f}")
    print(f"significance   : {SIGNIFICANCE_LEVEL}")

    if p_value < SIGNIFICANCE_LEVEL:
        print("Result         : STATISTICALLY SIGNIFICANT")
    else:
        print("Result         : NOT statistically significant")

    print("""
======================================
 Promotion Decision
======================================
""")

    champion_accuracy = champion_metrics["accuracy"]
    challenger_accuracy = challenger_metrics["accuracy"]

    if (
        challenger_accuracy > champion_accuracy
        and p_value < SIGNIFICANCE_LEVEL
    ):
        print("DECISION: PROMOTE CHALLENGER")
        print(
            "Challenger outperformed Champion "
            "with statistical significance."
        )

    else:
        print("DECISION: KEEP CHAMPION")

        if challenger_accuracy > champion_accuracy:
            print(
                "Challenger is better numerically, "
                "but improvement is not statistically significant."
            )
        else:
            print(
                "Challenger did not outperform Champion."
            )


if __name__ == "__main__":
    main()