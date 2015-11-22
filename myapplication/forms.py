from django import forms
from .models import Message

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
	subject = forms.CharField(label="Subject", max_length=50)
	msg = forms.CharField(label="Message", max_length=500)
	receiver = forms.CharField(label="Recipient", max_length=30)
	encrypt = forms.BooleanField(label="Encrypt Message", initial=False, required=False)

class SiteManagerUserForm(forms.Form):
    username = forms.CharField(label='User Name', max_length=30)
    CHOICES = (('1','Make User Site Manager',),('2','Suspend User',),('3','Reactivate User',))
    choice_field = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES)

class SiteManagerGroupForm(forms.Form):
    username = forms.CharField(label='User Name', max_length=30, required=False)
    groupname = forms.CharField(label='Group Name', max_length=80)
    CHOICES = (('1','Create group',),('2','Add user to group',),('3','Remove user from group',))
    choice_field = forms.ChoiceField(widget=forms.RadioSelect,choices=CHOICES)

