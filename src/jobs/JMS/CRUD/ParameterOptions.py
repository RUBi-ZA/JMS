from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

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