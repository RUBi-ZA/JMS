from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from jobs.JMS.resource_managers.objects import Setting
from utilities.io.filesystem import Directory

import getpass, os

#dynamically import the resource manager module
module_name = settings.JMS_SETTINGS["resource_manager"]["name"]
module = __import__('jobs.JMS.resource_managers.%s' % module_name, 
    fromlist=[module_name])

#get the resource manager class from the module
ResourceManager = getattr(module, module_name)

class Command(BaseCommand):
    args = '<action [param_1 param_2 ...]>'
    help = 'Parameters are specific to the operation being performed'
    
    def handle(self, *args, **options):
        temp_dir = os.path.join(settings.JMS_SETTINGS["JMS_shared_directory"], 
            "tmp/")
        
        action = args[0]
        
        if action == "setup_job":
            job_id = int(args[1])
            stage_index = int(args[2])
            user = User.objects.get(username=getpass.getuser())
            
            temp_job_dir = os.path.join(temp_dir, ".%s/%d" % (user, job_id))
            
            #get job details
            details = open(os.path.join(temp_job_dir, "details_%d.txt" % stage_index), 'rU').readlines()
            
            job_name = details[0]
            script_name = details[1].strip()
            dependencies = details[3]
            command = "\n".join(details[4:])
            
            parsed_settings = []
            for resource in details[2].strip().split(","):
                kv = resource.split("=")
                if len(kv) == 2:
                    s = Setting(kv[0], kv[1])
                    parsed_settings.append(s)
            
            #create job directory and copy tool files from temp directory
            job_dir = os.path.join(settings.JMS_SETTINGS["JMS_shared_directory"],
                "users/%s/jobs/%d" % (user, job_id)
            )
            
            Directory.copy_directory(temp_job_dir, job_dir)
            
            #create job script
            r = ResourceManager(user)
            script = r.CreateJobScript(job_name.replace(' ', '_'), job_dir, 
                script_name, parsed_settings, dependencies, command)
            
            return script
