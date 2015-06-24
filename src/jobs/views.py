from django.shortcuts import render
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.db import transaction

from JMS import JobManager
from JMS.CRUD import ToolPermissions

from serializers import *

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

import json, mimetypes, os

#Resource manager views

class Dashboard(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Get queue and node usage statistics for all nodes in the cluster
        """
        jms = JobManager(user=request.user)
        
        dashboard = jms.GetDashboard()
        return Response(json.dumps(dashboard, default=lambda o: o.__dict__, sort_keys=True))



class ServerSettings(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Get server settings
        """
        jms = JobManager(user=request.user)
        
        settings = jms.GetSettings()
        return Response(json.dumps(settings, default=lambda o: o.__dict__, sort_keys=True))
    
    def post(self, request):
        """
        Set server settings
        """
        s = json.loads(request.body)  
        
        jms = JobManager(user=request.user)
        settings = jms.UpdateSettings(s)
        
        return Response(json.dumps(settings, default=lambda o: o.__dict__))



class Nodes(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Get nodes
        """
        jms = JobManager(user=request.user)
        
        nodes = jms.GetNodes()
        return Response(json.dumps(nodes, default=lambda o: o.__dict__))
    
    def post(self, request):
        """
        Add node
        """
        n = json.loads(request.body) 
        
        jms = JobManager(user=request.user)
        jms.AddNode(n)
        
        nodes = jms.GetNodes()
        return Response(json.dumps(nodes, default=lambda o: o.__dict__))
        
    def put(self, request):
        """
        Update node
        """
        n = json.loads(request.body) 
        
        jms = JobManager(user=request.user)
        jms.UpdateNode(n)
        
        nodes = jms.GetNodes()
        return Response(json.dumps(nodes, default=lambda o: o.__dict__))
    
    

class NodeDetails(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def delete(self, request, node_name):
        """
        Delete node
        """
        jms = JobManager(user=request.user)
        jms.DeleteNode(node_name)
        
        nodes = jms.GetNodes()
        return Response(json.dumps(nodes, default=lambda o: o.__dict__))



class Queues(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def get(self, request):
        """
        Get queues
        """
        jms = JobManager(user=request.user)
        queues = jms.GetQueues()
        return Response(json.dumps(queues, default=lambda o: o.__dict__))



class QueueSettings(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def delete(self, request, queue):
        """
        Delete queue
        """
        jms = JobManager(user=request.user)
        jms.DeleteQueue(queue)
        
        queues = jms.GetQueues()
        return Response(json.dumps(queues, default=lambda o: o.__dict__))
    
    def post(self, request, queue):
        """
        Create queue
        """
        jms = JobManager(user=request.user)
        jms.AddQueue(queue)
        
        queues = jms.GetQueues()
        return Response(json.dumps(queues, default=lambda o: o.__dict__))
    
    def put(self, request, queue):
        """
        Update queue settings
        """
        q = json.loads(request.body)  
        
        jms = JobManager(user=request.user)
        jms.UpdateQueue(q)
        
        queues = jms.GetQueues()
        return Response(json.dumps(queues, default=lambda o: o.__dict__))



class Administrators(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Get administrators
        """
        jms = JobManager(user=request.user) 
        admins = jms.GetAdministrators()
        return Response(json.dumps(admins, default=lambda o: o.__dict__))
    
    
    def post(self, request):
        """
        Add administrator
        """
        a = json.loads(request.body)
        
        jms = JobManager(user=request.user)        
        jms.AddAdministrator(a)
        
        admins = jms.GetAdministrators()            
        return Response(json.dumps(admins, default=lambda o: o.__dict__))
    
    
    def put(self, request):
        """
        Update administrator
        """
        a = json.loads(request.body)
        
        jms = JobManager(user=request.user)        
        jms.UpdateAdministrator(a)
        
        admins = jms.GetAdministrators()            
        return Response(json.dumps(admins, default=lambda o: o.__dict__))



class AdministratorDetail(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def delete(self, request, admin):
        """
        Delete administrator
        """
        jms = JobManager(user=request.user)        
        jms.DeleteAdministrator(admin)
        
        admins = jms.GetAdministrators()             
        return Response(json.dumps(admins, default=lambda o: o.__dict__))



class ResourcesList(APIView):
    permission_classes = (IsAuthenticated,) 
    
    def get(self, request):
        """
        Get default resources for tool or custom job
        """
        
        jms = JobManager(user=request.user)        
        resources = jms.GetDefaultResources()
        
        return Response(json.dumps(resources, default=lambda o: o.__dict__))



#Tool views

class ToolList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Fetch a list of all available tools
        """
        jms = JobManager(user=request.user)
        tools = jms.GetTools()
        
        serializer = ToolListSerializer(tools, many=True)
        return Response(serializer.data)
    
    
    def post(self, request):
        """
        Create a new tool
        """
        tool = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        toolversion = jms.AddTool(tool)
        
        serializer = ToolVersionDetailSerializer(toolversion)
        return Response(serializer.data)
    


class ToolDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, tool_id):
        """
        Fetch tool
        """
        jms = JobManager(user=request.user)
        tool = jms.GetTool(tool_id)
        
        serializer = ToolListSerializer(tool)
        return Response(serializer.data)
    
    
    def delete(self, request, tool_id):
        """
        Delete a tool
        """
        jms = JobManager(user=request.user)
        jms.DeleteTool(tool_id)
        
        return Response(status=200)
    
    
    def put(self, request, tool_id):
        """
        Save the development version of the tool
        """
        version = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        jms.UpdateTool(tool_id, version)
        
        return Response(status=200)


  
class CategoryList(APIView):
    
    def get(self, request):
        """
        Get all tool categories
        """
        jms = JobManager(user=request.user)
        
        categories = jms.GetCategories()
        serializer = CategorySerializer(categories, many=True)
        
        return Response(serializer.data)
    
    
    def post(self, request):
        """
        Add tool category
        """
        category = request.body
        
        jms = JobManager(user=request.user)
        category = jms.AddCategory(category)
        
        serializer = CategorySerializer(category)
        return Response(serializer.data)


  
class CategoryDetail(APIView):
    
    def put(self, request, category_id):
        """
        Update tool category
        """
        category_name = request.body
        
        jms = JobManager(user=request.user)
        jms.UpdateCategory(category_id, category_name)
        
        categories = jms.GetCategories()
        serializer = CategorySerializer(categories, many=True)
        
        return Response(serializer.data)
    
    
    def delete(self, request, category_id):
        """
        Update tool category
        """
        jms = JobManager(user=request.user)
        jms.DeleteCategory(category_id)
        
        return Response(status=200)



class ToolVersionList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, tool_id):
        """
        Publish a new version of a tool
        """
        version_nums = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        toolversion = jms.PublishTool(tool_id, version_nums)
        
        serializer = ToolVersionListSerializer(toolversion)
        return Response(serializer.data)
    
    def put(self, request, tool_id):
        """
        Revert to an older version of a tool
        """
        version_num = request.body
        
        jms = JobManager(user=request.user)
        jms.RevertToolVersion(tool_id, version_num)
        
        return Response()
    
    def get(self, request, tool_id):
        """
        Get all versions of a tool
        """
        jms = JobManager(user=request.user)
        versions = jms.GetToolVersions(tool_id)
        
        serializer = ToolVersionListSerializer(versions, many=True)
        return Response(serializer.data)
    
    

class ToolVersionDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, tool_id, version_num):
        """
        Get a tool version based on the ToolID and ToolVersionNum fields
        """
        jms = JobManager(user=request.user)
        toolversion = jms.GetToolVersion(jms.GetTool(tool_id), version_num)
        
        serializer = ToolVersionDetailSerializer(toolversion)
        return Response(serializer.data)
    
    

class ToolShareDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request, tool_id, user_name):
        """
        Share a tool with a user
        """
        permissions = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        jms.ShareTool(tool_id, user_name, permissions)
        
        return Response()
    
    def delete(self, request, tool_id, user_name):
        """
        Unshare a tool with a user
        """
        jms = JobManager(user=request.user)
        jms.UnshareTool(tool_id, user_name)
        
        return Response()
    
    

class ToolShareList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, tool_id):
        """
        Get the access permissions for a tool
        """
        jms = JobManager(user=request.user)
        tool = jms.GetTool(tool_id)
        
        serializer = ToolPermissionSerializer(tool)
        return Response(serializer.data)


class ToolAvailability(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request, tool_id):
        """
        Make tool publically available
        """
        jms = JobManager(user=request.user)
        tool = jms.UpdateToolAvailability(tool_id, True)
        
        serializer = ToolPermissionSerializer(tool)
        return Response(serializer.data)
    
    def delete(self, request, tool_id):
        """
        Make tool private
        """
        jms = JobManager(user=request.user)
        tool = jms.UpdateToolAvailability(tool_id, False)
        
        serializer = ToolPermissionSerializer(tool)
        return Response(serializer.data)


class ParameterVersionList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, tool_id, version_num):
        """
        Get the parameters for a particular tool version
        """
        action = request.GET.get("action", "run")
        
        jms = JobManager(user=request.user)
        parameters = jms.GetParameters(tool_id, version_num, action)
        
        serializer = ParameterListSerializer(parameters, many=True)
        return Response(serializer.data)
    


class ParameterList(APIView):
    permission_classes = (IsAuthenticated,)
      
    def post(self, request, tool_id):
        """
        Add a new parameter
        """
        parameter_name = request.body
        
        jms = JobManager(user=request.user)
        parameter = jms.AddParameter(tool_id, parameter_name)
        
        serializer = ParameterDetailSerializer(parameter)
        return Response(serializer.data)
    
    def get(self, request, tool_id):
        """
        Get parameters
        """
        jms = JobManager(user=request.user)
        parameters = jms.GetRootParameters(tool_id)
        
        serializer = ParameterListSerializer(parameters, many=True)
        return Response(serializer.data)



class ParameterDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, parameter_id):
        """
        Get parameter details
        """
        jms = JobManager(user=request.user)
        
        #GetParameter will return a list as a parameter may have child parameters
        parameters = jms.GetParameter(parameter_id)
        serializer = ParameterDetailSerializer(parameters, many=True)
        return Response(serializer.data)
    
    def delete(self, request, parameter_id):
        """
        Delete parameter
        """
        jms = JobManager(user=request.user)
        jms.DeleteParameter(parameter_id)
        
        return Response(status=200)



class FileTypeList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Get file types
        """
        jms = JobManager(user=request.user)
        filetypes = jms.GetFileTypes()
        
        serializer = FileTypeSerializer(filetypes, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Add file types
        """
        file_type_name = request.body
        
        jms = JobManager(user=request.user)
        filetype = jms.AddFileType(file_type_name)
        
        serializer = FileTypeSerializer(filetype)
        return Response(serializer.data)



class ToolFileList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, tool_id):
        """
        Get development scripts and files for tool
        """
        jms = JobManager(user=request.user)
        dir_listing = jms.GetToolFiles(tool_id)
        return Response(dir_listing, status=200)
    
    def post(self, request, tool_id):
        """
        Upload files for tool
        """
        jms = JobManager(user=request.user)
        dir_listing = jms.UploadToolFiles(tool_id, request.FILES)      
                
        return Response(dir_listing, status=200)
    
    def put(self, request, tool_id):
        """
        Save a tool file 
        """
        file = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        jms.SaveToolFile(tool_id, file["FileName"], file["Content"])
        
        return Response(status=200)



class ToolFileDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, tool_id, file_name):
        """
        Create a new file
        """
        jms = JobManager(user=request.user)
        jms.CreateToolFile(tool_id, file_name)
        
        return Response(status=200)
    
    def delete(self, request, tool_id, file_name):
        """
        Delete a file
        """
        jms = JobManager(user=request.user)
        jms.DeleteToolFile(tool_id, file_name)
        
        return Response(status=200)
    
    def get(self, request, tool_id, file_name):
        """
        Get file content
        """
        jms = JobManager(user=request.user)
        content = jms.ReadToolFile(tool_id, file_name)
        
        return Response(content, status=200)



class WorkflowList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Get all workflows accessible to user
        """
        jms = JobManager(user=request.user)
        workflows = jms.GetWorkflows()
        
        serializer = WorkflowListSerializer(workflows, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Add a new workflow
        """
        workflow = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        version = jms.AddWorkflow(workflow)
        
        serializer = WorkflowVersionListSerializer(version)
        return Response(serializer.data)
    


class WorkflowDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, workflow_id):
        """
        Fetch workflow
        """
        jms = JobManager(user=request.user)
        workflow = jms.GetWorkflow(tool_id)
        
        serializer = WorkflowListSerializer(workflow)
        return Response(serializer.data)
    
    
    def delete(self, request, workflow_id):
        """
        Delete a workflow
        """
        jms = JobManager(user=request.user)
        jms.DeleteWorkflow(workflow_id)
        
        return Response(status=200)
    
    
    def put(self, request, workflow_id):
        """
        Update a workflow
        """
        workflow = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        jms.UpdateWorkflow(workflow_id, workflow)
        
        return Response(status=200)
    
    

class WorkflowVersionList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, workflow_id):
        """
        Publish a new version of a workflow
        """
        version_nums = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        version = jms.PublishWorkflow(workflow_id, version_nums)
        
        serializer = WorkflowVersionListSerializer(version)
        return Response(serializer.data)
    
    def put(self, request, workflow_id):
        """
        Revert to an older version of a workflow
        """
        version_num = request.body
        
        jms = JobManager(user=request.user)
        jms.RevertWorkflowVersion(workflow_id, version_num)
        
        return Response()
    
    def get(self, request, workflow_id):
        """
        Get all versions of a workflow
        """
        jms = JobManager(user=request.user)
        versions = jms.GetWorkflowVersions(workflow_id)
        
        serializer = WorkflowVersionListSerializer(versions, many=True)
        return Response(serializer.data)
    
    

class WorkflowVersionDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, workflow_id, version_num):
        """
        Get a workflow version based on the WorkflowID and WorkflowVersionNum fields
        """
        jms = JobManager(user=request.user)
        version = jms.GetWorkflowVersion(jms.GetWorkflow(workflow_id), version_num)
        
        serializer = WorkflowVersionDetailSerializer(version)
        return Response(serializer.data)
    
    

class WorkflowShareDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request, workflow_id, user_name):
        """
        Share a workflow with a user
        """
        permissions = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        jms.ShareWorkflow(workflow_id, user_name, permissions)
        
        return Response()
    
    def delete(self, request, workflow_id, user_name):
        """
        Unshare a workflow with a user
        """
        jms = JobManager(user=request.user)
        jms.UnshareWorkflow(workflow_id, user_name)
        
        return Response()
    
    

class WorkflowShareList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, workflow_id):
        """
        Get the access permissions for a workflow
        """
        jms = JobManager(user=request.user)
        workflow = jms.GetWorkflow(workflow_id)
        
        serializer = WorkflowPermissionSerializer(workflow)
        return Response(serializer.data)



class WorkflowAvailability(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request, workflow_id):
        """
        Make workflow publically available
        """
        jms = JobManager(user=request.user)
        workflow = jms.UpdateWorkflowAvailability(workflow_id, True)
        
        serializer = WorkflowPermissionSerializer(workflow)
        return Response(serializer.data)
    
    def delete(self, request, workflow_id):
        """
        Make workflow private
        """
        jms = JobManager(user=request.user)
        workflow = jms.UpdateWorkflowAvailability(workflow_id, False)
        
        serializer = WorkflowPermissionSerializer(workflow)
        return Response(serializer.data)    



class StageList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, workflow_id, version_num):
        """
        Get workflow stages
        """
        jms = JobManager(user=request.user)
        stages = jms.GetStages(workflow_id, version_num)
        
        serializer = StageListSerializer(stages, many=True)
        return Response(serializer.data)
    
    def post(self, request, workflow_id, version_num):
        """
        Add workflow stage
        """
        if version_num == "dev":
            stage = json.loads(request.body)
            
            jms = JobManager(user=request.user)
            stages = jms.AddStage(workflow_id, stage)
            
            serializer = StageListSerializer(stages)
            return Response(serializer.data)
            
        return Response("Stages can only be added to the development version", 
            status=403)
    


class StageDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, stage_id):
        """
        Get stage details
        """
        jms = JobManager(user=request.user)
        stage = jms.GetStage(stage_id)
        
        serializer = StageListSerializer(stage)
        return Response(serializer.data)
    
    def put(self, request, stage_id):
        """
        Update stage
        """
        stage = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        stage = jms.UpdateStage(stage_id, stage)
        
        return Response()
    
    def delete(self, request, stage_id):
        """
        Delete stage
        """
        jms = JobManager(user=request.user)
        stage = jms.DeleteStage(stage_id)
        
        return Response()



class StageLevels(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, workflow_id, version_num):
        """
        Get workflow stages
        """
        jms = JobManager(user=request.user)
        stages = jms.GetStages(workflow_id, version_num)
        
        serializer = StageLevelSerializer(stages, many=True)
        return Response(serializer.data)
    


class StagePosition(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request, stage_id):
        """
        Update stage
        """
        stage_pos = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        stage = jms.MoveStage(stage_id, stage_pos)
        
        return Response()



class DependencyList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, stage_id):
        """
        Add stage dependency
        """
        dependency = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        dep = jms.AddStageDependency(stage_id, dependency)
        
        serializer = StageDependencyList(dep)
        return Response(serializer.data)



class DependencyDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def put(self, request, dependency_id):
        """
        Update stage dependency
        """
        dependency = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        jms.UpdateStageDependency(dependency_id, dependency)
        
        return Response()
    
    def delete(self, request, dependency_id):
        """
        Delete stage dependency
        """
        jms = JobManager(user=request.user)
        stages = jms.DeleteStageDependency(dependency_id)
        
        serializer = StageLevelSerializer(stages, many=True)
        return Response(serializer.data)



class CustomJob(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        """
        Submit a custom script to be run on the cluster
        """
        job_name = request.POST["JobName"]
        description = request.POST["Description"]
        commands = request.POST["Commands"]
        settings = json.loads(request.POST["Settings"])
        
        files = request.FILES.getlist("files")
        
        jms = JobManager(user=request.user)
        
        with transaction.atomic():
            job = jms.CreateJob(job_name, description, None, 1)
            job = jms.RunCustomJob(job, commands, settings, files)
        
        return Response(job.JobID)



class ToolJob(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, version_id):
        """
        Run a tool on the cluster
        """
        job_name = request.POST["JobName"]
        description = request.POST["Description"]
        parameters = json.loads(request.POST["Parameters"])
        #settings = json.loads(request.POST["Settings"])
        
        files = []
        for k, v in request.FILES.iteritems():
            for f in request.FILES.getlist(k):
                files.append(f)
        
        jms = JobManager(user=request.user)
        version = jms.GetToolVersionByID(version_id)
        
        
        with transaction.atomic():
            job = jms.CreateJob(job_name, description, version, 2)
            job = jms.RunToolJob(job, parameters, files)
        
        return Response(job.JobID)



class WorkflowJob(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        """
        Run a workflow on the cluster
        """
        job_name = request.POST["JobName"]
        description = request.POST["Description"]
        commands = request.POST["Commands"]
        stages = json.loads(request.POST["Stages"])
        #settings = json.loads(request.POST["Settings"])
        
        files = request.FILES.getlist("files")
        
        jms = JobManager(user=request.user)
        job = jms.RunCustomJob(job_name, description, commands, settings, files)
        
        return Response(job.JobID)
    


class JobList(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        """
        Fetch all accessible jobs
        """
        jms = JobManager(user=request.user)
        jobs = jms.GetJobs()
        
        serializer = JobListSerializer(jobs, many=True)
        return Response(serializer.data)


class JobFilter(APIView):
    
    def post(self, request, detail):
        """
        Filter accessible jobs by parameters
        """
        fl = json.loads(request.body)
        
        jms = JobManager(user=request.user)
        jobs = jms.FilterJobsByParameter(fl)
        
        if detail == "list":
            serializer = JobListSerializer(jobs, many=True)
        elif detail == "detail":
            serializer = JobDetailSerializer(jobs, many=True)
        
        return Response(serializer.data)
    


class JobDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, job_id):
        """
        Fetch job details
        """
        jms = JobManager(user=request.user)
        job = jms.GetJob(job_id)
        
        serializer = JobDetailSerializer(job)
        return Response(serializer.data)
    
    def delete(self, request, job_id):
        """
        Delete job
        """
        jms = JobManager(user=request.user)
        job = jms.DeleteJob(job_id)
        
        return Response()



class PackageManagement(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        """
        Install packages
        """
        jms = JobManager(user=request.user)
        
        return Response("Ansible support is not enabled", status=400)



class FileDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, job_stage_id):
        """
        Get job file contents
        """
        log = request.GET.get("log", None)
        
        if not log:
            #We are fetching a job file
            try: 
                jms = JobManager(user=request.user)
                
                #create a temp copy
                filepath = request.GET.get("path", '')
                tmp_path = jms.get_tmp_job_file(job_stage_id, filepath)
                
                #Get file type
                mimetypes.init()
                name, file_ext = os.path.splitext(os.path.basename(filepath))        
                type = mimetypes.types_map.get(file_ext.lower(), "text/plain")
                if type == "application/javascript":
                    type = "text/plain"
                
                if request.method == "HEAD":
                    response = HttpResponse("", content_type=type)
                    return response
                else:  
                    wrapper = FileWrapper(open(tmp_path, "rb"))
                    response = HttpResponse(wrapper, content_type=type)
                    response['Content-Length'] = os.path.getsize(tmp_path)
                    return response
            except Exception, err:
                return Response(str(err), status=400) 
        
        else:
            #We are fetching a log file
            jms = JobManager(user=request.user)
            
            if log.lower() == "error":
                data = jms.get_job_error(job_stage_id)
            elif log.lower() == "output":
                data = jms.get_job_output(job_stage_id)
                
            return Response(data)



class DirectoryDetail(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, job_stage_id):
        """
        List job directory contents
        """
        path = request.GET.get("path", "/")
        jms = JobManager(user=request.user)
        data = jms.get_job_directory_listing(job_stage_id, path)
        
        return Response(data)
    