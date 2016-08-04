"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


from datetime import datetime
import logging
import sys

from modules.pluginregistry import IDgaPlugin
import modules.utils as utils

"""
	The DGA is based on the work published by FireEye.
	The original article can be found here - https://www.fireeye.com/blog/threat-research/2016/04/new_downloader_forl.html
"""

class LockyApril(IDgaPlugin):

	log = logging.getLogger(__name__)

	def _lockyDGA(self, pos, seed, date):
		# Rotate left
		rol = lambda val, r_bits, max_bits = 32: \
			utils.uint32((val << r_bits%max_bits) & (2**max_bits-1) | \
			((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits))))

		# Rotate right
		ror = lambda val, r_bits, max_bits = 32: \
			utils.uint32(((val & (2**max_bits-1)) >> r_bits%max_bits) | \
			(val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1)))

		const1 = 0xb11924e1
		const2 = 0x27100001

		edi = 0
		edx = date.day >> 1
		ecx = date.year
		var_18 = utils.uint32(rol(pos, 0x15) + rol(seed, 0x11))
		var_14 = edx
		var_10 = 7
		while var_10 != 0:
			eax = ror((ecx + edi + 0x1bf5)*const1, 7)
			eax = utils.uint32(eax + const2)
			edi = utils.uint32(eax ^ edi)
			eax = ror(((edi + seed) * const1), 7)
			eax = utils.uint32(eax + const2)
			edi = utils.uint32(eax ^ edi)
			eax = ror((edx + edi) * const1, 7)
			edx = 0xd8efffff - eax
			eax = date.month
			edi = utils.uint32(edi + edx)
			eax = ror((eax + edi - 0x65cad) * const1, 7)
			edi = utils.uint32(edi + eax + const2)
			var_18 = ror((var_18 + edi) * const1, 7) + const2
			edi = utils.uint32(var_18 ^ edi)
			var_10 = var_10 - 1
			edx = var_14
		edx = edi % 0xb
		var_18 = edx + 7
		var_10 = 0

		domain = ""

		if edx != 0:
			while var_10 < var_18:
				edi = rol(edi, var_10)
				eax = ror(edi * const1, 7) + const2
				edx = eax % 0x19
				dl = edx & 0x0f
				domain = domain + chr(dl + 0x61)
				var_10 += 1
		
			domain = domain + "."
			tlds = self.configuration.get("tlds")
			eax = utils.uint32(ror(edi * const1, 7) + const2)
			edx = eax % len(tlds)
			tld = tlds[edx]
			domain = domain + tld

		return domain


	def get_domain(self):
		date = self.configuration.get("date", datetime.today())
		seed = self.configuration.get("seed")
		minSeed = self.configuration.get("min_seed")
		maxSeed = self.configuration.get("max_seed")
		if minSeed and maxSeed:
			minSeed = int(minSeed)
			maxSeed = int(maxSeed)
		elif seed:
			minSeed = maxSeed = int(seed)
		else:
			log.error("Seed is missing from config")
			sys.exit()

		if isinstance(date, str):
			date = datetime.strptime(date, "%Y-%m-%d")

		seed = minSeed
		while seed <= maxSeed:
			for pos in range(12):
				domain = self._lockyDGA(pos, seed, date)
				if domain:
					yield domain
			seed += 1