from django.conf.urls import patterns, url, include
from jobs import views

public_urls = patterns('jobs.views',
    url(r'jobs/tool/versions/(?P<version_id>[^/]+)/?', views.ToolJob.as_view()),
    url(r'files/types', views.FileTypeList.as_view()),
    
    url(r'dashboard/?', views.Dashboard.as_view()), 
    
    #ANSIBLE
    url(r'packages/?', views.PackageManagement.as_view()),
    
    
    #JOB FILES
    
    url(r'jobstages/(?P<job_stage_id>[^/]+)/files/?', views.FileDetail.as_view()), 
    url(r'jobstages/(?P<job_stage_id>[^/]+)/directories/?', views.DirectoryDetail.as_view()), 
    
    
    
    #url(r'jobs/cluster/(?P<cluster_id>[^/]+)/?', views.ClusterJob.as_view()),
    
    #url(r'jobs/batch/(?P<batch_job_id>[^/]+)/files/(?P<file_type>[^/]+)/?', views.BatchFile.as_view()),
    #url(r'jobs/batch/(?P<batch_job_id>[^/]+)/(?P<action>[^/]+)/?', views.BatchJobUpdate.as_view()),
    #url(r'jobs/batch/(?P<batch_job_id>[^/]+)/?', views.BatchJobDetail.as_view()),
    #url(r'jobs/batch/?', views.BatchJob.as_view()),
    
    url(r'jobs/custom/?', views.CustomJob.as_view()),
    url(r'jobs/workflow/versions/(?P<version_id>[^/]+)/?', views.WorkflowJob.as_view()),
    
    #url(r'jobs/(?P<job_id>[^/]+)/permissions/users/(?P<user_id>[^/]+)/?', views.EditJobUserAccess.as_view()),
    #url(r'jobs/(?P<job_id>[^/]+)/permissions/users/?', views.JobUserAccess.as_view()),
    #url(r'jobs/(?P<job_id>[^/]+)/permissions/groups/(?P<group_id>[^/]+)/??', views.EditJobGroupAccess.as_view()),
    #url(r'jobs/(?P<job_id>[^/]+)/permissions/groups/?', views.JobGroupAccess.as_view()),
    #url(r'jobs/(?P<job_id>[^/]+)/permissions/?', views.JobAccess.as_view()),
    
    #url(r'jobs/(?P<job_id>[^/]+)/downloads/(?P<download_type>[^/]+)/(?P<type_id>[^/]+)/?', views.FileDownload.as_view()),  
    #url(r'jobs/(?P<job_id>[^/]+)/?', views.JobDetail.as_view()),
    url(r'jobs/(?P<job_id>[^/]+)/?', views.JobDetail.as_view()), 
    url(r'jobs/?', views.JobList.as_view()), 
       
    #url(r'jobstages/(?P<job_stage_id>[^/]+)/?', views.JobStage.as_view()),
    
    #url(r'inputprofiles/(?P<profile_id>[^/]+)/?', views.InputProfileDetail.as_view()),  
    #url(r'inputprofiles/?', views.InputProfile.as_view()),  
       
    #url(r'results/get/(?P<result_id>[^/]+)/?', views.Result.as_view()),
    #url(r'results/(?P<job_stage_id>[^/]+)/?', views.GetResults.as_view()),  
    
    #TOOLS
    
    #url(r'tools/import/?', views.ImportTool.as_view()),
    #url(r'tools/(?P<tool_id>[^/]+)/export/?', views.ExportTool.as_view()),
    
    url(r'tools/(?P<tool_id>[^/]+)/public/?', views.ToolAvailability.as_view()), 
    
    url(r'tools/(?P<tool_id>[^/]+)/share/(?P<user_name>[^/]+)?', views.ToolShareDetail.as_view()),  
    url(r'tools/(?P<tool_id>[^/]+)/share/?', views.ToolShareList.as_view()),  
    
    url(r'tools/(?P<tool_id>[^/]+)/files/(?P<file_name>[^/]+)?', views.ToolFileDetail.as_view()),
    url(r'tools/(?P<tool_id>[^/]+)/files/?', views.ToolFileList.as_view()),
    
    url(r'tools/categories/(?P<category_id>[^/]+)/?', views.CategoryDetail.as_view()), 
    url(r'tools/categories/?', views.CategoryList.as_view()),
    
    url(r'parameters/(?P<parameter_id>[^/]+)/?', views.ParameterDetail.as_view()),
    url(r'tools/(?P<tool_id>[^/]+)/parameters/?', views.ParameterList.as_view()),
    url(r'tools/(?P<tool_id>[^/]+)/versions/(?P<version_num>[^/]+)/parameters/?', views.ParameterVersionList.as_view()),
    
    url(r'tools/(?P<tool_id>[^/]+)/versions/(?P<version_num>[^/]+)/?', views.ToolVersionDetail.as_view()),
    url(r'tools/(?P<tool_id>[^/]+)/versions/?', views.ToolVersionList.as_view()),
    
    url(r'tools/(?P<tool_id>[^/]+)/?', views.ToolDetail.as_view()), 
    url(r'tools/?', views.ToolList.as_view()),
    
    #WORKFLOWS
    
    #url(r'workflows/import/?', views.ImportWorkflow.as_view()),
    #url(r'workflows/(?P<workflow_id>[^/]+)/export/?', views.ExportWorkflow.as_view()), 
    
    url(r'workflows/(?P<workflow_id>[^/]+)/public/?', views.WorkflowAvailability.as_view()), 
    
    url(r'workflows/(?P<workflow_id>[^/]+)/share/(?P<user_name>[^/]+)?', views.WorkflowShareDetail.as_view()),  
    url(r'workflows/(?P<workflow_id>[^/]+)/share/?', views.WorkflowShareList.as_view()),
    
    
    url(r'stages/dependencies/(?P<dependency_id>[^/]+)?', views.DependencyDetail.as_view()),
    url(r'stages/(?P<stage_id>[^/]+)/dependencies/?', views.DependencyList.as_view()),
    
    url(r'workflows/(?P<workflow_id>[^/]+)/versions/(?P<version_num>[^/]+)/stages/levels/?', views.StageLevels.as_view()),
    url(r'workflows/(?P<workflow_id>[^/]+)/versions/(?P<version_num>[^/]+)/stages/?', views.StageList.as_view()),
    
    url(r'stages/(?P<stage_id>[^/]+)/position/?', views.StagePosition.as_view()),
    url(r'stages/(?P<stage_id>[^/]+)/?', views.StageDetail.as_view()),
    
    url(r'workflows/(?P<workflow_id>[^/]+)/versions/(?P<version_num>[^/]+)/?', views.WorkflowVersionDetail.as_view()),
    url(r'workflows/(?P<workflow_id>[^/]+)/versions/?', views.WorkflowVersionList.as_view()),
    
    url(r'workflows/(?P<workflow_id>[^/]+)/?', views.WorkflowDetail.as_view()), 
    url(r'workflows/?', views.WorkflowList.as_view()),
    
    #SETTINGS
    
    url(r'settings/resources/?', views.ResourcesList.as_view()),
    url(r'settings/administrators/(?P<admin>[^/]+)/?', views.AdministratorDetail.as_view()),
    url(r'settings/administrators/?', views.Administrators.as_view()),
    url(r'settings/queues/(?P<queue>[^/]+)/?', views.QueueSettings.as_view()),
    url(r'settings/queues/?', views.Queues.as_view()),
    url(r'settings/nodes/(?P<node_name>[^/]+)/?', views.NodeDetails.as_view()),
    url(r'settings/nodes/?', views.Nodes.as_view()),
    url(r'settings/?', views.ServerSettings.as_view()),   
)
 
urlpatterns = patterns('',
	url(r'^', include(public_urls, namespace="public_urls")),       
)