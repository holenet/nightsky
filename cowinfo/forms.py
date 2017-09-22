from django import forms
from .models import DBFile

class DBFileForm(forms.ModelForm):
	class Meta:
		model = DBFile
		fields = ('db_file',)
