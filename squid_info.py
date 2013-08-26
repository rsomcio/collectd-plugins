#!/bin/env python

import collectd
import signal
import os,subprocess,re

###############################################################################
#         WARNING! Importing this script will break the exec plugin!          #
###############################################################################
# Use this if you want to create new processes from your python scripts.      #
# Normally you will get a OSError exception when the new process terminates   #
# because collectd will ignore the SIGCHLD python is waiting for.             #
# This script will restore the default SIGCHLD behavior so python scripts can #
# create new processes without errors.                                        #
###############################################################################
#         WARNING! Importing this script will break the exec plugin!          #
###############################################################################

def init():
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)

###############################################################################

def fetch_info(args):
	""" returns hash of 5min averages in squidclient """
	try:
        	data = subprocess.Popen(['/usr/bin/squidclient',args], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
	except:
		return None

        return parse_info(data.split('\n'))


def parse_info(info_lines):
        """Parse info response from squidclient"""
        info = {}

        for line in info_lines:
        	if '=' in line:
                	name, val = line.split(' = ')
                        info[name] = re.sub(r'\D','',val)

        return info
	
def dispatch_value(info, key, type, type_instance=None):
        """Read a key from info response data and dispatch a value"""
        if key not in info:
                print "warning"
                return

        if not type_instance:
                type_instance = key

        value = info[key]
#	print '%s %s' % (key, value)
	val = collectd.Values(type='gauge')
	val.type = type
	val.type_instance = type_instance
	val.values = [value]
	val.dispatch()

def read_callback(data=None):
	info = fetch_info('mgr:5min')
	for key in info:
		dispatch_value(info, key, 'gauge')



#read_callback()
# register callbacks
collectd.register_init(init)
collectd.register_read(read_callback);
