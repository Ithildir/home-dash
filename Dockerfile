FROM balenalib/raspberrypi3-python:3.7-latest-build

RUN install_packages python3-numpy python3-pil python3-setuptools python3-influxdb python3-rpi.gpio python3-smbus
RUN pip install enviroplus

WORKDIR /opt/app

COPY weather.py .

CMD ["python", "weather.py"]
