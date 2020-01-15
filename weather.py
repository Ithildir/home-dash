#!/usr/bin/env python

import time
from bme280 import BME280
from smbus import SMBus
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

dbClient = InfluxDBClient(host='192.168.86.34', port=8086, username='enviro', password='exXtxtnhlcT5dOOFN4re', database='enviro')

class WeatherHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""

    class Meta:
        """Meta class stores time series helper configuration."""

        # The client should be an instance of InfluxDBClient.
        client = dbClient

        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = 'weather.{room}'

        # Defines all the fields in this time series.
        fields = ['humidity', 'pressure', 'temperature']

        # Defines all the tags for the series.
        tags = ['room']

        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 5

        # autocommit must be set to True when using bulk_size
        autocommit = True

while True:
    temperatureVal = bme280.get_temperature()
    pressureVal = bme280.get_pressure()
    humidityVal = bme280.get_humidity()

    WeatherHelper(room='living', humidity=humidityVal, pressure=pressureVal, temperature=temperatureVal)

    time.sleep(1)
