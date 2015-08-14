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

var Node = function(name, state, num_cores, busy_cores, jobs) {
	this.Name = ko.observable(name);
	this.State = ko.observable(state);
	this.NumCores = ko.observable(num_cores);
	this.BusyCores = ko.observable(busy_cores);
	this.FreeCores = ko.observable(num_cores - busy_cores);
	this.Jobs = ko.observableArray(jobs);
}

var NodeJob = function(job_id, cores){
	this.JobID = ko.observable(job_id);
	this.Cores = ko.observable(cores);
}

var Job = function(job_id, username, job_name, nodes, cores, state, time, queue, server, resources){
	this.JobID = ko.observable(job_id);
	this.Username = ko.observable(username);
	this.JobName = ko.observable(job_name);
	this.Nodes = ko.observable(nodes);
	this.Cores = ko.observable(cores);
	this.State = ko.observable(state);
	this.Time = ko.observable(time);
	this.Queue = ko.observable(queue);
}

var Resource = function(resource, allocated) {
	this.ResourceName = ko.observable(resource)
	this.ResourcesAllocated = ko.observable(allocated)
}

var DiskUsage = function(disk_size, available_space, used_space){
	this.DiskSize = ko.observable(disk_size);
	this.AvailableSpace = ko.observable(available_space);
	this.UsedSpace = ko.observable(used_space);
}

var ClusterJob = function(job_id, job_name, user, status, exit_code, working_dir, error_log, output_log, data) {
    this.JobID = ko.observable(job_id);
    this.JobName = ko.observable(job_name);
    this.User = ko.observable(user);
    this.Status = ko.observable(status);
    this.ExitCode = ko.observable(exit_code);
    this.WorkingDir = ko.observable(working_dir);
    this.ErrorLog = ko.observable(error_log);
    this.OutputLog = ko.observable(output_log);
    this.DataSections = ko.observableArray(data)
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

function DashboardViewModel() {		
	var self = this;
	
	//Filters			
	self.QueueFilter = ko.observable("");
	self.NodeJobFilter = ko.observable("");
	
	//Data
	self.Nodes = ko.observableArray(null);
	self.Queue = ko.observableArray(null);
		
	//summary data	
	self.NodesOnline = ko.observable(0);

	self.NumCores = ko.observable(0);	
	self.BusyCores = ko.observable(0);

	self.JobsRunning = ko.observable(0);
	self.JobsWaiting = ko.observable(0);

	self.DiskUsage = ko.observable(new DiskUsage());
	
	//nodes graph data
	self.nodes_data = [];	

	//selected data
	self.Node = ko.observable(new Node("", "", 64, 0, []));
	self.selected_node_index = 0;
	self.Job = ko.observable();
	
	self.loading_dashboard = ko.observable(false);
	self.LoadDashboard = function() {
		$.ajax({
			url: "/api/jms/dashboard",
			success: function(json) {
				var data = JSON.parse(json);
				
				self.DiskUsage(new DiskUsage(data.disk.disk_size, 
					data.disk.available_space, data.disk.used_space));
				
				//Load queue
				jobs_running = 0;
				jobs_waiting = 0;
				
				var queue = []
				$.each(data.queue, function(index, q) {
					var j = new Job(q.job_id, q.username, 
						q.job_name, q.nodes, q.cores, q.state, 
						q.time, q.queue);
										
					queue.push(j);	
					
					if(q.state == "R")
						jobs_running++;
					else if(q.state == "Q" || q.state == "H")
						jobs_waiting++;			
				});				
				
				self.Queue(queue);				
				
				self.JobsRunning(jobs_running);
				self.JobsWaiting(jobs_waiting);
				
				//Load nodes
				self.nodes_data = [];
				
				self.NodesOnline(0);
				self.NumCores(0);	
				self.BusyCores(0);
					
				self.Nodes([]);
									
				$.each(data.nodes, function(i, node) {
					var n = new Node(node.name, node.state, 
						node.num_cores, node.busy_cores, 
						[]);
					
					$.each(node.jobs, function(j, job){
						n.Jobs().push(new NodeJob(job.job_id, job.cores));
					});
					
					self.Nodes.push(n);
					
					//data for morris chart
					self.nodes_data.push({ label: node.name, value: node.busy_cores });
					
					if(node.state != "down") {
						self.NodesOnline(self.NodesOnline() + 1);
					}
					
					self.NumCores(self.NumCores() + node.num_cores);	
					self.BusyCores(self.BusyCores() + node.busy_cores);
				});				
									
		        self.Node(self.Nodes()[self.selected_node_index]);
				
				//NB: SET LOADING TO FALSE BEFORE DRAWING CHARTS
				self.loading_dashboard(false);
		        
		        //Draw donut chart if there are busy nodes
		        if(self.BusyCores() > 0) {
					chart = Morris.Donut({
						element: 'node-usage-chart',
						data: self.nodes_data,
						resize: true,
					});
							
					chart.on('click', function(i, node){
						self.selected_node_index = i;
						self.Node(self.Nodes()[i]);
					});		
				}
			},
			error: function() {					
			},
			complete: function() {	
				self.loading_dashboard(false);
			}
		});		
	}
	
	self.FilterQueue = function(job) {
		if(self.QueueFilter().length > 0) {
			if(job.JobID().indexOf(self.QueueFilter()) >= 0) {
			   	return true;
		    } else if(job.JobName().indexOf(self.QueueFilter()) >= 0) {
			   	return true;
		    } else if(job.Username().indexOf(self.QueueFilter()) >= 0) {
			   	return true;
		    } else if(job.State() == self.QueueFilter()) {
			   	return true;
		    }    
		    
		    return false;
        }                
        return true;
	}
	
	self.FilterNodeJob = function(job)  {}
	
	self.StopJob = function(job_id) {
	    question.Show("Stop Job?", "Are you sure you want to stop this job (" + job_id + ")? You will not be able to reverse this action.", function() {
    		question.ToggleLoading(true);
    		
    		$("#n_" + job_id.replace('.', '_') + " > i").hide();
    		$("#n_" + job_id.replace('.', '_') + " > img").show();
    		
    		$("#q_" + job_id.replace('.', '_') + " > i").hide();
    		$("#q_" + job_id.replace('.', '_') + " > img").show();
    			
    		$.ajax({
    			url: "/api/jms/jobs/cluster/" + job_id,
    			type: "DELETE",
    			success: function() {
    				self.LoadDashboard();
    			},
    			error: function(jqXHR) {
    				var header = $("#modal-dialog > div.modal-dialog > div.modal-content > div.modal-header > h4.modal-title");
    				var body = $("#modal-dialog > div.modal-dialog > div.modal-content > div.modal-body");
    					
    				header.html('<span class="icon-box bg-color-red"><i class="fa fa-warning"></i></span> ');
    				if(jqXHR.status == 400) {
    					header.append("Error: Bad request");
    					body.text("Attempt to stop the job failed. The job may have already stopped.");
    				} else if (jqXHR.status == 403) {
    					header.append("Error: Permission denied");
    					body.text("You do not have permission to stop this job. Either the job was created by another user or your password on the server has changed. Try log in again.");
    				} else if (jqXHR.status == 404) {
    					header.append("Error: Job not found");
    					body.text("The job you tried to stop no longer exists on the server.");
    				} else if (jqXHR.status == 500) {
    					header.append("Error: Internal server error");
    					body.text("Something went wrong on the server. Please try again. If the problem persists, contact an administrator.");
    				} else {
    					header.append("Error: HTTP status code " + jqXHR.status);
    					body.text("Something went wrong on the server. Please try again. If the problem persists, contact an administrator.");
    				}
    					
    				$("#modal-dialog").modal();
    				
    				$("#n_" + job_id + " > img").hide();
    				$("#n_" + job_id + " > i").show();
    				
    				$("#q_" + job_id + " > img").hide();
    				$("#q_" + job_id + " > i").show();
    			},
    			complete: function() {
    			    question.Hide();
    			    question.ToggleLoading(false);
    			}
    		});
    	});
	}
    
	self.ViewDashboard = function() {
	    self.loading_dashboard(true);
	    
		self.LoadDashboard();
		
		clearInterval(interval);		
		interval = setInterval(self.LoadDashboard, 10000);
	}
	
	self.loading_job = ko.observable(false);
	self.Job = ko.observable();
	self.GetJob = function(id) {
	    
	    $.ajax({
	        url: "/api/jms/jobs/cluster/" + id,
	        success: function(job){
	            job = JSON.parse(job);
	            
	            self.Job(new ClusterJob(job.JobID, job.JobName, job.User, job.Status, job.ExitCode, job.WorkingDir, job.ErrorLog, job.OutputLog, []));
	            
	            $.each(job.DataSections, function(j, section){
                    var s = new JobStageDataSection(j, section.SectionHeader, []);
                    
                    $.each(section.DataFields, function(k, field){
                        if(section.SectionHeader == "Time"){
                            var f = new JobStageDataField(field.Key, timeConverter(field.DefaultValue), field.Label, field.ValueType);
                        } else {
                            var f = new JobStageDataField(field.Key, field.DefaultValue, field.Label, field.ValueType);
                        }
                        
                        s.DataFields.push(f);
                    });
                    
                    self.Job().DataSections.push(s);
                });
                
	            console.log(job);
	        },
	        complete: function() {
	            self.loading_job(false);
	        }
	    })
	}
	
	self.ViewJob = function(id) {
	    self.loading_job(true);
	    
	    self.GetJob(id);
	    
		clearInterval(interval);
		interval = setInterval(function() {
		    self.GetJob(id);
		    }, 10000);
	}
}

var interval;
var dashboard;
var question = new QuestionModal("question-dialog");

$(document).ready(function () {
    
    dashboard = new DashboardViewModel();
    ko.applyBindings(dashboard, document.getElementById("page-wrapper"));

    // initialize the application
	var app = Sammy(function() {
		
		this.get('#jobs/:id', function() {
		    $("#dashboard").fadeOut(200);
		    dashboard.ViewJob(this.params.id)
		    
		    setTimeout(function() {
		        $("#job-details").fadeIn();	
		    }, 300);
		});
		
		this.get('/', function() {
		    $("#job-details").fadeOut(200);
		    
		    setTimeout(function() {
		        $("#dashboard").fadeIn();
		        dashboard.ViewDashboard();	
		    }, 300);
		});
	});
	
	// start the application
	app.run('/');
});