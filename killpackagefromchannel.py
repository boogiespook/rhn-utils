#!/usr/bin/python
import os
import sys
import xmlrpclib
from datetime import datetime

SAT_USER = os.environ['SAT_USER']
SAT_PWD = os.environ['SAT_PWD']
SAT_HOST = os.environ['SAT_HOST']
SAT_URL = "http://%s/rpc/api" % (SAT_HOST,)


# read name for config channel from options
if len(sys.argv) != 8:
  print "no arguments\n"
  print "Expecting\nchannel-label, package, arch, epoch, version, release, <dryrun|force>\n"
  sys.exit(1)

chlabel = sys.argv[1]
pkgname = sys.argv[2]
pkgarch = sys.argv[3]
pkgepoch = sys.argv[4]
pkgversion = sys.argv[5]
pkgrelease = sys.argv[6]
force = (sys.argv[7] == "force")


client = xmlrpclib.Server(SAT_URL)

sessionKey = client.auth.login(SAT_USER, SAT_PWD)

# search for the package in the channel
# must find the package id
pkgs = client.packages.findByNvrea(sessionKey, pkgname, pkgversion, pkgrelease, pkgepoch, pkgarch)
if len(pkgs) != 1:
  if len(pkgs) == 0:
    print "No packages found"
  else:
    print "Too many packages: %d\n" % (len(pkgs),)
  exit(1)

pkgid = int(pkgs[0]['id'])
chlist = client.packages.listProvidingChannels(sessionKey, pkgid)
# admittedly, this check could be implemented much more fancy by real pythonists
chcontainspkg = False
for ch in chlist:
  if ch['label'] == chlabel:
    chcontainspkg = True
    break

if not chcontainspkg:
  print "Channel doesn't contain package\n"
  print pkgs[0]
  sys.exit(1)

if force:
  rc = client.channel.software.removePackages(sessionKey, chlabel, [pkgid])
  print "RC:\n"
  print rc
else:
  print "\nAbout to remove package from channel %s\n" % (chlabel,)
  print pkgs[0]

client.auth.logout(sessionKey)

