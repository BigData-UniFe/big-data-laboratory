# Big Data Laboratory

## Index

- [Prerequisites](#prerequisites)
	- [Java8](#java)
	- [Python](#python)
- [CLI](#cli)
- [Engines](#engines)
	- [Engines Root](#engines-root)
	- [Elasticsearch](#elasticsearch)
	- [Logstash](#logstash)
	- [Kibana](#kibana)
	- [Apache Kafka](#apache-kafka)
	- [Apache Spark](#apache-spark)
- [From Scratch](#from-scratch)
	- [OPC UA Client and Server](#opc-ua-client-and-server)
		- [Client](#client)
		- [Server](#server)
	- [Python Program for Sqlite DB](#python-program-for-sqlite-db)
		- [Program](#program)
	- [Logstash Pipeline](#logstash-pipeline)
	- [Apache Spark Program](#apache-spark-program)
		- [Program](#program-1)
- [Run the Big Data Pipeline](#run-the-big-data-pipeline)
	- [OPC UA](#opc-ua)
		- [Server](#server-1)
		- [Client](#client-1)
	- [Python SQLite](#python-sqlite)
	- [Apache Kafka](#apache-kafka-1)
		- [Apache ZooKeeper](#apache-zookeeper)
		- [Apache Kafka Server](#apache-kafka-server)
		- [Create Apache Kafka topic `sensors`](#create-apache-kafka-topic-sensors)
	- [Elasticsearch](#elasticsearch-1)
	- [Logstash](#logstash-1)
	- [Kibana](#kibana-1)
	- [Apache Spark](#apache-spark-1)

## Prerequisites

### Java

Check current version of Java

```bash
java -version
# output
# java version "1.8.0_241"
# Java(TM) SE Runtime Environment (build 1.8.0_241-b07)
# Java HotSpot(TM) 64-Bit Server VM (build 25.241-b07, mixed mode)
```

I nothing shows up, or the version is higher than 1.8.\*, Java 8 needs to be installed

```bash
sudo apt update
sudo apt install openjdk-8-jdk
```

In case Java version was wrong, use following command to switch the version to the needed one

```bash
sudo update-alternatives --config java
# choose the correct version -> java-8-openjdk
```

Then check the correct installation by running previous command

### Python

Check `curl` is installed

```bash
curl --version
# output
# curl 7.68.0 (x86_64-pc-linux-gnu) libcurl/7.68.0 OpenSSL/1.1.1f zlib/1.2.11 brotli/1.0.7 libidn2/2.2.0 libpsl/0.21.0 (+libidn2/2.2.0) libssh/0.9.3/openssl/zlib nghttp2/1.40.0 librtmp/2.3
# Release-Date: 2020-01-08
# Protocols: dict file ftp ftps gopher http https imap imaps ldap ldaps pop3 pop3s rtmp rtsp scp sftp smb smbs smtp smtps telnet tftp
# Features: AsynchDNS brotli GSS-API HTTP2 HTTPS-proxy IDN IPv6 Kerberos Largefile libz NTLM NTLM_WB PSL SPNEGO SSL TLS-SRP UnixSockets
```

If not, install it

```bash
sudo apt update
sudo apt install curl
```

Install `pyenv`, a python version manager, then restart the shell so path changes takes effect

```bash
curl https://pyenv.run | bash
exec $SHELL
```

Check that installation was successful

```bash
pyenv --version
# output
# pyenv 1.2.18
```

Install `python3.7.7` and set it as global version

```bash
pyenv install 3.7.7
pyenv global 3.7.7
```

### CLI

`cli.py` is a convenient python script to easily execute all the operations with few keyboard key press.

```bash
# Install the dependencies
pip install pyfiglet PyInquirer

# Check it out!
python cli.py
```

## Engines

All engines that will be used, will be downloaded and executed locally (no expensive installations on disk, since they can be easily deleted)

### Engines root

Create the `engines` directory and move in it

```bash
mkdir engines
cd engines
```

### Elasticsearch

Download Elasticsearch, un-tar it and remove the compressed file

```bash
curl -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.7.0-linux-x86_64.tar.gz
tar -xvzf elasticsearch-7.7.0-linux-x86_64.tar.gz
rm elasticsearch-7.7.0-linux-x86_64.tar.gz
```

### Logstash

Download Logstash, un-tar it and remove the compressed file

```bash
curl -O https://artifacts.elastic.co/downloads/logstash/logstash-7.7.0.tar.gz
tar -xvzf logstash-7.7.0.tar.gz
rm logstash-7.7.0.tar.gz
```

### Kibana

```bash
curl -O https://artifacts.elastic.co/downloads/kibana/kibana-7.7.0-linux-x86_64.tar.gz
tar -xvzf kibana-7.7.0-linux-x86_64.tar.gz
rm kibana-7.7.0-linux-x86_64.tar.gz
```

### Apache Kafka

Download Kafka, un-tar it and remove the compressed file

```bash
curl -O https://mirror.nohup.it/apache/kafka/2.5.0/kafka_2.12-2.5.0.tgz
tar -xvzf kafka_2.12-2.5.0.tgz
rm kafka_2.12-2.5.0.tgz
```

### Apache Spark

Download Spark, un-tar it and remove the compressed file

```bash
curl -O https://mirror.nohup.it/apache/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz
tar -xvzf spark-2.4.5-bin-hadoop2.7.tgz
rm spark-2.4.5-bin-hadoop2.7.tgz
```

## From Scratch

This section is useful to reproduce the project from scratch; if the github version is used, then this section can be skipped.

### OPC UA Client and Server

[opcua-asyncio](https://github.com/FreeOpcUa/opcua-asyncio) is an open source Python library that implements the OPC UA protocol.

[python-logstash](https://github.com/vklochan/python-logstash) is an open source Python library that allows to send data to Logstash.

```bash
# Check that dependencies are present and up-to-date
pip install --upgrade setuptools wheel
# Install OPC UA python library
pip install asyncua
# Install Logstash python library
pip install logstash-python
# Create a directory that will host the source code for OPC UA client and server
mkdir opc-ua
# Create client and server python files
touch opc-ua/client.py opc-ua/server.py
```

#### Client

Copy and paste the following code in `opc-ua/client.py`

```python
import asyncio
import logging
import json
import pytz
from datetime import datetime, timezone
from logstash import LogstashHandler
from asyncua import Client, ua, Node

# Setup logger with INFO level
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

# Urls and name for Server setup
_opc_ua_server = "opc.tcp://localhost:4840"
_opc_ua_namespace = "http://mechlav.opcua.io"

# Urls and name for Logstash
_logstash_host = "localhost"
_logstash_port = 50000
_logstash_logger = logging.getLogger('python-logstash-logger')
_logstash_logger.setLevel(logging.INFO)
_logstash_logger.addHandler(LogstashHandler(
	_logstash_host, _logstash_port, version=1))


class SubHandler(object):
	# The following method is used when a data change happens
	async def datachange_notification(self, node: Node, val, data: ua.DataChangeNotification):
		sensor_id = await(await (await node.get_parent()).get_child([f"{node.nodeid.NamespaceIndex}:id"])).read_value()
		sensor_name = await(await (await node.get_parent()).get_child([f"{node.nodeid.NamespaceIndex}:name"])).read_value()
		sensor_timestamp = data.monitored_item.Value.SourceTimestamp.replace(
			tzinfo=timezone.utc).astimezone(tz=None).strftime('%Y-%m-%dT%H:%M:%S.%f')

		_logger.info(f"Sensor id: {sensor_id}")
		_logger.info(f"Sensor name: {sensor_name}")
		_logger.info(f"Sensor value: {val}")
		_logger.info(f"Sensor timestamp: {sensor_timestamp}")

		formatted_data = {
			"sensor": {
				"sensor_id": sensor_id,
				"sensor_name": sensor_name,
				"sensor_value": val,
				"sensor_timestamp": sensor_timestamp
			}
		}

		_logstash_logger.info('OPC UA data', extra=formatted_data)


async def main():
	# Create client
	async with Client(_opc_ua_server) as client:
		# Retreive namespace index
		idx = await client.get_namespace_index(_opc_ua_namespace)

		# Retrieve Sensor0
		sensor0 = await client.nodes.objects.get_child([f"{idx}:Sensor0"])

		# Create the subscription to data changes
		handler = SubHandler()
		subscription = await client.create_subscription(500, handler)

		# Retrieve the variable to which subscribe and subscribe to data changes
		sensor0_value_var = await sensor0.get_child([f"{idx}:value"])
		handler = await subscription.subscribe_data_change(sensor0_value_var)

		# Infinite loop to keep on consuming data changes
		while True:
			await asyncio.sleep(1)

		# Automatically close subscriptions and connection to server


if __name__ == "__main__":
	try:
		asyncio.run(main())
	except (KeyboardInterrupt, SystemExit):
		_logger.info("Close client and exit...")
```

#### Server

Copy and paste the following code in `opc-ua/server.py`

```python
import asyncio
import copy
import logging
from asyncua import ua, Server
from random import uniform

# Setup logger with INFO level
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

# Urls and name for Server setup
_opc_ua_server = "opc.tcp://0.0.0.0:4840"
_opc_ua_server_name = "OPC UA Server"
_opc_ua_namespace = "http://mechlav.opcua.io"


async def main():
	# Create Server
	server = Server()
	await server.init()

	# Set server configuration
	server.set_endpoint(_opc_ua_server)
	server.set_server_name(_opc_ua_server_name)
	server.set_security_policy([
		ua.SecurityPolicyType.NoSecurity,
		ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
		ua.SecurityPolicyType.Basic256Sha256_Sign])

	# Set namespace
	idx = await server.register_namespace(_opc_ua_namespace)

	# Create Sensor object with two properties
	sensor = await server.nodes.base_object_type.add_object_type(idx, "Sensor")
	await (await sensor.add_variable(idx, "value", 0.0)).set_modelling_rule(True)

	# Populate the address space
	sensor0 = await server.nodes.objects.add_object(idx, "Sensor0", sensor)
	await (await sensor0.add_property(idx, "id", 0)).set_modelling_rule(True)
	await (await sensor0.add_property(idx, "name", "Sensor0")).set_modelling_rule(True)

	# Start Server
	async with server:
		# Retrieve Sensor0 value variable, in order to read/write it
		sensor0_value_var = await sensor0.get_child([f"{idx}:value"])

		while True:
			# Generate a random float between 0.0 and 100.0
			sensor0_value = uniform(0.0, 100.0)
			# Write the value to trigger data change
			await sensor0_value_var.write_value(sensor0_value)
			# Wait 5 seconds before triggering next event
			await asyncio.sleep(5)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except (KeyboardInterrupt, SystemExit):
		_logger.info("Close server and exit...")
```

### Python Program for Sqlite DB

[peewee](https://github.com/coleifer/peewee) is an open source Python library that allows to execute operations on a SQLite DB in an easy way (it is an [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping)).

```bash
# Install peewee
pip install peewee
# Create the program's directory
mkdir sqlite
# Create the python file that will host the python program
touch python-sqlite.py
```

#### Program

Copy and paste the following code in `sqlite/python-sqlite.py`

```python
import os
import time
from datetime import datetime
from random import uniform
from peewee import Model, CharField, FloatField, ForeignKeyField, SqliteDatabase

if not os.path.exists('sqlite/sensor.db'):
	os.mknod('sqlite/sensor.db')

database = SqliteDatabase('sqlite/sensor.db', pragmas={
	'journal_mode': 'wal',
	'cache_size': -1 * 64000,  # 64MB
	'foreign_keys': 1,
	'ignore_check_constraints': 0,
	'synchronous': 0})


class BaseModel(Model):
	class Meta:
		database = database


class Sensor(BaseModel):
	name = CharField()


class Measurement(BaseModel):
	sensor = ForeignKeyField(Sensor, backref='measurements')
	value = FloatField()
	timestamp = CharField()


def main():
	database.connect()
	database.create_tables([Sensor, Measurement])

	sensor, created = Sensor.get_or_create(id=1, defaults={"name": "Sensor1"})
	print(f"Sensor retrieved.") if created else print(f"Sensor created.")
	print(f"\tSensor id: {sensor.id}")
	print(f"\tSensor name: {sensor.name}")

	while(True):
		measurement = Measurement.create(
			sensor=sensor,
			value=uniform(0.0, 100.0),
			timestamp=datetime.now().isoformat()
		)
		print(
			f"\nNew measurement for sensor with id {sensor.id} and name {sensor.name} added.")
		print(f"\tMeasurement value: {measurement.value}")
		print(f"\tMeasurement timestamp: {measurement.timestamp}")
		measurement.save()
		time.sleep(5)


if __name__ == "__main__":
	try:
		main()
	except (KeyboardInterrupt, SystemExit):
		print("Closing db and exiting...")
		database.close()
```

### Logstash Pipeline

Logstash pipelines are used to collect incoming messages from specified inputs, maybe filter them and send them to specified output.

```bash
# Create a directory called logstash
mkdir logstash
# Create a file in logstash directory called sensor.cfg
touch logstash/sensors.cfg
# Insert the configuration for the pipeline
echo "" > logstash/sensors.cfg
```

Copy and paste the following code in `logstash/sensor.cfg`

```conf
input {
  # Input listen on TCP port 50000, using the json codec
  udp {
	id => "udp_input"
	port => 50000
	codec => json
  }
  jdbc {
	id => "jdbc_input"
	jdbc_driver_library => "../../logstash/sqlite-jdbc-3.30.1.jar"
	jdbc_driver_class => ""
	jdbc_user => ""
	jdbc_connection_string => "jdbc:sqlite:../../sqlite/sensor.db"
	parameters => { "sensor_id" => 1 }
	schedule => "*/1 * * * *"
	statement => "SELECT * from sensor as s JOIN measurement as m on s.id = m.sensor_id where s.id = :sensor_id"
  }
}

filter {
  mutate {
	id => "mutate_filter"
	# copy only important fields
	copy => {
	  "[name]" => "sensor_name"
	  "[timestamp]" => "sensor_timestamp"
	  "[value]" => "sensor_value"
	}
	copy => {
	  "[sensor][sensor_id]" => "sensor_id"
	  "[sensor][sensor_name]" => "sensor_name"
	  "[sensor][sensor_value]" => "sensor_value"
	  "[sensor][sensor_timestamp]" => "sensor_timestamp"
	}
	# remove unused fields
	remove_field => ["name", "timestamp", "value", "id", "logger_name", "level", "host", "stack_info", "type", "sensor", "path", "tags"]
  }
  date {
	id => "date_filter"
	match => [ "sensor_timestamp", "ISO8601" ]
	target => "sensor_timestamp"
  }
}

output {
  if [sensor_id] == 0 {
	# Output to Kafka
	kafka {
	  id => "kafka_output"
	  codec => json
	  topic_id => "sensors"
	  message_key => "%{message}"
	  bootstrap_servers => "http://localhost:9092"
	}
  }
  if [sensor_id] == 1 {
	# Output to Elasticsearch
	elasticsearch {
	  id => "elasticsearch_output"
	  hosts => ["localhost:9200"]
	  document_id => "%{sensor_name}_%{sensor_timestamp}"
	  index => "sensor"
	}
  }

  # Output to stdout
  stdout {
	id => "stdout_output"
  }
}
```

Above pipeline will need also the jdbc driver to connect to the database, so download it

```bash
# Move in logstash directory
cd logstash
# Download the driver
curl -O https://bitbucket.org/xerial/sqlite-jdbc/downloads/sqlite-jdbc-3.30.1.jar
# Exit from the directory
cd ..
```

### Apache Spark Program

[pyspark](https://github.com/apache/spark/tree/master/python) is an open source Python library that allows to create Spark programs that will be executed by Spark core to do the processing.

```bash
# Install Spark python library
pip install pyspark
# Create a directory that will host the source code for the Spark program
mkdir spark
# Create the Spark program file
touch spark/sensor-processing.py
```

#### Program

Copy and paste the following code in `spark/sensor-processing.py`

```python
from json import loads, dumps
from datetime import datetime
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


def reduce_callback(prev_value, curr_value):
	# Count the elements of the current stream
	if("sensor_data_count" in prev_value[1]):
		curr_value[1]["sensor_data_count"] = prev_value[1]["sensor_data_count"] + 1
	else:
		curr_value[1]["sensor_data_count"] = 2
	# Makes the sum of the sensor_value of the current stream entries
	curr_value[1]["sensor_value"] = prev_value[1]["sensor_value"] + \
		curr_value[1]["sensor_value"]
	return curr_value


def map_callback(value):
	# Add the processing timestamp
	value[1]["sensor_processing_timestamp"] = datetime.utcnow().isoformat()
	# Makes the average by dividing the sensor_value by the sensor_data_count
	value[1]["sensor_value"] = value[1]["sensor_value"] / \
		value[1]["sensor_data_count"]
	del value[1]["sensor_data_count"]

	# Add a doc_id used as id by Elasticsearch
	value[1]["doc_id"] = value[1]["sensor_name"] + value[1]["sensor_timestamp"]

	return (value[1]["doc_id"], dumps(value[1]))


# Set up the Spark context and set the log level to ERROR
sc = SparkContext(appName="SensorProcessing")
sc.setLogLevel("ERROR")
# Set up the streaming context, with batches every 20 seconds
ssc = StreamingContext(sc, 20)


def main():
	# Set up kafka parameters
	topics = ["sensors"]
	kafkaParams = {
		"bootstrap.servers": "localhost:9092",
		"group.id": "SensorGroup",
		"auto.offset.reset": "largest",
		"enable.auto.commit": "true"
	}

	# Create a direct stream to Kafka
	stream = KafkaUtils.createDirectStream(
		ssc, topics, kafkaParams=kafkaParams, valueDecoder=lambda val: loads(val.decode('utf-8')))

	# Use reduce function over the stream
	reduced_stream = stream.reduce(reduce_callback).map(map_callback)
	# Debug print
	reduced_stream.pprint()

	# Configuration for Elasticsearch
	es_write_conf = {
		"es.nodes": "localhost",
		"es.port": "9200",
		"es.resource": "sensor",
		"es.input.json": "yes",
		"es.mapping.id": "doc_id"
	}

	# Send each RDD in the current stream to Elasticsearch
	reduced_stream.foreachRDD(lambda rdd: rdd.saveAsNewAPIHadoopFile(
		path='-',
		outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
		keyClass="org.apache.hadoop.io.NullWritable",
		valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
		conf=es_write_conf))

	# Start the Streaming Context
	ssc.start()
	# Awaits the termination
	ssc.awaitTermination()


if __name__ == "__main__":
	try:
		main()
	except (KeyboardInterrupt, SystemExit):
		ssc.stop()
		print("End Spark processing and exit...")
```

Above program will need also es-hadoop driver to connect to Elasticsearch, so download it

```bash
# Move in spark directory
cd spark
# Download the driver
curl -O https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-hadoop/7.7.0/elasticsearch-hadoop-7.7.0.jar
# Exit from the directory
cd ..
```

## Run the Big Data Pipeline

### OPC UA

#### Server

```bash
# Open a new terminal window/tab

# Start OPC UA Server
python opc-ua/server.py
```

#### Client

```bash
# Open a new terminal window/tab

# Start OPC UA Client
python opc-ua/client.py
```

### Python SQLite

```bash
# Open a new terminal window/tab

# Start Python SQLite
python sqlite/python-sqlite.py
```

### Apache Kafka

#### Apache ZooKeeper

```bash
# Open a new terminal window/tab

# Move in Kafka directory
cd engines/kafka_2.12-2.5.0

# Start ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties
```

#### Apache Kafka Server

```bash
# Open a new terminal window/tab

# Move in Kafka directory
cd engines/kafka_2.12-2.5.0

# Start Kafka Server
bin/kafka-server-start.sh config/server.properties
```

#### Create Apache Kafka topic `sensors`

```bash
# Open a new terminal window/tab

# Move in Kafka directory
cd engines/kafka_2.12-2.5.0

# Create the topic 'sensors'
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic sensors

# OPTIONAL: verify that topic 'sensors' has been created by listing all topics
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
# -> sensors

# OPTIONAL: Start a consumer to track the messages sent to topic 'sensor'
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic sensors --from-beginning
# -> [<five_seconds_interval_message>]
```

### Elasticsearch

#### Server

```bash
# Open a new terminal window/tab

# Move in Elasticsearch directory
cd engines/elasticsearch-7.7.0

# Start Elasticsearch
bin/elasticsearch
```

#### Create Elasticsearch index `sensor`

```bash
# Create the index using the HTTP interface
curl -X PUT "localhost:9200/sensor?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings" : {
	"properties" : {
	  "sensor_id": { "type": "keyword" },
	  "sensor_name": { "type": "keyword" },
	  "sensor_value": { "type": "float" },
	  "sensor_timestamp": { "type": "date" },
	  "sensor_processing_timestamp": { "type": "date" },
	}
  }
}
'
```

### Logstash

```bash
# Open a new terminal window/tab

# Move in Logstash directory
cd engines/logstash

# Start Logstash specifing the pipeline
bin/logstash -f ../../logstash/sensor.cfg
```

### Kibana

```bash
# Open a new terminal window/tab

# Move in Kibana directory
cd engines/kibana-7.7.0-linux-x86_64
# Start Kibana
bin/kibana
```

### Apache Spark

```bash
# Open a new terminal window/tab

# Move in Spark directory
cd engines/spark-2.4.5-bin-hadoop2.7

# Submit the Spark program to Spark core
bin/spark-submit --packages org.apache.spark:spark-streaming-kafka_2.11:1.6.3 ../../spark/sensor-processing.py
```
