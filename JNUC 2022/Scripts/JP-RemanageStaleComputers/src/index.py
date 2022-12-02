"""
Given a Jamf Pro Advanced Search name, generate a list of computer IDs
and add them to an AWS SQS queue. The Advanced Search should contain 
computers that have checked in within a designated timeframe and remanaged.
"""

import os
import json
import urllib
import requests
import logging
import boto3
from botocore.exceptions import ClientError
from http.client import HTTPConnection


def api_get_advancedcomputersearch_by_name(name):
    """
    Retrieve saved search data given a group name.

    :param name: String The name of a Jamf Pro Advanced Search
    :return: JSON Object containing information about the requests get
        action. If error, returns None.
    """

    auth_tuple = (API_USER, API_PASS)
    headers = {'Accept': 'application/json'}
    url = f'{API_URL}/JSSResource/advancedcomputersearches/name/{name}'

    LOGGER.debug(f'URL generated: {url}')

    try:
        r = requests.get(url, auth=auth_tuple, headers=headers)
    except requests.exceptions.RequestException as e:
        LOGGER.error(e)
        return None
    return r.json()


def get_computer_ids_from_json(json_result):
    """
    Parse the Jamf Pro API JSON output and return a list of computer IDs.

    :param json_result: JSON Object containing Jamf Pro API output
    :return: [String] containing Computer IDs. If error, returns None.
    """

    LOGGER.debug('Value of the \'json\' parameter: '+json.dumps(json_result))

    output = []
    for computer in json_result['advanced_computer_search']['computers']:
        output.append(int(computer['id']))

    return output


def get_ssm_secret_value(parameter_name):
    """
    Retreive a stored parameter from the AWS Systems Manager parameter store.

    :param paramater_name: String The Parameter Key to retreive
    :return: String containing the Parameter Value
    """

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter
    return SSM.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    ).get("Parameter").get("Value")


def send_to_sqs(sqs_queue_url, message):
    """
    Publish a message to SNS.

    :param sqs_queue_url: String URL of SQS Queue
    :param message: String The message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """

    try:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html#SQS.Client.send_message
        response = SQS.send_message(
            QueueUrl=sqs_queue_url,
            MessageBody=str(message)
        )
    except ClientError as e:
        LOGGER.error(e)
        return None
    return response


def lambda_handler(event, context):
    name = urllib.parse.quote(os.getenv("GROUP_NAME", ""))
    if not os.getenv("GROUP_NAME"):
        LOGGER.critical('Invalid environment variable: GROUP_NAME')
        return

    sqs_queue_url = os.getenv("SQS_QUEUE_URL")
    if not sqs_queue_url:
        LOGGER.critical('Invalid environment variable: SQS_QUEUE_URL')
        return

    json_result = api_get_advancedcomputersearch_by_name(name)
    if not json_result:
        LOGGER.error('Failed to retreive a result from the Jamf Pro API.')
        return

    computer_ids = get_computer_ids_from_json(json_result)
    if computer_ids is None:
        LOGGER.error('Failed to retreive Computer IDs from the returned JSON.')
        return
    elif computer_ids == []:
        LOGGER.info('No Computer IDs returned. The search appears to be empty.')
        return

    for computer_id in computer_ids:
        LOGGER.info(
            f'Sending Computer ID \'{computer_id}\' to the queue to be remanaged.')
        send_to_sqs(sqs_queue_url, computer_id)


SQS = boto3.client('sqs')
SSM = boto3.client('ssm')
STAGE = os.getenv("STAGE", "dev").lower()
DEBUG = os.getenv("DEBUG", "False").lower()

logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
LOGGER = logging.getLogger(__name__)
if DEBUG == 'true':
    LOGGER.setLevel(logging.DEBUG)
    HTTPConnection.debuglevel = 1
else:
    LOGGER.setLevel(logging.INFO)

API_URL = get_ssm_secret_value(f'/{STAGE}/JamfPro/Address')
API_USER = get_ssm_secret_value(
    f'/{STAGE}/JamfPro/Accts/RemanageComputers/Username')
API_PASS = get_ssm_secret_value(
    f'/{STAGE}/JamfPro/Accts/RemanageComputers/Password')
