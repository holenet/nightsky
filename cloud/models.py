from django.db import models
from django.utils import timezone
from django.utils.encoding import smart_str


class Post(models.Model):
    author = models.ForeignKey('auth.User')
    title = models.CharField(max_length=200)
    text = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('cloud.Post', related_name='comments')
    author = models.ForeignKey('auth.User')
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    #	approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_commend = True
        self.save()

    def __str__(self):
        return self.text


def user_file_name(instance, filename):
    return '/'.join(['NightSky', instance.author.username, filename])


class UserFile(models.Model):
    author = models.ForeignKey('auth.User')
    user_file = models.FileField(upload_to=user_file_name)
    uploaded_at = models.DateTimeField(default=timezone.now)
    description = models.TextField()

    def __str__(self):
        return str(self.author) + "-" + smart_str(self.description)
