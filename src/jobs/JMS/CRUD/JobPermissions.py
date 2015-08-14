from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from jobs.models import UserJobPermission



def GetJobPermission(user, job):
    try:
        return UserJobPermission.objects.get(Job=job, User=user)
    except:
        raise PermissionDenied


def GetJobPermissions(job):
    return job.GetJobPermissions.all()
    

def CanView(user, job):
    return job.User.id == user.id or UserJobPermission(user, job)


def CanRepeat(user, job):
    return job.User.id == user.id or UserJobPermission(user, job).Repeat


def CanAdministrate(user, job):
    return job.User.id == user.id or UserJobPermission(user, job).Admin


def Share(user, job, share_user, Repeat=True, Admin=False):
    if CanAdministrate(user, tool):
        updated_values = {
            'Repeat': Repeat,
            'Admin': Admin,
        }
        
        perms, created = UserJobPermission.objects.update_or_create(
            Tool=tool, User=share_user, defaults=updated_values)
    else:
        raise PermissionDenied


def Unshare(user, tool, share_user):
    if CanAdministrate(user, tool):
        perm = get_object_or_404(UserJobPermission, Tool=tool, User=share_user)
        perm.delete()
    else:
        raise PermissionDenied
    