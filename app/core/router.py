import random

from app.core import config


def choose_model():

    random_number = random.random()

    if random_number < config.CHALLENGER_TRAFFIC_PERCENT:
        return "challenger"

    return "champion"