import json
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from json import loads


def main():
    # Set up the Spark context and set the log level to ERROR
    sc = SparkContext(appName="SensorProcessing")
    sc.setLogLevel("ERROR")

    # Set up the streaming context
    ssc = StreamingContext(sc, 20)

    # Set up kafka parameters
    topics = ["sensors"]
    kafkaParams = {
        "bootstrap.servers": "localhost:9092",
        "group.id": "SensorGroup",
        "auto.offset.reset": "largest",
        "enable.auto.commit": "false"
    }

    # Create a direct stream to Kafka, so it will pull
    stream = KafkaUtils.createDirectStream(
        ssc, topics, kafkaParams=kafkaParams, valueDecoder=lambda val: loads(val.decode('utf-8')))

    # Execute the processing
    stream.mapValues(lambda values: {"sensor_id": values['sensor']['sensor_id'],
                                     "sensor_value": values['sensor']['value'], "sensor_timestamp": values['sensor']['timestamp']}).pprint()

    # Start the Streaming Context
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("End Spark processing and exit...")
