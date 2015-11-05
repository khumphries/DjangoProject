from django.shortcuts import render

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import auth

from myapplication.models import Document
from myapplication.models import Dct
from myapplication.forms import DocumentForm
from myapplication.forms import UserForm


# TODO: MK: figure out where this function actually should belong
def get_home_dct_from_user(user):
    dct_name = user.username
    dct = Dct.objects.get(owner=user, stName=dct_name)
    return dct

def list(request):
    if request.user.is_authenticated():
	   # Handle file upload
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                newdoc = Document(docfile = request.FILES['docfile'], owner=request.user, dct=get_home_dct_from_user(request.user))
                newdoc.save()

                # Redirect to the document list after POST
                return HttpResponseRedirect(reverse('myapplication.views.list'))
        else:
            form = DocumentForm() # A empty, unbound form

        # Load documents for the list page
        documents = Document.objects.filter(owner=request.user)

        # Render list page with the documents and the form
        return render_to_response(
            'myapplication/list.html',
            {'documents': documents, 'form': form},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')
#For signup page
def sign_up(request):
    #if we need to process form data
    state = 'Please sign up below'
    if request.method == 'POST':
        form = UserForm(request.POST)
        #checks if data is valid and then 
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                state = "That user name is already taken, please try another."
            else:
                user = User.objects.create_user(form.cleaned_data['username'],'',form.cleaned_data['password'])
                user.save()
                home_dct = Dct(stName=form.cleaned_data['username'], owner=user)
                home_dct.save()
                user_authentication = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password'])
                login(request, user_authentication)
                return HttpResponseRedirect(reverse('myapplication.views.sign_up_complete'))

    else:
        form = UserForm()

    return render(request,'myapplication/sign_up.html', {'form' : form, 'state' : state})
#For page after sign up
def sign_up_complete(request):
    if request.user.is_authenticated():
        return render(request, 'myapplication/sign_up_complete.html')
    else:
        return render(request, 'myapplication/auth.html')

def login_user(request):
    state = "Please log in below..."
    username = password = ''
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
                return HttpResponseRedirect(reverse('myapplication.views.home_page'))
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render_to_response('myapplication/auth.html', RequestContext(request, {'state':state, 'username': username}))

def home_page(request):
    if request.user.is_authenticated():
        return render(request, 'myapplication/home.html')
    else:
        return render(request, 'myapplication/auth.html')
def logout_user(request):
    if request.user.is_authenticated():
        auth.logout(request)
        return render(request, 'myapplication/loggedout.html')
    else:
        return render(request, 'myapplication/auth.html')
# Create your views here.
