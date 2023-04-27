from django.contrib import admin

from . import models

class DocumentAdmin(admin.ModelAdmin):
	fields = ('title', 'datetime', 'content')
	list_display = ('title', 'datetime')

class MemberAdmin(admin.ModelAdmin):
	fields = ('name', 'birthday', 'phone', 'email')
	list_display = ('name', 'birthday', 'phone', 'email')

class SeminarAdmin(admin.ModelAdmin):
	fields = ('get_name', 'date')
	list_display = ('get_name', 'date')
	def get_name(self, obj):
		return obj.member.name

class StatusSharingAdmin(admin.ModelAdmin):
	fields = ('get_name', 'date')
	list_display = ('get_name', 'date')
	def get_name(self, obj):
		return obj.member.name

class CalendarAdmin(admin.ModelAdmin):
	fields = ('calendarid' 'get_name', 'starttime', 'endtime')
	list_display = ('calendarid' 'get_name', 'starttime', 'endtime')
	def get_name(self, obj):
		return obj.member.name




admin.site.register(models.VMODocument, DocumentAdmin)
admin.site.register(models.VMOMember, MemberAdmin)
admin.site.register(models.VMOSeminar, SeminarAdmin)
admin.site.register(models.VMOStatusSharing, StatusSharingAdmin)