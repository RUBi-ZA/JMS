from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from jobs.models import Workflow, Category
from utilities.io.filesystem import File

import WorkflowPermissions


def GetWorkflows(user):
    return Workflow.objects.filter(
        Q(DeletedInd=False) &
        (
            Q(PublicInd=True) | 
            Q(User__id=user.id) | 
            Q(UserWorkflowPermissions__User__id=user.id)
        )
    ).distinct()


def GetWorkflow(user, workflow_id):
    workflow = get_object_or_404(Workflow, pk=workflow_id)
    if WorkflowPermissions.CanView(user, workflow):
        return workflow
    else:
        raise PermissionDenied


def AddWorkflow(user, WorkflowName, CategoryID, Description, PublicInd=False):
    return Workflow.objects.create(WorkflowName=WorkflowName,
        Category_id=CategoryID, Description=Description, 
        PublicInd=PublicInd, User=user)


def DeleteWorkflow(user, workflow_id):
    workflow = get_object_or_404(Workflow, pk=workflow_id)
    if WorkflowPermissions.CanAdministrate(user, workflow):
        workflow.DeletedInd = True
        workflow.save()
    else:
        raise PermissionDenied


def UpdateWorkflow(user, workflow_id, WorkflowName, CategoryID, Description):
    workflow = GetWorkflow(user, workflow_id)
    if WorkflowPermissions.CanEdit(user, workflow):
        workflow.WorkflowName = WorkflowName
        workflow.Category_id = CategoryID
        workflow.Description = Description
        workflow.save()
        return workflow
    else:
        raise PermissionDenied


def UpdateAvailability(user, workflow, PublicInd):
    if WorkflowPermissions.CanAdministrate(user, workflow):
        workflow.PublicInd = PublicInd
        workflow.save()
        return workflow
    else:
        raise PermissionDenied


def ShareWorkflow(user, workflow, share_user, Run=True, Export=False, Publish=False, Edit=False, Admin=False):
    WorkflowPermissions.Share(user, workflow, share_user, Run, Export, Publish, Edit, Admin)


def UnshareWorkflow(user, workflow, share_user):
    WorkflowPermissions.Unshare(user, workflow, share_user)


def ExportWorkflow(user, workflow_id):
    workflow = GetWorkflow(user, workflow_id)
    if WorkflowPermissions.CanExport(user, workflow):
        raise NotImplementedError
    else:
        raise PermissionDenied
