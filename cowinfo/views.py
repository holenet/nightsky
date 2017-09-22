# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from django.conf import settings

from .models import DBFile
from .forms import DBFileForm
import os
import mimetypes
from wsgiref.util import FileWrapper
import urllib

def is_outer(user):
	return not user.groups.filter(name='cowinfo').exists()

def register(request):
	if request.user.is_authenticated():
		logout(request)
	if request.method=='POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = request.POST['username']
			password = request.POST['password1']
			user = authenticate(username=username, password=password)
			if user is not None:
				group = Group.objects.get(name='cowinfo')
				group.user_set.add(user)
				login(request, user)
				return HttpResponse()
	return HttpResponseBadRequest()

def db_list(request):
	if is_outer(user):
		response = HttpResponse()
		response.status_code = 999
		return response
	db_files = DBFile.objects.filter(author=request.user).order_by('-uploaded_at')
	queries = []
	
	for db_file in db_files:
	 	queries.append(str(db_file.uploaded_at))
	
	return JsonResponse(queries, safe=False)

def db_upload(request):
	if is_outer(user):
		response = HttpResponse()
		response.status_code = 999
		return response
	if request.method=='POST':
		form = DBFileForm(request.POST, request.FILES)
		if form.is_valid():
			db_file = form.save(commit=False)
			db_file.author = request.user
			db_file.save()
			return HttpResponse()
	return HttpResponseBadRequest()

def db_download(request, file_id):
	if is_outer(user):
		response = HttpResponse()
		response.status_code = 999
		return response
	db_file = get_object_or_404(DBFile, pk=file_id, author=request.user)
	file_name = os.path.basename(user_file.user_file.name)
	file_path = os.path.join(settings.MEDIA_ROOT, db_file.db_file.name)
	file_wrapper = FileWrapper(file(file_path, 'rb'))
	file_mimetype = mimetypes.guess_type(file_path)
	response = HttpResponse(file_wrapper, content_type=file_mimetype)
	response['X-Sendfile'] = file_path
	response['Content-Length'] = os.stat(file_path).st_size
	response['Content-Disposition'] = 'attachment; filename=%s' % urllib.quote(file_name.encode('utf-8'))
	return response
