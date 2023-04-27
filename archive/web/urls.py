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
	path('seminar/change/<str:day>', views.seminar_change),
	path('seminar/archive/<int:seminarid>', views.seminar_archive),

	path('status-sharing', views.status_sharing),
	path('status-sharing/add', views.status_sharing_add),
	path('status-sharing/modify/<int:statussharingid>', views.status_sharing_modify),
	path('status-sharing/delete/<int:statussharingid>', views.status_sharing_delete),
	path('status-sharing/change/<str:day>', views.status_sharing_change),
	path('status-sharing/archive/<int:statussharingid>', views.status_sharing_archive),
	
	#path('init', views.init),
	#path('index', views.index_file),
	path('login', views.login_view),
	path('logout', views.logout_view),

	path('mass', views.mass),
	path('server', views.server),
	path('calendar/<str:calendarid>', views.calendar),
	path('calendar-add/<str:calendarid>', views.calendar_add),

	path('reminder', views.reminder),
	path('status-report', views.status_report),
	path('server/update', views.server_update),
	
	path('server/<path:action>', views.server_action),
	path('server/<path:action>', views.server_action),
	

	path('serverroom', views.serverroom),
	path('serverroom/graph', views.serverroom_graph),
	path('serverroom/get', views.serverroom_get),
	
]
