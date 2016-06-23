#!/usr/bin/env python
import os, sys, base64, subprocess
from datetime import datetime

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

sys.path.append("..")
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
            process = subprocess.Popen('su %s -c " ../venv/bin/python login.py %s %s"' % (username, username, password), shell=True, stdout=subprocess.PIPE)
            output, error = process.communicate()
            
            print output, error
            
            if output.endswith('0\n'):
                self.processes.add(username, password)
            else: 
                return False
            
        elif process != password:
            self.process.expire(username)
            return False
        
        return True
    
    
    
    def render_POST(self, request):
        try:
            data = request.content.read()
            data_lines = data.split("\n")
            
            #get credentials
            decoded = base64.b64decode(data_lines[0])
            decrypted = PubPvtKey.decrypt(self.key, decoded)
            credentials = decrypted.split(":")
            
            command = data_lines[1]
            prompt = "prompt" #legacy - should be phased out
            sudo = False
            
            if len(data_lines) > 2:
                prompt = data_lines[2] #legacy - should be phased out
                if len(data_lines) > 3:
                    sudo = data_lines[3].lower() == "true"
            
            #if command should be run as sudo
            if sudo:
                command = 'sudo -S %s' % command
            
            #activate python virtual environment
            command = 'source ../venv/bin/activate;%s;deactivate' % command
            
            if self.authenticate(credentials[0], credentials[1]):
                
                cmd = "su - %s -c '%s'" % (credentials[0], command)
                process = subprocess.Popen(cmd, shell=True, 
                    stdin=subprocess.PIPE, stderr=subprocess.PIPE, 
                    stdout=subprocess.PIPE, universal_newlines=True)
                    
                if sudo:
                    #handle sudo prompt
                    output, error = process.communicate(credentials[1] + "\n")
                else:
                    output, error = process.communicate()
                               
                output = str(output).strip("None")
                
                return output
            else:
                
                request.setResponseCode(403)
                return "Permission denied"
            
        except Exception, err:
            print str(err)
            
            request.setResponseCode(400)
            return "Bad Request" 



resource = Impersonator()

path = os.path.dirname(os.path.realpath(__file__))
with cd(path):

    if __name__ == "__main__":
        
        port = 8124
        if len(sys.argv) > 1:
            port = int(sys.argv[1])
            
        root = Resource()
        root.putChild("impersonate", resource)
        
        factory = Site(root)
        reactor.listenTCP(port, factory)
        reactor.run()
