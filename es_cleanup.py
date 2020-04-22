#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This AWS Lambda function allowed to delete the old Elasticsearch index
"""
import datetime
import re
import sys
import time

import json
import os
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import create_credential_resolver
from botocore.httpsession import URLLib3Session
from botocore.session import get_session

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
        self.cfg["index"] = self.get_parameter("index", ".*")
        self.cfg["skip_index"] = self.get_parameter("skip_index", ".kibana*")

        self.cfg["delete_after"] = int(self.get_parameter("delete_after", 15))
        self.cfg["es_max_retry"] = int(self.get_parameter("es_max_retry", 3))
        self.cfg["index_format"] = self.get_parameter(
            "index_format", "%Y.%m.%d")

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

        headers = {
            "Host": self.cfg["es_endpoint"],
            "Content-Type": "application/json"
        }

        # send to ES with exponential backoff
        retries = 0
        while retries < int(self.cfg["es_max_retry"]):
            if retries > 0:
                seconds = (2 ** retries) * .1
                time.sleep(seconds)

            req = AWSRequest(
                method=method,
                url="https://{}{}".format(
                    self.cfg["es_endpoint"], quote(path)),
                data=json.dumps(payload),
                params={"format": "json"},
                headers=headers)
            credential_resolver = create_credential_resolver(get_session())
            credentials = credential_resolver.load_credentials()
            SigV4Auth(credentials, 'es', es_region).add_auth(req)

            try:
                preq = req.prepare()
                session = URLLib3Session()
                res = session.send(preq)
                if res.status_code >= 200 and res.status_code <= 299:
                    return json.loads(res.content)
                else:
                    raise ES_Exception(res.status_code, res._content)

            except ES_Exception as e:
                if (e.status_code >= 500) and (e.status_code <= 599):
                    retries += 1  # Candidate for retry
                else:
                    raise  # Stop retrying, re-raise exception

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


class DeleteDecider(object):
    def __init__(self, delete_after, idx_format, idx_regex, skip_idx_regex, today):
        self.delete_after = delete_after
        self.idx_format = idx_format
        self.idx_regex = idx_regex
        self.skip_idx_regex = skip_idx_regex
        self.today = today

    def should_delete(self, index):
        idx_split = index["index"].rsplit("-", 1 + self.idx_format.count("-"))
        idx_date_str = '-'.join(word for word in idx_split[1:])
        idx_name = idx_split[0]

        if not re.search(self.idx_regex, index["index"]):
            return False, "index '{}' name '{}' did not match pattern '{}'".format(index["index"],
                                                                                   idx_name,
                                                                                   self.idx_regex)

        earliest_to_keep = self.today - datetime.timedelta(days=self.delete_after)
        if re.search(self.skip_idx_regex, index["index"]):
            return False, "index matches skip condition"

        try:
            idx_datetime = datetime.datetime.strptime(idx_date_str, self.idx_format)
            idx_date = idx_datetime.date()
        except ValueError:
            raise ValueError("Unable to parse index date {0} - "
                             "incorrect index date format set?".format(idx_date_str))

        if idx_date < earliest_to_keep:
            return True, "all conditions satisfied"

        return False, "deletion age of has not been reached. " \
                      "Oldest index kept: {0}, Index Date: {1}".format(earliest_to_keep, idx_date)


def lambda_handler(event, context):
    """Main Lambda function
    Args:
        event (dict): AWS Cloudwatch Scheduled Event
        context (object): AWS running context
    Returns:
        None
    """
    es = ES_Cleanup(event, context)
    decider = DeleteDecider(delete_after=int(es.cfg["delete_after"]),
                            idx_regex=es.cfg["index"],
                            idx_format=es.cfg["index_format"],
                            skip_idx_regex=es.cfg["skip_index"],
                            today=datetime.date.today())

    for index in es.get_indices():
        d, reason = decider.should_delete(index)
        if d:
            print("Deleting index: {}".format(index["index"]))
            es.delete_index(index["index"])
        else:
            print("Skipping or keeping index: {}. Reason: {}".format(index["index"], reason))


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
