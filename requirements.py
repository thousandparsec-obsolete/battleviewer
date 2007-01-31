# This file checks you have installed the requirements for tpclient-pywx 
# It can be run as standalone but is also run by the client at startup

notfound    = []
recommended = []

# Try and figure out what type of system this computer is running.
import os
result = os.system('apt-get --version > /dev/null 2>&1') 
if result == 0:
	system = "debian-based"
elif result == 32512:
	system = "unknown"

from types import StringTypes
import re
def cmp(ver1, ver2):
	if type(ver2) in StringTypes:
		ver2 = [int(x) for x in ver2.split('.')]

	ver2 = list(ver2)
	for i,x in enumerate(ver2):
		try:
			ver2[i] = int(x)
		except ValueError:
			# This means there could be a "pre" or "rc" something in the version
			# We will treat this version as the one before.
			ver2[i] = int(re.search('(\d+)', x).group())-1

	for a, b in zip(ver1, ver2):
		if a <= b:
			continue
		return False
	return True

def tostr(ver1):
	s = ""
	for a in ver1:
		s += "."+str(a)
	return s[1:]

pygame_version = (1, 7, 1)
try:
	import pygame

	if not cmp(pygame_version, pygame.version.vernum):
		raise ImportError("pygame was too old")
except (ImportError, KeyError), e:
	print e

	if system == "debian-based":
		notfound.append("python-pygame")
	else:
		notfound.append("Pygame > " + ".".join(pygame_version))

libmng_version = (0, 0, 4)
try:
	import mng

	if not cmp(mng_version, mng.version):
		raise ImportError("libmng-py was too old")
except (ImportError, KeyError), e:
	print e

	if system == "debian-based":
		notfound.append("python-mng")
	else:
		notfound.append("libmng-py > " + ".".join(libmng_version))


import os
if os.environ.has_key("TPCLIENT_MEDIA"):
	graphics = os.environ["TPCLIENT_MEDIA"]
else:
	graphics = '.'

if len(notfound) > 0:
	print
	print "The following requirements where not met:"
	for module in notfound:
		print '\t', module

if len(recommended) > 0:
	print
	print "The following recommended modules where not found:"
	for module, reason in recommended:
		print '\t', module + ',\t', reason

# Check for an apt-get based system,
if system == "debian-based":
	notfound_debian = []
	for module in notfound:
		if module.find(' ') == -1:
			notfound_debian.append(module)
	if len(notfound_debian) > 0:
		print """
You may be able to install some of the requirements by running the following
command as root:

	apt-get install %s
""" % " ".join(notfound_debian)
	if len(recommended) > 0:
		print """
To install the modules recommended for full functionality, run the following
command as root:

	apt-get install %s
""" % " ".join(zip(*recommended)[0])


if len(notfound) > 0:
	import sys
	sys.exit(1)
