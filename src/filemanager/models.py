from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save

class FileManagerSettings(models.Model):
    HomeDirectory = models.TextField(default="/")
    AceTheme = models.CharField(max_length=30, default="chrome")
    FontSize = models.IntegerField(default=11)
    ServerPass = models.CharField(max_length=1024, null=True, blank=True)    
    User = models.OneToOneField(User)
    
    class Meta:
        db_table = "FileManagerSettings"
    
    
def create_settings(sender, instance, created, **kwargs):  
    if created:
       profile, created = FileManagerSettings.objects.get_or_create(User=instance)
	

post_save.connect(create_settings, sender=User) 
