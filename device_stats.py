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

# Get hostname as device ID
device_id = socket.gethostname()

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
    def get_snmp_value(command, default=0):
        result = os.popen(command).read().strip().split()
        return int(result[-1]) if result else default

    free_memory = get_snmp_value('snmpget -v 2c -c private 10.42.0.2 .1.3.6.1.4.1.17713.22.1.1.1.7.0')
    print("Free memory:", free_memory)

    cpu_utilisation = get_snmp_value('snmpget -v 2c -c private 10.42.0.2 .1.3.6.1.4.1.17713.22.1.1.1.6.0')
    print("CPU Utilisation:", cpu_utilisation)

    apclients = get_snmp_value('snmpget -v 2c -c private 10.42.0.2 .1.3.6.1.4.1.17713.22.1.1.1.14.0')
    print("AP Clients:", apclients)

    # Serial number extraction
    readserial = os.popen('snmpget -v 2c -c private 10.42.0.2 .1.3.6.1.4.1.17713.22.1.1.1.4.0').read()
    serial_matches = re.findall(r'"(.*?)"', readserial)
    serial_number = serial_matches[0] if serial_matches else "Unknown"
    print("Serial Number:", serial_number)

    # Interference and noise floor extraction
    interference = get_snmp_value('snmpget -v 2c -c private 10.42.0.2 .1.3.6.1.4.1.17713.22.1.2.1.17.0')
    print("Interference:", interference)

    noisefloor = get_snmp_value('snmpget -v 2c -c private 10.42.0.2 .1.3.6.1.4.1.17713.22.1.2.1.16.0')
    print("Noise Floor:", noisefloor)

    ping = run_ping_test()
    print("Ping to device:", ping)

    melbourne_tz = pytz.timezone("Australia/Melbourne")
    timestamp = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(melbourne_tz)

    point = Point("wifi_test") \
        .tag("serial_number", serial_number) \
        .tag("device", device_id) \
        .field("free_memory", free_memory) \
        .field("cpu_utilisation", cpu_utilisation) \
        .field("interference", interference) \
        .field("noisefloor", noisefloor) \
        .field("apclients", apclients) \
        .field("ping_device", ping if ping is not None else 0.0) \
        .time(timestamp)

    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Logged data at {timestamp}")

if __name__ == "__main__":
    while True:
        log_data()
        time.sleep(60)
