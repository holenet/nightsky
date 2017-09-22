# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

def db_file_name(instance, filename):
	return '/'.join(['cowinfo', instance.author.username, filename])

class DBFile(models.Model):
	author = models.ForeignKey('auth.User')
	db_file = models.FileField(upload_to=db_file_name)
	uploaded_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return str(self.author)+"["+str(self.uploaded_at)+"]"
