from myapplication.models import Document
from myapplication.models import Dct

# TODO: MK: currently this can totally throw error if you give an invalid path. Need to deal
# with that somehow, but for now just getting basic functionality

# TODO: MK: this function currently allows you to reach anything in the filesystem.
# Need to implement reasonable permissions policy here
def dctFromPath(path, user, dctCurr):
#    print(path)
    if path.endswith("/"):
        path = path[:-1]
    if path[0] == '/' or path[0] == '~':
        # absolute path
        rgstDct = path.split("/")
        if rgstDct[0] == "":
            if not rgstDct[1] == "root":
                raise ValueError # this is an error
            dct = None
            for stDct in rgstDct[2:]:
                dct = Dct.objects.filter(stName=stDct).filter(dctParent=dct)[0]
            return dct
        elif rgstDct[0] == "~":
            dct = get_home_dct_from_user(user)
            for stDct in rgstDct[1:]:
                dct = Dct.objects.filter(stName=stDct).filter(dctParent=dct)[0]
            return dct
        else:
            raise ValueError
    else:
        # relative path to dctCurr
        dct = dctCurr
        rgstDct = path.split("/")
        for stDct in rgstDct:
            if stDct == "..":
                dct = dct.dctParent
            else:
                rgdct = Dct.objects.filter(stName=stDct).filter(dctParent=dct)
                if len(rgdct) == 0:
                    raise ValueError
                dct = rgdct[0]
        if dct is not None:
            return dct
        else:
            raise ValueError

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

# shell returns either the current directory or an error

def shell(rgwrd, request, dctCurr):
    if len(rgwrd) == 0:
        return ""
    elif rgwrd[0] == 'mkdir':
        if len(rgwrd) > 1:
            dctNew = Dct(stName=rgwrd[1], owner=request.user, dctParent=dctCurr)
            dctNew.save()
            return dctCurr
        else:
            return "invalid argument to mkdir: " + " ".join(rgwrd[1:]) + "\n please supply the name of a new directory"
            
    elif rgwrd[0] == "cd":
        if len(rgwrd) == 2:
            stNameDctTarget = rgwrd[1]
            # if stNameDctTarget == "..":
            #     dctCurr = dctCurr.dctParent
            #     return dctCurr
            # rgdct = Dct.objects.filter(dctParent=dctCurr).filter(stName=stNameDctTarget)
            # if len(rgdct) > 0:
            #     dctCurr = rgdct[0]
            #     return dctCurr
            
            try:
                dctTarget = dctFromPath(stNameDctTarget, request.user, dctCurr)
                dctCurr = dctTarget
                return dctCurr
            except:
                return "cannot locate directory: " + stNameDctTarget
        else:
            return "invalid argument to cd: " + " ".join(rgwrd[1:]) + "\n please supply the name of a directory"
 
    elif rgwrd[0] == "rm":
        fForce = False
        if len(rgwrd) < 2:
            return "please supply a target for rm"
        if rgwrd[1].startswith("-"):
            if len(rgwrd) < 3:
                return "please supply a target for rm"
            # process flags
            pathToTarget = rgwrd[2]
            if "f" in rgwrd[1]:
                fForce = True
        else:
            pathToTarget = rgwrd[1]

        try:
            dctTarget = dctFromPath(pathToTarget, request.user, dctCurr)
        except:
            dctTarget = None

        if dctTarget is not None:
            cdct = Dct.objects.all().filter(dctParent=dctTarget)
            cdoc = Document.objects.all().filter(dct=dctTarget)
            if len(cdct) == 0 and len(cdoc) == 0 and fForce:
                dctTarget.delete()
                return dctCurr
            else:
                return "cannot remove " + pathToTarget + "; rm currently only supports empty directories"
 
        return "cannot remove " + pathToTarget + " since it does not exist or is not a directory"
        
    elif rgwrd[0] == "mv":
        if len(rgwrd) == 3:
            src = rgwrd[1]
            dst = rgwrd[2]
            try:
                dctSrc = dctFromPath(src, request.user, dctCurr)
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
                        dctDst = dctFromPath("/".join(dst.split("/")[:-1]), request.user, dctCurr)
                        stNameNew = dst.split("/")[-1]
                    except:
                        # an error - dst is not a valid directory
                        return dst + " is not a valid directory"
                dctSrc.dctParent = dctDst
                if stNameNew is not None:
                    dctSrc.stName = stNameNew
                dctSrc.save()
            else:
                return "mv does not currently support reports, and " + src + " is not a valid directory" 
               # TODO: MK: in here handle calling mv on reports
        else:
            return "mv requires two arguments"

    else:
        return rgwrd[0] + " is not recognized as a valid command"
