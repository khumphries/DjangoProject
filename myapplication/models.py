from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import datetime
# Hungarian tags for models:
# dct - a directory

# Our filesystem is basically a recursive list of directories
# Each directory knows its parent. If the parent is null, then it must be the root
# Reports also know which directory they belong in. Each report has to be in a directory
# When a user is created, a directory for them should be created automatically with null as its parent
# By default, reports should be uploaded into that directory -MK
    
def validate_dct_stName(stName, dct=None):
    if stName in Dct.objects.filter(dctParent=dct):
        raise ValidationError("cannot create new directory %s in directory %s: directory already exists" % stName,dct.stName)

class Dct(models.Model):
    dctParent = models.ForeignKey('self', null=True)
    stName = models.CharField(validators=[validate_dct_stName], max_length=80) # TODO: MK: why 80? No idea
    owner = models.ForeignKey(User, null=True)

class Report(models.Model):
    timeStamp = models.DateTimeField(auto_now_add=True)
    shortDescription = models.CharField(max_length=50)
    detailedDescription = models.CharField(max_length=500)
    private = models.BooleanField(default=False)
    dct = models.ForeignKey(Dct, null=True)
    owner = models.ForeignKey(User, null=True)

class Report_Group(models.Model):
    group = models.CharField(max_length=80)
    report = models.ForeignKey(Report)


class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    owner = models.ForeignKey(User, null=True)
    report = models.ForeignKey(Report, null=True)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    receiver = models.ForeignKey(User, related_name="receiver")
    subject = models.CharField(max_length=50, default="subject")
    msg = models.CharField(max_length=500)
    sentDate = models.DateTimeField(auto_now_add=True)
    display = models.BooleanField(default=True)
    encrypt = models.BooleanField(default=False)
    
