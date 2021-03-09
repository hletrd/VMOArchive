from django import forms
#from multiupload.fields import MultiFileField
# Register your models here.

from . import models
from django.forms import ModelChoiceField

class upload_form(forms.Form):
	title = forms.CharField(label='제목', max_length=1000)
	content = forms.CharField(label='내용', max_length=1000, required=False)
	date = forms.DateTimeField(input_formats=['%Y-%m-%d'])
	file = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

	'''file = MultiFileField(label='파일',
		min_num=1,
		max_num=20,
		max_file_size=1024*1024*1024
	)'''

class login_form(forms.Form):
	userid = forms.RegexField(label='아이디', max_length=50, regex=r'^[a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ0-9_\-+.!@#$%\^&*()=`~\[\]{}\\|;:\'"<>,/?]{2,50}$')
	password = forms.RegexField(label='비밀번호', max_length=200, regex=r'.{6,200}')

class member_form(forms.Form):
	name = forms.CharField(label='이름', max_length=100)
	birthday = forms.DateField(label='생일', input_formats=['%m%d'], required=False)
	phone = forms.RegexField(label='전화번호', regex=r'^0[0-9]{1,2}-[0-9]{3,4}-[0-9]{4}', required=False)
	email = forms.EmailField(label='이메일', required=False)
	email_reminder = forms.EmailField(label='Reminder 수신 이메일', required=False)

class mail_form(forms.Form):
	recipient = forms.EmailField(label='Recipient')
	range_ = forms.IntegerField(min_value=0, max_value=10)
	subject = forms.CharField(label='Subject', max_length=200)
	content = forms.CharField(label='Content', max_length=2000)

class NameChoiceField(ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.name

class seminar_form(forms.Form):
	member = NameChoiceField(queryset=models.VMOMember.objects.all(), to_field_name='id', widget=forms.Select(attrs={'class': 'form-control'}))
	date = forms.DateField(label='날짜', input_formats=['%Y-%m-%d'])


