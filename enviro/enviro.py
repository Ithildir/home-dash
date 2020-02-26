import os
import time

from bme280 import BME280
from enviroplus import gas
from influxdb import InfluxDBClient, SeriesHelper
from pms5003 import PMS5003, ReadTimeoutError
from smbus import SMBus

ROOM = os.getenv("ROOM")

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)
pms5003 = PMS5003()

influx_client = InfluxDBClient(
    host=os.getenv("INFLUX_HOST"),
    port=int(os.getenv("INFLUX_PORT", "8086")),
    username=os.getenv("INFLUX_USER", "enviro"),
    password=os.getenv("INFLUX_PASSWORD"),
    database=os.getenv("INFLUX_NAME", "enviro"),
)


class EnviroHelper(SeriesHelper):
    class Meta:
        client = influx_client
        series_name = "enviro"
        fields = [
            "humidity",
            "nh3",
            "oxidising",
            "pm1",
            "pm10",
            "pm2_5",
            "pressure",
            "reducing",
            "temperature",
        ]
        tags = ["room"]
        bulk_size = 5
        autocommit = True


next_sample_time = time.time()

while True:
    val_humidity = bme280.get_humidity()
    val_pressure = bme280.get_pressure()
    val_temperature = bme280.get_temperature()

    gas_readings = gas.read_all()

    try:
        pm_readings = pms5003.read()
    except ReadTimeoutError:
        pms5003 = PMS5003()

    val_pm1 = pm_readings.pm_ug_per_m3(1.0)
    val_pm_2_5 = pm_readings.pm_ug_per_m3(2.5)
    val_pm10 = pm_readings.pm_ug_per_m3(10)

    EnviroHelper(
        room=ROOM,
        humidity=val_humidity,
        nh3=gas_readings.nh3,
        oxidising=gas_readings.oxidising,
        pm1=val_pm1,
        pm10=val_pm10,
        pm2_5=val_pm_2_5,
        pressure=val_pressure,
        reducing=gas_readings.reducing,
        temperature=val_temperature,
    )

    next_sample_time += 1
    sleep_duration = max(next_sample_time - time.time(), 0)
    time.sleep(sleep_duration)
