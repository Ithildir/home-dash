FROM balenalib/raspberrypi3-python:3-build

RUN install_packages python3-numpy python3-pil python3-setuptools python3-influxdb
RUN pip install enviroplus smbus

WORKDIR /opt/app

COPY weather.py .

CMD ["python", "weather.py"]
