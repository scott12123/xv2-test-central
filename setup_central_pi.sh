#!/bin/bash
set -e

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing InfluxDB..."
wget -q https://repos.influxdata.com/influxdb.key
gpg --dearmor < influxdb.key | sudo tee /usr/share/keyrings/influxdb-archive-keyring.gpg > /dev/null
echo "deb [signed-by=/usr/share/keyrings/influxdb-archive-keyring.gpg] https://repos.influxdata.com/debian bookworm stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt update
sudo apt install -y influxdb2
sudo systemctl enable influxdb
sudo systemctl start influxdb

echo "Installing Grafana..."
sudo apt install -y apt-transport-https software-properties-common wget
wget -q -O - https://apt.grafana.com/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/grafana-archive-keyrings.gpg
echo "deb [signed-by=/usr/share/keyrings/grafana-archive-keyrings.gpg] https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install -y grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

echo "Installing Python3 and pip (if not already installed)..."
sudo apt install -y python3 python3-pip

echo "Installing Flask for optional HTTP API integration..."
pip3 install flask

echo "Installation complete."
echo "Access Grafana at: http://<YOUR_PI_IP>:3000 (default login: admin / admin)"