curl -X PUT "localhost:9200/sensor?pretty" -H 'Content-Type: application/json' -d'
{
  "mappings" : {
    "properties" : {
      "sensor_id": { "type": "keyword" },
      "sensor_name": { "type": "keyword" },
      "sensor_value": { "type": "float" },
      "sensor_timestamp": { "type": "date" },
      "sensor_processing_timestamp": { "type": "date" }
    }
  }
}
'

sleep 60