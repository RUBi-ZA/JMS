from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from jobs.models import ExpectedOutput

import ToolPermissions, ToolVersions

def AddExpectedOutput(user, tool, output_name, file_name, file_type_id):
    version = ToolVersions.GetToolVersion(tool, "dev")
    
    if ToolPermissions.CanEdit(user, tool):
        return ExpectedOutput.objects.create(OutputName=output_name, 
            FileName=file_name, FileType_id=file_type_id, 
            ToolVersion=version
        )
    else:
        raise PermissionDenied


def UpdateExpectedOutput(user, output_id, output_name, file_name, file_type_id):
    output = get_object_or_404(ExpectedOutput, pk=output_id)
    
    if ToolPermissions.CanEdit(user, output.ToolVersion.Tool):
        output.OutputName = output_name
        output.FileName = file_name
        output.FileType_id = file_type_id
        output.save()
        
        return output
    else:
        raise PermissionDenied


def DeleteExpectedOutput(user, output_id):
    output = get_object_or_404(ExpectedOutput, pk=output_id)
    
    if ToolPermissions.CanEdit(user, output.ToolVersion.Tool):
        output.delete()
    else:
        raise PermissionDenied


def CopyOutputs(user, old_version, new_version):
    if ToolPermissions.CanPublish(user, old_version.Tool):
        outputs = old_version.ExpectedOutputs.all()
        
        for out in outputs:
            out.ExpectedOutputID = None
            out.ToolVersion = new_version
            out.save()
    else:
        raise PermissionDenied


def DeleteOutputs(user, version):
    if ToolPermissions.CanEdit(user, version.Tool):
        for o in version.ExpectedOutputs.all():
            o.delete()
    else:
        raise PermissionDenied 

