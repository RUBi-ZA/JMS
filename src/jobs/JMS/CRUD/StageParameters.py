from django.core.exceptions import PermissionDenied
from django.db import transaction

from jobs.models import StageParameter

import WorkflowPermissions

def UpdateStageParameters(user, stage, parameters):
    if WorkflowPermissions.CanEdit(user, stage.WorkflowVersion.Workflow):
        with transaction.atomic():
            #delete all old stage parameters
            stage.StageParameters.all().delete()
            
            #add new stage parameters
            for p in parameters:
                StageParameter.objects.create(Stage=stage, 
                    Parameter_id=p["ParameterID"],
                    StageParameterType=p["StageParameterTypeID"], 
                    Value=p["Value"]
                )