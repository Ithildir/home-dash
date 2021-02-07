FROM sighmon/balena-enviro-plus:v1

WORKDIR /usr/src

RUN sudo pip3 install \
	influxdb-client \
	prometheus_client

COPY enviroplus_exporter/enviroplus_exporter.py enviroplus_exporter.py

CMD ["python3", "enviroplus_exporter.py", "--factor", "2.25", "--influxdb", "true"]
