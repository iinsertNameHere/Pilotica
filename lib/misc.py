import hashlib
import os
import re
from datetime import datetime, timedelta
from time import sleep

import requests


def get_uptime():
    start_time_str = os.environ.get("PILOTICA_START_TIME")
    if not start_time_str: return "0s"

    start_time = datetime.strptime(start_time_str, "%d-%m-%Y %H:%M")

    difference = datetime.now() - start_time
    seconds = difference.total_seconds()
    minutes = int(seconds / 60)
    hours = int(seconds / (60 * 60))
    days = int(seconds / (60 * 60 * 24))

    return (f"{days}d" if days > 0 else "") + (f"{hours}h" if hours > 0 else "") + (f"{minutes}m" if minutes > 0 else f"{int(seconds)}s") 

def generate_hwid(mac: str, hostname: str, cpu: str) -> str:
    """
    Generate a hardware ID based on provided parameters.

    Args:
        mac (str): MAC address of the device.
        hostname (str): Hostname of the device.
        cpu (str): CPU name.

    Returns:
        str: A hardware ID.
    """

    # Remove special characters and perform obfuscation
    clean_mac = re.sub(r'[^a-zA-Z0-9]', '', mac).upper()
    clean_hostname = re.sub(r'[^a-zA-Z0-9]', '', hostname).upper()
    clean_cpu = re.sub(r'[^a-zA-Z0-9]', '', cpu).lower()

    obfuscated_mac = ''.join(reversed(clean_mac))
    obfuscated_hostname = clean_hostname[::-1]
    obfuscated_cpu = ''.join(hex(ord(c))[2:] for c in clean_cpu)

    # Concatenate all parts with some delimiters for additional obfuscation
    combined_string = f"{obfuscated_mac}@{obfuscated_hostname}@{obfuscated_cpu}"
    
    # Compute SHA-256 hash of the combined string
    sha256_hash = hashlib.sha256(combined_string.encode()).hexdigest()

    return sha256_hash

def summarize_locations(locations):
    city_map = {}

    for loc in locations:
        if not loc: continue
        country = loc.get("country")
        city = loc.get("city")
        key = (country, city)

        if key not in city_map:
            city_map[key] = {
                "loc": f"{country}, {city}",
                "lat": loc.get("lat"),
                "lon": loc.get("lon"),
                "count": 0
            }

        city_map[key]["count"] += 1

    # convert mapping to list (and drop internal counter if not needed)
    result = []
    for data in city_map.values():
        result.append({
            "loc": data["loc"],
            "lat": data["lat"],
            "lon": data["lon"],
            "count": data["count"]
        })

    return result
