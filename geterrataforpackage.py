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
if len(sys.argv) != 6:
  print "no arguments\n"
  print "Expecting\npackage, arch, epoch, version, release\n"
  sys.exit(1)

pkgname = sys.argv[1]
pkgarch = sys.argv[2]
pkgepoch = sys.argv[3]
pkgversion = sys.argv[4]
pkgrelease = sys.argv[5]


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
print pkgs[0]

pkgid = int(pkgs[0]['id'])
ertlist = client.packages.listProvidingErrata(sessionKey, pkgid)
if len(ertlist) == 0:
  print "No errata found for this package. (Package only in self managed channel? You can yourself issue errata too!)\n"
  sys.exit(1)
elif len(ertlist) == 1:
  clonefrom = ertlist[0]['advisory']
  mergewith = ""
  print ertlist[0]
elif len(ertlist) == 2:
  # most cases, hopefully: RHxA and CLA
  clonefrom = ertlist[0]['advisory']
  mergewith = ertlist[1]['advisory']
  if mergewith.startswith("RH"):
    (clonefrom, mergewith) = (mergewith, clonefrom)
  print "Package found in 2 errata, most likely you must merge %s with %s for your channel\n" % (clonefrom, mergewith)
else:
  print "Package found in multiple errata:\n"
  print ertlist
client.auth.logout(sessionKey)

