# Big Data Laboratory

## Index

- [Prerequisites]()
	- [Java](#java)
	- [Python](#python)
- [Engines](#engines)
	- [Convenient Script](#convenient-script)
	- [Engine Root](#engine-root)
	- [Logstash](#logstash)
	- [Apache Kafka](#apache-kafka)
	- [Apache Spark](#apache-spark)
- [From Scratch](#from-scratch)
	- [Logstash Pipelines](#logstash-pipelines)
	- [OPC UA Client and Server](#opc-ua-client-and-server)
		- [Client](#client)
		- [Server](#server)
	- [Apache Spark Program](#apache-spark-program)
		- [Program](#program)
- [Run the Big Data Pipeline](#run-the-big-data-pipeline)
	- [Logstash](#logstash-1)
	- [OPC UA](#opc-ua)
		- [Server](#server-1)
		- [Client](#client-1)
	- [Apache Kafka](#apache-kafka-1)
		- [Apache ZooKeeper](#apache-zookeeper)
		- [Apache Kafka Server](#apache-kafka-server)
		- [Create Apache Kafka topic `sensors`](#create-apache-kafka-topic-sensors)
	- [Apache Spark](#apache-spark-1)

## Prerequisites

### Java

Check current version of Java

```bash
java -version
# output
# openjdk version "11.0.2" 2019-01-15
# OpenJDK Runtime Environment (build 11.0.2+9-Ubuntu-3ubuntu118.04.3)
# OpenJDK 64-Bit Server VM (build 11.0.2+9-Ubuntu-3ubuntu118.04.3, mixed mode, sharing)
```

I nothing shows up, Java is not installed, so install it

```bash
sudo apt update
sudo apt install default-jdk
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

## Engines

All engines that will be used, will be downloaded and executed locally (no expensive installations on disk, since they can be easily deleted)

### Convenient script

Use the convenient script to do all the operations automatically:

```bash
bash download-engines.sh
```

Otherwise it is possible to do all the operations manually, starting from the next chapter.

### Engines root

Create the `engines` directory and move in it

```bash
mkdir engines
cd engines
```

### Logstash

Download Logstash, un-tar it and remove the compressed file

```bash
curl -O https://artifacts.elastic.co/downloads/logstash/logstash-7.7.0.tar.gz
tar -xvzf logstash-7.7.0.tar.gz
rm logstash-7.7.0.tar.gz
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

### Logstash Pipelines

Logstash pipelines in logstash are used to collect incoming messages from specified inputs, maybe filter them and send them to specified output.

```bash
# Create a directory called logstash-pipelines
mkdir logstash-pipelines
# Create a file in logstash-pipelines directory called sensor.cfg
touch logstash-pipelines/sensors.cfg
# Insert the configuration for the pipeline
echo "input {
  # Input listen on UDP port 50000, parsing messages with the json codec
  udp {
    port => 50000
    codec => json
  }
}

output {
  # Output to Kafka, in sensors topic
  kafka {
    codec => json
    topic_id => "sensors"
    bootstrap_servers => "http://localhost:9092"
  }

  # Output to stdout
  stdout { }
}" > logstash-pipelines/sensors.cfg
```

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
        sensor_id = await(await (await node.get_parent()).get_child([f"{node.nodeid.NamespaceIndex}:sensor_id"])).read_value()
        timestamp = data.monitored_item.Value.SourceTimestamp.isoformat()

        _logger.info(f"Sensor id: {sensor_id}")
        _logger.info(f"Sensor value: {val}")
        _logger.info(f"Sensor timestamp: {timestamp}")

        formatted_data = {
            "sensor": {
                "sensor_id": sensor_id,
                "value": val,
                "timestamp": data.monitored_item.Value.SourceTimestamp.isoformat()
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
    await (await sensor.add_property(idx, "sensor_id", 0)).set_modelling_rule(True)
    await (await sensor.add_property(idx, "value", 0.0)).set_modelling_rule(True)

    # Populate the address space
    sensor0 = await server.nodes.objects.add_object(idx, "Sensor0", sensor)

    # Start Server
    async with server:
        # Retrieve Sensor0 value variable, in order to read/write it
        sensor0_value_var = await sensor0.get_child([f"{idx}:value"])

        while True:
            # In order to trigger data change, a deep copy is needed
            sensor0_value = copy.copy(await sensor0_value_var.read_value())
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

### Apache Spark Program

[pyspark](https://github.com/apache/spark/tree/master/python) is an open source Python library that allows to create Spark programs that will be executed by Spark core to do the processing.

```bash
# Install Spark python library
pip install pyspark
# Create a directory that will host the source code for the Spark program
mkdir spark-programs
# Create the Spark program file
touch spark-programs/sensor-processing.py
```

#### Program

Copy and paste the following code in `spark-programs/sensor-processing.py`

```python
import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from json import loads


def main():
    # Set up the Spark context and the streaming context
    sc = SparkContext(appName="SensorProcessing")
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, 20)

    topics = ["sensors"]
    kafkaParams = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "SensorGroup",
        "auto.offset.reset": "largest",
        "enable.auto.commit": "false"
    }
    stream = KafkaUtils.createDirectStream(
        ssc, topics, kafkaParams=kafkaParams, valueDecoder=lambda val: loads(val.decode('utf-8')))

    stream.mapValues(lambda values: {"sensor_id": values['sensor']['sensor_id'],
                                     "sensor_value": values['sensor']['value'], "sensor_timestamp": values['sensor']['timestamp']}).pprint()

    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Close consumer and exit...")
```

## Run the Big Data Pipeline

### Logstash

```bash
# Open a new terminal window

# Move in Logstash directory
cd engines/logstash

# Start Logstash specifing the pipeline
bin/logstash -f ../../logstash-pipelines/sensor.cfg
```

### OPC UA

#### Server

```bash
# Open a new terminal window

# Start OPC UA Server
python opc-ua/server.py
```

#### Client

```bash
# Open a new terminal window

# Start OPC UA Client
python opc-ua/client.py
```

### Apache Kafka

#### Apache ZooKeeper

```bash
# Open a new terminal window

# Move in Kafka directory
cd engines/kafka_2.12-2.5.0

# Start ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties
```

#### Apache Kafka Server

```bash
# Open a new terminal window

# Move in Kafka directory
cd engines/kafka_2.12-2.5.0

# Start Kafka Server
bin/kafka-server-start.sh config/server.properties
```

#### Create Apache Kafka topic `sensors`

```bash
# Open a new terminal window

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

### Apache Spark

```bash
# Open a new terminal window

# Move in Spark directory
cd engines/spark-2.4.5-bin-hadoop2.7

# Submit the Spark program to Spark core
bin/spark-submit --packages org.apache.spark:spark-streaming-kafka_2.11:1.6.3 ../../spark-programs/sensor-processing.py
```
