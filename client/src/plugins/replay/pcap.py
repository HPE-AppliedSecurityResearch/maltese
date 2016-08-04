"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


from scapy.all import *
import time
import datetime

from modules.pluginregistry import IReplayPlugin
import modules.utils as utils


"""
	Receives a pcap file as input.
	Returns DNS packets retrieved from the pcap for replay.
	Also handles time delays between each packet.
"""
class PcapReplay(IReplayPlugin):

	log = logging.getLogger(__name__)
	
	def get_input_type(self):
		return 'pcap'


	def get_domain(self):
		try:
			reader = PcapReader(self.file.name)
			prevTime = 0
			for p in reader:
				if not p.haslayer(DNSQR):
					continue
				if prevTime > 0:
					diffTime = p.time - prevTime
					log.info("Waiting " + str(diffTime) + "\n")
					self.delay = diffTime/60
				prevTime = p.time
				yield p
		finally:
			reader.close()
