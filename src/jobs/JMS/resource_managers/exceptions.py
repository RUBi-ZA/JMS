from django.conf import settings
from datetime import datetime

#set up logger
#import logging
#logging.basicConfig(filename=settings.JMS_SETTINGS["resource_manager"]["log_file"],
#level=logging.ERROR)



class ResourceManagerException(Exception):
    
    def __init__(self, message):
        super(ResourceManagerException, self).__init__(message)
        
        #log error
        #logging.error("%s ResourceManagerException:\n%s\n\n" % (str(datetime.now()), message))



class NotUpdatedException(Exception):
    
    def __init__(self, message):
        super(NotUpdatedException, self).__init__(message)
        
        #log error
        #logging.error("%s NotUpdatedException:\n%s\n\n" % (str(datetime.now()), message))



class NotCreatedException(Exception):
    
    def __init__(self, message):
        super(NotCreatedException, self).__init__(message)
        
        #log error
        #logging.error("%s NotCreatedException:\n%s\n\n" % (str(datetime.now()), message))



class NotDeletedException(Exception):
    
    def __init__(self, message):
        super(NotDeletedException, self).__init__(message)
        
        #log error
        #logging.error("%s NotDeletedException:\n%s\n\n" % (str(datetime.now()), message))



class NotRestartedException(Exception):
    
    def __init__(self, message):
        super(NotRestartedException, self).__init__(message)
        
        #log error
        #logging.error("%s NotRestartedException:\n%s\n\n" % (str(datetime.now()), message))