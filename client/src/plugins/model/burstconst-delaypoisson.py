"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import logging
import random

from modules.pluginregistry import *


class BurstConstDelayPoisson(IModelPlugin):
	"""
		In this model, a burst of requests will be sent, followed by a wait period.
		The wait period (delay) is calculated based on the rate in a poisson distribution.
	"""

	log = logging.getLogger(__name__)

	def get_delay(self):
		rate = self.configuration.get("delay_rate")
		if not rate:
			self.log.error("delay_rate config is missing")
		delay = random.expovariate(float(rate))
		return delay
