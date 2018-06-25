from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.conf import settings

from utilities.security.cryptography import PubPvtKey
from filemanager.models import FileManagerSettings

import json, requests


class LinuxBackend(ModelBackend):

    impersonator_settings = settings.JMS_SETTINGS["impersonator"]
    impersonator_endpoint = "http://%s:%s/tokens" % (
        impersonator_settings["host"],
        impersonator_settings["port"]
    )

    def authenticate(self, username=None, password=None):
        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist, ex:
            user = User.objects.create(username=username, email="", password="")

        payload = {
            "username": username,
            "password": password
        }

        token = self.linux_auth(payload)

        if token:
            fm_settings, created = FileManagerSettings.objects.get_or_create(User=user)

            fm_settings.ServerPass = token
            fm_settings.save()

            return user
        else:
            return None

    def linux_auth(self, payload):
        r = requests.post(self.impersonator_endpoint, json=payload)
        if r.status_code == requests.codes.ok:
            return r.text
        else:
            return None
