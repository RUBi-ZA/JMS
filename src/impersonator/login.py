#!/usr/bin/env python

import sys

sys.path.append("..")
from utilities.io.shell import UserProcess

username = sys.argv[1]
password = sys.argv[2]

venv = None
if len(sys.argv) > 3:
    venv = sys.argv[3]

try:
    process = UserProcess(username, password)
    if venv:    
        out = process.run_command("source %s" % venv)
    
    process.close()
except Exception, err:
    print(err)
            
print 0
