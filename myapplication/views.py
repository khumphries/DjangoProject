from django.shortcuts import render

from django.shortcuts import render_to_response
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

dctCurr = None

# TODO: MK: currently this can totally throw error if you give an invalid path. Need to deal
# with that somehow, but for now just getting basic functionality

# TODO: MK: this function currently allows you to reach anything in the filesystem.
# Need to implement reasonable permissions policy here
def dctFromPath(path, user):
#    print(path)
    if path.endswith("/"):
        path = path[:-1]
    if path[0] == '/' or path[0] == '~':
        # absolute path
        rgstDct = path.split("/")
        if rgstDct[0] == "":
            if not rgstDct[1] == "root":
                return # this is an error
            dct = None
            for stDct in rgstDct[2:]:
                dct = Dct.objects.filter(stName=stDct).filter(dctParent=dct)[0]
            return dct
        elif rgstDct[0] == "~":
            print("entering a ~ path")
            dct = get_home_dct_from_user(user)
            for stDct in rgstDct[1:]:
                dct = Dct.objects.filter(stName=stDct).filter(dctParent=dct)[0]
            print("leaving a ~ path")
            return dct
        else:
            return # this is an error
    else:
        # relative path to dctCurr
        dct = dctCurr
        rgstDct = path.split("/")
        for stDct in rgstDct:
            if stDct == "..":
                dct = dct.dctParent
            else:
                dct = Dct.objects.filter(stName=stDct).filter(dctParent=dct)[0]
        
        return dct

def pathFromDct(dct):
    path = ""
    while dct is not None:
        path = dct.stName + "/" + path
        dct = dct.dctParent
    path = "root/" + path
    return path

def get_home_dct_from_user(user):
    dct_name = user.username
    dct = Dct.objects.get(owner=user, stName=dct_name)
    return dct

def shell(rgwrd, request):
    global dctCurr
    if rgwrd[0] == 'mkdir':
        if len(rgwrd) > 1:
            dctNew = Dct(stName=rgwrd[1], owner=request.user, dctParent=dctCurr)
            dctNew.save()
            return
        else:
            return # return an error somehow?
            
    elif rgwrd[0] == "cd":
        if len(rgwrd) == 2:
            stNameDctTarget = rgwrd[1]
            if stNameDctTarget == "..":
                dctCurr = dctCurr.dctParent
                return
            rgdct = Dct.objects.filter(dctParent=dctCurr).filter(stName=stNameDctTarget)
            if len(rgdct) > 0:
                dctCurr = rgdct[0]
                return
            
            try:
                dctTarget = dctFromPath(stNameDctTarget, request.user)
                dctCurr = dctTarget
                return
            except:
                return # an error somehow
        else:
            return # an error somehow
 
    elif rgwrd[0] == "rm":
        fForce = False
        if rgwrd[1].startswith("-"):
            # process flags
            pathToTarget = rgwrd[2]
            if "f" in rgwrd[1]:
                fForce = True
        else:
            pathToTarget = rgwrd[1]
        
        dctTarget = dctFromPath(pathToTarget, request.user)
        if dctTarget is not None:
            cdct = Dct.objects.all().filter(dctParent=dctTarget)
            cdoc = Document.objects.all().filter(dct=dctTarget)
            if len(cdct) == 0 and len(cdoc) == 0 and fForce:
                dctTarget.delete()
 
    elif rgwrd[0] == "mv":
        if len(rgwrd) == 3:
            src = rgwrd[1]
            dst = rgwrd[2]
            try:
                dctSrc = dctFromPath(src, request.user)
            except:
                dctSrc = None
            
            if dctSrc is not None:
                stNameNew = None
                try:
                    dctDst = dstFromPath(dst, request.user)
                except:
                    dctDst = None
                if dctDst is None:
                    try:
                        dctDst = dctFromPath("/".join(dst.split("/")[:-1]), request.user)
                        stNameNew = dst.split("/")[-1]
                    except:
                        print("dctDst is not a valid directory")
                        return # an error - dst is not a valid directory
                dctSrc.dctParent = dctDst
                if stNameNew is not None:
                    dctSrc.stName = stNameNew
                dctSrc.save()
            else:
                return # TODO: MK: in here handle calling mv on reports
        else:
            return # an error

def list(request):
    global dctCurr

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
                    shell(rgwrd, request)
                    return HttpResponseRedirect(reverse('myapplication.views.list'))
           
        else:
            docform = DocumentForm() # A empty, unbound form
            cliform = CLIForm()

        # Load documents for the list page
        documents = Document.objects.filter(dct=dctCurr)
        rgdct = Dct.objects.filter(dctParent=dctCurr)

        # Render list page with the documents and the form
        return render_to_response(
            'myapplication/list.html',
            {'documents': documents, 'rgdct': rgdct, 'docform': docform, 'cliform': cliform, 'dctCurr' : dctCurr, 'path': pathFromDct(dctCurr)},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')

def groups_list(request):
    if request.user.is_authenticated():
        return

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
    
    if request.user.is_authenticated():
        messages = Message.objects.filter(receiver=request.user)

        # Render inbox page with the messages
        return render_to_response(
            'myapplication/inbox.html',
            {'messages': messages},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')

def outbox(request):
    
    if request.user.is_authenticated():
        messages = Message.objects.filter(sender=request.user)

        # Render inbox page with the messages
        return render_to_response(
            'myapplication/outbox.html',
            {'messages': messages},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')



# Create your views here.
