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

IP_GROUPS_FILE = "geolocs.log"

def get_ip_groups():
    try:
        with open(IP_GROUPS_FILE, "r") as f:
            data = f.read().strip()
        parts = data.split("|")
        if len(parts) < 2: return (None, "[]")
        time = datetime.strptime(parts[0].strip(), "%d-%m-%Y %H:%M")
        return (time, parts[1].strip())
    except:
        return (None, "[]")

async def create_ip_groups(ip_list):
    geo_api_url = "https://ipinfo.io/{}/json"  # Using ipinfo.io service for geolocation
    location_groups = {}

    # BLock file by changing the time to be now + 365days
    _, data = get_ip_groups()
    with open(IP_GROUPS_FILE, "w") as f:
        f.write((datetime.now() + timedelta(days=365)).strftime("%d-%m-%Y %H:%M") + " | " + data)

    for ip in ip_list:
        try:
            response = requests.get(geo_api_url.format(ip))
            response.raise_for_status()
            geo_data = response.json()
            
            # Retrieve location info
            city = geo_data.get('city', 'Unknown city')
            country = geo_data.get('country', 'Unknown country')
            location_key = f"{city}, {country}"
            
            # Retrieve latitude and longitude
            loc = geo_data.get('loc', 'Unknown location').split(',')
            latitude = loc[0] if len(loc) > 0 else 'Unknown latitude'
            longitude = loc[1] if len(loc) > 1 else 'Unknown longitude'

            # If location already exists, append the IP to the list of IPs for that location
            if location_key not in location_groups:
                location_groups[location_key] = {
                    'lat': latitude,
                    'long': longitude,
                    'ips': [],
                }
            location_groups[location_key]['ips'].append(ip)
            print(f"Fetched geolocation for: {ip}")
        
        except requests.RequestException as e:
            print(f"Error fetching geolocation for IP {ip}: {e}")
            break
        
        sleep(1.5)
    
    # Convert the location data to the required format [(Name, lat, long, count, ips)]
    result = []
    for location, data in location_groups.items():
        result.append({"loc": location, "lat": data['lat'],"lng": data['long'], "count": len(data['ips'])})

    with open(IP_GROUPS_FILE, "w") as f:
        f.write(datetime.now().strftime("%d-%m-%Y %H:%M") + " | " + str(result))