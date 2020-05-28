import os
import time
from pprint import pprint
from pyfiglet import Figlet
from PyInquirer import prompt, print_json, style_from_dict, Token, Separator

choices = [
    'Download Engines (Elasticsearch, Kafka, Kibana, Logstash, Spark)',
    Separator(),
    'Start OPC UA Server',
    'Start OPC UA Client',
    'Start Sqlite Python',
    'Start ZooKeeper',
    'Start Kafka',
    'Start Spark',
    'Start Elasticsearch',
    'Start Logstash',
    'Start Kibana',
    Separator(),
    'Create Elasticsearch Index',
    'Create Kafka Topic',
    'List Kafka Topics',
    'Consume from Kafka Topic',
    Separator(),
    'Exit'
]


def handle_answer(answer):
    if('choice' in answer):
        if(answer['choice'] == choices[0]):
            os.system('gnome-terminal -q -t "Download Engines" -e "bash bin/download-engines.sh" --tab')
        if(answer['choice'] == choices[2]):
            os.system('gnome-terminal -q -t "OPC UA Server" -e "bash bin/start-opc-ua-server.sh" --tab')
        if(answer['choice'] == choices[3]):
            os.system('gnome-terminal -q -t "OPC UA Client" -e "bash bin/start-opc-ua-client.sh" --tab')
        if(answer['choice'] == choices[4]):
            os.system('gnome-terminal -q -t "Sqlite Python" -e "bash bin/start-sqlite-python.sh" --tab')
        if(answer['choice'] == choices[5]):
            os.system('gnome-terminal -q -t "ZooKeeper" -e "bash bin/start-zookeeper.sh" --tab')
        if(answer['choice'] == choices[6]):
            os.system('gnome-terminal -q -t "Kafka" -e "bash bin/start-kafka.sh" --tab')
        if(answer['choice'] == choices[7]):
            os.system('gnome-terminal -q -t "Spark" -e "bash bin/start-spark.sh" --tab')
        if(answer['choice'] == choices[8]):
            os.system('gnome-terminal -q -t "Elasticsearch" -e "bash bin/start-elasticsearch.sh" --tab')
        if(answer['choice'] == choices[9]):
            os.system('gnome-terminal -q -t "Logstash" -e "bash bin/start-logstash.sh" --tab')
        if(answer['choice'] == choices[10]):
            os.system('gnome-terminal -q -t "Kibana" -e "bash bin/start-kibana.sh" --tab')
        if(answer['choice'] == choices[12]):
            os.system('gnome-terminal -q -t "Create Elasticsearch Index" -e "bash bin/create-elasticsearch-index.sh" --tab')
        if(answer['choice'] == choices[13]):
            os.system('gnome-terminal -q -t "Create Kafka Topic" -e "bash bin/create-kafka-topic.sh" --tab')
        if(answer['choice'] == choices[14]):
            os.system('gnome-terminal -q -t "List Kafka Topics" -e "bash bin/list-kafka-topics.sh" --tab')
        if(answer['choice'] == choices[15]):
            os.system('gnome-terminal -q -t "Consume from Kafka Topic" -e "bash bin/consume-kafka-topic.sh" --tab')
        if(answer['choice'] == choices[17]):
            return False
    return True


f = Figlet(font='slant')
print(f.renderText('FIAV1'))

questions = [
    {
        'type': 'list',
        'name': 'choice',
        'message': 'What do you want to do?',
        'choices': choices,
        'default': 'None'
    },
]

go_on = True

try:
    while go_on:
        answer = prompt(questions)
        go_on = handle_answer(answer)
except:
    print("Exception caught, exiting...")