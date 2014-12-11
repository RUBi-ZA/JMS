var ClusterJob = function() {
	this.ClusterJobID = ko.observable();
	this.JobName = ko.observable();
	this.JobOwner = ko.observable();
	
	this.MemoryRequested = ko.observable();
	this.NodesAvailable = ko.observable();
	this.NodesRequested = ko.observable();
	this.WalltimeRequested = ko.observable();
	
	this.CPUTimeUsed = ko.observable();
	this.MemoryUsed = ko.observable();
	this.VirtualMemoryUsed = ko.observable();
	this.WalltimeUsed = ko.observable();
	
	this.State = ko.observable();
	this.Queue = ko.observable();
	this.Server = ko.observable();
	this.ExecutionHost = ko.observable();
	this.SubmitArgs = ko.observable();
	this.SubmitHost = ko.observable();
	this.OutputPath = ko.observable();
	this.ErrorPath = ko.observable();
	this.ExecutionHost = ko.observable();
	this.Priority = ko.observable();
	
	this.CreatedTime = ko.observable();
	this.TimeEnteredQueue = ko.observable();
	this.EligibleTime = ko.observable();
	this.LastModified = ko.observable();
	this.StartTime = ko.observable();
	this.CompletionTime = ko.observable();
	this.TotalRuntime = ko.observable();
	
	this.VariableList = ko.observable();
	
	this.Comment = ko.observable();
	this.ExitStatus = ko.observable();
	
	this.OutputStream = ko.observable();
	this.ErrorStream = ko.observable();
}

var Job = function(job_id, job_name, description, workflow, stages) {
	this.JobID = ko.observable(job_id);
	this.JobName = ko.observable(job_name);
	this.Description = ko.observable(description);
	this.Workflow = ko.observable(workflow);
	this.JobStages = ko.observableArray(stages);
	
	this.UserAccessRights = ko.observableArray();
	this.GroupAccessRights = ko.observableArray();
}

var User = function(id, name) {
    this.UserID = ko.observable(id);
    this.Username = ko.observable(name);
    
    this.clone = function() {
        var copy = new User(this.UserID(), this.Username());
        return copy;
    }
}

var Group = function(id, name) {
    this.GroupID = ko.observable(id);
    this.GroupName = ko.observable(name);
    
    this.clone = function() {
        var copy = new Group(this.GroupID(), this.GroupName());
        return copy;
    }
}

var AccessRight = function(id, name) {
    this.AccessRightID = ko.observable(id);
    this.AccessRightName = ko.observable(name);
    
    this.clone = function() {
        var copy = new AccessRight(this.AccessRightID(), this.AccessRightName());
        return copy;
    }
}

var UserJobAccessRight = function(user, access_right) {
    self = this;
    
    self.User = ko.observable(user);
    self.AccessRight = ko.observable(access_right);
    
    this.clone = function() {
        var copy = new UserJobAccessRight(this.User().clone(), this.AccessRight().clone());
        return copy;
    }
}

var GroupJobAccessRight = function(group, access_right) {
    self = this;
    
    self.Group = ko.observable(group);
    self.AccessRight = ko.observable(access_right);
    
    this.clone = function() {
        var copy = new GroupJobAccessRight(self.Group().clone(), self.AccessRight.clone());
        return copy;
    }
}

var JobStage = function(job_stage_id, stage, cluster_job_id, state, params, outputs, visible) {
	this.JobStageID = ko.observable(job_stage_id);
	this.Stage = ko.observable(stage);
	this.ClusterJobID = ko.observable(cluster_job_id);
	this.State = ko.observable(state);
	this.Parameters = ko.observableArray(params);
	this.ExpectedOutputs = ko.observableArray(outputs)
	
	this.IsVisible = ko.observable(visible);
}

var Stage = function(stage_id, stage_name, index, stage_type, command) {
	this.StageID = ko.observable(stage_id);
	this.StageName = ko.observable(stage_name);
	this.StageIndex = ko.observable(index);
	this.StageType = ko.observable(stage_type);
	this.Command = ko.observable(command);
}

var Parameter = function(parameter_id, name, value, param_type) {
	this.ParameterID = ko.observable(parameter_id);
	this.ParameterName = ko.observable(name);
	this.Value = ko.observable(value);
	this.ParameterType = ko.observable(param_type);
}

var ExpectedOutput = function(expected_output_id, filename) {
    this.ExpectedOutputID = ko.observable(expected_output_id);
    this.ExpectedOutputFileName = ko.observable(filename);
}

var ProcessingMessage = function(success, message) {
    this.Success = ko.observable(success);
    this.Message = ko.observable(message);
}

function JobsViewModel() {
	var self = this;
    
    self.AccessRights = ko.observableArray([
    	new AccessRight(2, "Admin"),
    	new AccessRight(3, "View & Use"),
    	new AccessRight(4, "View"),
    ]);
	
	self.Loading = ko.observable(true);
	self.LoadingJob = ko.observable(true);
	self.LoadingClusterJob = ko.observable(true);
	self.VisibleWindow = ko.observable("job-details");
	
	self.Processing = ko.observable(false);
	self.ProcessingSuccess = ko.observable(true);
	self.ProcessingMessages = ko.observableArray([]);
	
	self.RepeatJobName = ko.observable();
	self.RepeatIndex = ko.observable();
	self.RepeatLoading = ko.observable();
	
	self.ClusterJob = ko.observable();
	
	self.cluster_job_id = ko.observable(null);
	
	self.Job = ko.observable(null);
	self.UserAccessRight = ko.observable(null);	
	
	self.job_id = ko.observable(null);
	
	self.Jobs = ko.observableArray();
		
	self.GetClusterJob = function() {
	
		$.ajax({
			url: "/api/jms/jobs/cluster/" + self.cluster_job_id(),
			success: function(json) {	
				job = new ClusterJob();
				job.ClusterJobID(json.ClusterJobID);
				job.JobName(json.JobName);
				job.JobOwner(json.JobOwner);
	
				job.MemoryRequested(json.MemoryRequested);
				job.NodesAvailable(json.NodesAvailable);
				job.NodesRequested(json.NodesRequested);
				job.WalltimeRequested(json.WalltimeRequested);
	
				job.CPUTimeUsed(json.CPUTimeUsed);
				job.MemoryUsed(json.MemoryUsed);
				job.VirtualMemoryUsed(json.VirtualMemoryUsed);
				job.WalltimeUsed(json.WalltimeUsed);
	
				job.State(json.State);
				job.Queue(json.Queue);
				job.Server(json.Server);
				job.ExecutionHost(json.ExecutionHost);
				job.SubmitArgs(json.SubmitArgs);
				job.SubmitHost(json.SubmitHost);
				job.OutputPath(json.OutputPath);
				job.ExecutionHost(json.ExecutionHost);
				job.ErrorPath(json.ErrorPath);
				job.Priority(json.Priority);
	
				job.CreatedTime(json.CreatedTime);
				job.TimeEnteredQueue(json.TimeEnteredQueue);
				job.EligibleTime(json.EligibleTime);
				job.LastModified(json.LastModified);
				job.StartTime(json.StartTime);
				job.CompletionTime(json.CompletionTime);
				job.TotalRuntime(json.TotalRuntime);
	
				job.VariableList(json.VariableList);
	
				job.Comment(json.Comment);
				job.ExitStatus(json.ExitStatus);
				
				job.OutputStream(json.OutputStream);
				job.ErrorStream(json.ErrorStream);
				
				self.ClusterJob(job);
				
				self.LoadingClusterJob(false);
			},
			error: function () {		
				self.LoadingClusterJob(false);		
			}
		});		
	}
	
	self.GetJob = function() {
	    if(self.job_id() != "cluster") {
		    $.ajax({
			    url: "/api/jms/jobs/" + self.job_id(),
			    success: function(data) {
				    if(self.Job() == null || self.Job().JobID() != data.JobID) {			
					    job = new Job(data.JobID, data.JobName, data.JobDescription, data.Workflow.WorkflowName, []);
				
					    $.each(data.JobStages, function(i, js) {
						    type = "Command-line Utility";
						    if(js.Stage.StageType == 2)
							    type = "Custom Script";
						    else if(js.Stage.StageType == 3)
							    type = "Workflow";
					
						    state = "Created";
						    if(js.State == 2)
							    state = "Queued";
						    else if(js.State == 3)
							    state = "Running";
						    else if(js.State == 4)
							    state = "Complete";
						    else if(js.State == 5)
							    state = "Awaiting User Input";
						    else if(js.State == 6)
							    state = "Stopped";
						    else if(js.State == 7)
							    state = "Failed";
						
						    jobstage = new JobStage(js.JobStageID, new Stage(js.Stage.StageID, js.Stage.StageName, js.Stage.StageIndex, type, js.Stage.Command), js.ClusterJobID, state, [], []);
					
						    $.each(js.Stage.ExpectedOutputs, function(j, output) {							
							    o = new ExpectedOutput(output.ExpectedOutputID, output.ExpectedOutputFileName);
							    jobstage.ExpectedOutputs.push(o);
						    });
					
						    $.each(js.JobStageParameters, function(j, param) {
							    type = "Text";
							    if(param.Parameter.ParameterType == 2)
								    type = "Number";
							    else if(param.Parameter.ParameterType == 3)
								    type = "True/False";
							    else if(param.Parameter.ParameterType == 4)
								    type = "Options";
							    else if(param.Parameter.ParameterType == 5)
								    type = "File";
							    else if(param.Parameter.ParameterType == 6)
								    type = "Previous Parameter";
							    else if(param.Parameter.ParameterType == 7) {
								    type = "JSON File";
							    }
							
							    p = new Parameter(param.Parameter.ParameterID, param.Parameter.ParameterName, param.Value, type);
						
							    jobstage.Parameters.push(p);
						    });
					
						    job.JobStages.push(jobstage);
					    });
				
					    self.Job(job);
				    } else {
					    //if it is an interval update, then update the job rather than replacing it					
					    $.each(data.JobStages, function(i, js) {
						    state = "Created";
						    if(js.State == 2)
							    state = "Queued";
						    else if(js.State == 3)
							    state = "Running";
						    else if(js.State == 4)
							    state = "Complete";
						    else if(js.State == 5)
							    state = "Awaiting User Input";
						    else if(js.State == 6)
							    state = "Stopped";
						    else if(js.State == 7)
							    state = "Failed";
						
						    jobstage = self.Job().JobStages()[i];
						    jobstage.State(state);					
					    });	
				    }
				
				    self.LoadingJob(false);
			    },
			    error: function() {
				    self.LoadingJob(false);
			    }
		    });
		}
	}
	
	self.GetJobs = function() {
		$.ajax({
			url: "/api/jms/jobs",
			success: function(data) {
				jobs = []
				$.each(data, function(i, job) {
					jobs.push(new Job(job.JobID, job.JobName, job.Description, job.Workflow.WorkflowName));
				});				
				self.Jobs(jobs);
				
				self.Loading(false);
			},
			error: function() {
				self.Loading(false);
			}
		});
	}
	    
	self.job_length = ko.observable(0);
	self.job_length.subscribe(function(value) {
	    if(value > 0) {
	        self.Processing(true);
	    } else {
	        self.Processing(false);
	    }
	});
	
	self.StopAllJobs = function() {
	    question.Show("Stop job?", "Are you sure you want to stop executing this job? Note that you will be able to restart the job at a later stage.", function() {
			question.Hide();
	        $("#submit-dialog").modal({ 
			    "backdrop": "static"
		    });
			
	        self.job_length(0);
	        self.ProcessingSuccess(true);	
	        self.ProcessingMessages([]);
	        
	        $.each(self.Job().JobStages(), function(i, stage) {
	            //if(stage.State() == "Running" || stage.State() == "Queued") {
	                self.job_length(self.job_length()+1);
        	        self.StopJob(stage.ClusterJobID());
	            //}
	        });
	    });    
	}
	
	self.StopJob = function(job_id) {
			
		$.ajax({
			url: "/api/jms/jobs/cluster/" + job_id,
			type: "DELETE",
			success: function() {
				clearInterval(interval);
			    jobs_model.LoadData();
			    interval = setInterval(jobs_model.LoadData, 30000);
				self.ProcessingMessages.push(new ProcessingMessage(true, job_id + " successfully stopped..."));
			},
			error: function(jqXHR) {
				
				var error_message = job_id + ": ";
				if(jqXHR.status == 400) {
					error_message += "Bad request - Attempt to stop the job failed. The job may have already stopped.";
				} else if (jqXHR.status == 403) {
					error_message += "Permission denied - You do not have permission to stop this job. Either the job was created by another user or your password on the server has changed. Try log in again.";
				} else if (jqXHR.status == 404) {
					error_message += "Job not found - The job you tried to stop no longer exists on the server.";
				} else if (jqXHR.status == 500) {
					error_message += "Internal server error - Something went wrong on the server. Please try again. If the problem persists, contact an administrator.";
				} else {
					error_message += "HTTP status code " + jqXHR.status + " - Something went wrong on the server. Please try again. If the problem persists, contact an administrator.";
				}
				
				self.ProcessingSuccess(false);				
				self.ProcessingMessages.push(new ProcessingMessage(false, error_message));
			},
			complete: function() {
			    self.job_length(self.job_length()-1);
			}
		});
	}
	
	self.DeleteJob = function() {	    
	    question.Show("Delete job?", "Are you sure you want to delete this job? You will not be able to reverse this process.", function() {
			question.ToggleLoading(true);
			
			job_id = self.Job().JobID();
	    
	        $.ajax({
			    url: "/api/jms/jobs/" + job_id,
			    type: "DELETE",
			    success: function() {
			        $.each(self.Jobs(), function(i, job) {
			            console.log(job.JobID() + " " + job_id);
			            if(job.JobID() == job_id) {
			                self.Jobs.remove(job);
			                return false;
			            }
			        });
			        
			        self.Job(null);
			        
			        question.Hide();
			        window.location = "/jobs/#";
			    },
			    error: function(jqXHR) {				
				    question.ToggleLoading(false);
			    }
		    });		
		});	    
	}
	
	self.RepeatJob = function() {
	    self.RepeatLoading(true);
	    
	    $.ajax({
	        url: "/api/jms/jobs/" + self.Job().JobID(),
	        type: "POST",
	        data: { JobName: self.RepeatJobName(), StartStage: self.RepeatIndex() },
	        success: function(job_id) {
	            self.ResetLoadInterval();
	            window.location = "/jobs/#" + job_id;
	            $("#repeat-dialog").modal('hide');
	        },
	        error: function() {
	            self.RepeatLoading(false);
	        }
	    });
	}
	
	self.ShowRepeatJob = function() {
	    self.RepeatJobName(self.Job().JobName());
	    self.RepeatIndex(1);
	    self.RepeatLoading(false);
	    $("#repeat-dialog").modal({ 
	        'backdrop': 'static' 
	    });
	}
	
	self.LoadData = function(j, c) {
		self.GetJobs();
		if(self.job_id() != null) {
			self.LoadingJob(true);
			self.GetJob();
			
			//load file manager
			if(elf_loaded) {
				elf.options.url = '/api/jms/filemanager/' + jobs_model.job_id()	+ '/';
				elf.exec('reload');
			} else {
				elf_loaded = true;
				elf = $('#elfinder').elfinder({
					url : '/api/jms/filemanager/' + jobs_model.job_id()	+ '/',
					sync: 30000
				}).elfinder('instance');
			}
			
		} else {
			self.LoadingJob(false);
		}
		
		if(self.cluster_job_id() != null) {
			self.LoadingClusterJob(true);
			self.GetClusterJob();
		} else {
			self.LoadingClusterJob(false);
		}
	}
	
	self.ResetLoadInterval = function() {
	    clearInterval(interval);
		jobs_model.LoadData();
		interval = setInterval(jobs_model.LoadData, 30000);
	}
	
	self.ToggleStageVisible = function(data) {
		$("#stage_" + data.JobStageID()).slideToggle();
		data.IsVisible(!data.IsVisible());
	}
	
	self.edit_mode = false;
	
	self.SaveUserAccessRight = function() {
	    $.ajax({
	        url: "/api/jms/jobs/" + self.Job().JobID() + "/permissions/users",
	        type: "POST",
	        data: { Username: self.UserAccessRight().User().Username(), AccessRightID: self.UserAccessRight().AccessRight().AccessRightID() },
	        success: function(data) {
	            access = new AccessRight(data.AccessRight.AccessRightID, data.AccessRight.AccessRightName);
	            
	            if(self.edit_mode) {
	                self.temp_share().AccessRight(access);
	            } else {
        	        user = new User(data.User.id, data.User.username);
    	            self.Job().UserAccessRights.push(new UserJobAccessRight(user, access, true));
	            }
	            
	            $("#user-share-dialog").modal('hide');
	        },
	        error: function() {
	        
	        }
	    });
	}
	
	self.ShowAddUserAccessRight = function() {
	    self.edit_mode = false;
	    self.UserAccessRight(new UserJobAccessRight(new User(0, ""), self.AccessRights()[2]));
	    $("#user-share-dialog").modal();
	}
	
	self.temp_share = ko.observable();
	self.ShowEditUserAccessRight = function(data) {
	    self.edit_mode = true;
	    self.temp_share(data);
	    
	    var r = data.clone();
	    console.log(data.User().Username());
	    console.log(r.User().Username());
	    index = r.AccessRight().AccessRightID() - 2;
	    r.AccessRight(self.AccessRights()[index]);
	    self.UserAccessRight(null);
	    self.UserAccessRight(r);
	    
	    $("#user-share-dialog").modal();
	}
	
	self.SaveGroupAccessRight = function() {
	    $.ajax({
	        url: "/api/jms/jobs/" + self.Job().JobID() + "/permissions/groups",
	        type: "POST",
	        data: { GroupID: self.GroupAccessRight().Group().GroupID(), AccessRightID: self.UserAccessRight().AccessRight().AccessRightID() },
	        success: function(data) {
	            group = new Group(data.Group.id, data.Group.name);
	            access = new AccessRight(data.AccessRight.AccessRightID, data.AccessRight.AccessRightName);
	                
	            self.Job().GroupAccessRights.push(new GroupJobAccessRight(group, access, true));
	            
	            $("#group-share-dialog").modal('hide');
	        },
	        error: function() {
	        
	        }
	    });
	}
	
	self.ShowAddGroupAccessRight = function() {
	    self.GroupAccessRight(new GroupJobAccessRight(new Group(0, ""), self.AccessRights()[2]));
	    $("#group-share-dialog").modal();
	}
	
	self.ShowEditGroupAccessRight = function(data) {
	    console.log(data.AccessRight().AccessRightID());
	    self.GroupAccessRight(data);
	    $("#group-share-dialog").modal();
	}
	
	self.DeleteUserAccessRight = function(data) {	    
	    question.Show("Remove user access?", "Are you sure you want to remove " + data.User().Username() + "'s access to this job?", function() {
			question.ToggleLoading(true);
			$.ajax({
			    url: "/api/jms/jobs/" + self.Job().JobID() + "/permissions/users/" + data.User().UserID(),
			    type: "DELETE",
    	        success: function() {
    	            self.Job().UserAccessRights.remove(data);
    	        },
    	        complete: function() {
    	            question.Hide();
    	        }
    	    });
	    });
	}
	
	self.DeleteGroupAccessRight = function(data) {
	    question.Show("Remove group access?", "Are you sure you want to remove " + data.Group().GroupName() + "'s access to this job?", function() {
			question.ToggleLoading(true);
			$.ajax({
			    url: "/api/jms/jobs/" + self.Job().JobID() + "/permissions/groups/" + data.Group().GroupID(),
			    type: "DELETE",
    	        success: function() {
    	            self.Job().GroupAccessRights.remove(data);
    	        },
    	        complete: function() {
    	            question.Hide(false);
    	        }
    	    });
	    });
	}
	
	self.ShowShareJob = function() {
	    var job = self.Job();
	    
	    $.ajax({
	        url: "/api/jms/jobs/" + job.JobID() + "/permissions",
	        success: function(data) {
	            self.Job().UserAccessRights([]);
	            self.Job().GroupAccessRights([]);
	            
	            $.each(data.UserJobAccessRights, function(i, access_right) {
	                user = new User(access_right.User.id, access_right.User.username);
	                access = new AccessRight(access_right.AccessRight.AccessRightID, access_right.AccessRight.AccessRightName);
	                
	                self.Job().UserAccessRights.push(new UserJobAccessRight(user, access, true));
	            });
	            
	            $.each(data.GroupJobAccessRights, function(i, access_right) {
	                group = new Group(access_right.group.id, access_right.group.groupname);
	                access = new AccessRight(access_right.AccessRight.AccessRightID, access_right.AccessRight.AccessRightName);
	                
	                self.Job().GroupAccessRights.push(new GroupJobAccessRight(group, access, true));
	            });
	        },
	        error: function() {
	        
	        }
	    });
	    
	    $("#share-dialog").modal();
	}
}


var interval;
var elf;
var elf_loaded = false;

var question = new QuestionModal("question-dialog");

var jobs_model = new JobsViewModel();
ko.applyBindings(jobs_model, document.getElementById("page-wrapper"));

$(function() {

	jobs_model.LoadData();
	interval = setInterval(jobs_model.LoadData, 30000);
	
	$('#job_list').slimScroll({
		height: '500px'
	});	

	// initialize the application
	var app = Sammy(function() {

		// define a 'route'
		this.get('#:job/:cluster_job', function() {
			jobs_model.job_id(this.params.job);
			jobs_model.cluster_job_id(this.params.cluster_job);
			
			clearInterval(interval);
			jobs_model.LoadData();
			interval = setInterval(jobs_model.LoadData, 30000);
			
		});
		
		this.get('#:job', function() {
			jobs_model.Job(null)	
			jobs_model.job_id(this.params.job);
			jobs_model.cluster_job_id(null);
			jobs_model.ClusterJob(null);
			
			clearInterval(interval);
			jobs_model.LoadData();
			interval = setInterval(jobs_model.LoadData, 30000);		
		});
		
		this.get('/jobs/', function() {
			jobs_model.LoadingJob(false);
		});
	});

	// start the application
	app.run('/jobs/#');
});
