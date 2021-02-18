#!/usr/bin/python3

import argparse
import sys
import time

from influxdb import InfluxDBClient
from sense_hat import SenseHat


"""InfluxDB"""
def create_influx_db_client(host, port, user, password, database, ssl):
    client = InfluxDBClient(host, port, user, password, database, ssl, ssl)
    ping = client.ping()
    if ping != 204:
        print("Cannot reach influxdb service, aborting....")
        sys.exit(-5)
    else:
        return client


def send_to_influx(room, house, data, influx_db_client):
    if data["temperature"] == 0 or data["pressure"] == 0 or data["humidity"] == 0:
        print("Faulty datapoint: "+ str(data))
    json_body = [
        {
            "measurement": "sensors",
            "tags": {"room": room, "house": house},
            "fields": {
                "temperature": data["temperature"],
                "pressure": data["pressure"],
                "humidity": data["humidity"],
            },
        }
    ]

    print("Inserting: " + str(json_body))

    success = influx_db_client.write_points(json_body)
    if success:
        print("Inserted successfully")
    else:
        print("Insertion failed")


"""SenseHat"""
def get_sense_hat():
    print("Retrieving SenseHat object...")
    return SenseHat()


def get_sensors(sense_hat, precision):
    data = {
        "temperature": round(sense_hat.get_temperature(), precision),
        "pressure": round(sense_hat.get_pressure(), precision),
        "humidity": round(sense_hat.get_humidity(), precision),
    }
    return data


"""Programmatic"""
def parse_args():
    parser = argparse.ArgumentParser(description="Stolen code to deal with args")
    parser.add_argument(
        "--host",
        type=str,
        required=False,
        default="localhost",
        help="Hostname/IP of the InfluxDB server. Default localhost",
    )
    parser.add_argument(
        "--port",
        type=int,
        required=False,
        default=8086,
        help="Port of InfluxDB http API. Default 8086",
    )
    parser.add_argument(
        "--ssl",
        type=bool,
        required=False,
        default=False,
        help="Use of SSl for InfluxDB http API. Default to False",
    )
    parser.add_argument(
        "--user",
        type=str,
        required=False,
        default="user",
        help="User to use for the InfluxDB connection. By default not needed",
    )
    parser.add_argument(
        "--password",
        type=str,
        required=False,
        default="password",
        help="User to use for the InfluxDB connection. By default not needed",
    )
    parser.add_argument(
        "--database",
        type=str,
        required=False,
        default="home",
        help="Database to use for the InfluxDB connection.",
    )
    parser.add_argument(
        "--house",
        type=str,
        required=False,
        default="My House",
        help="Name of the house/apartment to serve as an InfluxDB tag name. Optional, default My House",
    )
    parser.add_argument(
        "--room",
        type=str,
        required=True,
        help="Name of the room to serve as an InfluxDB tag name. Required",
    )
    parser.add_argument(
        "--precision",
        type=int,
        required=False,
        default="2",
        help="Decimal point round precision, e.g. with 3 the results will be 24.054. Default 2",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    print("Starting sense.py...")

    sense_hat = get_sense_hat()
    influx_db_client = create_influx_db_client(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        ssl=args.ssl,
    )

    # For initialization, the first time the values are retrieved, the sensor board returns incompatible points,
    # such as a pressure value of 0, in order to prevent these points to be inserted in the timeseries, we start by
    # retrieving these false values and discarding them
    sensors = get_sensors(sense_hat, precision=args.precision)
    time.sleep(5)

    while True:
        sensors = get_sensors(sense_hat, precision=args.precision)
        send_to_influx(
            room=args.room,
            house=args.house,
            data=sensors,
            influx_db_client=influx_db_client
        )
        time.sleep(30)
