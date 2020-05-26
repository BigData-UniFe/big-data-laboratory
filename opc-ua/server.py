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
