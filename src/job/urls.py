from django.conf.urls import patterns, url, include
from job import views

internal_urls = patterns('job.views',
    url(r'prologue/(?P<username>[^/]+)/(?P<cluster_job_id>[^/]+)/?', views.Prologue.as_view()), 
    url(r'epilogue/(?P<username>[^/]+)/(?P<cluster_job_id>[^/]+)/(?P<exit_code>[^/]+)/?', views.Epilogue.as_view()), 
)

public_urls = patterns('job.views',
    url(r'files/(?P<upload_type>[^/]+)/(?P<type_id>[^/]+)/(?P<file_name>[^/]+)?', views.FileDetail.as_view()), 
    url(r'files/(?P<upload_type>[^/]+)/(?P<type_id>[^/]+)/?', views.File.as_view()), 
    
    url(r'filemanager/(?P<job_id>[^/]+)/$', views.FileManager.as_view()),
    
    url(r'dashboard/?', views.Dashboard.as_view()), 
    
    url(r'jobs/cluster/(?P<cluster_id>[^/]+)/?', views.ClusterJob.as_view()),
    
    url(r'jobs/batch/(?P<batch_job_id>[^/]+)/files/(?P<file_type>[^/]+)/?', views.BatchFile.as_view()),
    url(r'jobs/batch/(?P<batch_job_id>[^/]+)/(?P<action>[^/]+)/?', views.BatchJobUpdate.as_view()),
    url(r'jobs/batch/(?P<batch_job_id>[^/]+)/?', views.BatchJobDetail.as_view()),
    url(r'jobs/batch/?', views.BatchJob.as_view()),
    
    url(r'jobs/custom/?', views.CustomJob.as_view()),
    
    url(r'jobs/(?P<job_id>[^/]+)/permissions/users/(?P<user_id>[^/]+)/?', views.EditJobUserAccess.as_view()),
    url(r'jobs/(?P<job_id>[^/]+)/permissions/users/?', views.JobUserAccess.as_view()),
    url(r'jobs/(?P<job_id>[^/]+)/permissions/groups/(?P<group_id>[^/]+)/??', views.EditJobGroupAccess.as_view()),
    url(r'jobs/(?P<job_id>[^/]+)/permissions/groups/?', views.JobGroupAccess.as_view()),
    url(r'jobs/(?P<job_id>[^/]+)/permissions/?', views.JobAccess.as_view()),
    
    url(r'jobs/(?P<job_id>[^/]+)/downloads/(?P<download_type>[^/]+)/(?P<type_id>[^/]+)/?', views.FileDownload.as_view()),  
    url(r'jobs/(?P<job_id>[^/]+)/?', views.JobDetail.as_view()),
    url(r'jobs/?', views.Job.as_view()), 
    
    url(r'inputprofiles/(?P<profile_id>[^/]+)/?', views.InputProfileDetail.as_view()),  
    url(r'inputprofiles/?', views.InputProfile.as_view()),     
    
    url(r'workflows/import/?', views.ImportWorkflow.as_view()),
    url(r'workflows/(?P<workflow_id>[^/]+)/export/?', views.ExportWorkflow.as_view()),
    
    url(r'workflows/(?P<workflow_id>[^/]+)/permissions/users/(?P<user_id>[^/]+)/?', views.EditWorkflowUserAccess.as_view()),
    url(r'workflows/(?P<workflow_id>[^/]+)/permissions/users/?', views.WorkflowUserAccess.as_view()),
    url(r'workflows/(?P<workflow_id>[^/]+)/permissions/groups/(?P<group_id>[^/]+)/??', views.EditWorkflowGroupAccess.as_view()),
    url(r'workflows/(?P<workflow_id>[^/]+)/permissions/groups/?', views.WorkflowGroupAccess.as_view()),
    url(r'workflows/(?P<workflow_id>[^/]+)/permissions/?', views.WorkflowAccess.as_view()),
    url(r'workflows/(?P<workflow_id>[^/]+)/?', views.Workflow.as_view()), 
    url(r'workflows/?', views.Workflows.as_view()),
    
    url(r'settings/administrators/?', views.AdminSettings.as_view()),
    url(r'settings/queues/(?P<queue>[^/]+)/?', views.QueueSettings.as_view()),
    url(r'settings/nodes/(?P<node_name>[^/]+)/?', views.NodeDetails.as_view()),
    url(r'settings/nodes/?', views.Nodes.as_view()),
    url(r'settings/?', views.ServerSettings.as_view()),
       
       
    #url(r'results/get/(?P<result_id>[^/]+)/?', views.Result.as_view()),
    #url(r'results/(?P<job_stage_id>[^/]+)/?', views.GetResults.as_view()),
    #url(r'(?P<job_id>[^/]+)/comments/(?P<comment_id>[^/]+)/?', views.CommentDetail.as_view()),
    #url(r'(?P<job_id>[^/]+)/comments?', views.Comments.as_view()),
    #url(r'(?P<job_stage_id>[^/]+)/continue/?', views.JobStage.as_view()),    
)

urlpatterns = patterns('',
	url(r'^', include(internal_urls, namespace="internal_urls")),
	url(r'^', include(public_urls, namespace="public_urls")),       
)
