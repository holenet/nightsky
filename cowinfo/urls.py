from django.conf.urls import url
from . import views

app_name = 'cowinfo'
urlpatterns = [
	url(r'^register/$', views.register, name='register'),

	url(r'^db/$', views.db_list, name='db_list'),
	url(r'^db/upload/$', views.db_upload, name='db_upload'),
	url(r'^db/download/(?P<file_id>[0-9]+)/$', views.db_download, name='db_download'),
]
