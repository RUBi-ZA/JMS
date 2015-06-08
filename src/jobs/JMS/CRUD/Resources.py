from jobs.models import ToolVersionResource
from django.core.exceptions import PermissionDenied

import ToolPermissions

def UpdateResources(user, version, resource_manager, resources):
    if ToolPermissions.CanEdit(user, version.Tool):
        #get existing resources
        existing = ToolVersionResource.objects.filter(ToolVersion=version,
            ResourceManager=resource_manager)
        
        #loop through new resources, add and update as required
        for r in resources:
            e = existing.filter(Key=r["Key"])
            if len(e) == 0:
                #resource doesn;t yet exist so add it
                ToolVersionResource.objects.create(ToolVersion=version,
                    ResourceManager=resource_manager, Key=r["Key"], 
                    Value=r["Value"], Label=r["Label"])
            else:
                #resource exists so update it
                e[0].Value = r["Value"]
                e[0].Label = r["Label"]
                e[0].save()
                
    else:
        raise PermissionDenied


def GetResources(user, version, resource_manager):
    return version.Resources.filter(ResourceManager=resource_manager)


def CopyResources(user, old_version, new_version):
    if ToolPermissions.CanPublish(user, old_version.Tool):
        resources = old_version.Resources.all()
        
        for old in resources:
            new = old
            new.ToolVersionResourceID = None
            new.ToolVersion = new_version
            new.save()
    else:
        raise PermissionDenied


def DeleteResources(user, version):
    if ToolPermissions.CanEdit(user, version.Tool):
        for r in version.Resources.all():
            r.delete()
    else:
        raise PermissionDenied 
    