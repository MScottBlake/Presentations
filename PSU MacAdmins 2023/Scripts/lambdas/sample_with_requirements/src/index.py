"""Sample Lambda with Python Requirements"""
import json
import os

from aws_lambda_powertools import Logger

LOGGER = Logger(level=os.environ.get("LOG_LEVEL"), default="WARNING")


def lambda_handler(event, context) -> None:
    """This is the function called during lambda invocation."""

    LOGGER.debug(event)
    LOGGER.debug(context)

    body = event.get("body")
    data = json.loads(body)

    print(f"Received data from webhook:\n{data}")
    print("Processing...")
