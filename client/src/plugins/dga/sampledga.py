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

from modules.pluginregistry import IDgaPlugin


"""
	This is a sample DGA and is not intended to reflect any specific malware.
"""

class SampleDga(IDgaPlugin):
	"""Example Dga plugin"""
	
	log = logging.getLogger(__name__)

	def get_domain(self):
		self.log.info("Sample DGA execution")
		
		domaincount = int(self.configuration.get("domaincount"))
		characters = self.configuration.get("characters")
		length = random.randint(int(self.configuration.get("min_length")), int(self.configuration.get("max_length")))
		tlds = self.configuration.get("suffixes")

		for dc in range(domaincount):
			name = ""
			for i in range(length):
				name = name + characters[random.randint(0, len(characters) - 1)]

			name = name + tlds[random.randint(0, len(tlds) - 1)]
			yield name