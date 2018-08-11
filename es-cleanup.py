#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This AWS Lambda function allowed to delete the old Elasticsearch index
"""
import os
import json
import time
import boto3
import datetime

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import create_credential_resolver
from botocore.session import get_session
from botocore.vendored.requests import Session
import sys
if sys.version_info[0] == 3:
    from urllib.request import quote
else:
    from urllib import quote


class ES_Exception(Exception):
    """Exception capturing status_code from Client Request"""
    status_code = 0
    payload = ""

    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        Exception.__init__(self,
                           "ES_Exception: status_code={}, payload={}".format(
                               status_code, payload))


class ES_Cleanup(object):

    name = "lambda_es_cleanup"

    def __init__(self, event, context):
        """Main Class init

        Args:
            event (dict): AWS Cloudwatch Scheduled Event
            context (object): AWS running context
        """
        self.report = []
        self.event = event
        self.context = context

        self.cfg = {}
        self.cfg["es_endpoint"] = self.get_parameter("es_endpoint")
        self.cfg["index"] = self.get_parameter("index", "all").split(",")

        self.cfg["delete_after"] = int(self.get_parameter("delete_after", 15))
        self.cfg["es_max_retry"] = int(self.get_parameter("es_max_retry", 3))
        self.cfg["index_format"] = self.get_parameter(
            "index_format", "%Y.%m.%d")
        self.cfg["sns_alert"] = self.get_parameter("sns_alert", "")

        if not self.cfg["es_endpoint"]:
            raise Exception("[es_endpoint] OS variable is not set")

    def get_parameter(self, key_param, default_param=None):
        """helper function to retrieve specific configuration

        Args:
            key_param     (str): key_param to read from "event" or "environment" variable
            default_param (str): default value

        Returns:
            string: parameter value or None

        """
        return self.event.get(key_param, os.environ.get(key_param, default_param))

    def send_to_es(self, path, method="GET", payload={}):
        """Low-level POST data to Amazon Elasticsearch Service generating a Sigv4 signed request

        Args:
            path (str): path to send to ES
            method (str, optional): HTTP method default:GET
            payload (dict, optional): additional payload used during POST or PUT

        Returns:
            dict: json answer converted in dict

        Raises:
            #: Error during ES communication
            ES_Exception: Description
        """
        if not path.startswith("/"):
            path = "/" + path

        es_region = self.cfg["es_endpoint"].split(".")[1]

        # send to ES with exponential backoff
        retries = 0
        while retries < int(self.cfg["es_max_retry"]):
            if retries > 0:
                seconds = (2**retries) * .1
                # print('Waiting for %.1f seconds', seconds)
                time.sleep(seconds)

            req = AWSRequest(
                method=method,
                url="https://{}{}?pretty&format=json".format(
                    self.cfg["es_endpoint"], quote(path)),
                data=payload,
                headers={'Host': self.cfg["es_endpoint"]})
            credential_resolver = create_credential_resolver(get_session())
            credentials = credential_resolver.load_credentials()
            SigV4Auth(credentials, 'es', es_region).add_auth(req)

            try:
                preq = req.prepare()
                session = Session()
                res = session.send(preq)
                if res.status_code >= 200 and res.status_code <= 299:
                    # print("%s %s" % (res.status_code, res.content))
                    return json.loads(res.content)
                else:
                    raise ES_Exception(res.status_code, res._content)

            except ES_Exception as e:
                if (e.status_code >= 500) and (e.status_code <= 599):
                    retries += 1  # Candidate for retry
                else:
                    raise  # Stop retrying, re-raise exception

    def send_error(self, msg):
        """Send SNS error

        Args:
            msg (str): error string

        Returns:
            None
        """
        _msg = "[%s][%s] %s" % (self.name, self.cur_account, msg)
        print(_msg)
        if self.cfg["sns_alert"] != "":
            sns_region = self.cfg["sns_alert"].split(":")[4]
            sns = boto3.client("sns", region_name=sns_region)
            sns.publish(TopicArn=self.cfg["sns_alert"], Message=_msg)

    def delete_index(self, index_name):
        """ES DELETE specific index

        Args:
            index_name (str): Index name

        Returns:
            dict: ES answer
        """
        return self.send_to_es(index_name, "DELETE")

    def get_indices(self):
        """ES Get indices

        Returns:
            dict: ES answer
        """
        return self.send_to_es("/_cat/indices")


def lambda_handler(event, context):
    """Main Lambda function
    Args:
        event (dict): AWS Cloudwatch Scheduled Event
        context (object): AWS running context
    Returns:
        None
    """
    es = ES_Cleanup(event, context)
    # Index cutoff definition, remove older than this date
    earliest_to_keep = datetime.date.today() - datetime.timedelta(
        days=int(es.cfg["delete_after"]))
    for index in es.get_indices():

        if index["index"] == ".kibana":
            # ignore .kibana index
            continue

        idx_split = index["index"].rsplit("-",
            1 + es.cfg["index_format"].count("-"))
        idx_name = idx_split[0]
        idx_date = '-'.join(word for word in idx_split[1:])

        if idx_name in es.cfg["index"] or "all" in es.cfg["index"]:

            if idx_date <= earliest_to_keep.strftime(es.cfg["index_format"]):
                print("Deleting index: %s" % index["index"])
                es.delete_index(index["index"])


if __name__ == '__main__':
    event = {
        'account': '123456789012',
        'region': 'eu-west-1',
        'detail': {},
        'detail-type': 'Scheduled Event',
        'source': 'aws.events',
        'time': '1970-01-01T00:00:00Z',
        'id': 'cdc73f9d-aea9-11e3-9d5a-835b769c0d9c',
        'resources':
        ['arn:aws:events:us-east-1:123456789012:rule/my-schedule']
    }
    lambda_handler(event, "")
