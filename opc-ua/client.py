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
