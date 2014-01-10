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

if not os.path.isdir(SAT_EXPORTDIR):
  os.makedirs(SAT_EXPORTDIR)

client = xmlrpclib.Server(SAT_URL)

sessionKey = client.auth.login(SAT_USER, SAT_PWD)

cfgchannelslist = client.configchannel.listGlobals(sessionKey)
for ch in cfgchannelslist:
  chdir = os.path.join(SAT_EXPORTDIR, ch['label'])
  os.mkdir(chdir)
  infof = open (os.path.join(chdir, 'info'), 'w')
  infof.write ("label: %s\n" % (ch['label'],))
  infof.write ("name: %s\n" % (ch['name'],))
  infof.write ("description: %s\n" % (ch['description'],))
  print ch
  
  files = client.configchannel.listFiles(sessionKey, ch['label'])
  infof.write ("nofiles: %d\n" % (len(files),))
  findex = 0
  for f in files:
    findex += 1
    print f
    fileinfof = open (os.path.join(chdir,"fileinfo_%d" % (findex,)), 'w')
    fileinfof.write("type: %s\n" % (f['type'],))
    fileinfof.write("path: %s\n" % (f['path'],))
    fdetail = client.configchannel.getFileRevisions(sessionKey, ch['label'], f['path'])
    lastfdetail = fdetail[-1]
    print lastfdetail
    # {'binary': False, 'macro-start-delimiter': '{|', 'group': 'cdrom', 'channel': 'cfg2', 'creation': <DateTime '20140108T15:23:51' at 2699560>, 'modified': <DateTime '20140108T15:23:51' at 2699e60>, 'macro-end-delimiter': '|}', 'contents_enc64': False, 'permissions_mode': '644', 'contents': '# test file for {| rhn.system.hostname |}\n# for channel 2\n', 'owner': 'abrt', 'path': '/etc/cfg1/testfile1', 'permissions': 644, 'type': 'file', 'md5': '7927c95097920257a98cabeaf76a4a94', 'revision': 2}
    fileinfof.write("owner: %s\n" % (lastfdetail['owner'],))
    fileinfof.write("group: %s\n" % (lastfdetail['group'],))
    fileinfof.write("permissions: %s\n" % (lastfdetail['permissions'],))
    if lastfdetail['type'] == 'file':
      fileinfof.write("binary: %s\n" % ('True' if lastfdetail['binary'] else 'False',))
      fileinfof.write("md5: %s\n" % (lastfdetail['md5'],))
      fileinfof.write("macro-start-delimiter: %s\n" % (lastfdetail['macro-start-delimiter'],))
      fileinfof.write("macro-end-delimiter: %s\n" % (lastfdetail['macro-end-delimiter'],))
      if lastfdetail['binary']:
        raise "Oops, cannot handle binary files"
      else:
        filecontentf = open (os.path.join(chdir, "filecontent_%d" % (findex,)), 'w')
        filecontentf.write(lastfdetail['contents'])
        filecontentf.close()
    elif lastfdetail['type'] == 'directory':
      pass
    else:
      raise "oops, cannot handle links yet"
    fileinfof.close()
    
  infof.close()

client.auth.logout(sessionKey)

