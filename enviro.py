import time
import os
from bme280 import BME280
from influxdb import InfluxDBClient, SeriesHelper
from smbus import SMBus
from pms5003 import PMS5003, ReadTimeoutError

ROOM = os.getenv("ROOM")

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)
pms5003 = PMS5003()

influxClient = InfluxDBClient(
    host=os.getenv("INFLUX_HOST"),
    port=int(os.getenv("INFLUX_PORT", "8086")),
    username=os.getenv("INFLUX_USER", "enviro"),
    password=os.getenv("INFLUX_PASSWORD"),
    database=os.getenv("INFLUX_NAME", "enviro"),
)


class EnviroHelper(SeriesHelper):
    class Meta:
        client = influxClient
        series_name = "enviro"
        fields = ["pm1", "pm2_5", "pm10", "humidity", "pressure", "temperature"]
        tags = ["room"]
        bulk_size = 5
        autocommit = True


while True:
    valHumidity = bme280.get_humidity()
    valPressure = bme280.get_pressure()
    valTemperature = bme280.get_temperature()

    try:
        readings = pms5003.read()
    except ReadTimeoutError:
        pms5003 = PMS5003()

    valPM1 = readings.pm_ug_per_m3(1.0)
    valPM2_5 = readings.pm_ug_per_m3(2.5)
    valPM10 = readings.pm_ug_per_m3(10)

    EnviroHelper(
        room=ROOM,
        humidity=valHumidity,
        pm1=valPM1,
        pm10=valPM10,
        pm2_5=valPM2_5,
        pressure=valPressure,
        temperature=valTemperature,
    )

    time.sleep(1)
