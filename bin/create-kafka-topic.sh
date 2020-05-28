cd engines/kafka_2.12-2.5.0
bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic sensors
sleep 60