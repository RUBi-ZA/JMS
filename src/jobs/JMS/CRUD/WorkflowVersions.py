from django.core.exceptions import PermissionDenied
from jobs.models import WorkflowVersion

from copy import deepcopy

import WorkflowPermissions

def AddWorkflowVersion(user, Workflow, WorkflowVersionNum, ShortDescription, 
    LongDescription):
    if WorkflowPermissions.CanPublish(user, Workflow):
        return WorkflowVersion.objects.create(
            Workflow=Workflow, 
            WorkflowVersionNum=WorkflowVersionNum, 
            ShortDescription=ShortDescription, 
            LongDescription=LongDescription
        )
    else:
        raise PermissionDenied


def UpdateWorkflowVersion(user, version, ShortDescription, LongDescription):
    if WorkflowPermissions.CanEdit(user, version.Workflow):
        version.ShortDescription = ShortDescription
        version.LongDescription = LongDescription
        version.save()
        return version
    else:
        raise PermissionDenied


def GetWorkflowVersions(Workflow):
    return Workflow.WorkflowVersions.all().order_by("-WorkflowVersionID")
    

def GetWorkflowVersion(Workflow, version_num):
    return Workflow.WorkflowVersions.get(WorkflowVersionNum=version_num)