from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from jobs.models import UserToolPermission



def GetToolPermission(user, tool):
    try:
        return UserToolPermission.objects.get(Tool=tool, User=user)
    except:
        raise PermissionDenied


def GetToolPermissions(tool):
    return tool.UserToolPermissions.all()
    

def CanView(user, tool):
    return tool.User.id == user.id or tool.PublicInd or GetToolPermission(user, tool)


def CanRun(user, tool):
    return tool.User.id == user.id or tool.PublicInd or GetToolPermission(user, tool).Run


def CanEdit(user, tool):
    return tool.User.id == user.id or GetToolPermission(user, tool).Edit


def CanPublish(user, tool):
    return tool.User.id == user.id or GetToolPermission(user, tool).Publish


def CanExport(user, tool):
    return tool.User.id == user.id or GetToolPermission(user, tool).Export


def CanAdministrate(user, tool):
    return tool.User.id == user.id or GetToolPermission(user, tool).Admin


def Share(user, tool, share_user, Run=True, Export=False, Publish=False, Edit=False, Admin=False):
    if CanAdministrate(user, tool):
        updated_values = {
            'Run': Run,
            'Export': Export,
            'Publish': Publish,
            'Edit': Edit,
            'Admin': Admin,
        }
        
        perms, created = UserToolPermission.objects.update_or_create(
            Tool=tool, User=share_user, defaults=updated_values)
    else:
        raise PermissionDenied


def Unshare(user, tool, share_user):
    if CanAdministrate(user, tool):
        perm = get_object_or_404(UserToolPermission, Tool=tool, User=share_user)
        perm.delete()
    else:
        raise PermissionDenied
    