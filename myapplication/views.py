from django.shortcuts import render

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login
from django.contrib import auth

from myapplication.models import Document
from myapplication.models import Dct
from myapplication.models import Message
from myapplication.forms import DocumentForm
from myapplication.forms import UserForm
from myapplication.forms import MessageForm
from myapplication.forms import CLIForm
from myapplication.forms import GroupsForm

from myapplication.shell import shell
from myapplication.shell import get_home_dct_from_user
from myapplication.shell import pathFromDct

dctCurr = None
fErrDisplayed = False
stErr = ""

def list(request):
    global dctCurr
    global fErrDisplayed
    global stErr

    if request.user.is_authenticated():
        
        if dctCurr is None:
            dctCurr = get_home_dct_from_user(request.user)
	   # Handle file upload
        if request.method == 'POST':
            if 'docfile' in request.FILES:
                docform = DocumentForm(request.POST, request.FILES)
                if docform.is_valid():
                    newdoc = Document(docfile = request.FILES['docfile'], owner=request.user, dct=dctCurr)
                    newdoc.save()

                # Redirect to the document list after POST
                    return HttpResponseRedirect(reverse('myapplication.views.list'))

            elif 'command' in request.POST:
                cliform = CLIForm(request.POST)
                if cliform.is_valid():
                    rgwrd = request.POST['command'].split(' ')
                    # parse commands
                    res = shell(rgwrd, request, dctCurr)
                    if isinstance(res, str):
                        stErr = res
                        fErrDisplay = False
                    else:
                        dctCurr = res
                    return HttpResponseRedirect(reverse('myapplication.views.list'))
           
        else:
            docform = DocumentForm() # A empty, unbound form
            cliform = CLIForm()

        # Load documents for the list page
        documents = Document.objects.filter(dct=dctCurr)
        rgdct = Dct.objects.filter(dctParent=dctCurr)

        stErrDisplay = None

        if not stErr == "" and not fErrDisplayed:
            stErrDisplay = stErr
            fErrDisplayed = True

        # Render list page with the documents and the form
        return render_to_response(
            'myapplication/list.html',
            {'documents': documents, 'rgdct': rgdct, 'docform': docform, 'cliform': cliform, 'dctCurr' : dctCurr, 'path': pathFromDct(dctCurr), 'stErr' : stErrDisplay},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')

def groups_list(request):
    if request.user.is_authenticated():

        groups = request.user.groups.values_list('name',flat=True)
        print(groups)
        return render_to_response('myapplication/groups.html', {'groups' : groups}, context_instance=RequestContext(request))
    else :
        return render(request, 'myapplication/auth.html')

def groups_creator(request):
    if request.user.is_authenticated():
        state = ''
        if request.method == 'POST':
            form = GroupsForm(request.POST)
            if form.is_valid():
                #checks if group already exists
                if Group.objects.filter(name=form.cleaned_data['groupname']).exists():
                    old_group = Group.objects.get(name=form.cleaned_data['groupname'])
                    #Checks if user is valid
                    if User.objects.filter(username=form.cleaned_data['username']).exists():
                        user = User.objects.get(username=form.cleaned_data['username'])
                        #checks if user is already in the group
                        if user.groups.filter(name=form.cleaned_data['groupname']).exists():
                            state = 'That user is already in the group.'

                        #adds user to group and saves it in the database
                        else:
                            if request.user.groups.filter(name=form.cleaned_data['groupname']).exists():
                                user.groups.add(old_group)
                                old_group.save()
                                user.save()
                                state = 'User successfully added.'
                                return HttpResponseRedirect(reverse('myapplication.views.groups_creator'))
                            else:
                                state = 'You must be in the group to add another user to the group.'
                    else :
                        state = 'That user does not exist. Please try again.'
                else :
                    if form.cleaned_data['username'] == request.user.get_username():
                        new_group = Group.objects.create(name=form.cleaned_data['groupname'])
                        new_group.user_set.add(request.user)
                        new_group.save()
                        request.user.save()
                        state = 'Group successfully created.'
                        return HttpResponseRedirect(reverse('myapplication.views.groups_creator'))
                    else :
                        state = 'Group with that name already exists.'
            else :
                state = 'Please fill all the fields.'
        else :
            form = GroupsForm()
            


        return render(request,'myapplication/groups_creator.html', {'form' : form, 'state' : state})
    else :
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
        else :
            state = 'Please fill out all fields.'
            return HttpResponseRedirect(reverse('myapplication.views.groups_creator'))
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

def messages(request):
    state = "Enter message and recipients username below"
    if request.user.is_authenticated():
       # Handle file upload
        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                if User.objects.filter(username=form.cleaned_data['receiver']).exists():
                    newmsg = Message(msg = request.POST.get('msg'), sender = request.user, receiver=(User.objects.get(username=form.cleaned_data['receiver'])))
                    newmsg.save()
                    return HttpResponseRedirect(reverse('myapplication.views.messages'))
                else:
                    state="That username does not exist. Please enter a valid username to send message."
                
        else:
            form = MessageForm() # An empty, unbound form

        # Load messages sent to user for the messages page
        messages = Message.objects.filter(receiver=request.user)

        # Render messages page with the messages, state, and form
        return render_to_response(
            'myapplication/messages.html',
            {'messages': messages, 'form': form, 'state':state},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')


def inbox(request):
    state = ""
    if request.user.is_authenticated():
        messages = Message.objects.filter(receiver=request.user, display=True)

        if request.method == 'POST':
            msg = request.POST.get('msg')
            sender = request.POST.get('sender')
            receiver = request.POST.get('receiver')
            deletedMessage = Message.objects.get(msg=request.POST.get('msg'))
            deletedMessage.display = False
            deletedMessage.save()
            state = "Message Deleted"
                #return HttpResponseRedirect(reverse('myapplication.views.inbox'))

        # Render inbox page with the messages
        return render_to_response(
            'myapplication/inbox.html',
            {'messages': messages, 'state':state},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')

def outbox(request):
    
    if request.user.is_authenticated():
        messages = Message.objects.filter(sender=request.user)

        # Render outbox page with the messages
        return render_to_response(
            'myapplication/outbox.html',
            {'messages': messages},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')



# Create your views here.
