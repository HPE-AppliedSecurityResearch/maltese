"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import logging

from modules.pluginregistry import IReplayPlugin


"""
	Receives a text file with a list of domains and parses the file.
	Returns each domain parsed from the file.
"""
class ListReplay(IReplayPlugin):

	log = logging.getLogger(__name__)

	def get_input_type(self):
		return 'txt'


	def get_domain(self):
		self.file.seek(0)
		for line in self.file:
			if not line or line.isspace():
				continue
			line = line.lstrip()
			if line.startswith("http://"):
				line = line[7:]
			line = line.strip()
			yield line