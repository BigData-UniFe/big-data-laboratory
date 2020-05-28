cd engines/spark-2.4.5-bin-hadoop2.7
bin/spark-submit --packages org.apache.spark:spark-streaming-kafka_2.11:1.6.3 --jars ../../spark/elasticsearch-hadoop-7.7.0.jar ../../spark/sensor-processing.py