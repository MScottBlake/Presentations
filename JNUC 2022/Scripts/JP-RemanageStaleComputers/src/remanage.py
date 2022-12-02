"""
Accepts Jamf Pro Computer IDs from an AWS SQS queue and remanages them. 
The list of computers should include machines that have checked in 
within a designated timeframe and unmanaged.
"""
import os
import json
import urllib
import requests
import logging
import boto3
from botocore.exceptions import ClientError
from http.client import HTTPConnection

def send_to_microsoft_teams(SendToMicrosoftTeams_URL, computer_id):
    """
    Publish a message to SNS.

    :param sqs_queue_url: String URL of SQS Queue
    :param computer_id: String identifier for a Jamf Pro computer object
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """
    webhook_url = get_ssm_secret_value(f'/{STAGE}/JamfPro/Webhooks/WVUAppleAdmins/AWS-Automation')
    computer_name = get_computer_name_by_id(computer_id)
    teams_title = "Automated Remanagement"
    teams_text = f"**Remanaged the following machine:**\n\rMachine Name: {computer_name}\n\rComputer ID: {computer_id}\n\rURL: {API_URL}/computers.html?id={computer_id}"

    msg = {
        "webhook": {
            "url": webhook_url
        },
        "message": {
            "title": teams_title,
            "text": teams_text
        }
    }

    encoded_msg = json.dumps(msg)
    LOGGER.debug('Message being sent: {encoded_msg}')

    return send_to_sqs(SendToMicrosoftTeams_URL, encoded_msg)

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
            MessageBody=message
        )
    except ClientError as e:
        LOGGER.error(e)
        return None
    return response

def api_get_request(url):
    """
    Make a GET request to the Jamf Pro API.

    :param url: String The url to connect to.
    :return: JSON Object containing information about the request's get
        action. If error, returns None.
    """
    auth_tuple = (API_USER, API_PASS)
    headers = { 'Accept': 'application/json' }

    try:
        r = requests.get(url, auth=auth_tuple, headers=headers)
    except requests.exceptions.RequestException as e:
        LOGGER.error(e)
        return None
    return r.json()

def api_put_request(url, data):
    """
    Make a change to an existing Jamf Pro object via API.

    :param url: String The url to connect to.
    :param data: String XML containing the changed elements.
    :return: Dictionary containing each cookie from the PUT request. If error, returns None.
    """
    auth_tuple = (API_USER, API_PASS)

    try:
        r = requests.put(url, auth=auth_tuple, data=data)
        LOGGER.debug(str(r.content))
    
    except requests.exceptions.RequestException as e:
        LOGGER.error(e)
        return None

    return r.cookies

def get_computer_name_by_id(computer_id):
    """
    Get a computer record from a Jamf Pro API given the computer ID.
    
    :param computer_id: String identifier for a Jamf Pro computer object
    :return: Response Object containing information about the requests get
        action. If error, returns None.
    """
    url = f'{API_URL}/JSSResource/computers/id/{computer_id}/subset/General'
    LOGGER.debug(f'URL generated: {url}')
   
    computer_record = api_get_request(url)

    return computer_record["computer"]["general"]["name"]

def api_remanage_computer_by_id(computer_id):
    """
    Remanage a computer from the Jamf Pro API given the computer ID.

    :param computer_id: String identifier for a Jamf Pro computer object
    :return: Response Object containing information about the requests 
        action. If error, returns None.
    """
    url = f'{API_URL}/JSSResource/computers/id/{computer_id}'
    LOGGER.debug(f'URL generated: {url}')

    remanage_computer_xml = u'<?xml version="1.0" encoding="UTF-8"?><computer><general><remote_management><managed>true</managed><management_username>automated-remanagenment</management_username><management_password>Remanaged-Machine</management_password></remote_management></general></computer>'

    return api_put_request(url, remanage_computer_xml)

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

def lambda_handler(event, context):
    SendToMicrosoftTeams_URL = os.getenv("SendToMicrosoftTeams_URL")
    if not SendToMicrosoftTeams_URL:
        LOGGER.critical('Invalid environment variable: SendToMicrosoftTeams_URL')
        return

    for record in event['Records']:
        computer_id = record["body"]

        LOGGER.info(f'Remanaging Computer ID: {computer_id}')
        LOGGER.debug('Debug is enabled. Computer will not be Remanaged.')

        if DEBUG == 'false':
            # Only perform remanage if not in debug mode
            if api_remanage_computer_by_id(computer_id):
                send_to_microsoft_teams(SendToMicrosoftTeams_URL, computer_id)

SSM = boto3.client('ssm')
SQS = boto3.client('sqs')
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
API_USER = get_ssm_secret_value(f'/{STAGE}/JamfPro/Accts/RemanageComputers/Username')
API_PASS = get_ssm_secret_value(f'/{STAGE}/JamfPro/Accts/RemanageComputers/Password')