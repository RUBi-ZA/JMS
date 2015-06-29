from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from jobs.JMS.resource_managers.objects import Setting
from jobs.JMS.CRUD import JobStages
from utilities.io.filesystem import Directory, File

import getpass, os

#dynamically import the resource manager module
module_name = settings.JMS_SETTINGS["resource_manager"]["name"]
module = __import__('jobs.JMS.resource_managers.%s' % module_name, 
    fromlist=[module_name])

#get the resource manager class from the module
ResourceManager = getattr(module, module_name)

class Command(BaseCommand):
    args = '<action [param_1 param_2 ...]>'
    help = 'Parameters are specific to the action being performed'
    
    def handle(self, *args, **options):
        temp_dir = os.path.join(settings.JMS_SETTINGS["JMS_shared_directory"], 
            "tmp/")
            
        user = User.objects.get(username=getpass.getuser())
        try:
            action = args[0]
            
            if action == "setup_job":
                job_stage_id = int(args[1])
                stage_index = int(args[2])
                
                jobstage = JobStages.GetJobStageByID(user, job_stage_id)
                
                temp_job_dir = os.path.join(temp_dir, ".%s/%d" % (user, job_stage_id))
                
                job_name = jobstage.Job.JobName
                script_name = "job.sh"
                
                parsed_settings = []
                for resource in jobstage.JobStageResources.all():
                    s = Setting(resource.Key, resource.Value)
                    parsed_settings.append(s)
                
                Directory.copy_directory(temp_job_dir, jobstage.WorkingDirectory)
                Directory.create_directory(os.path.dirname(jobstage.OutputLog))
                Directory.create_directory(os.path.dirname(jobstage.ErrorLog))
                
                #get dependencies
                has_dependencies = False
                if jobstage.Job.JobTypeID == 3:
                    has_dependencies = len(jobstage.Stage.StageDependencies.all()) > 0
                
                #create job script
                r = ResourceManager(user)
                script = r.CreateJobScript(job_name.replace(' ', '_'), 
                    jobstage.WorkingDirectory, script_name, jobstage.OutputLog, 
                    jobstage.ErrorLog, parsed_settings, has_dependencies, 
                    jobstage.Commands)
                
                return script
        
        except Exception, ex:
            File.print_to_file("/tmp/%s_acl.log" % user.username, str(ex))
