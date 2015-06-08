from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from jobs.models import StageDependency

import WorkflowPermissions

def GetStageDependency(user, id):
    dep = get_object_or_404(StageDependency, pk=id)
    if WorkflowPermissions.CanEdit(user, dep.StageOI.WorkflowVersion.Workflow):
        return dep
    else:
        raise PermissionDenied


def GetStageDependencies(user, workflow_version):
    if WorkflowPermissions.CanEdit(user, workflow_version.Workflow):
        return StageDependency.objects.filter(
            Stage__WorkflowVersion=workflow_version)
    else:
        raise PermissionDenied


def AddStageDependency(user, stage, dependant_on, condition, exit_code):
    if WorkflowPermissions.CanEdit(user, stage.WorkflowVersion.Workflow):
        return StageDependency.objects.create(StageOI=stage, 
            DependantOn_id=dependant_on, Condition_id=condition,
            ExitCodeValue=exit_code)
    else:
        raise PermissionDenied


def UpdateStageDependency(user, stage_dependency, condition, exit_code):
    if WorkflowPermissions.CanEdit(user, stage_dependency.StageOI.WorkflowVersion.Workflow):
        stage_dependency.Condition_id = condition
        stage_dependency.ExitCodeValue = exit_code
        stage_dependency.save()
        return stage_dependency
    else:
        raise PermissionDenied


def DeleteStageDependency(user, stage_dependency):
    if WorkflowPermissions.CanEdit(user, stage_dependency.StageOI.WorkflowVersion.Workflow):
        stage_dependency.delete()
    else:
        raise PermissionDenied