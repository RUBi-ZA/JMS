from __future__ import print_function

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from helpers import create_session


class ImpersonatorBackend(ModelBackend):

    def authenticate(self, username=None, password=None):
        user = User.objects.get(email=username)
        valid_password = check_password(password, user.password)

        try:
            user = create_session(user)
        except Exception as ex:
            print(str(ex))
            user = None

        return user
