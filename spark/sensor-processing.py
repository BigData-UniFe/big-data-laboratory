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
    if("sensor_data_count" in value[1]):
        value[1]["sensor_value"] = value[1]["sensor_value"] / \
            value[1]["sensor_data_count"]
        del value[1]["sensor_data_count"]
    else:
        value[1]["sensor_value"] = value[1]["sensor_value"] / 2

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
