"""
Accepts a message from an AWS SQS queue and sends it to Microsoft
Teams via an Incomming Webhook.

The message is expected to be in the following form.
{
    "webhook": {
        "url": "https://full.url/for/your/webhook"
    },
    "message": {
        "title": "Message Title",
        "text": "Message Body"
    }
}
"""

import json
import logging
import requests


def lambda_handler(event, context):
    for record in event["Records"]:
        message_body = json.loads(record["body"])

        url = message_body["webhook"]["url"]
        msg = json.dumps(message_body["message"])

        try:
            requests.post(url, data=msg)
        except requests.exceptions.RequestException as e:
            LOGGER.error(e)
            return None


logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
