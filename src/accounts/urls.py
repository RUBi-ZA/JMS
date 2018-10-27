from django.conf.urls import url
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from accounts.views import ProfileDetail, PasswordDetail, CredentialsDetail

urlpatterns = [
    url(r'profile/?', ProfileDetail.as_view(), name='profile_detail'),
    url(r'password/?', PasswordDetail.as_view(), name='password_detail'),
    url(r'credentials/?', CredentialsDetail.as_view(), name='credentials_detail'),
    url(r'^token/obtain/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
]