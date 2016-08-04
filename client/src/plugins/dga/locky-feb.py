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
	The DGA is based on the work done by ForcePoint.
	The original article is published here - https://blogs.forcepoint.com/security-labs/lockys-new-dga-seeding-new-domains
"""

class LockyFeb(IDgaPlugin):

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

		const1 = 0xB11924E1
		const2 = 0x27100001
		const3 = 0x2709A354

		modYear = ror(const1 * (date.year + 0x1BF5), 7)
		modYear = ror(const1 * (modYear + seed + const2), 7)
		modDay = ror(const1 * (modYear + utils.uint32(date.day >> 1) + const2), 7)
		modMonth = ror(const1 * (modDay + date.month + const3), 7)

		seed = rol(seed, 17)

		modBase = rol(pos & 7, 21)
		modFinal = ror(const1 * (modMonth + modBase + seed + const2), 7)
		modFinal += const2

		sldLength = modFinal % 11 + 5

		i = 0
		domain = ""
		while i < sldLength:
			x = rol(modFinal, i)
			y = ror(const1*x, 7)
			z = utils.uint32(y + const2)
			modFinal = z
			domain += chr(z % 25 + 97)
			i += 1

		domain += '.'
		
		tldchars = self.configuration.get("tldchars")
		x = ror(const1 * modFinal, 7)
		y = utils.uint32(x + const2) % (len(tldchars)/2)
		domain += tldchars[utils.uint32(2*y)]
		domain += tldchars[utils.uint32(2*y + 1)]

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
			for pos in range(8):
				yield self._lockyDGA(pos, seed, date)
			seed += 1