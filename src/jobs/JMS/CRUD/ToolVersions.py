from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from jobs.models import ToolVersion

from copy import deepcopy

import ToolPermissions

def AddToolVersion(user, Tool, ToolVersionNum, ShortDescription, LongDescription, Command=""):
    if ToolPermissions.CanPublish(user, Tool):
        return ToolVersion.objects.create(Tool=Tool, ToolVersionNum=ToolVersionNum,
            ShortDescription=ShortDescription, LongDescription=LongDescription,
            Command=Command)
    else:
        raise PermissionDenied

def PublishToolVersion(user, dev, version_num):
    if ToolPermissions.CanPublish(user, dev.Tool):
        new = deepcopy(dev)
        new.ToolVersionID = None
        new.ToolVersionNum = version_num
        new.save()
        
        return new
    else:
        raise PermissionDenied


def UpdateToolVersion(user, version, ShortDescription, LongDescription, Command):
    if ToolPermissions.CanEdit(user, version.Tool):
        version.ShortDescription = ShortDescription
        version.LongDescription = LongDescription
        version.Command = Command
        version.save()
        return version
    else:
        raise PermissionDenied


def GetToolVersions(Tool):
    return Tool.ToolVersions.all().order_by("-ToolVersionID")
    

def GetToolVersion(Tool, version_num):
    if version_num == "latest":
        return GetToolVersions(Tool)[0]
    else:
        return get_object_or_404(ToolVersion, Tool=Tool, ToolVersionNum=version_num)
    

def GetToolVersionByID(user, version_id):
    return get_object_or_404(ToolVersion, pk=version_id)
    

def GetLatestVersion(Tool):
    return Tool.ToolVersions.filter(ToolVersionNum!="dev").order_by("-ToolVersionID")[0]
    

def GetDevelopmentVersion(Tool):
    return Tool.ToolVersions.get(ToolVersionNum="dev")