from django.shortcuts import render

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User

from myapplication.models import Document
from myapplication.forms import DocumentForm
from myapplication.forms import UserForm

def list(request):
	# Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('myapplication.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'myapplication/list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )

#For signup page
def sign_up(request):
    #if we need to process form data
    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(request.POST['username'],'',request.POST['password'])
            user.save()
            return HttpResponseRedirect(reverse('myapplication.views.sign_up_complete'))

    else:
        form = UserForm()

    return render(request,'myapplication/sign_up.html', {'form' : form})
#For page after sign up
def sign_up_complete(request):
    return render(request, 'myapplication/sign_up_complete.html')

# Create your views here.
