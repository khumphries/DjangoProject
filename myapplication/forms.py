from django import forms

class DocumentForm(forms.Form):
	docfile = forms.FileField(label='Select a file', help_text='max. 42 megabytes')

class CLIForm(forms.Form):
	command = forms.CharField(label='Command', max_length=100, help_text='use standard UNIX file manipulation commands')

class UserForm(forms.Form):
	username = forms.CharField(label='User Name', max_length=30)
	password = forms.CharField(label='Password', max_length=30, widget=forms.PasswordInput)

class GroupsForm(forms.Form):
    groupname = forms.CharField(label='Group Name', max_length=80)
    username = forms.CharField(label='User Name', max_length=30)

class MessageForm(forms.Form):
	msg = forms.CharField(label="Message", max_length=500)
	receiver = forms.CharField(label="Recipient", max_length=30)
