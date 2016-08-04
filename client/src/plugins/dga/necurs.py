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

from modules.pluginregistry import IDgaPlugin


"""
	The DGA is based on the work published at https://www.johannesbader.ch/2015/02/the-dgas-of-necurs/
"""

class Necurs(IDgaPlugin):

	log = logging.getLogger(__name__)

	def necurs_domain(self, sequence_nr, magic_nr, date):
		def pseudo_random(value):
			loops = (value & 0x7F) + 21
			for index in range(loops):
				value += ((value*7) ^ (value << 15)) + 8*index - (value >> 5)
				value &= ((1 << 64) - 1)
			return value


		def mod64(nr1, nr2):
			return nr1 % nr2

		n = pseudo_random(date.year)
		n = pseudo_random(n + date.month + 43690)
		n = pseudo_random(n + (date.day>>2))
		n = pseudo_random(n + sequence_nr)
		n = pseudo_random(n + magic_nr)
		domain_length = mod64(n, 15) + 7

		domain = ""
		for i in range(domain_length):
			n = pseudo_random(n+i) 
			ch = mod64(n, 25) + ord('a') 
			domain += chr(ch)
			n += 0xABBEDF
			n = pseudo_random(n) 

		tlds = ['tj','in','jp','tw','ac','cm','la','mn','so','sh','sc','nu','nf','mu',
		'ms','mx','ki','im','cx','cc','tv','bz','me','eu','de','ru','co','su','pw',
		'kz','sx','us','ug','ir','to','ga','com','net','org','biz','xxx','pro','bit']

		tld = tlds[mod64(n, 43)]
		domain += '.' + tld
		return domain

	def get_domain(self):
		date = self.configuration.get("date", datetime.today())
		if isinstance(date, str):
			date = datetime.strptime(date, "%Y-%m-%d")
		for sequence_nr in range(2048):
			yield self.necurs_domain(sequence_nr, 9, date)