import mysql.connector
import json


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Abid@9216",
    "database": "champion_challenger_db"
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            request_id VARCHAR(36) PRIMARY KEY,
            timestamp DATETIME NOT NULL,
            model_used VARCHAR(20) NOT NULL,
            input_features JSON NOT NULL,
            prediction INT NOT NULL,
            probability FLOAT,
            actual_outcome INT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def log_prediction(
    request_id,
    timestamp,
    model_used,
    input_features,
    prediction,
    probability
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions (
            request_id,
            timestamp,
            model_used,
            input_features,
            prediction,
            probability,
            actual_outcome
        )
        VALUES (%s, %s, %s, %s, %s, %s, NULL)
    """, (
        request_id,
        timestamp,
        model_used,
        json.dumps(input_features),
        prediction,
        probability
    ))

    conn.commit()
    cursor.close()
    conn.close()


def update_actual_outcome(
    request_id,
    actual_outcome
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE predictions
        SET actual_outcome = %s
        WHERE request_id = %s
    """, (
        actual_outcome,
        request_id
    ))

    conn.commit()

    updated_rows = cursor.rowcount

    cursor.close()
    conn.close()

    return updated_rows