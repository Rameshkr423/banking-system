import logging
import json
import sys


def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}'
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
