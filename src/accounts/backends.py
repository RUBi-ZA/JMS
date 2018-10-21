from __future__ import print_function

from django.conf import settings

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from impersonator.client import Impersonator


class ImpersonatorBackend(ModelBackend):

    def authenticate(self, username=None, password=None):
        user = User.objects.get(email=username)
        valid_password = check_password(password, user.password)

        return self.create_session(user) if valid_password else None


    def create_session(self, user):
        config = settings.JMS_SETTINGS["impersonator"]

        client = Impersonator(config["host"], config["port"])

        username = user.userprofile.ssh_user
        private_key = user.userprofile.ssh_private_key
        token = user.userprofile.impersonator_token

        client.token = token

        if token and self.validate_token(client, username):
            return user

        try:            
            token = client.login(username, private_key=private_key)
        except Exception, ex:
            print("Login")
            print(str(ex))
            token = None

        profile = user.userprofile
        profile.impersonator_token = token
        profile.save()
        
        return user
    

    def validate_token(self, client, username):
        try:
            response = client.execute('whoami')
            print(response)
            if response['out'] == '%s\n' % username:
                return True
            else:
                return False
        except Exception as ex:
            print("Validate")
            print(str(ex))
            return False