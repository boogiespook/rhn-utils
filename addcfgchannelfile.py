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
if len(sys.argv) != 7:
  print "no arguments\n"
  print "Expecting\nchannel-label, path, contents_file, owner, group, permissions\n"
  print "contentsfile empty for dir\n"
  sys.exit(1)


def readfile(f):
  fd = open(f, 'r')
  contents = fd.read()
  fd.close()
  return contents

chlabel = sys.argv[1]
fpath = sys.argv[2]
if sys.argv[3] == '':
  filetype = 'd'
else:
  filecontents = readfile(sys.argv[3])
  filetype = 'f'
  print filecontents	
owner = sys.argv[4]
group = sys.argv[5]
permissions = sys.argv[6]


client = xmlrpclib.Server(SAT_URL)
sessionKey = client.auth.login(SAT_USER, SAT_PWD)
if filetype == 'd':
  isDir = True
  pathinfo = {"owner": owner, "group": group, "permissions": permissions}
else:
  isDir = False
  pathinfo = {"contents": filecontents, "owner": owner, "group": group, "permissions": permissions,
    "macro-start-delimiter": "{|", "macro-end-delimiter": "|}", "binary": False}
rc = client.configchannel.createOrUpdatePath(sessionKey, chlabel, fpath, isDir, pathinfo)

print "created: "
print rc

client.auth.logout(sessionKey)

