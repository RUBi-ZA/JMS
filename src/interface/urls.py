from django.conf.urls import url, include
from interface import views

urlpatterns = [
	url(r'^account/login/?', views.sign_in, name='sign_in'),	
	url(r'^account/logout/?', views.sign_out, name='sign_out'),	
	url(r'^workflows/visualize', views.workflow_visualizer, name='workflow_visualizer'),	
	url(r'^workflows', views.workflows, name='workflows'),
	url(r'^tools', views.tools, name='tools'),
	url(r'^jobs/?', views.jobs, name='jobs'),
	url(r'^settings/?', views.settings, name='settings'),
	url(r'^', views.index, name='index'),	
]
