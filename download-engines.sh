mkdir engines
cd engines

curl -O https://artifacts.elastic.co/downloads/logstash/logstash-7.7.0.tar.gz
tar -xvzf logstash-7.7.0.tar.gz
rm logstash-7.7.0.tar.gz

curl -O https://mirror.nohup.it/apache/kafka/2.5.0/kafka_2.12-2.5.0.tgz
tar -xvzf kafka_2.12-2.5.0.tgz
rm kafka_2.12-2.5.0.tgz

curl -O https://mirror.nohup.it/apache/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz
tar -xvzf spark-2.4.5-bin-hadoop2.7.tgz
rm spark-2.4.5-bin-hadoop2.7.tgz

cd ..