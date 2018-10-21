from django.conf.urls import url
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    url(r'^token/obtain/$', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
]