from django.db import models
from django.conf import settings

# Create your models here.
class VMOFile(models.Model):
	#file = models.FileField(upload_to=settings.MEDIA_ROOT)
	file = models.FileField()
	path_raw = models.TextField(default='')
	name = models.TextField(default='')
	metadata = models.TextField(default='')

	class Meta:
		verbose_name = 'File'

class VMOCategory(models.Model):
	name = models.CharField(max_length=100, default='')
	class Meta:
		verbose_name = 'Category'

class VMODocument(models.Model):
	files = models.ManyToManyField(VMOFile)
	datetime = models.DateTimeField()
	title = models.TextField()
	content = models.TextField()
	category = models.ForeignKey(VMOCategory, on_delete=models.CASCADE, null=True)
	class Meta:
		verbose_name = 'Document'

class VMOMember(models.Model):
	name = models.CharField(default='', max_length=100)
	birthday = models.DateField()
	phone = models.TextField()
	email = models.EmailField()
	email_reminder = models.EmailField(default='')
	class Meta:
		verbose_name = 'Member'

class VMOSeminar(models.Model):
	member = models.ForeignKey(VMOMember, on_delete=models.RESTRICT)
	date = models.DateField()
	class Meta:
		verbose_name = 'Seminar'

class VMOStatusSharing(models.Model):
	member = models.ForeignKey(VMOMember, on_delete=models.RESTRICT)
	date = models.DateField()
	class Meta:
		verbose_name = 'Status sharing'
