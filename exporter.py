import prometheus_client as prom
import json
import time
import requests
import websocket
import os

from dotenv import load_dotenv
from urllib.parse import parse_qs, urlparse

load_dotenv()

USERNAME = os.getenv('HV_USERNAME')
PASSWORD = os.getenv('HV_PASSWORD')
HEADERS = {
	"content-type": "application/x-www-form-urlencoded",
	# "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
	# "sec-fetch-dest": "document",
	# "sec-fetch-mode": "navigate",
	# "sec-fetch-site": "same-origin",
	# "sec-fetch-user": "?1",
	# "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
	# "sec-ch-ua-mobile": "?0",
	# "sec-ch-ua-platform": "Windows",
	# "origin": "https://auth.hypervolt.co.uk",
	# "dnt": "1"
	}

def create_authenticated_session():
	session = requests.Session()
	response = session.get('https://api.hypervolt.co.uk/login-url')
	url = json.loads(response.text)['login']
	session.headers.update(HEADERS)
	response = session.get(url)
	url = response.url
	STATE = parse_qs(urlparse(url).query)['state'][0]
	data = "state={}&username={}&password={}&action=default".format(STATE, USERNAME, PASSWORD)
	reponse = session.post(url, headers=session.headers, data=data)
	response = session.get('https://api.hypervolt.co.uk/charger/by-owner')
	if response.status_code != 200:
		print("It looks like authentication is failing. Exiting.")
		return False
		print("Hypervolt API session created. Storing.")
	return session


if __name__ == '__main__':

	# Initialize Prometheus Metrics
	info = prom.Gauge('hypervolt_charger_info', 'Charger Summary Info', ['charger_id'])
	led_brightness = prom.Gauge('hypervolt_charger_led_brightness_percentage', 'Charger LED Brightness', ['charger_id'])
	schedule_enabled = prom.Gauge('hypervolt_charger_schedule_enabled', 'Charger Schedule Enabled', ['charger_id'])
	max_current = prom.Gauge('hypervolt_charger_max_current_milliamps', 'Charger Max Charge Rate', ['charger_id'])
	ct_current = prom.Gauge('hypervolt_charger_ct_current_milliamps', 'Charger CT Clamp Milliamps', ['charger_id'])
	ct_voltage = prom.Gauge('hypervolt_charger_ct_voltage_volts', 'Charger CT Clamp Voltage', ['charger_id'])
	charging = prom.Gauge('hypervolt_charger_charging', 'Charger Currently Charging', ['charger_id'])
	charge_watt_hours = prom.Gauge('hypervolt_charger_charge_watt_hours', 'Current Charge Watt Hours', ['charger_id'])
	charge_current = prom.Gauge('hypervolt_charger_charge_current_milliamps', 'Current Charge Current Throughput', ['charger_id'])
	charge_ccy_cpent = prom.Gauge('hypervolt_charger_charge_ccy_spent', 'Current Charge Currency Spent', ['charger_id'])
	charge_carbon_saved = prom.Gauge('hypervolt_charger_charge_carbon_saved_grams', 'Current Charge Carbon Saved', ['charger_id'])

	# Set up web session
	session = create_authenticated_session()
	# Convert web session cookies to WS format
	requests_cookies = session.cookies.get_dict()
	cookies = ''
	for cookie in requests_cookies:
		cookies += "{}={};".format(str(cookie), str(requests_cookies[cookie]))

	# Get Charger ID
	response = session.get('https://api.hypervolt.co.uk/charger/by-owner')
	charger_id = response.json()['chargers'][0]['charger_id']

	# Launch web socket for charge data
	ws = websocket.WebSocket()
	ws.connect("wss://api.hypervolt.co.uk/ws/charger/{}/session/in-progress".format(charger_id), origin="https://hypervolt.co.uk", host="api.hypervolt.co.uk", cookie=cookies)


	prom.start_http_server(8080)

	while True:

		# Summary
		info.labels(charger_id).set(1)

		# Brightness
		uri = 'https://api.hypervolt.co.uk/charger/by-id/{}'.format(charger_id)
		url = uri + '/led/brightness'
		response = session.get(url)
		if response.status_code == 200:
			led_brightness.labels(charger_id).set(response.json()['brightness'])

		# Schedule Status
		url =  uri + '/schedule'
		response = session.get(url)
		if response.status_code == 200:
			if response.json()['enabled'] == False:
				schedule_enabled.labels(charger_id).set(0)
			else:
				schedule_enabled.labels(charger_id).set(1)
			
		# Max Current Limit
		url = uri + '/max-current'
		response = session.get(url)
		if response.status_code == 200:
			max_current.labels(charger_id).set(response.json()['milli_amps'])

		# Get Charge Data from WebSocket
		ws_response = ws.recv()
		ws_result = json.loads(ws_response)

		# Currently Charging
		current_charging = ws_result['charging']
		if current_charging == False:
			charging.labels(charger_id).set(0)
		else:
			charging.labels(charger_id).set(1)

		# CT Current
		ct_current.labels(charger_id).set(ws_result['ct_current'])

		# CT Voltage
		ct_current.labels(charger_id).set(ws_result['voltage'])

		# Current Charge Milliamps
		charge_current.labels(charger_id).set(ws_result['true_milli_amps'])

		# Current Charge Watt-Hours
		charge_watt_hours.labels(charger_id).set(ws_result['watt_hours'])

		# Current Charge Currency Spent
		charge_ccy_cpent.labels(charger_id).set(ws_result['ccy_spent'])

		# Current Charge Carbon Grams Saved
		charge_carbon_saved.labels(charger_id).set(ws_result['carbon_saved_grams'])

		time.sleep(15)