"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import random
import sys
from pluginmanager import *


"""
	The Plugin interface used to emulate DGA.
	All DGA plugins should be located in the plugins/dga folder.
"""
class IDgaPlugin(object, metaclass=IPluginManager):
	id = "dga"

	#The methods below can be implemented to provide services.
	def get_domain(self):
		raise NotImplementedError("Subclass must implement abstract method")



"""
	The Plugin interface used to replay various file types.
	All Replay plugins should be located in the plugins/replay folder.
"""
class IReplayPlugin(object, metaclass=IPluginManager):
	id = "replay"

	log = logging.getLogger(__name__)

	def __init__(self, file):	#Constructor
		ext = file.name[file.name.rfind('.') + 1:]
		if ext == self.get_input_type() :
			self.file = file
		else:
			log.error("Invalid input type for given plugin")
			sys.exit()

		override_model = False
		if self.configuration.get("override_model", "false").lower() == "true":
			override_model = True

		if override_model:
			setattr(self, "burst", 1)
			setattr(self, "delay", 0)

	def get_domain(self):
		raise NotImplementedError("Subclass must implement abstract method")

	def get_input_type(self):
		raise NotImplementedError("Subclass must implement abstract method")



"""
	The Plugin interface used to implement various traffic models.
	The model defines the pattern in which the requests must be sent.
	All Model plugins should be located in the plugins/model folder.
"""
class IModelPlugin(object, metaclass=IPluginManager):
	id = "model"

	#Delay is always returned in minutes
	def get_delay(self):
		raise NotImplementedError("Need to implement get_delay()")

	def get_burst_request_count(self):
		min = self.configuration.get("min_burst_requests")
		max = self.configuration.get("max_burst_requests")
		if not (min or max):
			self.log.error("Both min and max burst requests are required")
		return random.randint(int(min), int(max))

	#Interval is always returned in seconds
	def get_interval(self):
		if self.configuration.get("interval"):
			interval = float(self.configuration.get("interval"))
		else:
			interval = 0
		return interval