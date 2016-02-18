from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from copy import deepcopy

from jobs.models import ParameterOption

import ToolPermissions


def AddParameterOption(user, parameter, text, value):
    if ToolPermissions.CanEdit(user, parameter.ToolVersion.Tool):
        return ParameterOption.objects.create(ParameterOptionText=text,
            ParameterOptionValue=value, Parameter=parameter)
    else:
        raise PermissionDenied


def UpdateParameterOption(user, parameter, option_id, text, value):
    option = parameter.ParameterOptions.get(pk=option_id)
    if ToolPermissions.CanEdit(user, parameter.ToolVersion.Tool):
        option.ParameterOptionText = text
        option.ParameterOptionValue = value
        option.save()
        return option
    else:
        raise PermissionDenied


def DeleteParameterOption(user, parameter, option_id):
    option = parameter.ParameterOptions.get(pk=option_id)
    if ToolPermissions.CanEdit(user, parameter.ToolVersion.Tool):
        option.delete()
    else:
        raise PermissionDenied


def CopyOptions(user, old_parameter, new_parameter):
    if ToolPermissions.CanEdit(user, old_parameter.ToolVersion.Tool):
        for old_option in old_parameter.ParameterOptions.all():
            option = deepcopy(old_option)
            
            option.ParameterOptionID = None
            option.Parameter = new_parameter
            
            option.save()
    else:
        raise PermissionDenied