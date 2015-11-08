from django import forms

class DocumentForm(forms.Form):
	docfile = forms.FileField(label='Select a file', help_text='max. 42 megabytes')

class UserForm(forms.Form):
	username = forms.CharField(label='User Name', max_length=30)
	password = forms.CharField(label='Password', max_length=30, widget=forms.PasswordInput)

class MessageForm(forms.Form):
	msg = forms.CharField(label="Message", max_length=500)
	receiver = forms.CharField(label="Recipient", max_length=30)
	#sender = forms.CharField(label="Sender", max_length=30)
