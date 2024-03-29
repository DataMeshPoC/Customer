#!/usr/bin/env python3

import os
from random import randint
import datetime

from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
import traceback


def acked(err, msg):
	if err is not None:
		print('Failed to deliver message: {}'.format(err.str()))
	else:
		print('Produced to: {} [{}] @ {}'.format(msg.topic(), msg.partition(), msg.offset()))


def main(cus_id, email, term, ctype, name, desc, premiumpayment, premiumstructure):
	now = datetime.datetime.now()

	message = dict(
		ID=int(str(cus_id)+str(randint(0,1000))), # awful way of doing it! Should define a correct Unique ID
		CUSTOMEREMAIL=email,
		TERM=term,
		TYPE=ctype,
		NAME=name,
		DESCRIPTION=desc,
		CURRENCY='HKD',
		PREMIUMPAYMENT=premiumpayment,
		PREMIUMSTRUCTURE=premiumstructure,
		STATUS='Draft',
		BUYTIME=now.strftime("%Y-%m-%d %H:%M:%S")
	)

	sr = SchemaRegistryClient({
		"url": "https://psrc-9wjxm.southeastasia.azure.confluent.cloud",
		"basic.auth.user.info": "43EV26QTDLE26FWD:OFCaxYa3QQmoBU+TMpiKQrOFE43dRXVCy8iR0YsjTZf9NILxzSYcMpXy/d3t1ymp"
	})

	path = os.path.realpath(os.path.dirname(__file__))
	with open(f"{path}/policy_schema.avsc") as f:
		schema_str = f.read()

	avro_serializer = AvroSerializer(sr, schema_str)

	producer = SerializingProducer({
			'bootstrap.servers': 'pkc-epwny.eastus.azure.confluent.cloud:9092',
			'security.protocol': 'SASL_SSL',
			'sasl.mechanisms': 'PLAIN',
			'sasl.username': 'G43OXASWELV233ID',
			'sasl.password': '6AqiTiagib5OMxCcusHqevMihIhFbJBQ5VUEvjHeD9jYySLv/DQgkHuRXkV+t4sV',
			'value.serializer': avro_serializer
		})

	producer.produce(topic='Policy', key='', value=message, on_delivery=acked)
	producer.poll(0)
	producer.flush()


if __name__ == '__main__':
	try:
		main()
	except Exception:
		print(traceback.format_exc())