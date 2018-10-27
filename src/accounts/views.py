# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.db import transaction

from helpers import create_session


class ProfileDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Get user profile details
        """
        profile = {
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'blurb': request.user.userprofile.blurb,
            'ssh_user': request.user.userprofile.ssh_user
        }

        return Response(profile)
    
    def put(self, request):
        """
        Update user profile details
        """
        data = request.data        
        user = request.user

        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.userprofile.blurb = data.get('blurb', user.userprofile.blurb)

        with transaction.atomic():
            user.save()
            user.userprofile.save()

        return Response()


class PasswordDetail(APIView):

    def put(self, request):
        """
        Update password
        """
        password = request.data['password']
        user = request.user
        user.set_password(password)
        user.save()

        return Response()


class CredentialsDetail(APIView):

    def put(self, request):
        """
        Update cluster credentials
        """
        request.user.userprofile.ssh_user = request.data['ssh_user']
        request.user.userprofile.ssh_private_key = request.data['ssh_private_key']

        try:
            create_session(request.user)
        except Exception as ex:
            return Response(data={'errorMessage': str(ex)}, status=500)
            
        return Response()
