#!/usr/bin/env python 
# tells environment to use python to run the script
from threading import Thread
from queue import Queue

from kafka import KafkaConsumer, KafkaProducer

from codecs import getencoder
from distutils.sysconfig import customize_compiler
import email
from multiprocessing import pool
import os
import sys
from unicodedata import name
from threading import Thread, Event
from queue import Queue
from json import dumps

from pytz import country_names
from multiprocessing import Queue
from helpers import login_required, apology
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Define the input and output topics
topic_name_input = "PolicyDraftList"
topic_name_output = "PolicyUWResult"

data = Queue()

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

consumer = KafkaConsumer(topic_name_input,
    bootstrap_servers=['pkc-epwny.eastus.azure.confluent.cloud:9092'],
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="$Default",
    sasl_mechanism="PLAIN",
    sasl_plain_username="IHO7XVPCJCCBZAYX",
    sasl_plain_password="UAwjmSIn5xuAL7HZmBjU4NGt0nLfXbyjtlVA7imgCdGBYFkog5kw0gc4e5MYmiUE",
    security_protocol="SASL_SSL",
    value_deserializer=lambda x: x.decode("utf-8"))

producer = KafkaProducer(
    bootstrap_servers=['pkc-epwny.eastus.azure.confluent.cloud:9092'], value_serializer=lambda x: bytes(x))

