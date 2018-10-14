from django.conf.urls import url 
from filemanager import views
 
urlpatterns = [
	url(r'filemanager', views.index, name='index'),	
	url(r'directory', views.DirectoryDetail.as_view()),
	url(r'operation/(?P<op>[^/]+)/?', views.Operation.as_view()),
	url(r'jobstages/(?P<job_stage_id>[^/]+)/?', views.FileDetail.as_view()),
	url(r'transfer', views.FileTransfer.as_view()),
	url(r'settings', views.SettingsDetail.as_view()),
]
