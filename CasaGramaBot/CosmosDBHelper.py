#!/usr/local/bin python3.7
# -*- coding: utf-8 -*-
import logging
import os.path
from pydocumentdb import document_client

# Initialize Logging
# Output dir has to be set to system log path
output_dir = "$LOGPATH"
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler(os.path.join(output_dir, "logs.log")),
                        logging.StreamHandler()
                    ])


# Gets all documents from readings in hsludb
def get_last_entry(uri, key):

    client = document_client.DocumentClient(uri, {'masterKey': key})

    db_id = 'hsludb'
    db_query = "SELECT * FROM r WHERE r.id = '{0}'".format(db_id)
    db = list(client.QueryDatabases(db_query))[0]
    db_link = db['_self']

    coll_id = 'readings'
    coll_query = "SELECT * FROM r WHERE r.id = '{0}'".format(coll_id)
    coll = list(client.QueryCollections(db_link, coll_query))[0]
    coll_link = coll['_self']

    docs = client.ReadDocuments(coll_link)
    docs_list = list(docs)
    last_entry = docs_list[-1]
    LOG.info("last entry from db : [%s]", last_entry)

    return last_entry


def get_deviceid(last_entry):
    device_id = str(dict(last_entry)['deviceid'])
    return device_id


def get_timestamp(last_entry):
    timestamp = str(dict(last_entry)['cloud_timestamp'])
    return timestamp


def get_temperature(last_entry):
    last_temperature_value = str(dict(last_entry)['temperature'])
    return last_temperature_value


def get_humidity(last_entry):
    last_humidity_value = str(dict(last_entry)['humidity'])
    return last_humidity_value
