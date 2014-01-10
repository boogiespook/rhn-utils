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
if len(sys.argv) != 4:
  print "no arguments\n"
  print "Expecting\nchannel-label, channel-name, channel-description\n"
  sys.exit(1)

chlabel = sys.argv[1]
chname = sys.argv[2]
chdescr = sys.argv[3]


client = xmlrpclib.Server(SAT_URL)

sessionKey = client.auth.login(SAT_USER, SAT_PWD)

# check if channel exists, and exit if it so
# stupid way
#try:
  #cfgchannel = client.configchannel.getDetails(sessionKey, chlabel)
  #print "Channel %s exists already\n" % (chlabel,)
  #print cfgchannel
  #sys.exit(1)
#except SystemExit as ex:
  #raise ex
#except:
  #pass
if client.configchannel.channelExists(sessionKey, chlabel) == 1:
  print "Channel %s exists already\n" % (chlabel,)
  sys.exit(1)

print "continueing\n"
rc = client.configchannel.create(sessionKey, chlabel, chname, chdescr)
print "created: "
print rc
client.auth.logout(sessionKey)

