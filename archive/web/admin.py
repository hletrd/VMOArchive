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




admin.site.register(models.VMODocument, DocumentAdmin)
admin.site.register(models.VMOMember, MemberAdmin)
admin.site.register(models.VMOSeminar, SeminarAdmin)
admin.site.register(models.VMOStatusSharing, StatusSharingAdmin)


'''class VMOFile(models.Model):
	#file = models.FileField(upload_to=settings.MEDIA_ROOT)
	file = models.FileField()
	path_raw = models.TextField(default='')
	name = models.TextField(default='')
	metadata = models.TextField(default='')

class VMOCategory(models.Model):
	name = models.CharField(max_length=100, default='')

class VMODocument(models.Model):
	files = models.ManyToManyField(VMOFile)
	datetime = models.DateTimeField()
	title = models.TextField()
	content = models.TextField()
	category = models.ForeignKey(VMOCategory, on_delete=models.CASCADE, null=True)

class VMOMember(models.Model):
	name = models.CharField(default='', max_length=100)
	birthday = models.DateField()
	phone = models.TextField()
	email = models.EmailField()

class VMOSeminar(models.Model):
	member = models.ForeignKey(VMOMember, on_delete=models.RESTRICT)
	date = models.DateField()

class VMOStatusSharing(models.Model):
	member = models.ForeignKey(VMOMember, on_delete=models.RESTRICT)
	date = models.DateField()
'''