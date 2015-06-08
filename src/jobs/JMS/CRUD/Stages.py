from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction

from jobs.models import Stage

import WorkflowPermissions


def GetStages(version):
    return version.WorkflowVersionStages.all()


def GetStage(user, stage_id):
    stage = get_object_or_404(Stage, pk=stage_id)
    if WorkflowPermissions.CanView(user, stage.WorkflowVersion.Workflow):
        return stage
    else:
        raise PermissionDenied


def AddStage(user, workflow_version, tool_version=None, subworkflow_version=None,
    checkpoint=False, left=0, top=0):
    if WorkflowPermissions.CanEdit(user, workflow_version.Workflow):
        return Stage.objects.create(WorkflowVersion=workflow_version, 
            ToolVersion=tool_version, SubWorkflowVersion=subworkflow_version,
            Checkpoint=checkpoint, left_co_ord=left, top_co_ord=top
        )
    else:
        raise PermissionDenied


def UpdateStage(user, stage, tool_version=None, subworkflow_version=None,
    checkpoint=False):
    if WorkflowPermissions.CanEdit(user, stage.WorkflowVersion.Workflow):
        stage.ToolVersion = tool_version
        stage.SubWorkflowVersion = subworkflow_version
        stage.Checkpoint = checkpoint
        stage.save()
        return stage
    else:
        raise PermissionDenied


def MoveStage(user, stage, left, top):
    if WorkflowPermissions.CanEdit(user, stage.WorkflowVersion.Workflow):
        stage.left_co_ord = left
        stage.top_co_ord = top
        stage.save()
        return stage
    else:
        raise PermissionDenied


def DeleteStage(user, stage):
    if WorkflowPermissions.CanEdit(user, stage.WorkflowVersion.Workflow):
        stage.delete()
    else:
        raise PermissionDenied


def UpdateStageLevel(stage):
    with transaction.atomic():
        current_level = stage.StageLevel
        max_dependency = -1
        
        for s in stage.StageDependencies.all():
            if s.DependantOn.StageLevel > max_dependency:
                max_dependency = s.DependantOn.StageLevel
        
        stage.StageLevel = max_dependency + 1
        stage.save()
        
        #update reliant stages    
        for s in stage.ReliantStages.all():
            UpdateStageLevel(s.StageOI)
    