'''
Follow these steps to configure the webhook in Slack:

  1. Navigate to https://<your-team-domain>.slack.com/services/new

  2. Search for and select "Incoming WebHooks".

  3. Choose the default channel where messages will be sent and click "Add Incoming WebHooks Integration".

  4. Copy the webhook URL from the setup instructions and use it in the next section.


Follow these steps to encrypt your Slack hook URL for use in this function:

  1. Create a KMS key - http://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html.

  2. Encrypt the event collector token using the AWS CLI.
     $ aws kms encrypt --key-id alias/<KMS key name> --plaintext "<SLACK_HOOK_URL>"

     Note: You must exclude the protocol from the URL (e.g. "hooks.slack.com/services/abc123").

  3. Copy the base-64 encoded, encrypted key (CiphertextBlob) to the ENCRYPTED_HOOK_URL variable.

  4. Give your function's role permission for the kms:Decrypt action.
     Example:

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Stmt1443036478000",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt"
            ],
            "Resource": [
                "<your KMS key ARN>"
            ]
        }
    ]
}
'''
from __future__ import print_function

import boto3
import json
import logging

from base64 import b64decode
from urllib2 import Request, urlopen, URLError, HTTPError


ENCRYPTED_HOOK_URL = "<encrypted_url_here>";  # Enter the base-64 encoded, encrypted key (CiphertextBlob)
SLACK_CHANNEL = '<slack_channel>'  # Enter the Slack channel to send a message to
AWS_REGION = 'us-east-1' # Enter the AWS Region your CloudWatch alarm is configured in.

HOOK_URL = "https://" + boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_HOOK_URL))['Plaintext']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Event: " + str(event))
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    alarm_name = message['AlarmName']
    #old_state = message['OldStateValue']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']
    alarm_url = "https://console.aws.amazon.com/cloudwatch/home?region=" + AWS_REGION + "#alarm:alarmFilter=inOk;name=" + alarm_name
    metric_name = message['Trigger']['MetricName']
    namespace = message['Trigger']['Namespace']

    if new_state is "ALARM":
        color = "danger"
    elif new_state is "OK":
        color = "good"
    else:
        color = "#439fe0"

    slack_message = {
        'channel': SLACK_CHANNEL,
        "attachments": [
        {
            "fallback": "Fallback text",
            "color": color,
            "author_name": "CloudWatch Alarm - Staging",
            "title": alarm_name,
            "title_link": alarm_url,
            "text": "<%s|%s> state is now %s: \n %s" % (alarm_url, alarm_name, new_state, reason),
            "fields": [
                {
                    "title": "MetricName",
                    "value": metric_name,
                    "short": true
                },
                {
                    "title": "Namespace",
                    "value": namespace,
                    "short": true
                }
            ]
        }
    }

    req = Request(HOOK_URL, json.dumps(slack_message))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
