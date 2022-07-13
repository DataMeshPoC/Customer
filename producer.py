#!/usr/bin/env python 
# tells environment to use python to run the script
from confluent_kafka import Producer, KafkaError
from confluent_avro import AvroKeyValueSerde, SchemaRegistry
from avro.io import DatumReader, BinaryDecoder
import avro.schema
from codecs import getencoder
from distutils.sysconfig import customize_compiler
import email
import os
import sys
from threading import Thread, Event
from queue import Queue
from json import dumps
from pytz import country_names
from multiprocessing import Queue, pool

# Define the input and output topics
topic_name_input = "PolicyDraftList"
topic_name_output = "PolicyUWResult"

# Define avro schema for parsing
schema = avro.schema.Parse(open("Client/policydraftlistschema").read())
reader = DatumReader(schema)

data = Queue()

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

# Configure the producer to push data to the next topic
producer1 = KafkaProducer(
    sasl_mechanism="PLAIN",
    sasl_plain_username="IHO7XVPCJCCBZAYX",
    sasl_plain_password="UAwjmSIn5xuAL7HZmBjU4NGt0nLfXbyjtlVA7imgCdGBYFkog5kw0gc4e5MYmiUE",
    security_protocol="SASL_SSL",
    bootstrap_servers=['pkc-epwny.eastus.azure.confluent.cloud:9092'], value_serializer=lambda x: bytes(x, encoding='latin1'))

def send_data_to_topic():
    while True:
        print("starting write thread")
        producer1.send(topic_name_output, value=data.get())
        producer1.flush()

# Use thread to write to topics
if __name__ == "__main__":
    write_thread = Thread(target=send_data_to_topic)
    write_thread.start()