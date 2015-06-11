from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User, Group

from jobs.models import *

from CRUD import Tools, ToolVersions, Categories, Parameters
from CRUD import ParameterOptions, FileTypes, ExpectedOutputs, Resources
from CRUD import Workflows, WorkflowVersions, Stages, StageParameters
from CRUD import StageDependencies, Jobs, JobStages, JobStageDataSections
from CRUD import JobStageDataFields, JobPermissions

from helpers import *
from resource_managers import objects

from utilities.io.filesystem import *

import shutil, json

#dynamically import the resource manager module
module_name = settings.JMS_SETTINGS["resource_manager"]["name"]
module = __import__('jobs.JMS.resource_managers.%s' % module_name, 
    fromlist=[module_name])

#get the resource manager class from the module
ResourceManager = getattr(module, module_name)

class JobManager:
    
    def __init__(self, user=None):
        self.base_dir = settings.JMS_SETTINGS["JMS_shared_directory"]
        self.users_dir = os.path.join(self.base_dir, "users/")
        self.user = user
    
    
    def make_tool_directory(self, tool_id, version):
        tool_dir = os.path.join(self.base_dir, "tools/")
        path = os.path.join(tool_dir, "%d/%s" % (tool_id, version))
        Directory.create_directory(path, permissions=0700)
        return path
    
    
    def make_workflow_directory(self, workflow_id, version):
        workflow_dir = os.path.join(self.base_dir, "workflows/")
        path = os.path.join(workflow_dir, "%d/%s" % (workflow_id, version))
        Directory.create_directory(path, permissions=0775)
        return path
    
    
    def make_data_directory(self):
        data_dir = os.path.join(self.users_dir, "data/")
        Directory.create_directory(data_dir, permissions=0775)
        return data_dir
    
    
    def make_job_directory(self, job_id):
        job_dir = os.path.join(self.users_dir, self.user.username + "/jobs/")
        path = os.path.join(job_dir, str(job_id))
        Directory.create_directory(path, permissions=0775)
        return path

    
    def GetDashboard(self):
        r = ResourceManager(self.user)
        return r.GetDashboard()
    
    
    def GetSettings(self):
        r = ResourceManager(self.user)
        return r.GetSettings()
    
    
    def UpdateSettings(self, settings_sections_dict):
        r = ResourceManager(self.user)
        settings_sections = parse_settings_sections_dict(settings_sections_dict)
        r.UpdateSettings(settings_sections)
        return r.GetSettings()
    
    
    def GetNodes(self):
        r = ResourceManager(self.user)
        return r.GetNodes()
    
    
    def AddNode(self, node_dict):
        r = ResourceManager(self.user)
        node = parse_node_dict(node_dict)
        r.AddNode(node)
        return r.GetNodes()
    
    
    def UpdateNode(self, node_dict):
        r = ResourceManager(self.user)
        node = parse_node_dict(node_dict)
        r.UpdateNode(node)
        return r.GetNodes()
    
    
    def DeleteNode(self, id):
        r = ResourceManager(self.user)
        r.DeleteNode(id)
        return r.GetNodes()
    
    
    def GetAdministrators(self):
        r = ResourceManager(self.user)
        return r.GetAdministrators()
    
    
    def AddAdministrator(self, admin_dict):
        r = ResourceManager(self.user)
        r.AddAdministrator(admin_dict["AdministratorName"])
    
    
    def UpdateAdministrator(self, admin_dict):
        r = ResourceManager(self.user)
        administrator = parse_admin_dict(admin_dict)
        r.UpdateAdministrator(administrator)
    
    
    def DeleteAdministrator(self, admin_name):
        r = ResourceManager(self.user)
        r.DeleteAdministrator(admin_name)
    
    
    def GetQueues(self):
        r = ResourceManager(self.user)
        return r.GetQueues()
    
    
    def AddQueue(self, queue_name):
        r = ResourceManager(self.user)
        r.AddQueue(queue_name)
    
    
    def DeleteQueue(self, queue_name):
        r = ResourceManager(self.user)
        r.DeleteQueue(queue_name)
    
    
    def UpdateQueue(self, queue_dict):
        r = ResourceManager(self.user)
        queue = parse_queue_dict(queue_dict)
        r.UpdateQueue(queue)
    
    
    def GetDefaultResources(self):
        r = ResourceManager(self.user)
        return r.GetDefaultResources()
    
    
    def GetCategories(self):
        categories = Categories.GetCategories()
        return categories
    
    
    def AddCategory(self, category_name):
        category = Categories.AddCategory(self.user, category_name)
        return category
    
    
    def DeleteCategory(self, category_id):
        Categories.DeleteCategory(self.user, category_id)
    
    
    def UpdateCategory(self, category_id, category_name):
        category = Categories.UpdateCategory(self.user, category_id, 
            category_name)
        return category
    
    
    def GetTools(self):
        tools = Tools.GetTools(self.user)
        return tools
    
    
    def GetTool(self, tool_id):
        return Tools.GetTool(self.user, tool_id)
    
    
    def AddTool(self, tool):
        with transaction.atomic():
            #create the tool
            tool = Tools.AddTool(self.user, tool["ToolName"], 
                tool["Category"], tool["ToolDescription"], False)
            
            #create the development tool version
            toolversion = ToolVersions.AddToolVersion(self.user, tool, "dev", 
                tool.ToolDescription, "")
            
            self.make_tool_directory(tool.ToolID, toolversion.ToolVersionNum)
        
        return toolversion
    
    
    def DeleteTool(self, tool_id):
        Tools.DeleteTool(self.user, tool_id)
    
    
    def UpdateTool(self, tool_id, version):
        tool = self.GetTool(tool_id)
        with transaction.atomic():
            #update tool details
            tool_details = version["Tool"]
            tool = Tools.UpdateTool(self.user, tool, 
                ToolName=tool_details["ToolName"], 
                CategoryID=tool_details["CategoryID"],
                ToolDescription=version["ShortDescription"]
            )
            
            #update version details
            tool_version = self.GetToolVersion(tool, "dev")
            tool_version = ToolVersions.UpdateToolVersion(self.user,
                tool_version, version["ShortDescription"], 
                version["LongDescription"], version["Command"]
            )
            
            #update parameters
            for i, p in enumerate(version["Parameters"]):
                parameter = self.UpdateParameter(p, i)
            
            #update/add expected outputs
            for o in version["ExpectedOutputs"]:
                if o["ExpectedOutputID"]:
                    self.UpdateExpectedOutput(o)
                else:
                    self.AddExpectedOutput(tool, o)
            
            #update/add default resources
            Resources.UpdateResources(self.user, tool_version, 
                settings.JMS_SETTINGS["resource_manager"]["name"],
                version["Resources"]
            )
            
        return tool
    
    
    def UpdateToolAvailability(self, tool_id, publicInd):
        tool = self.GetTool(tool_id)
        return Tools.UpdateAvailability(self.user, tool, publicInd)
    
    
    def GetToolVersions(self, tool_id):
        tool = self.GetTool(tool_id)
        return ToolVersions.GetToolVersions(tool)
    
    
    def GetToolVersion(self, tool, version_num):
        return ToolVersions.GetToolVersion(tool, version_num)


    def PublishTool(self, tool_id, version_nums):
        tool = self.GetTool(tool_id)
        
        version_num = "%s.%s.%s" % (version_nums['Major'],version_nums['Minor'],
            version_nums['Patch'])
            
        with transaction.atomic():
            #copy the development tool version
            dev = ToolVersions.GetDevelopmentVersion(tool)
            new = ToolVersions.PublishToolVersion(self.user, dev, version_num)
            
            #copy dev scripts and files to new version
            dev_dir = os.path.join(self.base_dir, "tools/%s/dev" % str(tool_id))
            new_dir = os.path.join(self.base_dir, "tools/%s/%s" % (str(tool_id),
                new.ToolVersionNum))
            Directory.copy_directory(dev_dir, new_dir, 0755)
            
            #copy parameters
            Parameters.CopyParameters(self.user, dev, new)
            
            #copy outputs
            ExpectedOutputs.CopyOutputs(self.user, dev, new)
            
            #copy default resources
            Resources.CopyResources(self.user, dev, new)
        
        return new
    
    
    def RevertToolVersion(self, tool_id, version_num):
        tool = self.GetTool(tool_id)
            
        with transaction.atomic():
            dev = ToolVersions.GetDevelopmentVersion(tool)
            ver = ToolVersions.GetToolVersion(tool, version_num)
            
            #set development version details to old details
            dev.ShortDescription = ver.ShortDescription
            dev.LongDescription = ver.LongDescription
            dev.save()
            
            #delete development parameters and replace with old parameters
            Parameters.DeleteParameters(self.user, dev)
            Parameters.CopyParameters(self.user, ver, dev)
            
            #delete development outputs and replace with old outputs
            ExpectedOutputs.DeleteOutputs(self.user, dev)
            ExpectedOutputs.CopyOutputs(self.user, ver, dev)
            
            #delete development outputs and replace with old outputs
            Resources.DeleteResources(self.user, dev)
            Resources.CopyResources(self.user, ver, dev)
            
            #delete development scripts and files and replace with old
            dev_dir = os.path.join(self.base_dir, "tools/%s/dev" % str(tool_id))
            ver_dir = os.path.join(self.base_dir, "tools/%s/%s" % (str(tool_id),
                ver.ToolVersionNum))
            
            shutil.rmtree(dev_dir)
            Directory.copy_directory(ver_dir, dev_dir, 0755)
        
        return dev
    
    
    def GetRootParameters(self, tool_id):
        tool = self.GetTool(tool_id)
        return Parameters.GetRootParameters(tool)
    
    
    def GetParameter(self, parameter_id, with_children=True):
        if with_children:
            return Parameters.GetParameterAndChildren(self.user, parameter_id)
        else:
            return Parameters.GetParameter(self.user, parameter_id)
    
    
    def AddParameter(self, tool_id, parameter_name, parent_id=None):
        tool = Tools.GetTool(self.user, tool_id)
        return Parameters.AddParameter(self.user, tool, parameter_name, parent_id)
    
    
    def DeleteParameter(self, parameter_id):
        Parameters.DeleteParameter(self.user, parameter_id)
    
    
    def UpdateParameter(self, parameter, index):
        if parameter["DeleteInd"]:
            self.DeleteParameter(parameter["ParameterID"])
        else:
            param = self.GetParameter(parameter["ParameterID"], with_children=False)
            
            Parameters.UpdateParameter(self.user, param, parameter["ParameterName"], 
                parameter["Context"], parameter["InputBy"], parameter["Value"],
                parameter["Multiple"], parameter["ParameterType"], 
                parameter["Delimiter"], parameter["Optional"], index)
            
            #update parameter options
            for option in parameter["ParameterOptions"]:
                option_id = option["ParameterOptionID"]
                
                if option_id == 0:
                    #this is a new option
                    ParameterOptions.AddParameterOption(self.user, param,
                        option["ParameterOptionText"], 
                        option["ParameterOptionValue"]
                    )
                else:
                    #this is an existing option
                    if option["DeleteInd"]:
                        ParameterOptions.DeleteParameterOption(self.user, param,
                            option_id)
                    else:
                        ParameterOptions.UpdateParameterOption(self.user, param, 
                            option_id, option["ParameterOptionText"], 
                            option["ParameterOptionValue"]
                        )
            
            #update sub parameters
            for i, p in enumerate(parameter["parameters"]):
                if not p["ParameterID"]:
                    #this is a new parameter
                    sub_param = self.AddParameter(param.ToolVersion.Tool.ToolID, 
                        p["ParameterName"], param.ParameterID)
                    
                    p["ParameterID"] = sub_param.ParameterID
                
                self.UpdateParameter(p, i)
            
            return param
    
    
    def UpdateExpectedOutput(self, output):
        if output["DeleteInd"]:
            ExpectedOutputs.DeleteExpectedOutput(self.user, 
                output["ExpectedOutputID"])
        else:
            ExpectedOutputs.UpdateExpectedOutput(self.user, 
                output["ExpectedOutputID"], output["OutputName"],
                output["FileName"], output["FileTypeID"])
    
    
    def AddExpectedOutput(self, tool, output):
        ExpectedOutputs.AddExpectedOutput(self.user, tool, output["OutputName"],
            output["FileName"], output["FileTypeID"])


    def GetFileTypes(self):
        return FileTypes.GetFileTypes()
    
    
    def AddFileType(self, name):
        return FileTypes.AddFileType(self.user, name)
    
    
    def GetToolFiles(self, tool_id):
        path = self.make_tool_directory(int(tool_id), "dev")
        return Tools.GetFileList(self.user, tool_id, path)
        
    
    def UploadToolFiles(self, tool_id, file_dict):
        path = self.make_tool_directory(int(tool_id), "dev")
        return Tools.UploadFiles(self.user, tool_id, path, file_dict)
    
    
    def SaveToolFile(self, tool_id, filename, content):
        tool_dir = self.make_tool_directory(int(tool_id), "dev")
        path = os.path.join(tool_dir, filename)
        Tools.SaveFile(self.user, tool_id, path, content)
    
    
    def CreateToolFile(self, tool_id, filename):
        path = os.path.join(self.base_dir, "tools/%s/dev/%s" % (tool_id, filename))
        Tools.CreateFile(self.user, tool_id, path)
    
    
    def ReadToolFile(self, tool_id, filename):
        path = os.path.join(self.base_dir, "tools/%s/dev/%s" % (tool_id, filename))
        return Tools.ReadFile(self.user, tool_id, path)
    
    
    def DeleteToolFile(self, tool_id, filename):
        path = os.path.join(self.base_dir, "tools/%s/dev/%s" % (tool_id, filename))
        Tools.DeleteFile(self.user, tool_id, path)
    
    
    def ShareTool(self, tool_id, user_name, permissions):
        tool = self.GetTool(tool_id)
        user = User.objects.get(username=user_name)
        
        Tools.ShareTool(self.user, tool, user, Run=permissions["Run"], 
            Export=permissions["Export"], Publish=permissions["Publish"], 
            Edit=permissions["Edit"], Admin=permissions["Admin"]
        )
    
    
    def UnshareTool(self, tool_id, user_name):
        tool = self.GetTool(tool_id)
        user = User.objects.get(username=user_name)
        Tools.UnshareTool(self.user, tool, user)
    
    
    def GetWorkflows(self, ):
        return Workflows.GetWorkflows(self.user)
    
    
    def GetWorkflow(self, workflow_id):
        return Workflows.GetWorkflow(self.user, workflow_id)
    
    
    def AddWorkflow(self, workflow):
        with transaction.atomic():
            #create the workflow
            w = Workflows.AddWorkflow(self.user, workflow["WorkflowName"], 
                workflow["Category"], workflow["Description"], False)
            
            #create the development workflow version
            version = WorkflowVersions.AddWorkflowVersion(self.user, w, 
                "dev",  workflow["Description"], "")
        
        return version
    
    
    def DeleteWorkflow(self, workflow_id):
        Workflows.DeleteWorkflow(self.user, workflow_id)
    
    
    def UpdateWorkflow(self, workflow_id, workflow):
        with transaction.atomic():
            w = Workflows.UpdateWorkflow(self.user, workflow_id, workflow["WorkflowName"], 
                workflow["Category"], workflow["ShortDescription"])
            
            version = self.GetWorkflowVersion(w, 'dev')
            version = WorkflowVersions.UpdateWorkflowVersion(self.user, version, 
                workflow["ShortDescription"], workflow["LongDescription"])
        
        return w
    
    
    def PublishWorkflow(self, workflow_id, version_nums):
        workflow = self.GetWorkflow(workflow_id)
        
        version_num = "%s.%s.%s" % (version_nums['Major'],version_nums['Minor'],
            version_nums['Patch'])
        '''    
        with transaction.atomic():
            #copy the development tool version
            dev = ToolVersions.GetDevelopmentVersion(tool)
            new = ToolVersions.PublishToolVersion(self.user, dev, version_num)
            
            #copy dev scripts and files to new version
            dev_dir = os.path.join(self.base_dir, "tools/%s/dev" % str(tool_id))
            new_dir = os.path.join(self.base_dir, "tools/%s/%s" % (str(tool_id),
                new.ToolVersionNum))
            Directory.copy_directory(dev_dir, new_dir, 0755)
            
            #copy parameters
            Parameters.CopyParameters(self.user, dev, new)
            
            #copy outputs
            ExpectedOutputs.CopyOutputs(self.user, dev, new)
            
            #copy default resources
            Resources.CopyResources(self.user, dev, new)
        '''
        return new
    
    
    def RevertWorkflowVersion(self, workflow_id, version_nums):
        pass
    
    
    def GetWorkflowVersions(self, workflow_id):
        workflow = self.GetWorkflow(workflow_id)
        return WorkflowVersions.GetWorkflowVersions(workflow)
    
    
    def GetWorkflowVersion(self, workflow, version_num):
        return WorkflowVersions.GetWorkflowVersion(workflow, version_num)
    
    
    def ShareWorkflow(self, workflow_id, user_name, permissions):
        workflow = self.GetWorkflow(workflow_id)
        user = User.objects.get(username=user_name)
        
        Workflows.ShareWorkflow(self.user, workflow, user, Run=permissions["Run"], 
            Export=permissions["Export"], Publish=permissions["Publish"], 
            Edit=permissions["Edit"], Admin=permissions["Admin"]
        )
    
    
    def UnshareWorkflow(self, workflow_id, user_name):
        workflow = self.GetWorkflow(workflow_id)
        user = User.objects.get(username=user_name)
        Workflows.UnshareWorkflow(self.user, workflow, user)
    
    
    def UpdateWorkflowAvailability(self, worfklow_id, publicInd):
        workflow = self.GetWorkflow(worfklow_id)
        return Workflows.UpdateAvailability(self.user, workflow, publicInd)
    
    
    def GetStages(self, workflow_id, version_num):
        workflow = self.GetWorkflow(workflow_id)
        version = self.GetWorkflowVersion(workflow, version_num)
        return Stages.GetStages(version)
    
    
    def AddStage(self, workflow_id, stage):
        workflow = self.GetWorkflow(workflow_id)
        version = self.GetWorkflowVersion(workflow, "dev")
        
        tool = self.GetTool(stage["ID"])
        tool_version = self.GetToolVersion(tool, stage["VersionNum"])
        
        return Stages.AddStage(self.user, version, tool_version, None, False,
            stage["Left"], stage["Top"])
    
    
    def GetStage(self, stage_id):
        return Stages.GetStage(self.user, stage_id)
    
    
    def MoveStage(self, stage_id, stage_pos):
        stage = self.GetStage(stage_id)
        
        return Stages.MoveStage(self.user, stage, stage_pos['Left'], 
            stage_pos['Top'])
    
    
    def DeleteStage(self, stage_id):
        stage = self.GetStage(stage_id)
        Stages.DeleteStage(self.user, stage)
    
    
    def UpdateStage(self, stage_id, stage_details):
        with transaction.atomic():
            stage = self.GetStage(stage_id)
            tool = stage.ToolVersion.Tool
            version = self.GetToolVersion(tool, stage_details["VersionNum"])
            
            stage = Stages.UpdateStage(self.user, stage, version, None,
                stage_details["Checkpoint"])
            
            StageParameters.UpdateStageParameters(self.user, stage,
                stage_details["StageParameters"])
            
        return stage
    
    
    def AddStageDependency(self, stage_id, dependency):
        with transaction.atomic():
            stage = self.GetStage(stage_id)
        
            stage_dependency = StageDependencies.AddStageDependency(self.user, 
                stage, dependency['DependantOn'], dependency['Condition'], 
                dependency['ExitCodeValue'])
            
            Stages.UpdateStageLevel(stage)
        
        return stage_dependency
    
    
    def UpdateStageDependency(self, dependency_id, dependency):
        dep = StageDependencies.GetStageDependency(self.user, dependency_id)
        
        return StageDependencies.UpdateStageDependency(self.user, dep,
            dependency["Condition"], dependency["ExitCodeValue"])
    
    
    def DeleteStageDependency(self, dependency_id):
        with transaction.atomic():
            dep = StageDependencies.GetStageDependency(self.user, dependency_id)
            StageDependencies.DeleteStageDependency(self.user, dep)
            
            Stages.UpdateStageLevel(dep.StageOI)
        
        return self.GetStages(dep.StageOI.WorkflowVersion.Workflow.WorkflowID, "dev")
    
    
    def RunCustomJob(self, job_name, description, commands, settings, files):
        with transaction.atomic():
            #create db entries
            job = Jobs.AddJob(User=self.user, JobName=job_name, 
                Description=description, ToolVersion=None, JobTypeID=1)
            jobstage = JobStages.AddJobStage(self.user, job)
            
            #create job directory
            job_dir = self.make_job_directory(job.JobID)
            
            #create job script
            r = ResourceManager(self.user)
            script = r.CreateJobScript(job_name.replace(' ', '_'), job_dir, 
                "custom.pbs", parse_settings_list(settings), [], commands)
            
            #upload supporting files
            for f in files:
                full_path = os.path.join(job_dir, f.name)
                with open(full_path, 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                #set file permissions
                os.chmod(full_path, 0755)
            
            cluster_id = r.ExecuteJobScript(script)
            
            jobstage.ClusterJobID = cluster_id.strip()
            jobstage.save()
            
        return job
    
    
    def RunToolJob(self, tool_version_id, job_name, description, user_parameters, 
        files=[], dependencies=[]):
        version = ToolVersions.GetToolVersionByID(self.user, tool_version_id)
        with transaction.atomic():
            #create db entries
            job = Jobs.AddJob(User=self.user, JobName=job_name, 
                Description=description, ToolVersion=version, JobTypeID=2)
            jobstage = JobStages.AddJobStage(self.user, job)
            
            #create job directory
            job_dir = self.make_job_directory(job.JobID)
            
            #upload files to job directory
            for f in files:
                with open(os.path.join(job_dir, f.name), 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                os.chmod(os.path.join(rootpath, f.name), 0777)
            
            #create settings for tool script
            
            #TODO: user customized resources
            resources = Resources.GetResources(self.user, version, module_name)
            settings = []
            for resource in resources:
                settings.append(Setting(resource.Key, resource.Value))
            
            #generate command for tool script
            command = version.Command
            #TODO: move database call to bottom tier
            parameters = version.ToolParameters.all()
            
            params = ""
            for param in parameters:
                p = param.Context
                
                if param.InputBy == "user":
                    for up in user_parameters:
                        if up["ParameterID"] == param.ParameterID:
                            val = up["Value"]
                else:
                    val = param.Value
                
                #If parameter value comes from a previous stage, fetch the value
                if jobstage.Stage != None:
                    stage_parameter = jobstage.Stage.StageParameters.get(
                        Parameter__ParameterID=int(val)
                    )
                    
                    val = prev_param.Value
                  
                
                JobStageParameter.objects.create(JobStage=jobstage, Parameter=param,
                    ParameterName=param.ParameterName, Value=val)
                
                if param.ParameterType.ParameterTypeID != 3:
                    try:
                        #check if the ${VALUE} variable is located in the string
                        num = p.index("${VALUE}")
                        p = p.replace("${VALUE}", val)
                    except Exception, e:
                        #if the ${VALUE} variable is not located in the string, append the value to the end
                        p += " %s" % val                
                    
                    params += ' %s' % p
                    
                command += params
            
            r = ResourceManager(self.user)
            script = r.CreateJobScript(job_name.replace(' ', '_'), job_dir, 
                "tool.pbs", settings, dependencies, command)
            
            cluster_id = r.ExecuteJobScript(script)
            
            jobstage.ClusterJobID = cluster_id.strip()
            jobstage.save()
        
        return job
    
    
    def GetJobs(self):
        return Jobs.GetJobs(self.user)[0:100]
    
    
    def GetJob(self, job_id):
        return Jobs.GetJob(self.user, job_id)
    
    
    def StopJob(self, job):
        if JobPermissions.CanAdministrate(self.user, job):
            for s in job.JobStages.all():
                self.StopClusterJob(s.ClusterJobID, job.User)
        else:
            raise PermissionDenied
    
    
    def StopClusterJob(self, cluster_job_id, user=None):
        if not user:
            user = self.user
        
        r = ResourceManager(user)
        r.KillJob(cluster_job_id)
    
    
    def DeleteJob(self, job):
        if JobPermissions.CanAdministrate(self.user, job):
            self.StopJob(job)
            Jobs.DeleteJob(job)
        else:
            raise PermissionDenied
    
    
    def RepeatJob(self, job):
        pass
    
    
    def Share(self, job, user_name):
        user = User.objects.get(username=user_name)
        
        Jobs.Share(self.user, job, user, 
            Repeat=permissions["Repeat"], 
            Admin=permissions["Admin"]
        )
    
    
    def UpdateJobHistory(self):
        r = ResourceManager(self.user)
        jobs = r.GetDetailedQueue()
        
        f = open("/tmp/history.log", 'w')
        
        for job in jobs:
            try:
                JobData = json.dumps(job.DataSections, default=lambda o: o.__dict__, sort_keys=True)
                
                #update or create JobStage
                jobstage = JobStages.GetJobStage(job.JobID)
                
                if jobstage:
                    old_status = jobstage.Status.StatusID
                    jobstage = JobStages.UpdateJobStage(jobstage, job.Status, job.ExitCode, 
                        job.OutputLog, job.ErrorLog, job.WorkingDir, JobData)
                    
                    #if status has changed, handle change
                    if old_status != job.Status:
                        with transaction.atomic():
                            pass
                else:
                    with transaction.atomic():
                        user, created = User.objects.get_or_create(
                            username=job.User
                        )
                        
                        j = Jobs.AddJob(User=user, JobName=job.JobName, 
                            Description="External submission - job was not submitted via JMS", 
                            ToolVersion=None, JobTypeID=4)
                        
                        jobstage = JobStages.AddJobStage(user, j, StatusID=job.Status, 
                            ClusterJobID=job.JobID, ExitCode=job.ExitCode, 
                            ErrorLog=job.ErrorLog, OutputLog=job.OutputLog, 
                            PWD=job.WorkingDir, JobData=JobData)
                    
                    #if the job is already complete
                    if job.Status > 3:
                        with transaction.atomic():
                            pass
                
            except Exception, ex:
                print >> f, (str(ex)) 
        
        f.close()    
