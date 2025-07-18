#!/bin/bash

# Set default values (can be overridden with flags)
USERNAME="tester"
PASSWORD="secret"
ORG="xv2_tests"
BUCKET="test_data"
INFLUXD_URL="http://localhost:8086"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --username) USERNAME="$2"; shift ;;
        --password) PASSWORD="$2"; shift ;;
        --org) ORG="$2"; shift ;;
        --bucket) BUCKET="$2"; shift ;;
        --url) INFLUXD_URL="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "Waiting for InfluxDB to be ready..."
sleep 10  # wait for influxdb service to be ready

echo "Setting up InfluxDB with:"
echo "  Username: $USERNAME"
echo "  Org:      $ORG"
echo "  Bucket:   $BUCKET"

# Run influx setup
influx setup --username "$USERNAME" \
             --password "$PASSWORD" \
             --org "$ORG" \
             --bucket "$BUCKET" \
             --retention 0 \
             --token "$(uuidgen)" \
             --force

echo "InfluxDB setup complete."
echo "You can log into the UI at $INFLUXD_URL with:"
echo "  Username: $USERNAME"
echo "  Password: $PASSWORD"
echo
echo "Your token can be found with:"
echo "  influx auth list --user $USERNAME"