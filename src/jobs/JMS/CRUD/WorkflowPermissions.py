from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from jobs.models import UserWorkflowPermission


def GetWorkflowPermission(user, workflow):
    try:
        return UserWorkflowPermission.objects.get(Workflow=workflow, User=user)
    except:
        raise PermissionDenied


def GetToolPermissions(workflow):
    return workflow.UserWorkflowPermissions.all()
    

def CanView(user, workflow):
    return workflow.User.id == user.id or GetWorkflowPermission(user, workflow)


def CanRun(user, workflow):
    return workflow.User.id == user.id or GetWorkflowPermission(user, workflow).Run


def CanEdit(user, workflow):
    return workflow.User.id == user.id or GetWorkflowPermission(user, workflow).Edit


def CanPublish(user, workflow):
    return workflow.User.id == user.id or GetWorkflowPermission(user, workflow).Publish


def CanExport(user, workflow):
    return workflow.User.id == user.id or GetWorkflowPermission(user, workflow).Export


def CanAdministrate(user, workflow):
    return workflow.User.id == user.id or GetWorkflowPermission(user, workflow).Admin


def Share(user, workflow, share_user, Run=True, Export=False, Publish=False, Edit=False, Admin=False):
    if CanAdministrate(user, workflow):
        updated_values = {
            'Run': Run,
            'Export': Export,
            'Publish': Publish,
            'Edit': Edit,
            'Admin': Admin,
        }
        
        perms, created = UserWorkflowPermission.objects.update_or_create(
            Workflow=workflow, User=share_user, defaults=updated_values)
    else:
        raise PermissionDenied


def Unshare(user, workflow, share_user):
    if CanAdministrate(user, workflow):
        perm = get_object_or_404(UserWorkflowPermission, Workflow=workflow, User=share_user)
        perm.delete()
    else:
        raise PermissionDenied
