"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


from modules.configutils import *


class IPluginManager(type):
	"""This is the abstract class used by all plugin registries"""

	#plugins = dict()

	def __init__(cls, name, bases, dct):
		if not hasattr(cls, 'registry'):
			# this is the base class.  Create an empty registry
			cls.registry = []
		else:
			# this is a derived class.  Add cls to the registry
			cls.registry.append(cls)
			non_overridables = get_non_overridables(bases)
			for fn in dct:
				if fn in non_overridables:
					raise SyntaxError("Overriding " + fn + " is not allowed")


		if not hasattr(cls, "id"):
			raise SyntaxError("All Plugin Interfaces should define an id variable. This will be used as the folder name.")


		if not hasattr(cls, 'configuration'):
			cls.configuration = dict()
		else:
			readconfig(cls, cls.id)

		super(IPluginManager, cls).__init__(name, bases, dct)