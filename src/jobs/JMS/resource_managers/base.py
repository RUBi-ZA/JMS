'''
    The base class that all implemented resource managers should inherit from.
    
    This class provides the constructor and a small number of methods that can 
    be used in child classes. 
    
    All unimplemented methods must be overridden in child classes. Comments 
    within each method provide the required return values as well as the 
    exceptions that must be raised in the case of an error. 
    
    The specified objects and exceptions can be found in the objects.py and 
    exceptions.py files respectively.
'''

import requests

from objects import *
from exceptions import *

from django.conf import settings

class BaseResourceManager:
    
    def __init__(self, user):
        self.user = user
    
    def RunUserProcess(self, cmd, expect="prompt", sudo=False):
        payload = "%s\n%s\n%s\n%s" % (self.user.filemanagersettings.ServerPass, cmd, expect, str(sudo))
        r = requests.post("http://%s/impersonate" % settings.IMPERSONATOR_SETTINGS["url"], data=payload)
        return r.text
    
    def GetDashboard(self):
        return Dashboard(self.GetNodes(), self.GetQueue(), self.GetDiskUsage(settings.JMS_SETTINGS["JMS_shared_directory"]))
    
    def GetDiskUsage(self, path):
        out = self.RunUserProcess("df -h %s" % path)
        
        lines = out.split('\n')
        
        index = lines[0].index("Size")
        size = lines[1][index:index+5].strip()        
        used = lines[1][index+5:index+11].strip()
        available = lines[1][index+11:index+17].strip()
        
        return DiskUsage(size, available, used)
        
    def GetQueue(self):
        '''
        Success: return list of QueueItem objects
        Failure: raise ResourceManagerException 
        '''
        raise NotImplementedError
    
    def GetSettings(self):
        '''
        Success: return list of Data objects
        Failure: raise ResourceManagerException 
        '''
        raise NotImplementedError
        
    def UpdateSettings(self, settings):
        '''
        Success: return nothing
        Failure: raise NotUpdatedException 
        '''
        raise NotImplementedError
    
    def GetQueues(self, queue):
        '''
        Success: return list of Data objects
        Failure: raise ResourceManagerException 
        '''
        raise NotImplementedError
    
    def AddQueue(self, queue):
        '''
        Success: return nothing
        Failure: raise NotCreatedException 
        '''
        raise NotImplementedError
    
    def UpdateQueue(self, queue):
        '''
        Success: return nothing
        Failure: raise NotUpdatedException 
        '''
        raise NotImplementedError
    
    def DeleteQueue(self, queue):
        '''
        Success: return nothing
        Failure: raise NotDeletedException 
        '''
        raise NotImplementedError
    
    def GetAdministrators(self):
        '''
        Success: return list of Data objects
        Failure: raise ResourceManagerException 
        '''
        raise NotImplementedError
    
    def AddAdministrator(self, Administrators):
        '''
        Success: return nothing
        Failure: raise NotCreatedException 
        '''
        raise NotImplementedError
    
    def UpdateAdministrator(self, Administrators):
        '''
        Success: return nothing
        Failure: raise NotUpdatedException 
        '''
        raise NotImplementedError
    
    def DeleteAdministrator(self, Administrators):
        '''
        Success: return nothing
        Failure: raise NotDeletedException 
        '''
        raise NotImplementedError
    
    def GetNodes(self):
        '''
        Success: return list of Node objects
        Failure: raise ResourceManagerException 
        '''
        raise NotImplementedError
    
    def AddNode(self, node):
        '''
        Success: return nothing
        Failure: raise NotCreatedException 
        '''
        raise NotImplementedError
    
    def UpdateNode(self, node):
        '''
        Success: return nothing
        Failure: raise NotUpdatedException 
        '''
        raise NotImplementedError
    
    def DeleteNode(self, id):
        '''
        Success: return nothing
        Failure: raise NotDeletedException 
        '''
        raise NotImplementedError
    
    def Stop(self):
        '''
        Success: return nothing
        Failure: raise NotStoppedException 
        '''
        raise NotImplementedError
    
    def Start(self):
        '''
        Success: return nothing
        Failure: raise NotStartedException 
        '''
        raise NotImplementedError
    
    def Restart(self):
        '''
        Success: return nothing
        Failure: raise NotRestartedException 
        '''
        raise NotImplementedError
    
    
    def GetDefaultResources(self):
        '''
        Success: return DataSection object
        Failure: raise Exception
        '''
        raise NotImplementedError
    
    
    def CreateJobScript(self):
        '''
        Success: return path to job script
        Failure: raise NotCreatedException 
        '''
        raise NotImplementedError
        
    def ExecuteJobScript(self, cmd):
        '''
        Success: return job id
        Failure: raise NotExecutedException 
        '''
        raise NotImplementedError


