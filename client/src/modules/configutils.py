"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import os
import logging


log = logging.getLogger(__name__)

def non_overridable(f):
	f.overridable = True
	return f


def get_non_overridables(bases):
	ret = []
	for source in bases:
		for name, attr in source.__dict__.items():
			if getattr(attr, "non_overridable", False):
				ret.append(name)
		#ret.extend(get_overridables(source.__bases__))
	return ret


def readconfig(plugin, dir):
	try:
		path = os.path.join(os.getcwd(), "conf", dir)
		name = plugin.__module__
		if name == '__main__':
			name = plugin.configuration.get("conf_file")
		file = open(os.path.join(path, name + ".conf"), 'r')
		log.info("Configuration loaded from " + file.name)
	except FileNotFoundError:
		log.warning("No Configuration loaded...\n")
		return

	for line in file:
		line = line.strip()

		if not line:
			continue

		if line.startswith('#'):
			continue
		name, value = line.split(':')
		name = name.rstrip()
		value = value.lstrip()
		if name and value:
			if ' ' in value:
				value = value.split()
			plugin.configuration[name] = value
