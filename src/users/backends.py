from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

import pexpect

class LinuxBackend(ModelBackend):
    
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)            
            
            if self.linux_auth(username, password):
                user.set_password(password)
                user.userprofile.Code = password
                user.userprofile.save()
                user.save()
                return user
            
        except User.DoesNotExist:
        	
            if self.linux_auth(username, password):
        	    user = User.objects.create(username=username, email='', password=password)
        	    user.userprofile.Code = password
        	    user.userprofile.save()
        	    return user
            else:
                return None
            
        return None 
    
       
    def linux_auth(self, username=None, password=None):
        child = pexpect.spawn('su - %s' % username)
        child.expect('Password:')
        child.sendline (password)
        
    	i = child.expect (['su: Authentication failure', '[#\$] '], timeout=6)
        child.close(force=True)
            
        return i == 1
