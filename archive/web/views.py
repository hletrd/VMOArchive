from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.core.files import File
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string

from . import forms
from . import models

import random, string
import datetime
import os
import re

import PyPDF2
from pptx import Presentation

import threading, ssl, smtplib
from email.mime.text import MIMEText
from email.header import Header

# Create your views here.
def index(request):
	return show_list(request)

def user_is_staff(user):
	return user.is_staff

class SendMail(threading.Thread):
	def __init__(self, title, content, to):
		threading.Thread.__init__(self)
		msg = MIMEText(content.encode('utf-8'), 'html', 'utf-8')
		msg['Subject'] = Header(title, 'utf-8')
		msg['From'] = settings.MAIL_ID + '@' + settings.MAIL_DOMAIN
		msg['To'] = to
		self.msg = msg

	def run(self):
		context = ssl.SSLContext(ssl.PROTOCOL_TLS)
		connection = smtplib.SMTP(settings.MAIL_SMTP, settings.MAIL_PORT)
		connection.ehlo()
		connection.starttls(context=context)
		connection.ehlo()
		connection.login(settings.MAIL_ID + '@' + settings.MAIL_DOMAIN, settings.MAIL_PW)
		connection.sendmail(self.msg['From'], self.msg['To'], self.msg.as_string())
		connection.quit()

def reminder(request):
	if request.GET.get('key', '') == settings.KEY:
		members = models.VMOMember.objects.all()
		recipients = []
		for i in members:
			if re.match(r'[^@]+@[^.]+\..*', i.email_reminder):
				recipients.append(i.email_reminder)

		title = 'Seminar Reminder'

		seminar = models.VMOSeminar.objects.all()[:5]
		statussharing = models.VMOStatusSharing.objects.all()[:5]
		content = render_to_string('reminder.html', {'seminar': seminar, 'statussharing': statussharing})

		result = 'Sent mail: <br/><br/>' + content
		result += '<br/><br/>To: '
		
		for i in recipients:
			SM = SendMail(title, content, i)
			SM.start()
			result += i + ', '
		return HttpResponse(result)
	else:
		return redirect('/')

@login_required
def mass(request):
	if request.method == 'POST':
		form = forms.mail_form(request.POST)
		if form.is_valid():
			if form.cleaned_data.get('recipient') == 'mass@altair.snu.ac.kr':
				recipients = [settings.EMAIL_PROF]
			elif form.cleaned_data.get('recipient') == 'masss@altair.snu.ac.kr':
				recipients = []
			else:
				return render(request, 'mail_form.html', {'error': '잘못된 입력값이 있습니다.', 'range': form.cleaned_data.get('range_', 2), 'subject': form.cleaned_data.get('subject', ''), 'content': form.cleaned_data.get('content', '')})
			members = models.VMOMember.objects.all()
			for i in members:
				if re.match(r'[^@]+@[^.]+\..*', i.email_reminder):
					recipients.append(i.email_reminder)

			subject = form.cleaned_data.get('subject', '(No subject)')
			content = form.cleaned_data.get('content', '(No content)').replace("\n", "<br/>")

			for i in recipients:
				SM = SendMail(subject, content, i)
				SM.start()
			return render(request, 'jumbotron.html', {'output': 'Mail successfully sent to: {}'.format(', '.join(recipients))})
		else:
			return render(request, 'mail_form.html', {'error': '잘못된 입력값이 있습니다.', 'range': form.cleaned_data.get('range_', 2), 'subject': form.cleaned_data.get('subject', ''), 'content': form.cleaned_data.get('content', '')})
	else:
		return render(request, 'mail_form.html', {'range': 2})

@login_required
@user_passes_test(user_is_staff)
def upload(request):
	if request.method == 'POST':
		form = forms.upload_form(request.POST, request.FILES)
		if form.is_valid():
			post = models.VMODocument(title=form.cleaned_data['title'], content=form.cleaned_data['content'])
			post.datetime = form.cleaned_data['date']
			post.save()
			files = request.FILES.getlist('file')
			for i in files:
				path = create_random_path(10)
				file = models.VMOFile(path_raw=path, name=i.name, metadata='')
				i.name = path
				file.file = i
				file.save()
				create_index(file)
				post.files.add(file)
			post.save()
			return redirect('/')
		else:
			return render(request, 'upload.html', {'date': form.cleaned_data.get('date', datetime.datetime.now()).strftime('%Y-%m-%d'), 'title': form.cleaned_data.get('title', ''), 'content': form.cleaned_data.get('content', ''), 'error': '잘못된 입력값이 있습니다.', 'url': '/archive/upload'})
	else:
		return render(request, 'upload.html', {'date': datetime.datetime.now().strftime('%Y-%m-%d'), 'url': '/archive/upload'})

@login_required
@user_passes_test(user_is_staff)
def modify(request, postid):
	post = models.VMODocument.objects.get(id=postid)
	if post is not None:
		if request.method == 'POST':
			form = forms.upload_form(request.POST, request.FILES)
			if form.is_valid():
				post.title = form.cleaned_data['title']
				post.content = form.cleaned_data['content']
				post.datetime = form.cleaned_data['date']
				post.save()
				file_prev = request.POST.getlist('file_prev[]')
				for i in post.files.all():
					if not str(i.id) in file_prev:
						remove = post.files.get(id=i.id)
						print(remove.file.path)
						if os.path.isfile(remove.file.path):
							os.remove(remove.file.path)
						remove.delete()
					else:
						create_index(i)
				files = request.FILES.getlist('file')
				for i in files:
					path = create_random_path(10)
					file = models.VMOFile(path_raw=path, name=i.name, metadata='')
					i.name = path
					file.file = i
					file.save()
					create_index(file)
					post.files.add(file)
				post.save()
				return redirect('/archive')
			else:
				return render(request, 'upload.html', {'date': form.cleaned_data.get('date', datetime.datetime.now()).strftime('%Y-%m-%d'), 'title': form.cleaned_data.get('title', ''), 'content': form.cleaned_data.get('content', ''), 'error': '잘못된 입력값이 있습니다.', 'files': post.files, 'url': '/archive/modify/{}'.format(postid)})
		else:
			return render(request, 'upload.html', {'date': post.datetime.strftime('%Y-%m-%d'), 'title': post.title, 'content': post.content, 'files': post.files, 'url': '/archive/modify/{}'.format(postid)})
	else:
		return redirect('/archive')

@login_required
@user_passes_test(user_is_staff)
def delete(request, postid):
	post = models.VMODocument.objects.get(id=postid)
	if post is not None:
		if request.method == 'POST':
			for i in post.files.all():
				if os.path.isfile(i.file.path):
					os.remove(i.file.path)
				i.delete()
			post.delete()
			return redirect('/archive')
		else:
			return render(request, 'delete.html', {'name': post.title, 'url': '/archive/delete/{}'.format(postid)})
	else:
		return redirect('/archive') #404

@login_required
@user_passes_test(user_is_staff)
def init(request):
	import sqlite3
	import requests

	db = '../posts.db'
	conn = sqlite3.connect(db)

	models.VMODocument.objects.all().delete()
	models.VMOFile.objects.all().delete()

	c = conn.cursor()

	c.execute('SELECT * FROM posts ORDER BY `id` DESC;')
	posts = c.fetchall()

	for i in posts:
		content = ''
		if i[3] != 'None':
			content = i[3].rstrip()
		post = models.VMODocument(title=i[2], content=content)
		post.datetime = i[1]
		post.save()
		c.execute('SELECT * FROM files where postid=?', (i[0],))
		files = c.fetchall()
		for j in files:
			file = models.VMOFile(path_raw=j[2], name=j[1], metadata='')
			file.file = File(open('./files/' + j[2], 'rb'), name=j[2])
			file.save()
			post.files.add(file)
		post.save()
	return redirect('/archive')


@login_required
@user_passes_test(user_is_staff)
def index_file(request):
	files = models.VMOFile.objects.all()
	for i in files:
		create_index(i)
	return redirect('/')

def create_index(file):
	ext = file.name.split('.')[-1].lower()
	path = settings.MEDIA_ROOT + '/' + file.path_raw
	text = ''
	if ext == 'pptx':
		try:
			reader = Presentation(path)
			for slide in reader.slides:
				for shape in slide.shapes:
					if hasattr(shape, 'text'):
						text += shape.text + ' '
		except:
			print(file.path_raw)
			print(file.name)
			pass
	elif ext == 'pdf':
		reader = PyPDF2.PdfFileReader(path)
		for page in range(0, reader.getNumPages()):
			text += reader.getPage(page).extractText() + ' '
	file.metadata = text
	file.save()

@login_required
def show_list(request, page=1):
	search_text = request.GET.get('search', '')
	if search_text != '':
		search_inputs = search_text.split(' ')
		query = Q()
		for i in search_inputs:
			query |= Q(files__name__contains=i) | Q(title__contains=i) | Q(content__contains=i) | Q(files__metadata__contains=i)
		posts = models.VMODocument.objects.filter(query).order_by('-id')
	else:
		posts = models.VMODocument.objects.all().order_by('-id')

	page = int(page)
	paginator = Paginator(posts, 20)
	posts = paginator.get_page(page)

	num_pages = paginator.num_pages
	last_page = min(page+3, num_pages)+1
	pages = range(max(page-3, 1), last_page)

	for i in posts:
		i.content = i.content.replace('\n', '<br/>')

	return render(request, 'archive.html', {'posts': posts, 'pages': pages, 'num_pages': num_pages, 'last_page': last_page, 'search': search_text})

@login_required
def download(request, fileid):
	file = models.VMOFile.objects.get(path_raw=fileid)
	if file is not None:
		return FileResponse(file.file, filename=file.name)
	else:
		return redirect('/archive')

def create_random_path(length=10):
	path = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
	return path

def handle_file(f):
	path = create_random_path(10)
	file = models.VMOFile.objects.create(path_raw=path, name=f.name, metadata='', file=f)
	#with open(settings.MEDIA_ROOT + '/' + path, 'wb+') as dest:
	#	for chunk in f.chunks():
	#		dest.write(chunk)
	return file

def login_view(request):
	if request.user.is_authenticated:
		return redirect('/')
	if request.method == 'POST':
		form = forms.login_form(request.POST)
		if form.is_valid():
			user = authenticate(request, username=form.cleaned_data['userid'], password=form.cleaned_data['password'])
			if user is not None:
				login(request, user)
				return redirect(request.GET.get('next', '/'))
			else:
				return render(request, 'login.html', {'error': '로그인에 실패했습니다.'})
		else:
			return render(request, 'login.html', {'error': '로그인에 실패했습니다.'})
	return render(request, 'login.html', {'next': request.GET.get('next')})

@login_required
def logout_view(request):
	logout(request)
	return redirect('/')

@login_required
def members(request):
	members = models.VMOMember.objects.all()
	return render(request, 'members.html', {'members': members})

@login_required
@user_passes_test(user_is_staff)
def members_add(request):
	if request.method == 'POST':
		form = forms.member_form(request.POST)
		if form.is_valid():
			member = models.VMOMember(name=form.cleaned_data['name'], birthday=form.cleaned_data['birthday'], phone=form.cleaned_data['phone'], email=form.cleaned_data['email'],email_reminder=form.cleaned_data['email_reminder'])
			member.save()
			return redirect('/members')
		else:
			return render(request, 'members_form.html', {'url': '/members/add', 'name': form.cleaned_data.get('name', ''), 'birthday': form.cleaned_data.get('birthday', ''), 'phone': form.cleaned_data.get('phone', ''), 'email': form.cleaned_data.get('email', ''), 'email_reminder': form.cleaned_data.get('email_reminder', ''), 'error': '잘못된 입력값이 있습니다.'})
	else:
		return render(request, 'members_form.html', {'url': '/members/add'})

@login_required
@user_passes_test(user_is_staff)
def members_modify(request, memberid):
	member = models.VMOMember.objects.get(id=memberid)
	if member is not None:
		if request.method == 'POST':
			form = forms.member_form(request.POST)
			if form.is_valid():
				member.name = form.cleaned_data['name']
				member.birthday = form.cleaned_data['birthday']
				member.phone = form.cleaned_data['phone']
				member.email = form.cleaned_data['email']
				member.email_reminder = form.cleaned_data['email_reminder']
				member.save()
				return redirect('/members')
			else:
				return render(request, 'members_form.html', {'url': '/members/modify/{}'.format(memberid), 'name': form.cleaned_data.get('name', ''), 'birthday': form.cleaned_data.get('birthday', ''), 'phone': form.cleaned_data.get('phone', ''), 'email': form.cleaned_data.get('email', ''), 'email_reminder': form.cleaned_data.get('email_reminder', ''), 'error': '잘못된 입력값이 있습니다.'})
		else:
			return render(request, 'members_form.html', {'url': '/members/modify/{}'.format(memberid), 'name': member.name, 'birthday': member.birthday.strftime("%m%d"), 'phone': member.phone, 'email': member.email, 'email_reminder': member.email_reminder})
	else:
		return redirect('/members')

@login_required
@user_passes_test(user_is_staff)
def members_delete(request, memberid):
	member = models.VMOMember.objects.get(id=memberid)
	if member is not None:
		if request.method == 'POST':
			member.delete()
			return redirect('/members')
		else:
			return render(request, 'delete.html', {'name': member.name, 'url': '/members/delete/{}'.format(memberid)})
	else:
		return redirect('/members')

#@login_required
def seminar(request):
	seminar = models.VMOSeminar.objects.all()
	return render(request, 'seminar.html', {'seminar': seminar, 'pagename': 'Seminar 일정', 'url': '/seminar'})

@login_required
@user_passes_test(user_is_staff)
def seminar_add(request):
	if request.method == 'POST':
		form = forms.seminar_form(request.POST)
		if form.is_valid():
			seminar = models.VMOSeminar(member=form.cleaned_data.get('member'), date=form.cleaned_data['date'])
			seminar.save()
			return redirect('/seminar')
		return render(request, 'seminar_form.html', {'form': form, 'url': '/seminar/add', 'member': form.cleaned_data.get('member', ''), 'date': form.cleaned_data.get('date', datetime.datetime.now()).strftime('%Y-%m-%d'), 'error': '잘못된 입력값이 있습니다.'})
	else:
		form = forms.seminar_form()
		return render(request, 'seminar_form.html', {'form': form, 'url': '/seminar/add'})

@login_required
@user_passes_test(user_is_staff)
def seminar_modify(request, seminarid):
	seminar = models.VMOSeminar.objects.get(id=seminarid)
	if seminar is not None:
		if request.method == 'POST':
			form = forms.seminar_form(request.POST, initial={'member': seminar.member})
			if form.is_valid():
				seminar.member = form.cleaned_data.get('member')
				seminar.date = form.cleaned_data['date']
				seminar.save()
				return redirect('/seminar')
			return render(request, 'seminar_form.html', {'form': form, 'url': '/seminar/modify/{}'.format(seminarid), 'member': form.cleaned_data.get('member', None), 'date': form.cleaned_data.get('date', datetime.datetime.now()).strftime('%Y-%m-%d'), 'error': '잘못된 입력값이 있습니다.'})
		else:
			form = forms.seminar_form(initial={'member': seminar.member})
			return render(request, 'seminar_form.html', {'form': form, 'url': '/seminar/modify/{}'.format(seminarid), 'member': seminar.member, 'date': seminar.date.strftime("%Y-%m-%d")})
	else:
		return redirect('/seminar')

@login_required
@user_passes_test(user_is_staff)
def seminar_delete(request, seminarid):
	seminar = models.VMOSeminar.objects.get(id=seminarid)
	if seminar is not None:
		if request.method == 'POST':
			seminar.delete()
			return redirect('/seminar')
		else:
			return render(request, 'delete.html', {'name': seminar.member.name + '의 ' + seminar.date.strftime("%m월 %d일 seminar"), 'url': '/seminar/delete/{}'.format(seminarid)})
	else:
		return redirect('/seminar')

@login_required
@user_passes_test(user_is_staff)
def seminar_change(request, day):
	seminar = models.VMOSeminar.objects.all()
	try:
		day = int(day)
	except:
		day = 0
	days = datetime.timedelta(days=day)
	for i in seminar:
		i.date += days
		i.save()
	return redirect('/seminar')

@login_required
@user_passes_test(user_is_staff)
def seminar_archive(request, seminarid):
	seminar = models.VMOSeminar.objects.get(id=seminarid)
	if seminar is not None:
		form = forms.upload_form()
		return render(request, 'upload.html', {'date': seminar.date.strftime("%Y-%m-%d"), 'title': 'Status Report {}'.format(seminar.date.strftime("%Y-%m-%d")), 'content': 'Status Report\n{}\n\n{}'.format(seminar.date.strftime("%Y-%m-%d"), seminar.member.name), 'url': '/archive/upload'})
	return redirect('/seminar')

#@login_required
def status_sharing(request):
	statussharing = models.VMOStatusSharing.objects.all()
	return render(request, 'seminar.html', {'seminar': statussharing, 'pagename': 'Status sharing 일정', 'url': '/status-sharing'})

@login_required
@user_passes_test(user_is_staff)
def status_sharing_add(request):
	if request.method == 'POST':
		form = forms.seminar_form(request.POST)
		if form.is_valid():
			status_sharing = models.VMOStatusSharing(member=form.cleaned_data.get('member'), date=form.cleaned_data['date'])
			status_sharing.save()
			return redirect('/status-sharing')
		return render(request, 'seminar_form.html', {'form': form, 'url': '/status-sharing/add', 'member': form.cleaned_data.get('member', ''), 'date': form.cleaned_data.get('date', datetime.datetime.now()).strftime('%Y-%m-%d'), 'error': '잘못된 입력값이 있습니다.'})
	else:
		form = forms.seminar_form()
		return render(request, 'seminar_form.html', {'form': form, 'url': '/status-sharing/add'})

@login_required
@user_passes_test(user_is_staff)
def status_sharing_modify(request, statussharingid):
	statussharing = models.VMOStatusSharing.objects.get(id=statussharingid)
	if statussharing is not None:
		if request.method == 'POST':
			form = forms.seminar_form(request.POST, initial={'member': statussharing.member})
			if form.is_valid():
				statussharing.member = form.cleaned_data.get('member')
				statussharing.date = form.cleaned_data['date']
				statussharing.save()
				return redirect('/status-sharing')
			return render(request, 'seminar_form.html', {'form': form, 'url': '/status-sharing/modify/{}'.format(statussharingid), 'member': form.cleaned_data.get('member', None), 'date': form.cleaned_data.get('date', datetime.datetime.now()).strftime('%Y-%m-%d'), 'error': '잘못된 입력값이 있습니다.'})
		else:
			form = forms.seminar_form(initial={'member': statussharing.member})
			return render(request, 'seminar_form.html', {'form': form, 'url': '/status-sharing/modify/{}'.format(statussharingid), 'member': statussharing.member, 'date': statussharing.date.strftime("%Y-%m-%d")})
	else:
		return redirect('/status-sharing')

@login_required
@user_passes_test(user_is_staff)
def status_sharing_delete(request, statussharingid):
	statussharing = models.VMOStatusSharing.objects.get(id=statussharingid)
	if statussharing is not None:
		if request.method == 'POST':
			statussharing.delete()
			return redirect('/status-sharing')
		else:
			return render(request, 'delete.html', {'name': statussharing.member.name + '의 ' + statussharing.date.strftime("%m월 %d일 status sharing"), 'url': '/status-sharing/delete/{}'.format(statussharingid)})
	else:
		return redirect('/status-sharing')

@login_required
@user_passes_test(user_is_staff)
def status_sharing_change(request, day):
	statussharing = models.VMOStatusSharing.objects.all()
	try:
		day = int(day)
	except:
		day = 0
	days = datetime.timedelta(days=day)
	for i in statussharing:
		i.date += days
		i.save()
	return redirect('/status-sharing')

@login_required
@user_passes_test(user_is_staff)
def status_sharing_archive(request, statussharingid):
	statussharing = models.VMOStatusSharing.objects.get(id=statussharingid)
	if statussharing is not None:
		form = forms.upload_form()
		return render(request, 'upload.html', {'date': statussharing.date.strftime("%Y-%m-%d"), 'title': '', 'content': 'VMOLAB Seminar\n{}\n\n'.format(statussharing.date.strftime("%Y-%m-%d")), 'url': '/archive/upload'})
	return redirect('/statussharing')