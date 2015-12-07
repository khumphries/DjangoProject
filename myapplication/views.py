from django.shortcuts import render

from django.conf import settings

import string
import random

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.core.files import File
from django.http import HttpResponse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login
from django.contrib import auth

from myapplication.models import Document
from myapplication.models import Dct
from myapplication.models import Message
from myapplication.models import Report
from myapplication.models import Report_Group
from myapplication.models import Questions

from myapplication.forms import DocumentForm
from myapplication.forms import UserForm
from myapplication.forms import MessageForm
from myapplication.forms import CLIForm
from myapplication.forms import GroupsForm
from myapplication.forms import ReportForm
from myapplication.forms import QueryForm
from myapplication.forms import ChangePasswordForm
from myapplication.forms import SecurityQuestionForm
from myapplication.forms import UsernameForm
from myapplication.forms import EmailForm

from myapplication.forms import SiteManagerUserForm
from myapplication.forms import SiteManagerGroupForm

from myapplication.shell import shell
from myapplication.shell import get_home_dct_from_user
from myapplication.shell import pathFromDct

from myapplication.encrypt_message import encrypt_msg, decrypt_msg

from myapplication.search import make_search

from Crypto.Hash import SHA256

import base64
import os

mpuser_dctCurr = {}
fErrDisplayed = False
stErr = ""

def list(request):
    global mpuser_dctCurr
    global fErrDisplayed
    global stErr

    if request.user.is_authenticated():
        SM = request.user.groups.filter(name='Site_Managers').exists()        
        if request.user.username not in mpuser_dctCurr:
            print(request.user.username)
            mpuser_dctCurr[request.user.username] = get_home_dct_from_user(request.user)
	   # Handle file upload

        if 'command' in request.POST:
            cliform = CLIForm(request.POST)
            if cliform.is_valid():
                rgwrd = request.POST['command'].split(' ')
                # parse commands
                res = shell(rgwrd, request, mpuser_dctCurr[request.user.username])
                if isinstance(res, str):
                    stErr = res
                    fErrDisplay = False
                else:
                    mpuser_dctCurr[request.user.username] = res
                return HttpResponseRedirect(reverse('myapplication.views.list'))
           
        else:
            cliform = CLIForm()

        # Load documents for the list page
        reports = Report.objects.filter(dct=mpuser_dctCurr[request.user.username])
        documents = Document.objects.all()
        rgdct = Dct.objects.filter(dctParent=mpuser_dctCurr[request.user.username])

        stErrDisplay = None

        if not stErr == "" and not fErrDisplayed:
            stErrDisplay = stErr
            fErrDisplayed = True

        # Render list page with the documents and the form
        return render_to_response(
            'myapplication/list.html',
            {'documents': documents, 'reports': reports, 'rgdct': rgdct, 'cliform': cliform, 'dctCurr' : mpuser_dctCurr[request.user.username], 'path': pathFromDct(mpuser_dctCurr[request.user.username]), 'stErr' : stErrDisplay, 'SM':SM},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')

def create_report(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        if request.method == 'POST':
            reportform = ReportForm(request.POST, user=request.user)
            if reportform.is_valid():
                newreport = Report(name = reportform.cleaned_data['name'], shortDescription = reportform.cleaned_data['shortDescription'], detailedDescription = reportform.cleaned_data['detailedDescription'], private = reportform.cleaned_data['private'], owner=request.user, dct=mpuser_dctCurr[request.user.username])
                newreport.save()
                site_manager_report_group = Report_Group(group='Site_Managers')
                newreport.report_group_set.add(site_manager_report_group)

                #Adding code to give permissions based on group selected
                if reportform.cleaned_data['private']:
                    if reportform.cleaned_data['groups_list'] != 'None':
                        new_report_group = Report_Group(group=reportform.cleaned_data['groups_list'])
                        newreport.report_group_set.add(new_report_group)
                        newreport.save()
                        new_report_group.save()
                    else :
                        private_report_group_name = request.user.get_username() + '_private'
                        new_report_group = Report_Group(group=private_report_group_name)
                        newreport.report_group_set.add(new_report_group)
                        newreport.save()
                        new_report_group.save()
                else :
                    public_report_group = Report_Group(group='public')
                    newreport.report_group_set.add(public_report_group)
                    newreport.save()
                    new_report_group.save()

                
                for f in request.FILES.getlist('file'):
                    h = SHA256.new()
                    contents = f.read()
                    h.update(contents)
                    s = bytes(h.hexdigest(), 'UTF-8')
                    contents = base64.b64encode(contents)
                    encrypt = f.name[-4:]
                    if encrypt == '.enc':
                        newdoc = Document(docfile = f, owner=request.user, report=newreport, dochash=s, encrypt=True, content=contents)
                    else:
                        newdoc = Document(docfile = f, owner=request.user, report=newreport, dochash=s, content=contents)
                    newdoc.save()
                    print(contents)
                return HttpResponseRedirect(reverse('myapplication.views.list'))

            else:
                reportform = ReportForm(user=request.user)
                return HttpResponseRedirect(reverse('myapplication.views.create_report'))
        else:
            reportform = ReportForm(user=request.user)
            #return HttpResponseRedirect(reverse('myapplication.views.create_report'))

        return render_to_response(
            'myapplication/create_report.html',
            {'dctCurr' : mpuser_dctCurr[request.user.username], 'path': pathFromDct(mpuser_dctCurr[request.user.username]), 'reportform' : reportform,'SM':SM},
            context_instance=RequestContext(request)
        )

    else:
        return render(request, 'myapplication/auth.html')

def view_all_reports(request):
    if request.user.is_authenticated():
        user_group_dict = dict(request.user.groups.values_list(flat=True))
        user_group_list = []
        for value in user_group_dict.values():
            user_group_list.append(value)
        all_reports = Report.objects.filter(report_group__group__in=user_group_list)
        return render_to_response(
            'myapplication/all_reports.html',
            {'all_reports':all_reports},
            context_instance=RequestContext(request)
            )
    else :
        return render(request, 'myapplication/auth.html')
def view_report(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            report = Report.objects.filter(shortDescription=(request.POST.get('shortDescription')))[0]
            documents = Document.objects.filter(report=report)
            SM = request.user.groups.filter(name='Site_Managers').exists()
            return render_to_response(
            'myapplication/view_report.html',
            {'report':report, 'documents':documents, 'SM':SM},
            context_instance=RequestContext(request)
            )
    else:
        return render(request, 'myapplication/auth.html')

def edit_report(request):
    if request.user.is_authenticated():
        if request.method == 'POST':
            report = Report.objects.get(reportID=request.POST.get('reportID'))
            #report = Report.objects.filter(shortDescription=(request.POST.get('shortDescription')))[0]
            documents = Document.objects.filter(report=report)
            SM = request.user.groups.filter(name='Site_Managers').exists()

            if 'updateReport' in request.POST:
                report.shortDescription = request.POST.get('shortDescription')
                report.detailedDescription = request.POST.get('detailedDescription')
                report.save()
                return HttpResponseRedirect(reverse('myapplication.views.list'))
            
            if 'delete' in request.POST:
                deletedDoc = Document.objects.get(docfile=request.POST.get('docfile'))
                deletedDoc.delete()
                return HttpResponseRedirect(reverse('myapplication.views.list'))

            if 'uploadFiles' in request.POST:
                for f in request.FILES.getlist('file'):
                    h = SHA256.new()
                    contents = f.read()
                    h.update(contents)
                    s = bytes(h.hexdigest(), 'UTF-8')
                    contents = base64.b64encode(contents)
                    newdoc = Document(docfile = f, owner=request.user, report=report, dochash=s, content=contents)
                    newdoc.save()
                return HttpResponseRedirect(reverse('myapplication.views.list'))

            return render_to_response(
            'myapplication/edit_report.html',
            {'report':report, 'documents':documents, 'SM':SM},
            context_instance=RequestContext(request)
            )
    else:
        return render(request, 'myapplication/auth.html')

def groups_list(request):
    if request.user.is_authenticated():
        groups = request.user.groups.values_list('name',flat=True)
        SM = request.user.groups.filter(name='Site_Managers').exists()
        return render_to_response('myapplication/groups.html', {'groups' : groups,'SM':SM}, context_instance=RequestContext(request))
    else :
        return render(request, 'myapplication/auth.html')

def groups_creator(request):
    if request.user.is_authenticated():
        state = ''
        if request.method == 'POST':
            form = GroupsForm(request.POST)
            if form.is_valid():
                #checks if group already exists
                if form.cleaned_data['choice_field'] == '1':
                    if Group.objects.filter(name=form.cleaned_data['groupname']).exists():
                        state = 'Group with that name already exists'
                    else:
                        new_group = Group.objects.create(name=form.cleaned_data['groupname'])
                        new_group.user_set.add(request.user)
                        new_group.save()
                        request.user.save()
                        state = 'Group successfully created.'
                        #return HttpResponseRedirect(reverse('myapplication.views.groups_creator'))
                else :
                    if Group.objects.filter(name=form.cleaned_data['groupname']).exists():
                        old_group=Group.objects.get(name=form.cleaned_data['groupname'])
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
                                    #return HttpResponseRedirect(reverse('myapplication.views.groups_creator'))
                                else:
                                    state = 'You must be in the group to add another user to the group.'
                        else :
                            state = 'That user does not exist. Please try again.'
                    else :
                        state = 'That Group does not exist.'
        else :
            form = GroupsForm()
            
       	SM = request.user.groups.filter(name='Site_Managers').exists()
        return render(request,'myapplication/groups_creator.html', {'form' : form, 'state' : state,'SM':SM})
    else :
        return render(request, 'myapplication/auth.html')        

#For signup page
def sign_up(request):
    #if we need to process form data
    state = 'Please sign up below'
    if request.method == 'POST':
        form = UserForm(request.POST)
        securityForm=SecurityQuestionForm(request.POST)
        #checks if data is valid and then 
        if form.is_valid():
            if securityForm.is_valid():
                if User.objects.filter(username=form.cleaned_data['username']).exists():
                    state = "That user name is already taken, please try another."
                else:
                    user = User.objects.create_user(form.cleaned_data['username'],'',form.cleaned_data['password'])
                    user.email = form.cleaned_data['email']
                    group = Group.objects.get(name='public')
                    private_group_name = form.cleaned_data['username'] + '_private'
                    private_group = Group.objects.create(name=private_group_name)
                    user.groups.add(group)
                    user.groups.add(private_group)
                    private_group.save()
                    group.save()
                    user.save()
                    SQ = Questions(securityowner=user,Q1=securityForm.cleaned_data['Q1'].lower(),Q2=securityForm.cleaned_data['Q2'].lower(),Q3=securityForm.cleaned_data['Q3'].lower())
                    SQ.save()
                    user.save()
                    home_dct = Dct(stName=form.cleaned_data['username'], owner=user)
                    home_dct.save()
                    user_authentication = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password'])
                    login(request, user_authentication)


                    return HttpResponseRedirect(reverse('myapplication.views.home_page'))
            else :
                state = 'Please fill out all fields.'
        else :
            state = 'Please fill out all fields.'
    else:
        form = UserForm()
        securityForm = SecurityQuestionForm()
    SM = request.user.groups.filter(name='Site_Managers').exists()
    return render(request,'myapplication/sign_up.html', {'form' : form, 'state' : state,'SM':SM, 'securityForm':securityForm})
#For page after sign up

def change_email(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        state = 'Type a valid email that you want to replace your current email.'
        if request.method == 'POST':
            form = EmailForm(request.POST)
            securityForm = SecurityQuestionForm(request.POST)
            if form.is_valid():
                if securityForm.is_valid():
                    SQ = Questions.objects.get(securityowner=request.user)
                    if getattr(SQ,'Q1') == securityForm.cleaned_data['Q1'] and getattr(SQ,'Q2') == securityForm.cleaned_data['Q2'] and getattr(SQ,'Q3') == securityForm.cleaned_data['Q3']:
                        request.user.email = form.cleaned_data['email']
                        state = 'Email changed to ' + form.cleaned_data['email']
                        request.user.save()
                    else:
                        state = 'Atleast one question was not answered correctly.'
                else:
                    state = 'Please answer the security questions.'
            else:
                state = 'Please put a viable email in the box.'
        else:
            form = EmailForm()
            securityForm = SecurityQuestionForm()
        return render(request, 'myapplication/change_email.html', {'state':state, 'SM':SM, 'form':form, 'securityForm':securityForm})
    else:
        return render(request, 'myapplication/auth.html')
def sign_up_complete(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        return render(request, 'myapplication/sign_up_complete.html', {'SM':SM})
    else:
        return render(request, 'myapplication/auth.html')
def change_password(request):
    if request.user.is_authenticated():
        SM = is_SM(request)
        state = ''
        if request.method == 'POST':
            form = ChangePasswordForm(request.POST)
            securityForm = SecurityQuestionForm(request.POST)
            if form.is_valid():
                if securityForm.is_valid():
                    if request.user.check_password(form.cleaned_data['old_password']):
                        if form.cleaned_data['new_password1'] == form.cleaned_data['new_password2']:
                            SQ = Questions.objects.get(securityowner=request.user)
                            if getattr(SQ,'Q1') == securityForm.cleaned_data['Q1'] and getattr(SQ,'Q2') == securityForm.cleaned_data['Q2'] and getattr(SQ,'Q3') == securityForm.cleaned_data['Q3']:
                                request.user.set_password(form.cleaned_data['new_password1'])
                                request.user.save()
                                user_authentication = authenticate(username=request.user.get_username(),password=form.cleaned_data['new_password1'])
                                login(request, user_authentication)
                                #state = 'Password changed.'
                                return HttpResponseRedirect(reverse('myapplication.views.change_password'))
                            else:
                                state = 'At least on security question incorrect'
                        else:
                            state = 'Passwords did not match'
                    else:
                        state = 'Password incorrect.'
                else:
                    state = 'Please fill out all the fields'
            else:
                state = 'Please fill out all the fields'
        else:
            form = ChangePasswordForm()
            securityForm = SecurityQuestionForm()
        return render(request, 'myapplication/change_password.html', {'form':form,'SM':SM, 'state':state, 'securityForm':securityForm})
    else:
        return render(request, 'myapplication/auth.html')

def forgot_password(request):
    state = 'Type your username below, if you did not give an email at sign up this will not work.'
    if request.method == 'POST':
        form = UsernameForm(request.POST)
        if form.is_valid(): 
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                user = User.objects.get(username=form.cleaned_data['username'])
                user_email = user.email
                print(user_email)
                if user_email == '':
                    state = 'We have no email on record for you.'
                else:
                    temp_pass=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
                    user.set_password(temp_pass)
                    send_mail('Forgotten password.','The temporary password is "' + temp_pass + '".', settings.EMAIL_HOST_USER, [user_email], fail_silently=False)
                    state = 'Email sent.'
                    user.save()
            else:
                state='That user does not exist.'
        else:
            state = 'Plese fill out the field.'
    else:
        form = UsernameForm()
    return render(request, 'myapplication/forgot_password.html', {'state':state, 'form':form})

def login_user(request):
    state = "Please log in below..."
    username = password = ''
    SM = request.user.groups.filter(name='Site_Managers').exists()
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

    return render_to_response('myapplication/auth.html', RequestContext(request, {'state':state, 'username': username,'SM':SM}))

def home_page(request):
    if request.user.is_authenticated():
        SM = request.user.groups.filter(name='Site_Managers').exists()
        unread = len(Message.objects.filter(receiver=request.user, read=False))
        return render_to_response('myapplication/home.html', {'SM':SM, 'unread':unread})
    else:
        return render(request, 'myapplication/auth.html')
def site_manager(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        if is_SM:
            return render(request, 'myapplication/Site_manager.html',{'SM':SM})
        else:
            return render(request, 'myapplication/home.html',{'SM':SM})
    return render(request, 'myapplication/auth.html')
def site_manager_groups(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        State = 'Enter the Group you want to affect and pick an action, Username is only necessary for adding and removing.'
        if is_SM(request):
            if request.method == 'POST':
                Form = SiteManagerGroupForm(request.POST)
                if Form.is_valid():
                    if Form.cleaned_data['choice_field'] == '1':
                        if Group.objects.filter(name=Form.cleaned_data['groupname']).exists():
                            State = 'Group with that name already exists.'
                        else :
                            new_group = Group.objects.create(name=Form.cleaned_data['groupname'])
                            new_group.save()
                            State = 'Group successfully created.'
                    else:
                        if Form.cleaned_data['username'] == '':
                            State = 'Please enter the name of the user you want to add or remove.'
                        else :
                            if Group.objects.filter(name=Form.cleaned_data['groupname']).exists():
                                old_group = Group.objects.get(name=Form.cleaned_data['groupname'])
                                if User.objects.filter(username=Form.cleaned_data['username']).exists():
                                    user = User.objects.get(username=Form.cleaned_data['username'])
                                    if Form.cleaned_data['choice_field']== '2':
                                        if user.groups.filter(name=Form.cleaned_data['groupname']).exists():
                                            State = 'That user is already in the group.'
                                        else :
                                            user.groups.add(old_group)
                                            old_group.save()
                                            user.save()
                                            State = 'User successfully added.'
                                    else :
                                        if user.groups.filter(name=Form.cleaned_data['groupname']).exists():
                                            user.groups.remove(old_group)
                                            old_group.save()
                                            user.save()
                                            State = 'User successfully removed.'
                                        else :
                                            State = 'That user is not in that group.'
                                else :
                                    State = 'That user does not exist.'
                            else :
                                State = 'That Group does not exist.'
                else:
                    State = 'Please make sure that the groupname box was filled and an action was selcted.'
            else:
                Form = SiteManagerGroupForm()     
            return render (request, 'myapplication/Site_manager_groups.html', {'State':State, 'Form':Form,'SM':SM})
        else :
            return render(request, 'myapplication/home.html', {'SM':SM})
    else:
        return render(request, 'myapplication/auth.html')    

def site_manager_users(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        State = 'Please input the name of the user and check the box of the action you want to do.'
        if is_SM(request):
            if request.method == 'POST':
                Form = SiteManagerUserForm(request.POST)
                if Form.is_valid():
                    if User.objects.filter(username=Form.cleaned_data['username']).exists():
                        user = User.objects.get(username=Form.cleaned_data['username'])
                        if Form.cleaned_data['choice_field'] == '1':
                            site_manager_group = Group.objects.get(name='Site_Managers')
                            user.groups.add(site_manager_group)
                            user.save()
                            site_manager_group.save()
                            State = 'User given Site Manager priveleges.'
                        elif Form.cleaned_data['choice_field'] == '3':
                            if user.is_active == False:
                                State = 'User was reactivated.'
                                user.is_active = True
                                user.save()
                            else:
                                State = 'User was already active.'
                        else :
                            if user.is_active == True:
                                user.is_active = False
                                user.save()
                                State = 'User was suspended.'
                            else :
                                State = 'User is already inactive.'
                    else :
                        State = 'That user does not exist.'
                else :
                    State = 'Please fill out all the fields.'
            else :
                Form = SiteManagerUserForm()
            return render(request, 'myapplication/Site_manager_users.html', {'State':State, 'Form':Form, 'SM':SM})
        else :
            return render(request, 'myapplication/home.html', {'SM':SM})
    else:
        return render(request, 'myapplication/auth.html')

def logout_user(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        auth.logout(request)
        return render(request, 'myapplication/loggedout.html', {'SM':SM})
    else:
        return render(request, 'myapplication/auth.html')

def messages(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    state = "Enter message and recipients username below"
    if request.user.is_authenticated():
       # Handle file upload
        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                if User.objects.filter(username=form.cleaned_data['receiver']).exists():
                    msg = request.POST.get('msg')
                    if form.cleaned_data['encrypt'] == True:
                        if form.cleaned_data['key'] != '':                      
                            msg = str(encrypt_msg(msg, form.cleaned_data['key']))   
                        else:
                            msg = str(encrypt_msg(msg))

                    newmsg = Message(subject= form.cleaned_data['subject'], msg = msg, sender = request.user, receiver=(User.objects.get(username=form.cleaned_data['receiver'])), encrypt=form.cleaned_data['encrypt'])
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
            {'messages': messages, 'form': form, 'state':state,'SM':SM},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')


def inbox(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    state = ""
    if request.user.is_authenticated():
        messages = Message.objects.filter(receiver=request.user, display=True).order_by('-sentDate')
        for m in messages:
            m.read = True
            m.save()

        if request.method == 'POST':
            msg = request.POST.get('msg')
            sender = request.POST.get('sender')
            receiver = request.POST.get('receiver')
            message = Message.objects.filter(msg=request.POST.get('msg'), display=True)[0]
            if 'decrypt' in request.POST:
                key = request.POST.get('key')
                if key != '':
                    message.msg = decrypt_msg(message.msg, key)
                else:
                    message.msg = decrypt_msg(message.msg)
                message.encrypt = False
                message.save()
                state = "Message Decrypted"

            elif 'delete' in request.POST:
                message.display = False
                message.save()
                state = "Message Deleted"
            return HttpResponseRedirect(reverse('myapplication.views.inbox'))

        # Render inbox page with the messages
        return render_to_response(
            'myapplication/inbox.html',
            {'messages': messages, 'state':state,'SM':SM},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')

def outbox(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        messages = Message.objects.filter(sender=request.user).order_by('-sentDate')

        # Render outbox page with the messages
        return render_to_response(
            'myapplication/outbox.html',
            {'messages': messages,'SM':SM},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')


#Returns true if user is Site-Manager
def is_SM(request):
    return request.user.groups.filter(name='Site_Managers').exists()
# Create your views here.

def post_request(request):
    if request.method == 'GET':
        reports = Report.objects.all()
        documents = Document.objects.all()
        return render_to_response(
        'myapplication/post_request.html',
        {'reports':reports, 'documents':documents},
        context_instance=RequestContext(request)
        )



    # # Load documents for the list page
    # reports = Report.objects.filter(dct=dctCurr)
    # documents = Document.objects.all()
    # rgdct = Dct.objects.filter(dctParent=dctCurr)

    # # Render list page with the documents and the form
    # return render_to_response(
    #     'myapplication/post_request.html',
    #     {'documents': documents, 'reports': reports, 'rgdct': rgdct, 'dctCurr' : dctCurr, 'path': pathFromDct(dctCurr)},
    #     context_instance=RequestContext(request)
    # )

def search(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        if 'queryText' in request.POST:
            # we've already made a search, so do the work and return the results
            resultsAsRep = make_search(request.POST['queryText'], request)
        else:
            resultsAsRep = None

        queryForm = QueryForm()
    
        return render(
            request,
            'myapplication/search.html',
            {'results' : resultsAsRep, 'queryForm': queryForm, 'SM' : SM}
            )
    else :
        return render(request, 'myapplication/auth.html')

def unix_help(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        return render(
            request,
            'myapplication/unix_help.html',
            {'SM' : SM}
            )
    else :
        return render(request, 'myapplication/auth.html')
