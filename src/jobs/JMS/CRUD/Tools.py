from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from jobs.models import Tool, Category
from utilities.io.filesystem import File

import ToolPermissions, os


def GetTool(user, ToolID):
    tool = get_object_or_404(Tool, pk=ToolID)
    if ToolPermissions.CanView(user, tool):
        return tool
    else:
        raise PermissionDenied


def GetTools(user):
    return Tool.objects.filter(
        Q(DeletedInd=False) &
        (
            Q(PublicInd=True) | 
            Q(User__id=user.id) | 
            Q(UserToolPermissions__User__id=user.id)
        )
    )


def AddTool(user, ToolName, CategoryID, ToolDescription, PublicInd = False):
    return Tool.objects.create(ToolName=ToolName,Category_id=CategoryID,
        ToolDescription=ToolDescription,PublicInd=PublicInd,User=user)


def DeleteTool(user, ToolID):
    tool = GetTool(user, ToolID)
    if ToolPermissions.CanAdministrate(user, tool):
        tool.DeletedInd = True
        tool.save()
    else:
        raise PermissionDenied


def UpdateTool(user, tool, ToolName, CategoryID, ToolDescription):
    if ToolPermissions.CanEdit(user, tool):
        tool.ToolName = ToolName
        tool.Category_id = CategoryID
        tool.ToolDescription = ToolDescription
        tool.save()
        return tool
    else:
        raise PermissionDenied


def UpdateAvailability(user, tool, PublicInd):
    if ToolPermissions.CanAdministrate(user, tool):
        tool.PublicInd = PublicInd
        tool.save()
        return tool
    else:
        raise PermissionDenied


def ShareTool(user, tool, share_user, Run=True, Export=False, Publish=False, Edit=False, Admin=False):
    ToolPermissions.Share(user, tool, share_user, Run, Export, Publish, Edit, Admin)


def UnshareTool(user, tool, share_user):
    ToolPermissions.Unshare(user, tool, share_user)


def ExportTool(user, ToolID):
    tool = GetTool(user, ToolID)
    if ToolPermissions.CanExport(user, tool):
        raise NotImplementedError
    else:
        raise PermissionDenied


def GetFileList(user, ToolID, path):
    tool = GetTool(user, ToolID)
    if ToolPermissions.CanEdit(user, tool):
        return os.listdir(path)
    else:
        raise PermissionDenied

    
def UploadFiles(user, ToolID, path, file_dict):
    tool = GetTool(user, ToolID)
    if ToolPermissions.CanEdit(user, tool):
        for k, v in file_dict.iteritems():
            for f in file_dict.getlist(k):
                with open(os.path.join(path, f.name), 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                        
                os.chmod(os.path.join(path, f.name), 0700) 
        
        return os.listdir(path)
    else:
        raise PermissionDenied


def SaveFile(user, ToolID, path, content):
    tool = GetTool(user, ToolID)
    if ToolPermissions.CanEdit(user, tool):
        File.print_to_file(path, content, permissions=0777)
    else:
        raise PermissionDenied


def CreateFile(user, ToolID, path):
    tool = GetTool(user, ToolID)
    if ToolPermissions.CanEdit(user, tool):
        if os.path.exists(path) and os.path.isfile(path):
            raise Exception("Cannot create file with this name. File already exists.")
        
        File.print_to_file(path, '', permissions=0755)
    else:
        raise PermissionDenied


def ReadFile(user, ToolID, path):
    tool = GetTool(user, ToolID)
    if ToolPermissions.CanEdit(user, tool):
        return File.read_file(path)
    else:
        raise PermissionDenied


def DeleteFile(user, ToolID, path):
    tool = GetTool(user, ToolID)
    if ToolPermissions.CanEdit(user, tool):
        os.remove(path)
    else:
        raise PermissionDenied