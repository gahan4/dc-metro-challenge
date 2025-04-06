#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 20:57:38 2025

@author: neil
"""



import requests

API_KEY = "fd8ee9e70a71430d89a160f375f15937"
BASE_URL = "https://api.wmata.com"

# Example to get metro schedule (you can modify to get specific schedule info)
url = f"{BASE_URL}/Rail.svc/json/jStations"
headers = {'api_key': API_KEY}

response = requests.get(url, headers=headers)
data = response.json()

# Buses - P12
#        - The Bus 21, 21X
#       -Wmata G14
#       - The Bus 16
#       - Metro F4
#       - Ride on 49, Ride on 10
#      - 