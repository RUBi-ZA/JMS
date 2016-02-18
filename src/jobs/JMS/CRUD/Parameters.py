from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from copy import deepcopy

from jobs.models import Parameter

import ToolPermissions, ToolVersions, ParameterOptions

def GetParameters(version, with_children=True):
    if with_children:
        return version.ToolParameters.all()
    else:
        return version.ToolParameters.filter(ParentParameter=None)
    
    
def CopyParameters(user, old_version, new_version):
    if ToolPermissions.CanPublish(user, old_version.Tool):
        parameters = GetParameters(old_version)
        params = {}
        
        for old_param in parameters:
            parent_param_id = old_param.ParameterID
            
            param = deepcopy(old_param)
            
            param.ParameterID = None
            param.ToolVersion = new_version
            
            #if this is a child parameter, update the parent to the copy of the parent
            if param.ParentParameter:
                param.ParentParameter = params[param.ParentParameter.ParameterID]
            
            #save to add copy to datebase with new ID
            param.save()
            
            ParameterOptions.CopyOptions(user, old_param, param)
            
            #store the ID change for any child parameters
            params[parent_param_id] = param
    else:
        raise PermissionDenied


def DeleteParameters(user, version):
    if ToolPermissions.CanEdit(user, version.Tool):
        for p in version.ToolParameters.all():
            p.delete()
    else:
        raise PermissionDenied   


def GetUserParameters(version):
    return version.ToolParameters.filter(DeletedInd=False, InputBy="system")


def GetParameterAndChildren(user, parameter_id):
    param = Parameter.objects.filter(
        Q(ParameterID=parameter_id) |
        Q(ParentParameter_id=parameter_id)
    )
    
    if ToolPermissions.CanView(user, param[0].ToolVersion.Tool):
        return param
    else:
        raise PermissionDenied


def GetParameter(user, parameter_id):
    param = Parameter.objects.get(ParameterID=parameter_id)
    
    if ToolPermissions.CanView(user, param.ToolVersion.Tool):
        return param
    else:
        raise PermissionDenied


def AddParameter(user, tool, parameter_name, parent_id=None):
    version = ToolVersions.GetToolVersion(tool, "dev")
    index = len(version.ToolParameters.all())
    
    if ToolPermissions.CanEdit(user, tool):
        return Parameter.objects.create(ParameterName=parameter_name, Context="",
            InputBy="user", Value="", ParameterType_id=1, ToolVersion=version,
            ParameterIndex=index, ParentParameter_id=parent_id)
    else:
        raise PermissionDenied


def UpdateParameter(user, parameter, param_name, context, input_by, value, 
    multiple, param_type, delimiter, optional, index):
    
    if ToolPermissions.CanEdit(user, parameter.ToolVersion.Tool):
        parameter.ParameterName = param_name
        parameter.Context = context
        parameter.InputBy = input_by
        parameter.Value = value
        parameter.Multiple = multiple    
        parameter.ParameterType_id = param_type
        parameter.Delimiter = delimiter
        parameter.Optional = optional
        parameter.ParameterIndex = index
        parameter.save()
    else:
        raise PermissionDenied


def DeleteParameter(user, parameter_id):
    param = Parameter.objects.get(ParameterID=parameter_id)
    
    if ToolPermissions.CanEdit(user, param.ToolVersion.Tool):
        param.delete()
    else:
        raise PermissionDenied
  
    