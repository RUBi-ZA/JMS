from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q

from jobs.models import JobStageDataField

def AddOrUpdate(data_section, data_field):
    try:
        data = JobStageDataField.objects.get(
            JobStageDataSection=data_section, Key=data_field.Key
        )
        data.Value = data_field.DefaultValue
        data.Label = data_field.Label
        data.ValueType = data_field.ValueType
        
        data.save()
        return data
        
    except Exception, ex:
        return JobStageDataField.objects.create(JobStageDataSection=data_section,
            Key=data_field.Key, Value=data_field.DefaultValue, 
            Label=data_field.Label, ValueType = data_field.ValueType)
    
    return data