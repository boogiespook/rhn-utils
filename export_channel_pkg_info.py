#!/usr/bin/python
import os
import xmlrpclib
from datetime import datetime

SAT_USER = os.environ['SAT_USER']
SAT_PWD = os.environ['SAT_PWD']
SAT_HOST = os.environ['SAT_HOST']
SAT_URL = "http://%s/rpc/api" % (SAT_HOST,)
SAT_EXPORTDIR = os.environ['SAT_EXPORTDIR']

# add datetime for now
SAT_EXPORTDIR = os.path.join(SAT_EXPORTDIR, str(datetime.now())).replace(' ','_').replace(':', '-')


def dateparse(datestrmmddyy):
  (mm,dd,yy) = datestrmmddyy.split('/')
  (mmm,ddd,yyyy) = ('0' + mm, '0' + dd, '20' + yy)
  return "%s-%s-%s" % (yyyy, mmm[-2:], ddd[-2:])

if not os.path.isdir(SAT_EXPORTDIR):
  os.makedirs(SAT_EXPORTDIR)

client = xmlrpclib.Server(SAT_URL)

sessionKey = client.auth.login(SAT_USER, SAT_PWD)

channellist = client.channel.listMyChannels(sessionKey)
for ch in channellist:
  # create label dir in export
  chinfo = client.channel.software.getDetails(sessionKey, ch['label'])
  chdir = os.path.join(SAT_EXPORTDIR, ch['label'])
  os.mkdir(chdir)
  # add relevant info in info file in export/label
  infof = open(os.path.join(chdir, "chinfo"), 'w')
  infof.write("label: %s\n" % (chinfo['label'],))
  infof.write("name: %s\n" % (chinfo['name'],))
  infof.write("summary: %s\n" % (chinfo['summary'],))
  infof.write("arch_name: %s\n" % (chinfo['arch_name'],))
  infof.write("parent_channel_label: %s\n" % (chinfo['arch_name'],))
  infof.write("clone_original: %s\n" % (chinfo['clone_original'],))
  infof.write("gpg_key_id: %s\n" % (chinfo['gpg_key_id'],))
  infof.write("gpg_key_url: %s\n" % (chinfo['gpg_key_url'],))


  #print chinfo
  packages = client.channel.software.listLatestPackages(sessionKey, ch['label'])
  pkginfolist = []
  for pkg in packages:
    # write name, arch, epoch, version, release
    pkginfolist.append("%s,%s,%s,%s,%s\n" % (
        pkg['name'], pkg['arch_label'],
        # if epoch is not just a space
        '' if pkg['epoch'] == ' ' else pkg['epoch'],
        pkg['version'], pkg['release']))
  pkginfof = open(os.path.join(chdir, "pkginfo"), 'w')
  pkginfolist.sort()
  # add packages info in packageinfo file export/label
  for pinfostr in pkginfolist:
    pkginfof.write(pinfostr)
  pkginfof.close()

  infof.close()

  erratas = client.channel.software.listErrata(sessionKey, ch['label'])
  erratainfof = open(os.path.join(chdir, "erratainfo"), 'w')
  for errata in erratas:
    erratadetail = client.errata.getDetails(sessionKey, errata['advisory_name'])
    

    erratainfof.write("%s,%s,%s\n" % (errata['advisory_name'], dateparse(erratadetail['issue_date']), dateparse(erratadetail['update_date'])))
client.auth.logout(sessionKey)

