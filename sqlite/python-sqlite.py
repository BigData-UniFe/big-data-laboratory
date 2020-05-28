import os
import time
from datetime import datetime
from random import uniform
from peewee import Model, CharField, FloatField, ForeignKeyField, SqliteDatabase

if not os.path.exists('sqlite/sensor.db'):
    os.mknod('sqlite/sensor.db')

database = SqliteDatabase('sqlite/sensor.db', pragmas={
    'journal_mode': 'wal',
    'cache_size': -1 * 64000,  # 64MB
    'foreign_keys': 1,
    'ignore_check_constraints': 0,
    'synchronous': 0})


class BaseModel(Model):
    class Meta:
        database = database


class Sensor(BaseModel):
    name = CharField()


class Measurement(BaseModel):
    sensor = ForeignKeyField(Sensor, backref='measurements')
    value = FloatField()
    timestamp = CharField()


def main():
    database.connect()
    database.create_tables([Sensor, Measurement])

    sensor, created = Sensor.get_or_create(id=1, defaults={"name": "Sensor1"})
    print(f"Sensor retrieved.") if created else print(f"Sensor created.")
    print(f"\tSensor id: {sensor.id}")
    print(f"\tSensor name: {sensor.name}")

    while(True):
        measurement = Measurement.create(
            sensor=sensor,
            value=uniform(0.0, 100.0),
            timestamp=datetime.now().isoformat()
        )
        print(
            f"\nNew measurement for sensor with id {sensor.id} and name {sensor.name} added.")
        print(f"\tMeasurement value: {measurement.value}")
        print(f"\tMeasurement timestamp: {measurement.timestamp}")
        measurement.save()
        time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Closing db and exiting...")
        database.close()
