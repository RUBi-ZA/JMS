from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q

import JobPermissions

from jobs.models import Job

def AddJob(User, JobName, Description, ToolVersion, JobTypeID):
    return Job.objects.create(User=User, JobName=JobName, 
        JobDescription=Description, ToolVersion=ToolVersion, JobTypeID=JobTypeID)
    

def GetJobs(user):
    return Job.objects.filter(
        Q(DeletedInd=False) &
        (
            Q(User=user) |
            Q(UserJobPermissions__User=user)
        )
    )


def GetJob(user, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if JobPermissions.CanView(user, job):
        return job
    else:
        raise PermissionDenied


def FilterJobsByParameter(user, filters):
    #get all user jobs
    jobs = GetJobs(user)
    
    #build filter
    kwargs = {}
    for f in filters:
        kwargs[f["Field"]] = f["Value"]
    
    return jobs.filter(**kwargs)
    
    