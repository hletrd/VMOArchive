from django.urls import path, include
from . import views

urlpatterns = [
	path('', views.index),
	path('archive/upload', views.upload),
	path('archive/modify/<int:postid>', views.modify),
	path('archive/delete/<int:postid>', views.delete),
	path('archive', views.show_list),
	path('archive/<int:page>', views.show_list),
	path('archive/download/<str:fileid>', views.download),

	path('members', views.members),
	path('members/add', views.members_add),
	path('members/modify/<int:memberid>', views.members_modify),
	path('members/delete/<int:memberid>', views.members_delete),
	
	path('seminar', views.seminar),
	path('seminar/add', views.seminar_add),
	path('seminar/modify/<int:seminarid>', views.seminar_modify),
	path('seminar/delete/<int:seminarid>', views.seminar_delete),

	path('status-sharing', views.status_sharing),
	path('status-sharing/add', views.status_sharing_add),
	path('status-sharing/modify/<int:statussharingid>', views.status_sharing_modify),
	path('status-sharing/delete/<int:statussharingid>', views.status_sharing_delete),
	
	#path('init', views.init),
	#path('index', views.index_file),
	path('login', views.login_view),
	path('logout', views.logout_view),

	path('reminder', views.reminder),
	path('mass', views.mass),
]
