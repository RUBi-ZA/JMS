var Job = function(job_id, job_name, description, workflow, tool, type, time, stages) {
	this.JobID = ko.observable(job_id);
	this.JobName = ko.observable(job_name);
	this.Description = ko.observable(description);
	this.WorkflowVersion = ko.observable(workflow);
	this.ToolVersion = ko.observable(tool);
	this.JobTypeID = ko.observable(type);
	this.SubmittedAt = ko.observable(time)
	this.JobStages = ko.observableArray(stages);
	
	this.state = ko.observable();
}


var JobStage = function(id, stage, name, status, requires_edit, exit, cluster_id, data, error, out, dir) {
    this.JobStageID = ko.observable(id);
    this.Stage = ko.observable(stage);
    this.ToolName = ko.observable(name);
    this.Status = ko.observable(status);
    this.RequiresEditInd = ko.observable(requires_edit);
    this.ExitCode = ko.observable(exit);
    this.ClusterJobID = ko.observable(cluster_id);
    this.JobData = ko.observable(data);
    this.JobStageParameters = ko.observableArray();
    
    this.ErrorLog = ko.observable(error);
    this.OutputLog = ko.observable(out);
    this.WorkingDirectory = ko.observable(dir);
}


var JobStageDataSection = function(id, section) {
    this.DataSectionID = ko.observable(id);
    this.DataSectionName = ko.observable(section);
}
    

var JobStageDataField = function(id, key, value, label, type) {  
    this.DataFieldID = ko.observable(id);
    this.Key = ko.observable(key);
    this.Value = ko.observable(value);
    this.Label = ko.observable(label);
    this.ValueType = ko.observable(type);
}


var Stage = function(id, checkpoint){
    this.StageID = ko.observable(id);
    this.Checkpoint = ko.observable(checkpoint);
}


var JobStageParameter = function(id, name, value) {
    this.JobStageParameterID = ko.observable(id);
    this.ParameterName = ko.observable(name);
    this.Value = ko.observable(value);
}


function JobsViewModel() {
    self = this;
    
    self.loading = ko.observable(true)
    
    self.Jobs = ko.observableArray();
    self.Job = ko.observable();
    
    self.LoadHistory = function() {
		$.ajax({
			url: "/api/jms/jobs",
			success: function(data) {
				var jobs = []
				$.each(data, function(i, job) {
				    var j = new Job(job.JobID, job.JobName, job.JobDescription, 
    	                null, null, job.JobTypeID, job.SubmittedAt, []);
    	            
    	            if(job.JobTypeID == 2) {
    	                //tool
    	                j.ToolVersion(job.ToolVersion.Tool.ToolName + " (" + 
    				        job.ToolVersion.ToolVersionNum + ")")
    	            } else if(job.JobTypeID == 3) {
    	                //workflow
    	                j.WorkflowVersion(job.WorkflowVersion.Workflow.WorkflowName + " (" + 
    				       job.WorkflowVersion.WorkflowVersionNum + ")")
    	            }
					
					//variables to determine job state
					var min = 4;
					var max = 0;
					var running = false;
					$.each(job.JobStages, function(i, stage){
					    var s = new JobStage(null, null, null, stage.Status, 
					        null, null, stage.ClusterJobID, null, null, null, null);
					    
					    if(min > stage.Status) {
					        min = stage.Status;
					    }
					    if(max < stage.Status ) {
					        max = stage.Status
					    }
					    if(stage.Status ==  3) {
					        running = true;
					    }
					    
					    j.JobStages.push(s);
					});
					
					var state = ""
					if(running)
					    j.state = "Running";
					else {
					    if(min < 3) {
					        j.state = "Queued"
					    }
					    if(max == 7) {
					        j.state = "Errors encountered"
					    }
					}
					
					jobs.push(j);
				});	
				
				self.Jobs(jobs);
				
				self.loading(false);
			},
			error: function() {
				self.loading(false);
			}
		});
	}
	
	self.GetJob = function(job_id) {
	    $.ajax({
	        url: "/api/jms/jobs/" + job_id,
	        success: function(j) {
	            var job = new Job(j.JobID, j.JobName, j.JobDescription, 
	                null, null, j.JobTypeID, j.SubmittedAt, []);
	            
	            if(j.JobTypeID == 2) {
	                //tool
	                job.ToolVersion(j.ToolVersion.Tool.ToolName + " (" + 
				        j.ToolVersion.ToolVersionNum + ")")
	            } else if(j.JobTypeID == 3) {
	                //workflow
	                job.WorkflowVersion(j.WorkflowVersion.Workflow.WorkflowName + " (" + 
				        j.WorkflowVersion.WorkflowVersionNum + ")")
	            }
	            
	            $.each(j.JobStages, function(i, js) {
	                var stage = js.Stage
	                if(stage != null) {
	                    stage = new Stage(js.Stage.StageID, js.Stage.Checkpoint)
	                }
	                
	                var jobstage = new JobStage(js.JobStageID, stage, js.ToolName, 
	                    js.Status, js.RequiresEditInd, js.ExitCode,
	                    js.ClusterJobID, js.JobData, js.ErrorLog, js.OutputLog, 
	                    js.WorkingDirectory)
	                
	                $.each(js.JobStageParameters, function(j, jsp){
	                    var jsparam = new JobStageParameter(jsp.JobStageParameterID,
	                        jsp.ParameterName, jsp.Value);  
	                    
	                    jobstage.JobStageParameters.push(jsparam);
	                })
	                
	                job.JobStages.push(jobstage);
	            });
	            
	            self.Job(job);
	        }
	    })
	}
}

var question = new QuestionModal("question-dialog");
var jobs;
var queue_interval;
var job_interval;

$(function() {
    jobs = new JobsViewModel();
    ko.applyBindings(jobs, document.getElementById("page-wrapper"));
    
	jobs.LoadHistory();
	queue_interval = setInterval(jobs.RefreshHistory, 10000);
	
	$('#job_list').slimScroll({
		height: '500px'
	});	

	// initialize the application
	var app = Sammy(function() {

		this.get('#:job', function() {
			
			clearInterval(job_interval);
			jobs.GetJob(this.params.job);	
		});
		
		this.get('/jobs/', function() {
		    // set iframe url
			jobs.loading(false);
		});
	});

	// start the application
	app.run('/jobs/#');
});