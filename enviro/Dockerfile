FROM balenalib/raspberrypi3-python:3.7-latest-build

RUN pip3 install \
	enviroplus \
	requests \
	spidev \
	RPi.GPIO

RUN install_packages \
	libatlas-base-dev \
	python3-dev \
	python3-influxdb \
	python3-numpy \
	python3-pil \
	python3-setuptools \
	python3-smbus

WORKDIR /usr/src/app

COPY enviro.py .

CMD ["python", "enviro.py"]
