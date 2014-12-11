from django.conf.urls import patterns, url
from users import views

urlpatterns = patterns('users.views',
    
    url(r'login/?', views.Login.as_view()), 
    url(r'logout/?', views.Logout.as_view()),  
    url(r'profile/?', views.Profile.as_view()), 
    url(r'password/?', views.Password.as_view()), 
    url(r'contacts/(?P<contact_id>[^/]+)/?', views.Contacts.as_view()),
    url(r'contacts/?', views.Contacts.as_view()), 
    url(r'groups/(?P<group_id>[^/]+)/?', views.GroupDetail.as_view()),
    url(r'groups/?', views.Groups.as_view()),
    url(r'conversations/(?P<message_id>[^/]+)/?', views.Conversations.as_view()),
    url(r'conversations/?', views.Conversations.as_view()),
    url(r'messages/(?P<conversation_id>[^/]+)/?', views.Messages.as_view()),  
    url(r'', views.Register.as_view()),    
)
