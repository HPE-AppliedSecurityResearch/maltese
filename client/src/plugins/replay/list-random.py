"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import random as random
import linecache as linecache
import logging

from modules.pluginregistry import IReplayPlugin


"""returns domains in random order from a given list"""
class ListRandom(IReplayPlugin):
	
	log = logging.getLogger(__name__)
	length = 0


	def get_input_type(self):
		return 'txt'


	def get_domain(self):
		if self.length == 0:
			self.length = self._file_len()
		self.file.seek(0)
		for i in range(0, self.length):
			lineNum = random.randint(1, self.length)
			line = linecache.getline(self.file.name, lineNum)
			if not line or line.isspace():
				continue
			line = line.lstrip()
			if line.startswith("http://"):
					line = line[7:]
			line = line.strip()
			yield line


	def _file_len(self):
		i = -1
		for i, l in enumerate(self.file):
			pass
		return i + 1