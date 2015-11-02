from django import forms

class DocumentForm(forms.Form):
	docfile = forms.FileField(label='Select a file', help_text='max. 42 megabytes')

class UserForm(forms.Form):
	username = forms.CharField(label='User Name', max_length=30)
	password = forms.CharField(label='Password', max_length=30, widget=forms.PasswordInput)
