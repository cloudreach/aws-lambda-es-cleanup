#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This AWS Lambda function allowed to delete the old Elasticsearch index
"""
import re
import os
import json
import time
import datetime
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import create_credential_resolver
from botocore.httpsession import URLLib3Session
from botocore.session import get_session
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
        self.cfg["index"] = self.get_parameter("index", ".*")
        self.cfg["skip_index"] = self.get_parameter("skip_index", ".kibana*")

        self.cfg["delete_after"] = int(self.get_parameter("delete_after", 15))
        self.cfg["es_max_retry"] = int(self.get_parameter("es_max_retry", 3))
        self.cfg["index_format"] = self.get_parameter(
            "index_format", "%Y.%m.%d")

        self.cfg["snapshot_enabled"] = bool(self.get_parameter("snapshot_enabled", False))
        self.cfg["snapshot_delete_after"] = int(self.get_parameter("snapshot_delete_after", 15))
        self.cfg["snapshot_repository"] = self.get_parameter("snapshot_repository", "es_snapshots")

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
                seconds = (2**retries) * .1
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

    def snapshot_index(self, index_name, snapshot_repository):
        """ES PUT specific index snapshot

        Args:
            index_name (str): Index name

        Returns:
            dict: ES answer
        """

        snapshot_payload = {
          "indices": index_name,
          "ignore_unavailable": True,
          "include_global_state": False
        }

        # Append a timestamp to deduplicate multiple snapshots for same index
        now = str(datetime.datetime.now().timestamp())
        snapshot_name = "{}_{}".format(index_name, now)

        # create snapshot
        snapshot = self.send_to_es("_snapshot/{}/{}".format(snapshot_repository, snapshot_name), method="PUT", payload=snapshot_payload)

        # Wait for snapshot to be sucessful
        retries = 0
        while retries < int(self.cfg["es_max_retry"]):
            if retries > 0:
                seconds = (5**retries) * .1
                time.sleep(seconds)
            snapshots = self.get_snapshot(snapshot_repository, snapshot_name)
            if snapshots["snapshots"][0]["state"] == "SUCCESS":
                break
        return snapshot


    def get_indices(self):
        """ES Get indices

        Returns:
            dict: ES answer
        """
        return self.send_to_es("/_cat/indices")

    def get_snapshots(self, snapshot_repository):
        """ES Get snapshots of a repository

        Returns:
            dict: ES answer
        """
        return self.send_to_es("/_snapshot/{}/_all".format(snapshot_repository))

    def get_snapshot(self, snapshot_repository, snapshot_name):
        """ES Get snapshot

        Returns:
            dict: ES answer
        """
        return self.send_to_es("/_snapshot/{}/{}".format(snapshot_repository, snapshot_name))

    def delete_snapshot(self, snapshot_repository, snapshot_name):
        """ES Get snapshot

        Returns:
            dict: ES answer
        """
        return self.send_to_es("/_snapshot/{}/{}".format(snapshot_repository, snapshot_name), method="DELETE")


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
        print("Found index: {}".format(index["index"]))
        if re.search(es.cfg["skip_index"], index["index"]):
            # ignore .kibana index
            continue

        idx_split = index["index"].rsplit("-",
            1 + es.cfg["index_format"].count("-"))
        idx_name = idx_split[0]
        idx_date = '-'.join(word for word in idx_split[1:])

        if re.search(es.cfg["index"], index["index"]):

            if idx_date <= earliest_to_keep.strftime(es.cfg["index_format"]):
                # Create snapshot named as the index if snapshots are enabled
                if es.cfg["snapshot_enabled"]:
                    print("Creating snapshot for index: {} in repository {}".format(index["index"], es.cfg["snapshot_repository"]))
                    es.snapshot_index(index["index"], es.cfg["snapshot_repository"])

                # Delete index
                print("Deleting index: {}".format(index["index"]))
                es.delete_index(index["index"])
            else:
                print("Keeping index: {}".format(index["index"]))
        else:
            print("Index '{}' name '{}' did not match pattern '{}'".format(index["index"], idx_name, es.cfg["index"]))

    if es.cfg["snapshot_enabled"]:
        # Snapshot cutoff definition, remove older than this date
        snapshot_earliest_to_keep = datetime.date.today() - datetime.timedelta(
            days=int(es.cfg["snapshot_delete_after"]))
        for snapshot in es.get_snapshots(es.cfg["snapshot_repository"])["snapshots"]:
            # split by "-", ignoring the timestamp part of the snapshot name:
            timestamp_pos=snapshot["snapshot"].rfind("_")
            timestamp_pos=timestamp_pos+1 if timestamp_pos >= 0 else len(snapshot["snapshot"])
            snapshot_split = snapshot["snapshot"][:timestamp_pos].rsplit("-",
                1 + es.cfg["index_format"].count("-"))
            snapshot_name = snapshot_split[0]
            snapshot_date = '-'.join(word for word in snapshot_split[1:])

            if snapshot_date <= snapshot_earliest_to_keep.strftime(es.cfg["index_format"]):
                # Delete snapshot
                print("Deleting snapshot: {}".format(snapshot["snapshot"]))
                es.delete_snapshot(es.cfg["snapshot_repository"], snapshot["snapshot"])
            else:
                print("Keeping snapshot: {}".format(snapshot["snapshot"]))


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

