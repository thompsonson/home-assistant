import http.cookiejar
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json
import os
import base64
import logging
import socket

from homeassistant.components.thermostat import ThermostatDevice
from homeassistant.const import (
	CONF_PASSWORD, CONF_USERNAME, TEMP_CELSIUS, TEMP_FAHRENHEIT)

_LOGGER = logging.getLogger(__name__)

CONF_AWAY_TEMP = "away_temperature"
DEFAULT_AWAY_TEMP = 16

class Hive:

	def makeRequest(self,url,payload):
		# global urllib2
		# global opener
		if payload:
			# Use urllib to encode the payload
			data = urllib.parse.urlencode(payload)
			binary_data = data.encode('ascii')
			req = urllib.request.Request(url, binary_data)
		else:
			req = urllib.request.Request(url)

		# Make the request and read the response
		try:
			resp = urllib.request.urlopen(req)
		except urllib.error.URLError as e:
			print(e.code)
		else:
			#body = resp.read()
			body = resp.read().decode('ascii')
			return body;
		return None;

	def __init__(self, username, password):
		self.username = username
		self.password = password
		
		self._hubIds = []

		# Store the cookies and create an opener that will hold them
		self.cj = http.cookiejar.CookieJar()
		self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))

		# Add headers
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36')]

		# Install opener
		urllib.request.install_opener(self.opener)		
		
	def logon(self):
		url = 'https://api.hivehome.com/v5/login'
		payload = {
		  'username':self.username,
		  'password':self.password
		  }

		# Login
		body = self.makeRequest(url,payload)
		response = json.loads(body)
		self._hubIds = response["hubIds"]
		
	def deviceList(self):
		# /users/:username/hubs/:hubId/devices
		url = 'https://api.hivehome.com/v5/users/' + self.username + '/hubs/' + self._hubIds[0] + '/devices'
		body = self.makeRequest(url,None)
		response = json.loads(body)
		x= json.dumps(response, sort_keys=True, indent=4)
		print(x)
		return response			
				
	def temperatureDetails(self):
		# Get temperature (weather) data for inside and out
		self.opener.addheaders = [('X-Requested-With', 'XMLHttpRequest')];
		url = 'https://api.hivehome.com/v5/users/' + self.username + '/widgets/temperature'
		body = self.makeRequest(url,None)
		return json.loads(body)		

	@property
	def should_poll(self):
		"""No polling needed for a demo thermostat."""
		return True

	@property
	def name(self):
		"""Return the name of the thermostat."""
		return "Hive Thermostat [TODO: get name or ID from deviceList]"

	@property
	def unit_of_measurement(self):
		"""Return the unit of measurement."""
		return TEMP_CELSIUS
		
	@property
	def current_temperature(self):
		"""Return the current temperature."""
		temp = self.temperatureDetails()
		return temp['inside']['now']

	@property
	def target_temperature(self):
		"""Return the temperature we try to reach."""
		# Get heating target temperature
		url = 'https://api.hivehome.com/v5/users/' + self.username + '/widgets/climate/targetTemperature?precision=0.5'
		body = self.makeRequest(url,None)
		# print(body)
		target = json.loads(body)
		return target['temperature']

	def set_temperature(self, temperature):
		# Set heating target temperature
		url = 'https://api.hivehome.com/v5/users/' + self.username + '/widgets/climate/targetTemperature'
		payload = {
		  'temperature':temperature,
		  'temperatureUnit':'C'
		  }
		body = self.makeRequest(url,payload)
		_LOGGER.info(body)			

	def logout(self):
		url = 'https://my.hivehome.com/logout'
		self.makeRequest(url,None)

		
# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
	"""Setup the honeywel thermostat."""
	username = config.get(CONF_USERNAME)
	password = config.get(CONF_PASSWORD)

	if username is None or password is None:
		_LOGGER.error("Missing required configuration items %s or %s",
					  CONF_USERNAME, CONF_PASSWORD)
		return False

	try:
		client = Hive(hiveuser,hivepass)
	except:
		_LOGGER.error('Failed to login to honeywell account %s', username)
		return False		
	
	add_devices(client)
	
	return True





