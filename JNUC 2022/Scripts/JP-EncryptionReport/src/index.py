"""
Deletes computers via the Jamf Pro API based on given Computer IDs.
"""

import os
import logging
import urllib
import json
import xml.etree.ElementTree as ElementTree
import requests
import boto3
from botocore.exceptions import ClientError


def api_get_sites():
    """
    Get a dictionary listing each site from a Jamf Pro API.

    :return: Dictionary containing each site ID and Name. If error, returns None.
    """
    auth_tuple = (API_USER, API_PASS)
    url = f'{API_URL}/JSSResource/sites'
    LOGGER.debug(f'URL generated: {url}')

    try:
        xml = requests.get(url, auth=auth_tuple).content
        LOGGER.debug(f'XML Returned: {xml}')
    except requests.exceptions.RequestException as e:
        LOGGER.error(e)
        return None

    try:
        sites = ElementTree.fromstring(xml).findall('site')
        LOGGER.debug(f'Sites list: {sites}')
    except ElementTree.ParseError as e:
        LOGGER.error(e)
        return None

    output = {}
    for site in sites:
        output[site.find('id').text] = site.find('name').text

    LOGGER.debug(f'api_get_sites() output: {output}')
    return output


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
    except requests.exceptions.RequestException as e:
        LOGGER.error(e)
        return None

    return r.cookies


def get_encrypted_count_by_site_id(site_id):
    """
    Gets the number of encrypted devices within a given site.

    :param site_id: Integer The ID of a Jamf Pro site.
    :return: Integer containing the number of computers that are encrypted. If error, returns None.
    """
    change_site_xml = f'<advanced_computer_search><site><id>{site_id}</id></site></advanced_computer_search>'

    auth_tuple = (API_USER, API_PASS)
    name = urllib.parse.quote(os.getenv("GROUP_NAME", ""))

    url = f'{API_URL}/JSSResource/advancedcomputersearches/name/{name}'
    LOGGER.debug(f'URL generated: {url}')

    r = api_put_request(url, change_site_xml)
    cookies = dict(APBALANCEID=r.get('APBALANCEID'))

    try:
        xml = requests.get(url, auth=auth_tuple, cookies=cookies).content
    except requests.exceptions.RequestException as e:
        LOGGER.error(e)
        return None

    try:
        encrypted_count = ElementTree.fromstring(xml).findtext('computers/size')
    except ElementTree.ParseError as e:
        LOGGER.debug('Value of the \'xml\' parameter: '+str(xml))
        LOGGER.error(e)
        return None

    return encrypted_count


def get_ssm_secret_value(parameter_name):
    return SSM.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    ).get("Parameter").get("Value")


def send_to_sns(sns_topic_arl, subject, message):
    """
    Publish a message to SNS.

    :param sns_topic_arl: String ARL of SNS Topic
    :param subject: String The message subject
    :param message: String The message body
    :return: Dictionary containing information about the sent message. If
        error, returns None.
    """
    try:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html#SNS.Client.publish
        response = SNS.publish(
            TargetArn=sns_topic_arl,
            Message=json.dumps({'default': json.dumps(message), 'email': message}),
            Subject=subject,
            MessageStructure='json'
        )
    except ClientError as e:
        LOGGER.error(e)
        return None
    return response


def table_print(data, title_row):
    """
    :param data: list of dicts,
    :param title_row: e.g. [('name', 'Programming Language'), ('type', 'Language Type')]
    :return: String containing an ASCII table view of the given data.
    """
    max_widths = {}
    data_copy = [dict(title_row)] + list(data)
    for col in data_copy[0].keys():
        max_widths[col] = max([len(str(row[col])) for row in data_copy])
    cols_order = [tup[0] for tup in title_row]
    underline = '-+-'.join(['-' * max_widths[col] for col in cols_order])

    def custom_just(col, value):
        if type(value) == int:
            return str(value).rjust(max_widths[col])
        else:
            return value.ljust(max_widths[col])

    output = f'+-{underline}-+{os.linesep}'
    for row in data_copy:
        row_str = ' | '.join([custom_just(col, row[col]) for col in cols_order])
        output += f'| {row_str} |{os.linesep}'
        if data_copy.index(row) == 0:
            output += f'+-{underline}-+{os.linesep}'
    output += f'+-{underline}-+{os.linesep}'

    return output


def lambda_handler(event, context):
    name = urllib.parse.quote(os.getenv("GROUP_NAME", ""))
    if not os.getenv("GROUP_NAME"):
        LOGGER.critical('Invalid environment variable: GROUP_NAME')
        return

    sns_topic_arl = os.getenv("SNS_TOPIC_ARN")
    if not sns_topic_arl:
        LOGGER.critical('Invalid environment variable: SNS_TOPIC_ARN')
        return

    data = []
    sites = api_get_sites()
    for site_id, site_name in sorted(sites.items(), key=lambda x: x[1]):
        val = int(get_encrypted_count_by_site_id(site_id))
        data.append(dict(count=val, site=site_name))

    titles = [('count', 'Count'),
              ('site', 'Jamf Pro Site Name')]

    table = table_print(data, titles)

    print(table)
    send_to_sns(sns_topic_arl, 'Jamf Pro Encryption Report', table)

    # Set the site back to -1 to set it back to 'Full JSS"
    url = f'{API_URL}/JSSResource/advancedcomputersearches/name/{name}'
    change_site_xml = '<advanced_computer_search><site><id>-1</id></site></advanced_computer_search>'
    api_put_request(url, change_site_xml)


SNS = boto3.client('sns')
SSM = boto3.client('ssm')
STAGE = os.getenv("STAGE", "dev").lower()
DEBUG = os.getenv("DEBUG", "False").lower()

logging.basicConfig(format='%(levelname)s: %(asctime)s: %(message)s')
LOGGER = logging.getLogger(__name__)
if DEBUG == 'true':
    LOGGER.setLevel(logging.DEBUG)
else:
    LOGGER.setLevel(logging.INFO)

API_URL = get_ssm_secret_value(f'/{STAGE}/JamfPro/Address')
API_USER = get_ssm_secret_value(f'/{STAGE}/JamfPro/Accts/EncryptionReport/Username')
API_PASS = get_ssm_secret_value(f'/{STAGE}/JamfPro/Accts/EncryptionReport/Password')
