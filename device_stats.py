#!/usr/bin/env python3
import os
import re
import time
import socket
import subprocess
from datetime import datetime
import pytz
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def run_ping_test(target="10.42.0.2"):
    try:
        output = subprocess.check_output(f"ping -c 4 {target}", shell=True).decode()
        for line in output.split("\n"):
            if "avg" in line:
                return float(line.split('/')[4])
    except Exception as e:
        print("Error in ping test:", e)
    return None

def log_data():
    getmemory = os.popen('snmpget -v 2c -c private 10.42.0.2 .1.3.6.1.4.1.17713.22.1.1.1.7.0')
    readmemory = getmemory.read()
    free_memory = int(readmemory.strip().split()[-1])

    getserial = os.popen('snmpget -v 2c -c private 10.42.0.2 .1.3.6.1.4.1.17713.22.1.1.1.4.0')
    readserial = getserial.read()
    serial_number = re.findall(r'"(.*?)"', readserial)[0]

    ping = run_ping_test()

    melbourne_tz = pytz.timezone("Australia/Melbourne")
    timestamp = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(melbourne_tz)

    point = Point("wifi_test") \
        .tag("serial_number", serial_number) \
        .field("free_memory", free_memory) \
        .field("ping_device", ping if ping is not None else 0.0) \
        .time(timestamp)

    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Logged data at {timestamp}")

if __name__ == "__main__":
    while True:
        log_data()
        time.sleep(60)
