from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q

from jobs.models import JobStageDataSection

def GetJobStageDataSection(jobstage, section_name):
    data_section, created = JobStageDataSection.objects.get_or_create(JobStage=jobstage,
        DataSectionName=section_name)
    return data_section