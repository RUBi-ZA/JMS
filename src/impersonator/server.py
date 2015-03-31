#!/usr/bin/env python
import os, sys, base64, subprocess
from datetime import datetime

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

sys.path.append("/srv/JMS/src")
from utilities.structures import TimeExpiredDict
from utilities.context_managers import cd
from utilities.security.cryptography import PubPvtKey

import pxssh

class Impersonator(Resource):
    
    def __init__(self):
        self.processes = TimeExpiredDict(600)
        with open("pvt.key", "r") as key_file:
            self.key = key_file.read()
            
            
    def authenticate(self, username, password, venv=None):
        process = self.processes.get(username)
        if process == None:
            process = subprocess.Popen('su %s -c " python login.py %s %s"' % (username, username, password), shell=True, stdout=subprocess.PIPE)
            output, error = process.communicate()
            print output
            
            if output.startswith("0"): 
                self.processes.add(username, "")
            else:
                return False
            
        return True
    
    
    def render_POST(self, request):
        try:
            data = request.content.read()
            print data
            
            data_arr = data.split("\n")
            
            decoded = base64.b64decode(data_arr[0])
            decrypted = PubPvtKey.decrypt(self.key, decoded)
            credentials = decrypted.split(":")            
                        
            command = data_arr[1]
                    
            if self.authenticate(credentials[0], credentials[1]):           
                print "Permission granted. Running '%s' as '%s'..." % (command, credentials[0])
                cmd = "su - %s -c '%s'" % (credentials[0], command)
                print cmd
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                output, error = process.communicate()
                print output
                
                return output
            else:
                print "Permission denied!"
                
                request.setResponseCode(403)
                return "Permission denied!"
        except Exception, err:
            print(err)
            
            request.setResponseCode(400)
            return "Bad Request" 


resource = Impersonator()

path = os.path.dirname(os.path.realpath(__file__))
with cd(path):
    if __name__ == "__main__":
        port = 8123
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
            
        root = Resource()
        root.putChild("impersonate", resource)
        factory = Site(root)
        reactor.listenTCP(port, factory)
        reactor.run()

