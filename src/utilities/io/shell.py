import pexpect, pxssh

class UserProcess:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
        self.login(username, password)
    
    
    def login(self, username, password):
        child = pexpect.spawn('su - %s' % username)
        child.expect("Password:")
        child.sendline(password)        

        i = child.expect(['su: Authentication failure', '[#\$] '], timeout=6)
        if i == 1:
            self.process = child
        else:
            raise Exception("Authentication failed")    
    
    
    def run_command(self, command, expect='[#\$] ', timeout=6):
        self.process.sendline(command)
        i = self.process.expect(expect, timeout=timeout)
        return '\n'.join(self.process.before.split('\n')[1:-1])    
    
    
    def flush(self):
        return '\n'.join((self.process.before.split('\n') + self.process.after.split('\n'))[1:-1]) 
        
    
    def close(self):
        self.process.close(force=True)



class RemoteProcess:

    def __init__(self, username, password, hostname="127.0.0.1"):
        self.username = username
        self.password = password
        self.hostname = hostname
        
        self.process = pxssh.pxssh()
        self.process.login(hostname, username, password)
    
    
    def run_command(self, command, expect='[#\$] ', timeout=6):
        self.process.sendline(command)
        self.process.prompt(timeout=6)
        # remove the first and last lines to cut off the terminal prompts
        return '\n'.join(self.process.before.split('\n')[1:-1])    
    
    
    def flush(self):
        return '\n'.join((self.process.before.split('\n') + self.process.after.split('\n'))[1:-1])  
        
    
    def logout(self):
        self.process.logout()
        
        
    def __del__(self):
        self.logout()