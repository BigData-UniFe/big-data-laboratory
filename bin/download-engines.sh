[ ! -d "engines" ] && mkdir engines
cd engines

curl -O -k https://artifacts.elastic.co/downloads/logstash/logstash-7.7.0.tar.gz
tar -xvzf logstash-7.7.0.tar.gz
rm logstash-7.7.0.tar.gz

curl -O -k https://mirror.nohup.it/apache/kafka/2.5.0/kafka_2.12-2.5.0.tgz
tar -xvzf kafka_2.12-2.5.0.tgz
rm kafka_2.12-2.5.0.tgz

curl -O -k https://mirror.nohup.it/apache/spark/spark-2.4.5/spark-2.4.5-bin-hadoop2.7.tgz
tar -xvzf spark-2.4.5-bin-hadoop2.7.tgz
rm spark-2.4.5-bin-hadoop2.7.tgz

curl -O -k https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.7.0-linux-x86_64.tar.gz
tar -xvzf elasticsearch-7.7.0-linux-x86_64.tar.gz
rm elasticsearch-7.7.0-linux-x86_64.tar.gz

curl -O -k https://artifacts.elastic.co/downloads/kibana/kibana-7.7.0-linux-x86_64.tar.gz
tar -xvzf kibana-7.7.0-linux-x86_64.tar.gz
rm kibana-7.7.0-linux-x86_64.tar.gz

cd ..

sleep 60