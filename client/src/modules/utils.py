"""
	(c) Copyright 2016 Hewlett Packard Enterprise Development LP

	This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
	as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. 
	This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
	You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import os
import imp
import dns
import dns.resolver
import socket
import random
import logging
from contextlib import contextmanager
import ctypes


@contextmanager
def redirect_stderr(new_target):
    import sys
    old_target, sys.stderr = sys.stderr, new_target # replace sys.stdout
    try:
        yield new_target # run some code with the replaced stdout
    finally:
        sys.stderr = old_target # restore to the previous value


# Don't print the annoying warning message that occurs on import
with open(os.devnull, 'w') as errf, redirect_stderr(errf):
	from scapy.all import *

log = logging.getLogger(__name__)


def get_plugins(plugintype, module = None):
	""" Discover the plugin classes contained in Python files.
		Return a list of plugin classes.
	"""
	dir = os.path.join(os.getcwd(), "plugins", plugintype.id)
	loaded = 0
	plugins = []
	for filename in os.listdir(dir):
		modname, ext = os.path.splitext(filename)
		if ext == '.py':
			file, path, descr = imp.find_module(modname, [dir])
			if file:
				if module == modname:
				# Loading the module registers the plugin in
				# the corresponding base classes
					mod = imp.load_module(modname, file, path, descr)
					loaded += 1
				elif not module:
					plugins.append(modname)
					loaded += 1
	if plugins:
		return plugins
	else:
		return plugintype.registry


def send_dns_request(item, interval = None, src = None, dryrun = True, interface = None):
	ns = get_default_dnsserver()
	domain = ""

	if interface == "lo":
		conf.L3socket = L3RawSocket

	if isinstance(item, Packet):
		p = item
		domain = p[DNSQR].qname.decode('ascii').strip('.')
		if not dryrun:
			if src is None:
				p[IP].src = get_local_ip()
			else:
				p[IP].src = src
			sendp(p, iface=interface)
	else:
		domain = item
		if not dryrun:
			if src is None:
				sendp(Ether()/IP(dst=ns)/UDP()/DNS(rd=1, qd=DNSQR(qname=domain)), inter=interval, iface=interface)
			else:
				sendp(Ether()/IP(dst=ns, src=src)/UDP()/DNS(rd=1, qd=DNSQR(qname=domain)), inter=interval, iface=interface)

	print(domain)
	




def get_local_ip():
	local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
	print(local_ip)
	return local_ip


def get_default_dnsserver():
	default = dns.resolver.get_default_resolver()
	return default.nameservers[0]


def uint32(i):
	return ctypes.c_uint32(int(i)).value