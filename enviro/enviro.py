import logging
import os
import time

import requests
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


def get_serial_number():
    with open("/proc/device-tree/serial-number", "r") as f:
        return f.read()


def send_to_luftdaten(pin, values):
    res = requests.post(
        "https://api.luftdaten.info/v1/push-sensor-data/",
        headers={
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "X-PIN": str(pin),
            "X-Sensor": sensor_uid,
        },
        json={
            "sensordatavalues": [
                {"value_type": key, "value": val} for key, val in values.items()
            ],
            "software_version": "enviro-plus 0.0.1",
        },
    )

    if not res.ok:
        logging.warn(res.text)


sensor_uid = f"raspi-{get_serial_number()}"

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

    send_to_luftdaten(1, {"P1": val_pm10, "P2": val_pm_2_5})

    time.sleep(1)
