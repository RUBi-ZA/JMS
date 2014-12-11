import json, os, requests, shutil 
from zipfile import ZipFile

from django.db import transaction
from django.http import HttpResponse, QueryDict
from django.core.servers.basehttp import FileWrapper 
from django.core import serializers as django_serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from job.Utilities import *
from job.JMS import JMS
import objects
from job.models import *
from job.serializers import * 

###
# Helper methods
###

def CreateParameters(parameter, map_param_ids, stageID, jms):
    #create parameter
    val = parameter["Value"]
                    
    if not parameter["ParameterType"]:
        parameter["ParameterType"] = 1
    elif parameter["ParameterType"] == 6:
        val = map_param_ids[int(val)]
    
    parent_id = parameter.get("ParentParameter", None)
    if parent_id != None:
        parent_id = map_param_ids[parent_id]
                    
    paramID = jms.CreateParameter(ParameterName=parameter["ParameterName"], Context=parameter["Context"], InputBy=parameter["InputBy"], 
        Value=parameter["Value"], Multiple=parameter["Multiple"], Optional=parameter["Optional"], ParameterTypeID=parameter["ParameterType"], StageID=stageID, 
        ParameterIndex=parameter["ParameterIndex"], ParentParameterID=parent_id)
                    
    map_param_ids[parameter["ParameterID"]] = paramID
                    
    #create parameter options
    for po in parameter["ParameterOptions"]:
        jms.CreateParameterOption(ParameterOptionText=po["ParameterOptionText"], ParameterOptionValue=po["ParameterOptionValue"], ParameterID=paramID)    
    

def RecursiveCreateParameters(parameter, map_param_ids, stageID, jms):
    #create parameter
    val = parameter["Value"]
                    
    if not parameter["Type"]:
        parameter["Type"] = 1
    elif parameter["Type"] == 6:
        val = map_param_ids[int(val)]
    
    parent_id = parameter.get("ParentParameterID", None)
    if parent_id != None:
        parent_id = map_param_ids[parent_id]
                    
    paramID = jms.CreateParameter(ParameterName=parameter["ParameterName"], Context=parameter["Context"], InputBy=parameter["InputBy"], 
        Value=parameter["Value"], Multiple=parameter["Multiple"], Optional=parameter["Optional"], ParameterTypeID=parameter["Type"], StageID=stageID, 
        ParameterIndex=parameter["ParameterIndex"], ParentParameterID=parent_id)
                    
    map_param_ids[parameter["ParameterID"]] = paramID
                    
    #create parameter options
    for po in parameter["ParameterOptions"]:
        jms.CreateParameterOption(ParameterOptionText=po["ParameterOptionText"], ParameterOptionValue=po["ParameterOptionValue"], ParameterID=paramID)    
    
    #create sub-parameters
    for sub_param in parameter["parameters"]:
        RecursiveCreateParameters(sub_param, map_param_ids, stageID, jms)
        

def RecursiveFindParameter(current_params, old_param):
    for current_param in current_params:
        if current_param["ParameterID"] == old_param.ParameterID:
            return True
        
        if RecursiveFindParameter(current_param["parameters"], old_param):
            return True
    
    return False


def RecursiveUpdateParameters(parameter, map_param_ids, stageID, jms):
    #update parameter
    val = parameter["Value"]
                        
    if not parameter["Type"]:
        parameter["Type"] = 1
    elif parameter["Type"] == 6:
        val = map_param_ids[int(val)]
        
    jms.UpdateParameter(ParameterID=parameter["ParameterID"], ParameterName=parameter["ParameterName"], Context=parameter["Context"], 
        InputBy=parameter["InputBy"], Value=val, Multiple=parameter["Multiple"], Optional=parameter["Optional"], ParameterTypeID=parameter["Type"], 
        StageID=stageID, Delimiter=parameter.get("Delimiter", None), ParameterIndex=parameter["ParameterIndex"])
                                    
    map_param_ids[parameter["ParameterID"]] = parameter["ParameterID"]
                                    
    ops = jms.GetParameterOptions(parameter["ParameterID"])
                                    
    #delete removed parameter options
    for old_op in ops:
        Include = False
        for current_op in parameter["ParameterOptions"]:
            if current_op["ParameterOptionID"] == old_op.ParameterOptionID:
                Include = True
                break
                            
        if not Include:
            jms.DeleteParameterOption(ParameterOptionID=old_op.ParameterOptionID)
                                
    #update parameter options
    for current_op in parameter["ParameterOptions"]:
        
        if current_op["ParameterOptionID"] > 0:
            #update option
            jms.UpdateParameterOption(ParameterOptionID=current_op["ParameterOptionID"], ParameterOptionText=current_op["ParameterOptionText"], 
            ParameterOptionValue=current_op["ParameterOptionValue"], ParameterID=parameter["ParameterID"])
        else:
            #create option
            jms.CreateParameterOption(ParameterOptionText=current_op["ParameterOptionText"], ParameterOptionValue=current_op["ParameterOptionValue"], 
                ParameterID=parameter["ParameterID"])
    
    #create or update sub-parameters
    for current_param in parameter["parameters"]:
                                        
        param_exists = True
        try:
            jms.GetParameter(ParameterID=current_param["ParameterID"])
        except Exception, e:
            param_exists = False
        
        if not current_param["Type"]:
            current_param["Type"] = 1
        elif current_param["Type"] == 6:
            val = map_param_ids[int(val)]
        
        if param_exists:
            #recursively update parameters
            RecursiveUpdateParameters(current_param, map_param_ids, stageID, jms)
        else:                                        
            #create parameter    
            RecursiveCreateParameters(current_param, map_param_ids, stageID, jms)
                                    
                                
def CreateStage(stage, workflowID, map_ids, map_param_ids, jms):
    stageID = jms.CreateStage(StageName=stage["StageName"], StageTypeID=stage["StageType"], WorkflowID=workflowID, 
        Command=stage["Command"], StageIndex=stage["StageIndex"], Queue=stage["Queue"], MaxCores=stage["MaxCores"],
        Nodes=stage["Nodes"], Memory=stage["Memory"], Walltime=stage["Walltime"])
    
    map_ids[stage["StageID"]] = stageID
    
    #create stage dependencies
    for d in stage["StageDependencies"]:
        try:
            jms.CreateStageDependency(StageID=stageID, DependantOnID=map_ids[d["StageID"]], ConditionID=d["ConditionID"], ExitCodeValue=d["Value"])
        except Exception, e:
            jms.CreateStageDependency(StageID=stageID, DependantOnID=map_ids[d["DependantOn"]], ConditionID=d["Condition"], ExitCodeValue=d["ExitCodeValue"])
    
    #recursively create parameters
    for parameter in stage["Parameters"]:
        try:
            p_type = parameter["Type"]
            RecursiveCreateParameters(parameter, map_param_ids, stageID, jms)
        except Exception, e:
            CreateParameters(parameter, map_param_ids, stageID, jms)
                                
    #create outputs
    for current_output in stage["ExpectedOutputs"]:
        jms.CreateExpectedOutput(ExpectedOutputFileName=current_output["ExpectedOutputFileName"], StageID=stageID)        
                                    
                                                    


###
# API Views
###

class Dashboard(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Get queue and node usage statistics for all nodes in the cluster
        """
        jms = JMS()
        dashboard = jms.GetDashboard(request.user.username, request.user.userprofile.Code)
        return Response(json.dumps(dashboard, default=lambda o: o.__dict__, sort_keys=True))

class Workflows(APIView):
    permission_classes = (IsAuthenticated,)
    
    """
    Fetch all workflows
    """
    def get(self, request):
        jms = JMS(user=request.user)
        data = jms.GetWorkflows()
        serializer = WorkflowSerializer(data, many=True)
        return Response(serializer.data)
    
    
    """
    Save workflow (create a new workflow or update an existing one)
    """    
    def post(self, request):
        #parse POST json
        workflow = lambda:None
        workflow.__dict__ = json.loads(request.body)
        
        jms = JMS(user=request.user)
        
        workflowID = workflow.WorkflowID
        
        with transaction.atomic():
            
            #if the workflow ID is <= 0, this is a new workflow that we must create
            if workflow.WorkflowID <= 0:
                
                #Create workflow    
                workflowID = jms.CreateWorkflow(WorkflowName=workflow.WorkflowName, Description=workflow.Description)
                
                #create workflow stages
                map_ids = {}
                map_param_ids = {}
                for stage in workflow.Stages:
                    CreateStage(stage, workflowID, map_ids, map_param_ids, jms)
            
            #if the workflow ID is > 0, this workflow already exists in the database and we must update it
            elif workflow.WorkflowID > 0:
                old_workflow = jms.GetWorkflow(workflow.WorkflowID)
                
                #Update workflow
                jms.UpdateWorkflow(WorkflowID=workflow.WorkflowID, WorkflowName=workflow.WorkflowName, Description=workflow.Description)
                
                stages = jms.GetStages(workflow.WorkflowID)
                    
                #delete removed stages
                for old_stage in stages:
                    include = False
                    for current_stage in workflow.Stages:
                        if current_stage["StageID"] == old_stage.StageID:
                            include = True
                            break
                    
                    if not include:
                        jms.DeleteStage(StageID=old_stage.StageID)
                
                map_ids = {}
                map_param_ids = {}
                #update existing stages and create new stages
                for current_stage in workflow.Stages:
                    
                    stage_exists = False
                    for s in old_workflow.Stages.all():
                        if s.StageID == current_stage["StageID"]:
                            stage_exists = True
                            break
                                            
                    if stage_exists:
                        #update stage                
                        command = current_stage["Command"]
                        
                        jms.UpdateStage(StageID=current_stage["StageID"], StageName=current_stage["StageName"], StageTypeID=current_stage["StageType"], 
                            WorkflowID=workflow.WorkflowID, Command=command, StageIndex=current_stage["StageIndex"], Queue=current_stage["Queue"], 
                            MaxCores=current_stage["MaxCores"], Nodes=current_stage["Nodes"], Memory=current_stage["Memory"], Walltime=current_stage["Walltime"])
                        
                        map_ids[current_stage["StageID"]] = current_stage["StageID"]
                                    
                        deps = jms.GetStageDependencies(current_stage["StageID"])
                        
                        #delete dependencies
                        for old_dep in deps:
                            jms.DeleteStageDependency(StageDependencyID=old_dep.StageDependencyID)
                                
                        #add dependencies
                        for current_dep in current_stage["StageDependencies"]:
                            jms.CreateStageDependency(StageID=current_stage["StageID"], DependantOnID=map_ids[current_dep["StageID"]], ConditionID=current_dep["ConditionID"], ExitCodeValue=current_dep["Value"])                            
                        
                        params = jms.GetParameters(current_stage["StageID"])
                        
                        #delete removed parameters
                        for old_param in params:
                            #if old_param doesn't exist in the new set of parameters, delete it from the DB
                            Include = RecursiveFindParameter(current_stage["Parameters"], old_param)                                
                            if not Include:
                                jms.DeleteParameter(ParameterID=old_param.ParameterID)
                        
                        #loop through parameters, updating existing parameters and creating new ones
                        for current_param in current_stage["Parameters"]:
                            
                            param_exists = True
                            try:
                                jms.GetParameter(ParameterID=current_param["ParameterID"])
                            except Exception, e:
                                param_exists = False
                            
                            val = current_param["Value"]
                            
                            if not current_param["Type"]:
                                current_param["Type"] = 1
                            elif current_param["Type"] == 6:
                                val = map_param_ids[int(val)]
                            
                            if param_exists:
                                #recursively update parameters
                                RecursiveUpdateParameters(current_param, map_param_ids, current_stage["StageID"], jms)
                            else:                                        
                                #create parameter    
                                RecursiveCreateParameters(current_param, map_param_ids, current_stage["StageID"], jms)                        
                        
                        outputs = jms.GetExpectedOutputs(current_stage["StageID"])
                        
                        #delete removed outputs
                        for old_out in outputs:
                            Include = False
                            for current_out in current_stage["ExpectedOutputs"]:
                                if current_out["ExpectedOutputID"] == old_out.ExpectedOutputID:
                                    Include = True
                                    break
                            
                            if not Include:
                                jms.DeleteExpectedOutput(ExpectedOutputID=old_out.ExpectedOutputID)
                        
                        #update outputs
                        for current_output in current_stage["ExpectedOutputs"]:                                
                                
                            if current_output["ExpectedOutputID"] > 0:
                                #update output
                                jms.UpdateExpectedOutput(ExpectedOutputID=current_output["ExpectedOutputID"], ExpectedOutputFileName=current_output["ExpectedOutputFileName"])
                            else:
                                #create output
                                output_id = jms.CreateExpectedOutput(ExpectedOutputFileName=current_output["ExpectedOutputFileName"], StageID=current_stage["StageID"])
                                                                    
                    else:
                        #stage doesn't exist so create it
                        CreateStage(current_stage, workflowID, map_ids, map_param_ids, jms)
            
            #create the directory where the workflow scripts will be stored
            jms.createJobDir(os.path.join(jms.users_dir, request.user.username + "/workflows/" + str(workflowID)))
                            
        #we will only get here if the update has executed successfully            
        data = jms.GetWorkflow(workflowID)
        serializer = WorkflowDetailSerializer(data)
        return Response(serializer.data)
        
            
class Workflow(APIView):
    authentication_classes = (BasicAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, workflow_id):
        """
        Fetch workflow by WorkflowID
        """
        jms = JMS(user=request.user)
        data = jms.GetWorkflow(workflow_id)        
        serializer = WorkflowDetailSerializer(data)
        return Response(serializer.data)
        
    
    def delete(self, request, workflow_id):
        """
        Delete workflow by WorkflowID
        """    
        jms = JMS(user=request.user)
        jms.DeleteWorkflow(workflow_id)
        return Response()
        
        

class InputProfile(APIView):
    authentication_classes = (BasicAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        """
        Create a new input profile
        """
        input_profile = lambda:None
        input_profile.__dict__ = json.loads(request.body)
        
        with transaction.atomic():
            jms = JMS(user=request.user)
            profile = jms.CreateInputProfile(input_profile.InputProfileName, input_profile.Description, input_profile.WorkflowID)
            
            for ip in input_profile.InputProfileParameters:                
                profile_param = jms.CreateInputProfileParameter(InputProfileID=profile.InputProfileID, ParameterID=ip["ParameterID"], Value=ip["Value"])
        
        return Response(profile.InputProfileID)



class InputProfileDetail(APIView):
    authentication_classes = (BasicAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, profile_id):
        """
        Fetch an input profile
        """
        jms = JMS(user=request.user)
        profile = jms.GetInputProfile(profile_id)
        serializer = InputProfileDetailSerializer(profile)
        return Response(serializer.data)
        
    
    def put(self, request, profile_id):
        """
        Update an input profile
        """
        input_profile = lambda:None
        input_profile.__dict__ = json.loads(request.body)
        
        with transaction.atomic():
            jms = JMS(user=request.user)
            profile = jms.UpdateInputProfile(InputProfileID=profile_id, InputProfileName=input_profile.InputProfileName, Description=input_profile.Description)
            
            #delete current profile parameters
            for ip in profile.InputProfileParameters.all():
                ip.delete()
            
            #replace deleted params with new ones
            for ip in input_profile.InputProfileParameters:                
                profile_param = jms.CreateInputProfileParameter(InputProfileID=profile.InputProfileID, ParameterID=ip["ParameterID"], Value=ip["Value"])

        return Response()
    
    
    def delete(self, request, profile_id):
        """
        Delete an input profile
        """
        jms = JMS(user=request.user)
        jms.DeleteInputProfile(profile_id)
        return Response()
        
        
        
class ExportWorkflow(APIView):
    
    def get(self, request, workflow_id):
        """
        Export workflow to zip file
        """
        jms = JMS(user=request.user)
        workflow = jms.GetWorkflow(workflow_id)
        serializer = WorkflowDetailSerializer(workflow)
        
        json_path = "/tmp/workflow_%s_%s.json" % (str(workflow_id), request.user.username)
        with open(json_path, 'w') as f:
            f.write(JSONRenderer().render(serializer.data))
        
        zip_path = '/tmp/workflow_%s_%s.zip' % (str(workflow_id), request.user.username)
        workflow_dir = '%s/%s/workflows/%s/' % (jms.users_dir, request.user.username, str(workflow_id))
        
        with ZipFile(zip_path, 'w') as myzip:
            myzip.write(json_path, "workflow.json")
            for root, dirs, files in os.walk(workflow_dir):
                for f in files:
                    myzip.write(os.path.join(root, f), "scripts/%s" % f)                    
        
        wrapper = FileWrapper(file(zip_path))        
        
        response = HttpResponse(wrapper, content_type='application/force-download')
        response['Content-Length'] = os.path.getsize(zip_path)
        response['Content-Disposition'] = 'attachment; filename=workflow_%s_%s.zip' % (str(workflow_id), request.user.username)
        
        return response
                  

class ImportWorkflow(APIView):
    
    def post(self, request):
        """
        Import workflow in the form of a zip file
        """
        zipped = request.FILES.get("file")
        unzipped = ZipFile(zipped)
        
        unzipped.extract("workflow.json", "/tmp/")
        
        data = None
        with open("/tmp/workflow.json", 'r') as f:
            data = f.read()
        
        data = data.strip()
        
        workflow = lambda:None
        workflow.__dict__ = json.loads(data)
        
        with transaction.atomic():           
            
            jms = JMS(user=request.user)
            
            #Create workflow    
            workflowID = jms.CreateWorkflow(WorkflowName=workflow.WorkflowName, Description=workflow.Description)
            script_dir = os.path.join(jms.users_dir, request.user.username + "/workflows/" + str(workflowID))
            
            #create workflow stages
            map_ids = {}
            map_param_ids = {}
            for stage in workflow.Stages:
                CreateStage(stage, workflowID, map_ids, map_param_ids, jms)
            
            for f in unzipped.namelist():
                if f.startswith("scripts/"):
                    unzipped.extract(f, script_dir)
                    shutil.copyfile(os.path.join(script_dir, f), os.path.join(script_dir, os.path.basename(f)))
                    shutil.rmtree(os.path.join(script_dir, "scripts"))
        
        unzipped.close()
        
        return Response()       
        
    
        

class BatchJob(APIView):
    
    def post(self, request):
        """
        Create new batch job
        """        
        job = lambda:None
        job.__dict__ = json.loads(request.body)
        
        batch_job_name = job.JobName
        description = job.Description
        
        jms = JMS(user=request.user)
        batch_job = jms.CreateBatchJob(batch_job_name, description)
        
        return Response(batch_job.BatchJobID)
        
        
    def get(self, request):
        """
        Get all batch jobs
        """
        jms = JMS(user=request.user)
        jobs = jms.GetBatchJobs()
        serializer = BatchJobSerializer(jobs, many=True)
        return Response(serializer.data)
               


class BatchJobDetail(APIView):
    
    def get(self, request, batch_job_id):
        """
        Fetch batch job details
        """
        jms = JMS(user=request.user)
        job = jms.GetBatchJob(batch_job_id)
        serializer = BatchJobSerializer(job)
        return Response(serializer.data)
        
        
    def delete(self, request, batch_job_id):
        """
        Delete batch job - deletes all individual jobs as well
        """
        jms = JMS(user=request.user)
        jms.DeleteBatchJob(batch_job_id)
        return Response()
    
    
    def put(self, request, batch_job_id):
        """
        Start batch job
        """
        jms = JMS(user=request.user)
        jms.StartBatchJob(batch_job_id)
        return Response()
 
 
 
class BatchFile(APIView):
    permission_classes = (IsAuthenticated,)    
    
    def post(self, request, batch_job_id, file_type):
        """
        Uploads batch files
        """        
        jms = JMS(user=request.user)
        
        if file_type == 'batch':
            rootpath = os.path.join(jms.users_dir, jms.user.username + '/jobs/batch_jobs/' + batch_job_id + '/')
        elif file_type == 'input':
            rootpath = os.path.join(jms.users_dir, jms.user.username + '/jobs/batch_jobs/' + batch_job_id + '/files')
        else:
            return Response(status=404)
             
        jms.createJobDir(rootpath)
        
        for k, v in request.FILES.iteritems():
            for f in request.FILES.getlist(k):
                with open(os.path.join(rootpath, f.name), 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                os.chmod(os.path.join(rootpath, f.name), 0777)       
                
        return Response(os.listdir(rootpath), status=200)      
        
        
        
class BatchJobUpdate(APIView):
    
    def put(self, request, batch_job_id, action):
        """
        Update batch job
        """
        jms = JMS(user=request.user)
        if action.lower() == "stop":
            jms.StopBatchJob(batch_job_id)
            return Response()
        else:
            return Response(status=404)   
    


class Job(APIView):    
    authentication_classes = (BasicAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        """
        Submit a new job
        """
        job = lambda:None
        job.__dict__ = json.loads(request.body)
        
        name = job.JobName
        wokflow_id = job.WorkflowID
        user = request.user
        description = job.Description
        
        stages = []
        for s in job.Stages:
            stage = objects.JobStageInput(s["StageID"], s["Parameters"], False)
            stages.append(stage)        
        
        jms = JMS(user=request.user)        
        job_id = jms.CreateJob(name, wokflow_id, description, stages)
        
        return Response(job_id, status=200)
    
    def get(self, request):
        """
        Fetch all jobs for user
        """
        jms = JMS(user=request.user)
        jobs = jms.GetJobs()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data);


class JobDetail(APIView):
    authentication_classes = (BasicAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def put(self, request, job_id):
        """
        Start a created job
        """
        jms = JMS(user=request.user)
        jms.StartJob(job_id)
        
        return Response()
    
    def get(self, request, job_id):
        """
        Fetch a job based on its ID
        """
        jms = JMS(user=request.user)
        response = jms.GetJob(job_id)
        serializer = JobDetailSerializer(response)
        return Response(serializer.data)
    
    
    def delete(self, request, job_id):
        """
        Delete a job from history
        """
        jms = JMS(user=request.user)
        jms.DeleteJob(job_id)
        return Response(status=200)
        
    def post(self, request, job_id):
        """
        Repeat a job
        """        
        new_job_name = request.POST["JobName"];
        start_stage = int(request.POST.get('StartStage', 0))        
        
        jms = JMS(user=request.user)
        new_job_id = jms.RepeatJobFromStage(int(job_id), new_job_name, int(start_stage))
        
        return Response(new_job_id, status=status.HTTP_200_OK)
    
    

class ClusterJob(APIView):
    permission_classes = (IsAuthenticated,)
    
    """
    Get details of a job running on the cluster
    """
    def get(self, request, cluster_id):
        jms = JMS()
        job = jms.GetClusterJob(job_id=cluster_id, username=request.user.username, password=request.user.userprofile.Code)
        
        serializer = ClusterJobSerializer(job)
        return Response(serializer.data)
    
    """
    Stop a job running on the cluster
    """
    def delete(self, request, cluster_id):    
        password = request.user.userprofile.Code
        
        jms = JMS(user=request.user)
        code = jms.StopClusterJob(cluster_id)
        
        return Response(status=200)



class JobStage(APIView):
    permission_classes = (IsAuthenticated,)    
    
    def put(self, request, job_stage_id):
        jms = JMS()
        jms.ContinueJob(job_stage_id)
        
        return Response(status=status.HTTP_200_OK)



class WorkflowAccess(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def get(self, request, workflow_id):
        '''
        Get users that have access to workflow
        '''
        jms = JMS(user=request.user)
        if jms.GetUserWorkflowAccess(request.user.id, workflow_id) <= 2:
            workflow = jms.GetWorkflow(workflow_id)
            serializer = WorkflowAccessRightSerializer(workflow)
            return Response(serializer.data)
        else:
            return Response(status=403)
            


class WorkflowUserAccess(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def post(self, request, workflow_id):
        '''
        Add workflow user access rights
        '''
        username = request.POST.get("Username", False)
        access_right_id = request.POST.get("AccessRightID", False)
        
        if username and access_right_id:
            user = User.objects.get(username=username)
            
            jms = JMS(user=request.user)
            access_right = jms.SaveUserWorkflowAccessRight(workflow_id, user.id, access_right_id)
            serializer = UserWorkflowAccessRightSerializer(access_right)
            return Response(serializer.data)
        else:
            return Response(status=400)



class EditWorkflowUserAccess(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def delete(self, request, workflow_id, user_id):
        '''
        Remove access to workflow for user
        '''
        jms = JMS(user=request.user)
        jms.DeleteUserWorkflowAccessRight(workflow_id, user_id)
        return Response()
            


class WorkflowGroupAccess(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def post(self, request, workflow_id):
        '''
        Add workflow group access rights
        '''
        group_id = request.POST.get("GroupID", False)
        access_right_id = request.POST.get("AccessRightID", False)
        
        if group_id and access_right_id:            
            jms = JMS(user=request.user)
            access_right = jms.SaveGroupWorkflowAccessRight(workflow_id, group_id, access_right_id)
            serializer = GroupWorkflowAccessRightSerializer(access_right)
            return Response(serializer.data)
        else:
            return Response(status=400)



class EditWorkflowGroupAccess(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def delete(self, request, workflow_id, group_id):
        '''
        Remove access to workflow for group
        '''
        jms = JMS(user=request.user)
        jms.DeleteGroupWorkflowAccessRight(workflow_id, group_id)
        return Response()



class JobAccess(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def get(self, request, job_id):
        '''
        Get users that have access to workflow
        '''
        jms = JMS(user=request.user)
        if jms.GetUserJobAccess(request.user.id, job_id) <= 2:
            job = jms.GetJob(job_id)
            serializer = JobAccessRightSerializer(job)
            return Response(serializer.data)
        else:
            return Response(status=403)
            


class JobUserAccess(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def post(self, request, job_id):
        '''
        Update user's access to job
        '''
        username = request.POST.get("Username", False)
        access_right_id = request.POST.get("AccessRightID", False)
        
        if username and access_right_id:
            user = User.objects.get(username=username)
            
            jms = JMS(user=request.user)
            access_right = jms.SaveUserJobAccessRight(job_id, user.id, access_right_id)
            serializer = UserJobAccessRightSerializer(access_right)
            return Response(serializer.data)
        else:
            return Response(status=400)



class EditJobUserAccess(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def delete(self, request, job_id, user_id):
        '''
        Remove user's access to job
        '''
        jms = JMS(user=request.user)
        jms.DeleteUserJobAccessRight(job_id, user_id)
        return Response()
            


class JobGroupAccess(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def post(self, request, job_id):
        '''
        Update groups's access to job
        '''
        group_id = request.POST.get("GroupID", False)
        access_right_id = request.POST.get("AccessRightID", False)
        
        if group_id and access_right_id:            
            jms = JMS(user=request.user)
            access_right = jms.SaveGroupJobAccessRight(job_id, group_id, access_right_id)
            serializer = GroupJobAccessRightSerializer(access_right)
            return Response(serializer.data)
        else:
            return Response(status=400)



class EditJobGroupAccess(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def delete(self, request, job_id, group_id):
        '''
        Remove groups's access to job
        '''
        jms = JMS(user=request.user)
        jms.DeleteGroupJobAccessRight(job_id, group_id)
        return Response()

'''
class GetResults(APIView):
    permission_classes = (IsAuthenticated,)    
    
    def get(self, request, job_stage_id):
        """
        Get the results for a particular stage of a job
        """
        jms = JMS()
        results = jms.GetResults(job_stage_id, request.user.id)
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data)
        
        
class Result(APIView):
    permission_classes = (IsAuthenticated,)    

    def get(self, request, result_id):
        """
        Fetch a result
        """    
        jms = JMS()
        filename = jms.GetResultFilePath(result_id, request.user.id)                              
        wrapper = FileWrapper(file(filename))
        response = HttpResponse(wrapper, content_type='application/force-download')
        response['Content-Length'] = os.path.getsize(filename)
        response['Content-Disposition'] = 'attachment'
        return response
    
    def put(self, request, result_id):
        """
        Update result file
        """
        put = QueryDict(request.body)
        f = put.get('result', False)
        if f:
            jms = JMS()
            jms.UpdateResult(result_id, f)
        
            return Response(status=status.HTTP_200_OK)
        else:
            return Response("The result file was not received by the server", status=400)
'''

class FileManager(APIView):
    permission_classes = (IsAuthenticated,)    

    def get(self, request, job_id):
        jms = JMS(user=request.user)
        path = "_"
        
        if job_id != "cluster":
            job = jms.GetJob(job_id)    
            path = os.path.join(jms.users_dir, job.User.username + "/jobs/" + str(job_id))
        
        url = 'http://jms.biosci.ru.ac.za/assets/lib/elfinder-2.0-rc1/php/connector.php?path=%s&user=%s' % (path, request.user.username)
        
        for k, v in request.GET.iteritems():
            url += "&%s=%s" % (k, v)
            
        r = requests.get(url)
        
        return Response(r.json())
    
    def post(self, request, job_id):
        jms = JMS(user=request.user)
        path = "_"
        
        if job_id != "cluster":
            job = jms.GetJob(job_id)    
            path = os.path.join(jms.users_dir, job.User.username + "/jobs/" + str(job_id))
        
        url = 'http://jms.biosci.ru.ac.za/assets/lib/elfinder-2.0-rc1/php/connector.php?path=%s' % path
        
        for k, v in request.GET.iteritems():
            url += "&%s=%s" % (k, v)
            
        r = requests.get(url)
        
        return Response(r.json())
        


class FileDownload(APIView):
    permission_classes = (IsAuthenticated,)    

    def get(self, request, job_id, download_type, type_id):
        """
        Fetch a job file
        """    
        jms = JMS(user=request.user)
        
        filename = ''                
        if download_type.lower() == "parameters":
            param = JobStageParameter.objects.get(Parameter__ParameterID=type_id, JobStage__Job__JobID=job_id)
            filename = param.Value
        elif download_type.lower() == "outputs":
            output = ExpectedOutput.objects.get(pk=type_id)
            filename = output.ExpectedOutputFileName
        
        path = "%s/%s" % (job_id, filename)
        
        job = jms.GetJob(job_id)    
        filepath = os.path.join(jms.users_dir, job.User.username + "/jobs/" + path)                          
        wrapper = FileWrapper(file(filepath))
        
        
        response = HttpResponse(wrapper, content_type='application/force-download')
        response['Content-Length'] = os.path.getsize(filepath)
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


class File(APIView):
    permission_classes = (IsAuthenticated,)    
    
    def post(self, request, upload_type, type_id):
        """
        Uploads files to the server and returns the list of files for a job or workflow
        """        
        jms = JMS()
        
        if upload_type == 'jobs':
            rootpath = os.path.join(jms.users_dir, request.user.username + '/jobs/' + type_id + '/')
        elif upload_type == 'workflows':
            rootpath = os.path.join(jms.users_dir, request.user.username + '/workflows/' + type_id + '/')
        else:
            return Response(status=404)
             
        jms.createJobDir(rootpath)
        
        for k, v in request.FILES.iteritems():
            for f in request.FILES.getlist(k):
                with open(os.path.join(rootpath, f.name), 'wb+') as destination:
                    for chunk in f.chunks():
                        destination.write(chunk)
                os.chmod(os.path.join(rootpath, f.name), 0777)       
                
        return Response(os.listdir(rootpath), status=200)


    #class File(APIView):

    def get(self, request, upload_type, type_id):
        """
        Returns the list of files for a job or workflow
        """        
        jms = JMS()
        
        if upload_type == 'jobs':
            rootpath = os.path.join(jms.users_dir, request.user.username + '/jobs/' + type_id + '/')
        elif upload_type == 'workflows':
            rootpath = os.path.join(jms.users_dir, request.user.username + '/workflows/' + type_id + '/')
            
        return Response(os.listdir(rootpath), status=200)



class FileDetail(APIView):
    permission_classes = (IsAuthenticated,)    
    
    def get(self, request, upload_type, type_id, file_name):
        """
        Returns the contents of a job or workflow file
        """        
        jms = JMS()
        
        if upload_type == 'jobs':
            path = os.path.join(jms.users_dir, request.user.username + '/jobs/' + type_id + '/' + file_name)
        elif upload_type == 'workflows':
            path = os.path.join(jms.users_dir, request.user.username + '/workflows/' + type_id + '/' + file_name)
        else:
            return Response(status=404)
    
        content = ""
        with open(path, 'r') as f:
            content = f.read()
        
        return Response(content)
    
    def delete(self, request, upload_type, type_id, file_name):
        """
        Delete a job or workflow file
        """    
        jms = JMS()
        
        if upload_type == 'jobs':
            path = os.path.join(jms.users_dir, request.user.username + '/jobs/' + type_id + '/' + file_name)
        elif upload_type == 'workflows':
            path = os.path.join(jms.users_dir, request.user.username + '/workflows/' + type_id + '/' + file_name)
        else:
            return Response(status=404)
            
        os.remove(path)
        
        return Response(status=200)
    
    def put(self, request, upload_type, type_id, file_name):
        """
        Update a job or workflow file
        """
        jms = JMS()
        
        if upload_type == 'jobs':
            rootpath = os.path.join(jms.users_dir, request.user.username + '/jobs/' + type_id)
        elif upload_type == 'workflows':
            rootpath = os.path.join(jms.users_dir, request.user.username + '/workflows/' + type_id)
        else:
            return Response(status=404)
         
        jms.createJobDir(rootpath)
        path = os.path.join(rootpath, file_name);
        
        with open(path, 'w') as f:
            print >> f, request.body
        
        return Response(os.listdir(rootpath), status=200)
        


class Comments(APIView):
    permission_classes = (IsAuthenticated,)    

    def get(self, request, job_id):
        """
        Get comments on a job
        """
        jms = JMS()
        comments,response_code = jms.GetComments(job_id, request.user)
        serializer = CommentSerializer(comments, many=True)
            
        return Response(serializer.data, status=response_code)
    
    def post(self, request, job_id):
        """
        Post a comment on a job
        """
        p = lambda:None
        p.__dict__ = json.loads(request.body)
        
        jms = JMS()
        response_code = jms.AddComment(job_id, p.Comment, request.user)
        
        return Response(status=response_code)



class CommentDetail(APIView):
    permission_classes = (IsAuthenticated,)    

    def delete(self, request, job_id, comment_id):
        """
        Delete a comment - must be your comment unless you have admin privileges for the job
        """
        jms = JMS()
        response_code = jms.DeleteComment(comment_id, request.user)
        
        return Response(status=response_code)



class ServerSettings(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def get(self, request):
        """
        Get server settings
        """
        jms = JMS(user=request.user)
        settings = jms.GetServerSettings()
        return Response(json.dumps(settings, default=lambda o: o.__dict__))
    
    def post(self, request):
        """
        Set server settings
        """
        s = lambda:None
        s.__dict__ = json.loads(request.body)  
        
        jms = JMS(user=request.user)
        jms.UpdateServerSettings(s.KeepCompleted, s.JobStatRate, s.SchedularIteration, s.NodeCheckRate, s.TCPTimeout, s.QueryOtherJobs, s.MOMJobSync, s.MoabArrayCompatible, s.Scheduling)
        
        settings = jms.GetServerSettings()
        return Response(json.dumps(settings, default=lambda o: o.__dict__))



class AdminSettings(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def put(self, request):
        """
        Update administrators
        """
        admins = lambda:None
        admins = json.loads(request.body)
        
        administrators = []
        for a in admins:
            administrators.append(objects.ServerAdministrator(Username=a["Username"], Host=a["Host"], Manager=a.get("Manager", False), Operator=a.get("Operator", False)))
        
        jms = JMS(user=request.user)        
        jms.SaveAdministrator(administrators)
        
        settings = jms.GetServerSettings()            
        return Response(json.dumps(settings, default=lambda o: o.__dict__))



class QueueSettings(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def delete(self, request, queue):
        """
        Delete queue
        """
        jms = JMS(user=request.user)
        jms.DeleteQueue(queue)
        
        settings = jms.GetServerSettings()
        return Response(json.dumps(settings, default=lambda o: o.__dict__))
    
    def post(self, request, queue):
        """
        Create queue
        """
        jms = JMS(user=request.user)
        jms.CreateQueue(queue)
        
        settings = jms.GetServerSettings()
        return Response(json.dumps(settings, default=lambda o: o.__dict__))
    
    def put(self, request, queue):
        """
        Update queue settings
        """
        q = lambda:None
        q.__dict__ = json.loads(request.body)  
        
        jms = JMS(user=request.user)
        jms.UpdateQueue(queue, q.Type, q.Enabled, q.Started, q.MaxQueable, q.MaxRun, q.MaxUserQueable, q.MaxUserRun, q.MaxNodes, q.DefaultNodes, q.MaxCPUs, q.DefaultCPUs, q.MaxMemory, q.DefaultMemory, q.MaxWalltime, q.DefaultWalltime, q.DefaultQueue)
        
        settings = jms.GetServerSettings()
        return Response(json.dumps(settings, default=lambda o: o.__dict__))



class Nodes(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def get(self, request):
        """
        Get nodes
        """
        jms = JMS(user=request.user)
        nodes = jms.GetNodes()
        return Response(json.dumps(nodes, default=lambda o: o.__dict__))
    
    def post(self, request):
        """
        Add node
        """
        n = lambda:None
        n.__dict__ = json.loads(request.body) 
        
        jms = JMS(user=request.user)
        jms.AddNode(NodeName=n.NodeName, NumProcessors=n.NumProcessors, Properties=n.Properties, IPAddress=n.IPAddress)
        
        nodes = jms.GetNodes()
        return Response(json.dumps(nodes, default=lambda o: o.__dict__))
    
    

class NodeDetails(APIView):
    permission_classes = (IsAuthenticated,) 
        
    def put(self, request, node_name):
        """
        Update node
        """
        n = lambda:None
        n.__dict__ = json.loads(request.body) 
        
        jms = JMS(user=request.user)
        jms.UpdateNode(NodeName=node_name, NumProcessors=n.NumProcessors, Properties=n.Properties)
        
        nodes = jms.GetNodes()
        return Response(json.dumps(nodes, default=lambda o: o.__dict__))
    
    
    def delete(self, request, node_name):
        """
        Delete node
        """
        jms = JMS(user=request.user)
        jms.DeleteNode(node_name)
        
        nodes = jms.GetNodes()
        return Response(json.dumps(nodes, default=lambda o: o.__dict__))
        
        



#URLs excluded from docs

class Prologue(APIView):

    def get(self, request, username, cluster_job_id):
        try:
            jms = JMS()
            jms.AddUpdateClusterJob(cluster_job_id, username)
                    
        
            jms.UpdateJobState(ClusterJobID=cluster_job_id, StatusID=objects.Status.Running)            
        except Exception, e:
            File.print_to_file("/obiwanNFS/open/pro.log", str(e) + "\n\n", 'w')
            
        return Response(status=200)



class Epilogue(APIView):
    
    def get(self, request, username, cluster_job_id, exit_code):
        try:
            jms = JMS()
            jms.AddUpdateClusterJob(cluster_job_id, username)
            
            jms.FinishStage(cluster_job_id, int(exit_code))
        except Exception, e:
            File.print_to_file("/obiwanNFS/open/epi.log", str(e) + "\n\n", 'w')
        
        return Response(status=200)




    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def createJobDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        os.chmod(directory, 0777)
