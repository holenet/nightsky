from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.encoding import smart_str
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse
from .models import Post, Comment, UserFile
from .forms import PostForm, CommentForm, UserFileForm
import os
import mimetypes
from wsgiref.util import FileWrapper
import urllib
import json


def is_outer(user):
    return not user.groups.filter(name='NightSky').exists()


def redirect_next(url_name, next_url_name, **kwargs):
    url = reverse(url_name)
    next_url = reverse(next_url_name, kwargs=kwargs)
    return HttpResponseRedirect(url + '?next=' + next_url)


def register(request):
    if request.user.is_authenticated():
        logout(request)
        redirect('cloud:register')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                group = Group.objects.get(name='NightSky')
                group.user_set.add(user)
                login(request, user)
                return redirect('cloud:post_list')
            else:
                return redirect('cloud:register')
    else:
        form = UserCreationForm()
    return render(request, 'cloud/register.html', {'form': form})


def post_list(request):
    if is_outer(request.user):
        return redirect_next('login', 'cloud:post_list')
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'cloud/post_list.html', {'posts': posts})


def post_detail(request, post_id):
    if is_outer(request.user):
        return redirect_next('login', 'cloud:post_detail', post_id=post_id)
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'cloud/post_detail.html', {'post': post})


def post_new(request):
    if is_outer(request.user):
        return redirect_next('login', 'cloud:post_new')
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('cloud:post_detail', post_id=post.pk)
    else:
        form = PostForm()
    return render(request, 'cloud/post_edit.html', {'form': form, 'mode': 'New Post'})


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if is_outer(request.user) or post.author != request.user:
        return redirect_next('login', 'cloud:post_edit', post_id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('cloud:post_detail', post_id=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'cloud/post_edit.html', {'form': form, 'mode': 'Edit Post'})


def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if is_outer(request.user) or post.author != request.user:
        return redirect_next('login', 'cloud:post_detail', post_id=post_id)
    post.delete()
    return redirect('cloud:post_list')


def add_comment_to_post(request, post_id):
    if is_outer(request.user):
        return redirect_next('login', 'cloud:add_comment_to_post', post_id=post_id)
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('cloud:post_detail', post_id=post.pk)
    else:
        form = CommentForm()
    return render(request, 'cloud/add_comment_to_post.html', {'form': form})


def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if is_outer(request.user) or comment.user != request.user:
        return redirect_next('login', 'cloud:post_detail', post_id=comment.post.pk)
    comment.delete()
    return redirect('cloud:post_detail', post_id=comment.post.pk)


def file_list(request):
    if is_outer(request.user):
        return redirect_next('login', 'cloud:file_list')
    user_files = UserFile.objects.filter(author=request.user).order_by('-uploaded_at')
    return render(request, 'cloud/file_list.html', {'user_files': user_files})


def file_upload(request):
    if is_outer(request.user):
        return redirect_next('login', 'cloud:file_upload')
    if request.method == 'POST':
        form = UserFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.save(commit=False)
            user_file.author = request.user
            if user_file.description == '':
                user_file.description = os.path.basename(user_file.user_file.name)
            user_file.save()
            return redirect('cloud:file_list')
    else:
        form = UserFileForm()
    return render(request, 'cloud/file_upload.html', {'form': form})


def file_download(request, file_id):
    if is_outer(request.user):
        return redirect_next('login', 'cloud:file_list')
    user_file = get_object_or_404(UserFile, pk=file_id, author=request.user)
    file_name = os.path.basename(user_file.user_file.name)
    file_path = os.path.join(settings.MEDIA_ROOT, user_file.user_file.name)
    file_wrapper = FileWrapper(file(file_path, 'rb'))
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype)
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % urllib.quote(file_name.encode('utf-8'))
    return response


def post_find_by_index(request, post_index):
    if is_outer(request.user):
        return redirect_next('login', 'cloud:post_find_by_index')
    post = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')[int(post_index)]
    queries = dict(
        title=post.title,
        text=post.text,
        author=str(post.author),
        datetime=str(post.published_date),
        id=post.pk)
    comments = post.comments.all()
    comments_list = []
    for comment in comments:
        comment_dict = dict(
            author=str(comment.author),
            text=comment.text,
            datetime=str(comment.created_date),
            id=comment.pk)
        comments_list.append(comment_dict)
    queries['comments'] = comments_list
    return JsonResponse(queries, safe=False)
