from django.db import models
from django.core.exceptions import ValidationError

# Hungarian tags for models:
# rep - a report
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

# TODO: LH: Presumably this needs to be fleshed out a bit... - MK
class Rep(models.Model):
    dct = models.ForeignKey(Dct)
