from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from jobs.models import JobStage

import JobPermissions


def AddJobStage(user, job, Stage=None, RequiresEditInd=False, StatusID=1,
    ClusterJobID=None, ExitCode=None, OutputLog=None, ErrorLog=None, PWD=None, 
    JobData=None, Commands=None):
    return JobStage.objects.create(Job=job, Stage=Stage, 
        RequiresEditInd=RequiresEditInd, Status_id=StatusID,
        ClusterJobID=ClusterJobID, ExitCode=None, JobData=JobData, 
        Commands=Commands)


def UpdateJobStage(jobstage, Status, ExitCode, OutputLog, ErrorLog, PWD, JobData):
    jobstage.Status_id = Status
    jobstage.ExitCode = ExitCode
    jobstage.ErrorLog = ErrorLog
    jobstage.OutputLog = OutputLog
    jobstage.WorkingDirectory = PWD
    jobstage.JobData = JobData
    
    jobstage.save()
    return jobstage


def GetJobStage(cluster_id):
    stage = JobStage.objects.filter(ClusterJobID=cluster_id)
    if len(stage) == 1:
        return stage[0]
    else:
        return None


def GetJobStageByID(user, id):
    stage = JobStage.objects.get(pk=id)
    if JobPermissions.CanView(user, stage.Job):
        return stage
    else:
        raise PermissionDenied

    