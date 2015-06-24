function timeConverter(UNIX_timestamp){
    var a = new Date(UNIX_timestamp*1000);
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var year = a.getFullYear();
    var month = months[a.getMonth()];
    var date = a.getDate();
    var hour = a.getHours();
    var min = a.getMinutes();
    var sec = a.getSeconds();
    var time = date + ' ' + month + ' ' + year + ' - ' + hour + ':' + min + ':' + sec ;
    return time;
}

function DirectoryObject(name, path, type) {
    this.Name = ko.observable(name);
    this.FullPath = ko.observable(path);
    this.Type = ko.observable(type);
}

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
    this.DataSections = ko.observableArray();
    
    this.ErrorLog = ko.observable(error);
    this.ErrorContent = ko.observable('');
    this.OutputLog = ko.observable(out);
    this.OutputContent = ko.observable('');
    this.WorkingDirectory = ko.observable(dir);
    
    this.FMDirectory = ko.observableArray();
    this.FMDirectoryListing = ko.observableArray();
}


var JobStageDataSection = function(id, section, fields) {
    this.id = ko.observable(id);
    this.SectionHeader = ko.observable(section);
    this.DataFields = ko.observableArray(fields);
    
    this.Visible = ko.observable(false);
}
    

var JobStageDataField = function(key, value, label, type) {  
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
    
    self.job_menu = ko.observableArray([{
            text: "<i class='fa fa-share'></i> Share",
            action: function(data) { self.Share(data); }
        }, {
            text: "<i class='fa fa-download'></i> Download",
            action: function(data) { self.Download(data); }
        }, { 
            text: "<i class='fa fa-play'></i> Repeat", 
            action: function(data) { self.ShowRepeatJob(data); }
        }, {
            separator: true
        }, {
            text: "<i class='fa fa-copy'></i> Stop",
            action: function(data) { self.StopJob(data); }
        }, {
            text: "<i class='fa fa-trash-o'></i> Delete",
            action: function(data) { self.DeleteJob(data); }
        }  
    ]);
    
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
	                    if(jsp.Parameter.ParentParameter == null){
    	                    var jsparam = new JobStageParameter(jsp.JobStageParameterID,
    	                        jsp.ParameterName, jsp.Value);  
    	                    
    	                    jobstage.JobStageParameters.push(jsparam);
	                    }
	                })
	                
	                var details = JSON.parse(js.JobData);
	                $.each(details, function(j, section){
	                    var s = new JobStageDataSection(j, section.SectionHeader, []);
	                    
	                    $.each(section.DataFields, function(k, field){
	                        if(section.SectionHeader == "Time"){
	                            var f = new JobStageDataField(field.Key, timeConverter(field.DefaultValue), field.Label, field.ValueType);
	                        } else {
	                            var f = new JobStageDataField(field.Key, field.DefaultValue, field.Label, field.ValueType);
	                        }
	                        
	                        s.DataFields.push(f);
	                    });
	                    
	                    jobstage.DataSections.push(s);
	                })
	                
	                self.GetErrorLog(jobstage);
	                self.GetOutputLog(jobstage);
	                self.GetDirectoryListing(jobstage, "/");
	                
	                job.JobStages.push(jobstage);
	            });
	            
	            self.Job(job);
	        }
	    })
	}
	
	self.GetErrorLog = function(data) {
	    $.ajax({
	        url: "/api/jms/jobstages/" + data.JobStageID() + "/files?log=error",
	        success: function(content) {
	            data.ErrorContent(content);
	        }
	    });
	}
	
	self.GetOutputLog = function(data) {
	    $.ajax({
	        url: "/api/jms/jobstages/" + data.JobStageID() + "/files?log=output",
	        success: function(content) {
	            data.OutputContent(content);
	        }
	    });
	}
	
	self.GetDirectoryListing = function(data, path) {
	    $.ajax({
	        url: "/api/jms/jobstages/" + data.JobStageID() + "/directories?path=" + path,
	        success: function(dir) {
	            dir = JSON.parse(dir)
                
                data.FMDirectory([]);
                $.each(dir.cwd, function(i, d) {
                    data.FMDirectory.push(new DirectoryObject(d.name, d.fullpath, d.type));
                });
                
                data.FMDirectoryListing([]);
                $.each(dir.dir_contents, function(i, d) {
                    data.FMDirectoryListing.push(new DirectoryObject(d.name, d.fullpath, d.type));
                });
	        }
	    });
	}
	
	self.GetFile = function(data, path) {
        var url = "/api/jms/jobstages/" + data.JobStageID() + "/files?path=" + path; 
        
        content = $("#content");
        content.html("");
        
        //send a HEAD request to check the content type of the file
        $.ajax({
            url: url,
            type: "HEAD",
            success: function(result, status, xhr){       
                
                //do something based on the content type
                var ct = xhr.getResponseHeader("content-type");
                if(ct.startsWith("image")) {
                    var img = new Image();
                    img.src = url;
                    img.className = "tab-image";
                    content.append(img);
                } else if (ct == "application/pdf") {
                    var pdf = document.createElement("object");
                    pdf.type = "application/pdf";
                    pdf.value = "Adobe Reader is required for Internet Explorer."
                    pdf.data = url;
                    pdf.className = "tab-pdf";
                    content.append(pdf);
                } else if(ct.startsWith("video")) {
                    var video = "<video class='tab-video' controls>";
                    video += "<source src='" + url + "' />";
                    video += "</video>"
                    content.append(video);
                } else if(ct.startsWith("audio")) {
                    var audio = "<audio class='tab-audio' controls>";
                    audio += "<source src='" + url + "' />";
                    audio += "</audio>"
                    content.append(audio);
                } else { 
                    $.ajax({
                        url: url,
                        success: function(result) {
                            var txt = document.createElement("textarea");
                            txt.value = result;
                            txt.className = "tab-text";
                            content.append(txt);
                            
                            make_editor($(txt), path);
                        }
                    });
                }
            },
            error: function(http) {
                console.log(http.responseText);
            }
        });        
    }
    
    
    self.downloadFile = function(data) {
        var url = "/files/transfer?path=" + data.fullpath();
        window.location = url;
    }
	
	self.ToggleVisible = function(id) {
	    $("#" + id).slideToggle();
	}
}

var make_editor = function(textarea, filename) {      
    var modelist = ace.require('ace/ext/modelist');
    mode = modelist.getModeForPath(filename).mode;
    
    var langauge_tools = ace.require("ace/ext/language_tools");
    
    var editDiv = $('<div>', {
        position: 'absolute',
        width: $("#page").width(),
        height: "500px",
        'class': textarea.attr('class')
    }).insertBefore(textarea);
    textarea.css('display', 'none');
    
    var editor = ace.edit(editDiv[0]);
    editor.getSession().setValue(textarea.val());
    editor.getSession().setMode(mode);
    editor.setAutoScrollEditorIntoView(true);
    editor.setTheme("ace/theme/merbivore_soft"); 
    editor.setOptions({
        fontSize: "13pt",
        enableBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true
    });                 
    
    editor.getSession().on('change', function(){
        content = editor.getSession().getValue();
        textarea.val(content);
        //tool.SelectedFile().Content(content);
    });
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