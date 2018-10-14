from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
	url(r'^api/jms/', include('jobs.urls')),
	url(r'^api/users/', include('users.urls')),
	url(r'^api/auth/', include('authentication.urls')),
	url(r'^files/', include('filemanager.urls')),
    url(r'^admin/?', include(admin.site.urls)),
	url(r'^', include('interface.urls')),
]
