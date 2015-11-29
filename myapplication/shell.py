from myapplication.models import Dct
from myapplication.models import Report

# TODO: MK: this function currently allows you to reach anything in the filesystem.
# Need to implement reasonable permissions policy here
def dctFromPath(path, user, dctCurr):
#    print(path)
    if path.strip() == "":
        return dctCurr

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

def remove(dct):
    rgdct = Dct.objects.all().filter(dctParent=dct)
    rgrep = Report.objects.all().filter(dct=dct)
    for rep in rgrep:
        rep.delete()
    
    for dctInner in rgdct:
        remove(dctInner)
    
    dct.delete()

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
        fRecur = False
        if len(rgwrd) < 2:
            return "please supply a target for rm"
        if rgwrd[1].startswith("-"):
            if len(rgwrd) < 3:
                return "please supply a target for rm"
            # process flags
            pathToTarget = rgwrd[2]
            if "f" in rgwrd[1]:
                fForce = True
            if "r" in rgwrd[1]:
                fRecur = True
        else:
            pathToTarget = rgwrd[1]

        try:
            dctTarget = dctFromPath(pathToTarget, request.user, dctCurr)
        except:
            dctTarget = None

        if dctTarget is not None:
            rgdct = Dct.objects.all().filter(dctParent=dctTarget)
            rgrep = Report.objects.all().filter(dct=dctTarget)
            if fRecur or (len(rgdct) == 0 and len(rgrep) == 0):
                remove(dctTarget)
                return dctCurr
            else:
                return "cannot remove " + pathToTarget + " since it is not empty. Supply the -r option to rm to recursively delete"
 
        # if we make it this far, then the target must be a report
        dct = dctFromPath("/".join(pathToTarget.split("/")[:-1]), request.user, dctCurr)
        name = pathToTarget.split("/")[-1]
        try:
            rep = Report.objects.all().filter(dct=dct, name=name)[0]
        except:
            rep = None

        if rep is not None:
            rep.delete()
            return dctCurr

        return "cannot remove " + pathToTarget + " since it does not exist"
        
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
                try:
                    dctSrc = dctFromPath("/".join(src.split("/")[:-1]), request.user, dctCurr)
                except:
                    dctSrc = None
                repName = src.split("/")[-1]
                if dctSrc is None:
                    dctSrc = dctCurr
                try:
                    rep = Report.objects.all().filter(dct=dctSrc, name=repName)[0]
                except:
                    return "cannot find " + src

                try:
                    dctDst = dctFromPath(dst, request.user, dctCurr)
                except:
                    dctDst = None

                if dctDst is not None:
                    rep.dct = dctDst
                    rep.save()
                    return dctCurr

                try:
                    dctDst = dctFromPath("/".join(dst.split("/")[:-1]), request.user, dctCurr)
                    stNameNew = dst.split("/")[-1]
                except:
                    return "mv: cannot find " + dst
                
                rep.dct = dctDst
                rep.name = stNameNew
                rep.save()
                return dctCurr

        else:
            return "mv requires two arguments"

    else:
        return rgwrd[0] + " is not recognized as a valid command"
