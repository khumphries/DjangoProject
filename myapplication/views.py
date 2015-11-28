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
from myapplication.models import Report
from myapplication.models import Report_Group
from myapplication.forms import DocumentForm
from myapplication.forms import UserForm
from myapplication.forms import MessageForm
from myapplication.forms import CLIForm
from myapplication.forms import GroupsForm
from myapplication.forms import ReportForm

from myapplication.forms import SiteManagerUserForm
from myapplication.forms import SiteManagerGroupForm

from myapplication.shell import shell
from myapplication.shell import get_home_dct_from_user
from myapplication.shell import pathFromDct

from myapplication.encrypt_message import encrypt_msg, decrypt_msg

dctCurr = None
fErrDisplayed = False
stErr = ""

def list(request):
    global dctCurr
    global fErrDisplayed
    global stErr

    if request.user.is_authenticated():
        SM = request.user.groups.filter(name='Site_Managers').exists()        
        if dctCurr is None:
            print(request.user.username)
            dctCurr = get_home_dct_from_user(request.user)
	   # Handle file upload

        if 'command' in request.POST:
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
            cliform = CLIForm()

        # Load documents for the list page
        reports = Report.objects.filter(dct=dctCurr)
        documents = Document.objects.all()
        rgdct = Dct.objects.filter(dctParent=dctCurr)

        stErrDisplay = None

        if not stErr == "" and not fErrDisplayed:
            stErrDisplay = stErr
            fErrDisplayed = True

        # Render list page with the documents and the form
        return render_to_response(
            'myapplication/list.html',
            {'documents': documents, 'reports': reports, 'rgdct': rgdct, 'cliform': cliform, 'dctCurr' : dctCurr, 'path': pathFromDct(dctCurr), 'stErr' : stErrDisplay, 'SM':SM},
            context_instance=RequestContext(request)
        )
    else:
        return render(request, 'myapplication/auth.html')

def create_report(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        dctCurr = get_home_dct_from_user(request.user)
        if request.method == 'POST':
            reportform = ReportForm(request.POST, user=request.user)
            if reportform.is_valid():
                newreport = Report(shortDescription = reportform.cleaned_data['shortDescription'], detailedDescription = reportform.cleaned_data['detailedDescription'], private = reportform.cleaned_data['private'], owner=request.user, dct=dctCurr)
                newreport.save()
                #Adding code to give permissions based on group selected
                if reportform.cleaned_data['private']:
                    if reportform.cleaned_data['groups_list'] != 'None':
                        new_report_group = Report_Group(group=reportform.cleaned_data['groups_list'])
                        newreport.report_group_set.add(new_report_group)
                        #print(newreport.groups_list)
                else :
                    public_report_group = Report_Group(group='public')
                    newreport.report_group_set.add(public_report_group) 

                for f in request.FILES.getlist('file'):
                    newdoc = Document(docfile = f, owner=request.user, report=newreport)
                    newdoc.save()
                return HttpResponseRedirect(reverse('myapplication.views.list'))

            else:
                reportform = ReportForm(user=request.user)
                return HttpResponseRedirect(reverse('myapplication.views.create_report'))
        else:
            reportform = ReportForm(user=request.user)
            #return HttpResponseRedirect(reverse('myapplication.views.create_report'))

        return render_to_response(
            'myapplication/create_report.html',
            {'dctCurr' : dctCurr, 'path': pathFromDct(dctCurr), 'reportform' : reportform,'SM':SM},
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
        #checks if data is valid and then 
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                state = "That user name is already taken, please try another."
            else:
                user = User.objects.create_user(form.cleaned_data['username'],'',form.cleaned_data['password'])
                group = Group.objects.get(name='public')
                user.groups.add(group)
                group.save()
                user.save()
                home_dct = Dct(stName=form.cleaned_data['username'], owner=user)
                home_dct.save()
                user_authentication = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password'])
                login(request, user_authentication)
                return HttpResponseRedirect(reverse('myapplication.views.sign_up_complete'))
        else :
            state = 'Please fill out all fields.'
    else:
        form = UserForm()
    SM = request.user.groups.filter(name='Site_Managers').exists()

    return render(request,'myapplication/sign_up.html', {'form' : form, 'state' : state,'SM':SM})
#For page after sign up
def sign_up_complete(request):
    SM = request.user.groups.filter(name='Site_Managers').exists()
    if request.user.is_authenticated():
        return render(request, 'myapplication/sign_up_complete.html', {'SM':SM})
    else:
        return render(request, 'myapplication/auth.html')

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
        return render_to_response('myapplication/home.html', {'SM':SM})
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
                #return HttpResponseRedirect(reverse('myapplication.views.inbox'))

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


def get_all_available_reports(request):
    user_group_dict = dict(request.user.groups.values_list(flat=True))
    user_group_list = []
    for value in user_group_dict.values():
        user_group_list.append(value)
    all_reports = Report.objects.filter(report_group__group__in=user_group_list)
#Returns true if user is Site-Manager
def is_SM(request):
    return request.user.groups.filter(name='Site_Managers').exists()
# Create your views here.

def post_request(request):
    global dctCurr
    global fErrDisplayed
    global stErr
    SM = request.user.groups.filter(name='Site_Managers').exists()    
    if dctCurr is None:
        dctCurr = get_home_dct_from_user(request.user)
   # Handle file upload

    if 'command' in request.POST:
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
        cliform = CLIForm()

    # Load documents for the list page
    reports = Report.objects.filter(dct=dctCurr)
    documents = Document.objects.all()
    rgdct = Dct.objects.filter(dctParent=dctCurr)

    stErrDisplay = None

    if not stErr == "" and not fErrDisplayed:
        stErrDisplay = stErr
        fErrDisplayed = True
    # Render list page with the documents and the form
    return render_to_response(
        'myapplication/post_request.html',
        {'documents': documents, 'reports': reports, 'rgdct': rgdct, 'cliform': cliform, 'dctCurr' : dctCurr, 'path': pathFromDct(dctCurr), 'stErr' : stErrDisplay,'SM':SM},
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
