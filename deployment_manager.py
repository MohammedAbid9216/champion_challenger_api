import json
import os
import shutil

from app.core import config


STATE_FILE = "deployment_state.json"

MODEL_DIR = "app/models"
BACKUP_DIR = "app/models/backup"

CHAMPION_MODEL = os.path.join(
    MODEL_DIR,
    "champion_model.pkl"
)

CHALLENGER_MODEL = os.path.join(
    MODEL_DIR,
    "challenger_model.pkl"
)

BACKUP_MODEL = os.path.join(
    BACKUP_DIR,
    "previous_champion_model.pkl"
)


def load_state():

    if not os.path.exists(STATE_FILE):

        return {
            "current_champion": "champion",
            "challenger_status": "testing",
            "traffic_percent": 0.10
        }

    with open(STATE_FILE, "r") as file:

        return json.load(file)


def save_state(state):

    with open(STATE_FILE, "w") as file:

        json.dump(
            state,
            file,
            indent=4
        )


def show_status():

    state = load_state()

    print("\n================================")
    print(" Deployment Status")
    print("================================")

    print(
        f"Current Champion : "
        f"{state['current_champion']}"
    )

    print(
        f"Challenger Status: "
        f"{state['challenger_status']}"
    )

    print(
        f"Challenger Traffic: "
        f"{state['traffic_percent'] * 100:.0f}%"
    )


def promote_to_50():

    state = load_state()

    if state["challenger_status"] != "testing":

        print("\nCannot move to 50%.")

        return

    state["traffic_percent"] = 0.50

    config.CHALLENGER_TRAFFIC_PERCENT = 0.50

    save_state(state)

    print(
        "\nChallenger traffic increased "
        "from 10% to 50%."
    )


def promote_to_100():

    state = load_state()

    if state["challenger_status"] != "testing":

        print(
            "\nCannot promote Challenger."
        )

        print(
            "Challenger must be in testing state."
        )

        return

    if not os.path.exists(CHALLENGER_MODEL):

        print(
            "\nERROR: Challenger model not found."
        )

        return

    # ---------------------------------------
    # Backup current Champion
    # ---------------------------------------

    os.makedirs(
        BACKUP_DIR,
        exist_ok=True
    )

    shutil.copy2(
        CHAMPION_MODEL,
        BACKUP_MODEL
    )

    print(
        "\nPrevious Champion backed up."
    )

    # ---------------------------------------
    # Replace Champion with Challenger
    # ---------------------------------------

    shutil.copy2(
        CHALLENGER_MODEL,
        CHAMPION_MODEL
    )

    print(
        "Challenger model copied "
        "to Champion model."
    )

    # ---------------------------------------
    # Update deployment state
    # ---------------------------------------

    state["traffic_percent"] = 0.00
    state["current_champion"] = "champion"
    state["challenger_status"] = "promoted"

    config.CHALLENGER_TRAFFIC_PERCENT = 0.00

    save_state(state)

    print(
        "\n================================"
    )

    print(
        "Challenger PROMOTED!"
    )

    print(
        "New Champion is now the "
        "Challenger model."
    )

    print(
        "Traffic is now 100% Champion."
    )

    print(
        "================================"
    )


def rollback():

    if not os.path.exists(BACKUP_MODEL):

        print(
            "\nERROR: No Champion backup found."
        )

        return

    # ---------------------------------------
    # Restore previous Champion
    # ---------------------------------------

    shutil.copy2(
        BACKUP_MODEL,
        CHAMPION_MODEL
    )

    print(
        "\nPrevious Champion model restored."
    )

    # ---------------------------------------
    # Update state
    # ---------------------------------------

    state = load_state()

    state["traffic_percent"] = 0.00
    state["current_champion"] = "champion"
    state["challenger_status"] = "rolled_back"

    config.CHALLENGER_TRAFFIC_PERCENT = 0.00

    save_state(state)

    print(
        "ROLLBACK completed."
    )

    print(
        "Champion restored to production."
    )

def reset_experiment():

    state = load_state()

    state["traffic_percent"] = 0.10
    state["current_champion"] = "champion"
    state["challenger_status"] = "testing"

    config.CHALLENGER_TRAFFIC_PERCENT = 0.10

    save_state(state)

    print(
        "\n================================"
    )

    print(
        "Experiment RESET"
    )

    print(
        "Challenger is now in testing."
    )

    print(
        "Challenger traffic: 10%"
    )

    print(
        "================================"
    )
    
def main():

    print(
        "\n================================"
    )

    print(
        " Champion-Challenger Deployment"
    )

    print(
        "================================"
    )

    show_status()

    print("\nAvailable commands:")

    print(
        "1. 50       -> Challenger gets 50%"
    )

    print(
        "2. 100      -> Promote Challenger"
    )

    print(
        "3. rollback -> Restore previous Champion"
    )

    print(
        "4. status   -> Show deployment status"
    )
    print(
    "5. reset    -> Start new Challenger test"
    )

    command = input(
        "\nEnter command: "
    ).strip().lower()

    if command == "50":

        promote_to_50()

    elif command == "100":

        promote_to_100()

    elif command == "rollback":

        rollback()

    elif command == "status":

        show_status()
    elif command == "reset":

        reset_experiment()
    else:

        print(
            "\nUnknown command."
        )


if __name__ == "__main__":

    main()