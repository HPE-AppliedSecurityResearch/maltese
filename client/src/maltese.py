"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import sys
import argparse
import logging
import time
import ipaddress

from modules.pluginregistry import *
import modules.utils as utils
import modules.configutils as configutils

log = logging.getLogger(__name__)

class main():

	configuration = dict()

	def get_algo(self):
		if args.mode == "dga":
			#Starting DGA logic
			log.info('DGA Mode')
			p = utils.get_plugins(IDgaPlugin, args.plugin)
			p = p[0]()
			

		elif args.mode == "replay":
			#Starting Replay mode
			log.info("Replay Mode")
			p = utils.get_plugins(IReplayPlugin, args.plugin)
			p = p[0](args.input)

		#Loading global config into the loaded plugin
		for key, value in self.configuration.items():
			if not key in p.configuration:
				p.configuration[key] = value

		return p


	def send_requests(self, model, algo):
		count = 0
		loop = False
		src = algo.configuration.get("srcip")
		if src is not None:
			try:
				ipaddress.ip_address(src)
			except ValueError:
				log.error("Invalid IP specified in srcip configuration: {}".format(src))
				sys.exit()

		if algo.configuration.get("loop", "false").lower() == "true":
			loop = True
		enter_once = True
		dryrun = True
		if algo.configuration.get("dryrun", "true").lower() == "false":
			dryrun = False
		override_model = False
		if algo.configuration.get("override_model", "false").lower() == "true":
			override_model = True
		log.info("loop: %s", str(loop))
		log.info("dryrun: %s", str(dryrun))
		
		#Get count for first burst
		if override_model:
			burst = algo.burst
		else:
			burst = model.get_burst_request_count()
		log.info("Burst: %s", str(burst))
		interval = 0

		while loop or enter_once:
			enter_once = False
			for item in algo.get_domain():
				if count == burst:
					if override_model:
						delay = algo.delay
					else:
						delay = model.get_delay()
					log.info("Delay: " + str(delay))
					time.sleep(delay*60)
					count = 0
					#Get count for next burst
					if not override_model:
						burst = model.get_burst_request_count()
						log.info("Burst: %s", str(burst))
						interval = model.get_interval()
						log.info("Interval: %s secs", str(interval))
				utils.send_dns_request(item, interval, src, dryrun, algo.configuration.get("interface"))
				count += 1


	def main(self):
		#Read master config
		configutils.readconfig(self, ".")

		algo = self.get_algo()
		m = algo.configuration.get("model")
		model = utils.get_plugins(IModelPlugin, m)
		if not model:
			log.error("Unable to find model: {}\nThe available models are: ".format(m) + str(utils.get_plugins(IModelPlugin)))
			sys.exit()
		model = model[0]()

		#Send requests
		self.send_requests(model, algo)



if __name__ == "__main__":
	try:
		parser = argparse.ArgumentParser()
		subparsers = parser.add_subparsers(title='commands', dest='mode')
		
		dgaparser = subparsers.add_parser('dga', help='Execute DGA plugins')
		dgarequired = dgaparser.add_argument_group('required arguments')
		dgarequired.add_argument('-p', dest='plugin', required=True, help='DGA Plugin module to run', choices=utils.get_plugins(IDgaPlugin))
		dgaparser.add_argument('-l', dest='loglevel', choices=['error', 'warning', 'info', 'debug'], default='error', help='Logging level. Default is error')
		
		replayparser = subparsers.add_parser('replay', help='Execute Replay plugins')
		replayrequired = replayparser.add_argument_group('required arguments')
		replayrequired.add_argument('-p', dest='plugin', required=True, help='Replay Plugin module to run', choices=utils.get_plugins(IReplayPlugin))
		replayrequired.add_argument('-i', dest='input', type=argparse.FileType('r'), required=True, help='Input file for replay.')
		replayparser.add_argument('-l', dest='loglevel', choices=['error', 'warning', 'info', 'debug'], default='error', help='Logging level. Default is error')

		args = parser.parse_args()

		if not args.mode:
			parser.error("Enter a command to execute")
			sys.exit()

		if args.loglevel == 'debug':
			logging.basicConfig(level=logging.DEBUG)
		elif args.loglevel == 'info':
			logging.basicConfig(level=logging.INFO)
		elif args.loglevel == 'warning':
			logging.basicConfig(level=logging.WARNING)
		else:
			logging.basicConfig(level=logging.ERROR)

		m = main()
		m.main()
	except KeyboardInterrupt:
		print("Exiting...")
		sys.exit()