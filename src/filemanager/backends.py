from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.conf import settings

from utilities.io.impersonator import Impersonator
from filemanager.models import FileManagerSettings


class ImpersonatorBackend(ModelBackend):

    def authenticate(self, username=None, password=None):
        config = settings.JMS_SETTINGS["impersonator"]

        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist, ex:
            user = User.objects.create(username=username, email="", password="")

        client = Impersonator(config["host"], config["port"])

        try:
            token = client.login(username, password)
        except Exception, ex:
            print str(ex)
            token = None

        return self.create_session(user, token) if token else None

    def create_session(self, user, token):
        fm_settings, created = FileManagerSettings.objects.get_or_create(User=user)

        fm_settings.ServerPass = token
        fm_settings.save()

        return user
