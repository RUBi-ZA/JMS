from django.db import models

class CharNullField(models.CharField): #subclass the CharField
    description = "CharField that stores NULL but returns ''"
    __metaclass__ = models.SubfieldBase #this ensures to_python will be called
    
    
    def to_python(self, value):  #this is the value right out of the db, or an instance
        if isinstance(value, models.CharField): #if an instance, just return the instance
            return value 
        if value == None:   # if the db has a NULL (==None in Python)
            return ""  # convert it into the Django-friendly '' string
        else:
            return value # otherwise, return just the value

    
    def get_prep_value(self, value):  # catches value right before sending to db
        if value == "":     #if Django tries to save '' string, send the db None (NULL)
            return None
        else:
            return value #otherwise, just pass the value