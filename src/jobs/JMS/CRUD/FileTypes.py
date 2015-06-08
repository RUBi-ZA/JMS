from django.core.exceptions import PermissionDenied

from jobs.models import FileType

def GetFileTypes():
    return FileType.objects.all()


def AddFileType(user, file_type_name):
    filetypes = FileType.objects.filter(FileTypeName__iexact=file_type_name)
    if len(filetypes) == 0:
        return FileType.objects.create(FileTypeName=file_type_name)
    else:
        #this file type already exists
        raise Exception("This file type already exists")