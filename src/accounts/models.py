# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    blurb = models.TextField(null=True, blank=True)
    ssh_user = models.CharField(max_length=20, null=True, blank=True)
    ssh_private_key = models.TextField(null=True, blank=True)
    impersonator_token = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'UserProfiles'


def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance) 

post_save.connect(create_user_profile, sender=User) 