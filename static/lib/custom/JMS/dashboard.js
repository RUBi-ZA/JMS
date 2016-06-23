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

var JobQueue = function() {
    this.ColumnNames = ko.observableArray();
    this.Rows = ko.observableArray();
}

var JobRow = function() {
    this.JobID = ko.observable();
    this.Values = ko.observableArray();
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
	self.QueueFilter.subscribe(function(){
	    self.FilterQueue();
	});
	
	self.page = ko.observable(1);
	self.page.subscribe(function(){
	    self.ShowVisibleJobs();
	});
	
	self.page_size = ko.observable(20);
	self.last_page = ko.observable()
	self.range_start = ko.observable();
	self.range_end = ko.observable()
	
	//Data
	self.Nodes = ko.observableArray(null);
	
	self.Queue = ko.observable(new JobQueue());
	self.queue = [];
	self.FilteredQueue = ko.observable(new JobQueue());
	self.VisibleQueue = ko.observable(new JobQueue());
		
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
	
	self.ShowVisibleJobs = function() {
	    var queue_length = self.FilteredQueue().Rows().length;
	    var range_end = self.page_size() * self.page();
	    
	    self.range_start(range_end - self.page_size());
	    self.range_end(Math.min(range_end, queue_length));
	    
	    self.last_page(Math.ceil(
	            queue_length/self.page_size()
	        ));
	    
	    var vis = [];
	    
	    for(var i = self.range_start(); i < self.range_end(); i++) {
	        var q = self.FilteredQueue().Rows()[i];
	        vis.push(q);
	    }
	    
	    self.VisibleQueue().Rows(vis);
	}
	
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
				self.queue = JSON.parse(json);
				var data = self.queue;
				
				self.DiskUsage(new DiskUsage(data.disk.disk_size, 
					data.disk.available_space, data.disk.used_space));
				
				//Load queue
				jobs_running = 0;
				jobs_waiting = 0;
				
				var queue = new JobQueue();
				var filtered = new JobQueue();
				var visible = new JobQueue();
				
				queue.ColumnNames(data.queue.column_names);
				filtered.ColumnNames(data.queue.column_names);
				visible.ColumnNames(data.queue.column_names);
				
				$.each(data.queue.rows, function(index, row) {
					var j = new JobRow();
					j.JobID(row.job_id);
					j.Values(row.values);
					
					queue.Rows.push(j);	
					
					if(row.state == 3)
						jobs_running++;
					else if(row.state < 3)
						jobs_waiting++;	
						
					if(self.Filter(j)) {
					    filtered.Rows.push(j)
					}
				});			
				
				self.Queue(queue);
				self.FilteredQueue(filtered);
				self.VisibleQueue(visible);
				
				self.ShowVisibleJobs();
				
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
    			    
	            interval = setTimeout(function() {
	                self.LoadDashboard() }, 20000);
			}
		});		
	}
	
	self.Filter = function(job_row) {
		if(self.QueueFilter().length > 0) {
			if(job_row.JobID().indexOf(self.QueueFilter()) >= 0) {
			   	return true;
		    } else { 
		        var found = false;
			   	$.each(job_row.Values(), function(i, val) {
			   	    if (typeof val != "string") {
			   	        val = val.toString();
			   	    }
			   	    index = val.indexOf(self.QueueFilter());
			   	    
			   	    if(index >= 0) {
			   	        found = true;
			   	        
			   	        return false;
			   	    }
			   	});
		    }    
		    
		    return found;
        }                
        return true;
	}
	
	self.FilterQueue = function() {
	    var filtered = new JobQueue();
	    
	    $.each(self.Queue().Rows(), function(i, j) {
	        if(self.Filter(j)) {
	            filtered.Rows.push(j);
	        }
	    });
	    
	    self.FilteredQueue(filtered);
	    self.ShowVisibleJobs();
	}
	
	self.FirstPage = function() {
	   self.page(1);
	}
	
	self.PreviousPage = function() {
	    self.page(self.page() - 1);
	}
	
	self.NextPage = function() {
	    self.page(self.page() + 1);
	}
	
	self.LastPage = function() {
	    self.page(self.last_page());
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
    			    
    			    clearTimeout(interval);
		            self.LoadDashboard();
    			}
    		});
    	});
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
        		
        		if(self.Job().Status() < 4) {
            		interval = setTimeout(function() {
            		        self.GetJob(id);
            		    }, 10000);
        		}
	        }
	    })
	}
	
	self.ViewJob = function(id) {
	    self.loading_job(true);
	    
	    clearTimeout(interval);
	    self.GetJob(id);
	}
    
	self.ViewDashboard = function() {
	    self.loading_dashboard(true);
	    
	    clearTimeout(interval);
		self.LoadDashboard();
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