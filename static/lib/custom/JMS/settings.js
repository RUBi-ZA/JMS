var ServerSettings = function(name, keep, stat, iter, check, tcp, other_jobs, mom_sync, moab, sched) {
    this.ServerName = ko.observable(name);
    this.KeepCompleted = ko.observable(keep);
    this.JobStatRate = ko.observable(stat);
    this.SchedularIteration = ko.observable(iter);
    this.NodeCheckRate = ko.observable(check);
    this.TCPTimeout = ko.observable(tcp);
    this.QueryOtherJobs = ko.observable(other_jobs);
    this.MOMJobSync = ko.observable(mom_sync);
    this.MoabArrayCompatible = ko.observable(moab);
    this.Scheduling = ko.observable(sched);
    
    this.ServerAdministrators = ko.observableArray();
    this.Queues = ko.observableArray();
}

var ServerAdministrator = function(name, host, manager, operator) {
    this.Username = ko.observable(name);
    this.Host = ko.observable(host);
    this.Manager = ko.observable(manager);
    this.Operator = ko.observable(operator);
}

var Queue = function(name, type, enabled, started, max_queuable, max_run, max_user_queuable, max_user_run, max_nodes, default_nodes, max_cpu, default_cpu, max_mem, default_mem, max_walltime, default_walltime, default_queue) {
    this.QueueName = ko.observable(name);
    this.Type = ko.observable(type);
    this.Enabled = ko.observable(enabled);
    this.Started = ko.observable(started);
    this.MaxQueable = ko.observable(max_queuable);
    this.MaxRun = ko.observable(max_run);
    this.MaxUserQueable = ko.observable(max_user_queuable);
    this.MaxUserRun = ko.observable(max_user_run);
    this.MaxNodes = ko.observable(max_nodes);
    this.DefaultNodes = ko.observable(default_nodes);
    this.MaxCPUs = ko.observable(max_cpu);
    this.DefaultCPUs = ko.observable(default_cpu);
    this.MaxMemory = ko.observable(max_mem);
    this.DefaultMemory = ko.observable(default_mem);
    this.MaxWalltime = ko.observable(max_walltime);
    this.DefaultWalltime = ko.observable(default_walltime);
    this.DefaultQueue = ko.observable(default_queue);
}

var Node = function(name, state, cpu, prop, ip) {
    this.NodeName = ko.observable(name);
    this.State = ko.observable(state);
    this.NumProcessors = ko.observable(cpu);
    this.Properties = ko.observable(prop);
    
    //only used when adding a new node
    this.IPAddress = ko.observable(ip);
}

function SettingsViewModel() {
	var self = this;
	
	self.Loading = ko.observable(true);
	self.LoadingServer = ko.observable(false);
	self.LoadingQueue = ko.observable(false);
	self.LoadingAdmins = ko.observable(false);
	self.LoadingNodes = ko.observable(true);
	
	self.ServerVisible = false;
	self.AdminVisible = false;
	self.Queues = false;
		
	self.Settings = ko.observable();
	self.Nodes = ko.observableArray();
	
	self.SelectedQueues = ko.observableArray();
	self.SelectedQueue = ko.observable();
	self.SelectedQueues.subscribe(function(value){
	    if(value.length > 0) {
	        self.SelectedQueue(value[0]);
	    } else {
	        self.SelectedQueue(null);
	    }
	});
	
	self.SelectedNodes = ko.observableArray();
	self.SelectedNode = ko.observable();
	self.SelectedNodes.subscribe(function(value){
	    if(value.length > 0) {
	        self.SelectedNode(value[0]);
	    } else {
	        self.SelectedNode(null);
	    }
	});
	self.NewNode = ko.observable();
	
	self.SelectedAdministrators = ko.observableArray();
	self.SelectedAdministrator = ko.observable();
	self.SelectedAdministrators.subscribe(function(value){
	    if(value.length > 0) {
	        self.SelectedAdministrator(value[0]);
	    } else {
	        self.SelectedAdministrator(null);
	    }
	});
	
	//Functions
	
	self.GetServerSettings = function() {
	    $.ajax({
	        url: "/api/jms/settings/",
	        success: function(settings) {
	            settings = JSON.parse(settings);
	            self.LoadData(settings);
	            self.Loading(false);
	        }
	    });
	}
	
	self.LoadData = function(settings) {
	    var s = new ServerSettings(settings.ServerName, settings.KeepCompleted, settings.JobStatRate, settings.SchedularIteration, settings.NodeCheckRate, settings.TCPTimeout, settings.QueryOtherJobs, settings.MOMJobSync, settings.MoabArrayCompatible, settings.Scheduling);
	            
        $.each(settings.Queues, function(i, q) {
            var queue = new Queue(q.QueueName, q.Type, q.Enabled, q.Started, q.MaxQueable, q.MaxRun, q.MaxUserQueable, q.MaxUserRun, q.MaxNodes, q.DefaultNodes, q.MaxCPUs, q.DefaultCPUs, q.MaxMemory, q.DefaultMemory, q.MaxWalltime, q.DefaultWalltime, q.DefaultQueue);
            
            s.Queues.push(queue);
        });
        
        $.each(settings.ServerAdministrators, function(i, a) {
            var admin = new ServerAdministrator(a.Username, a.Host, a.Manager, a.Operator);
            
            s.ServerAdministrators.push(admin);
        });
        
        self.Settings(s);
	}
	
	self.SaveServerSettings = function() {
	    self.LoadingServer(true);
	    
	    var s = new Object();
	    s.ServerName = self.Settings().ServerName();
        s.KeepCompleted = self.Settings().KeepCompleted();
        s.JobStatRate = self.Settings().JobStatRate();
        s.SchedularIteration = self.Settings().SchedularIteration();
        s.NodeCheckRate = self.Settings().NodeCheckRate();
        s.TCPTimeout = self.Settings().TCPTimeout();
        s.QueryOtherJobs = self.Settings().QueryOtherJobs();
        s.MOMJobSync = self.Settings().MOMJobSync();
        s.MoabArrayCompatible = self.Settings().MoabArrayCompatible();
        s.Scheduling = self.Settings().Scheduling();
        
        var data = JSON.stringify(s);
        
        $.ajax({
            url: "/api/jms/settings",
            type: "POST",
            data: data,
            success: function(settings) {
                settings = JSON.parse(settings);
                self.LoadData(settings); 
            },
            error: function() {
            
            },
            complete: function() {
	            self.LoadingServer(false);
	        }
        });
	}
	
	//administrator functions	
	
	self.ShowAddAdministrator = function() {
        self.LoadingAdmins(false);
        
	    var s = new ServerAdministrator();
	    s.Host = self.Settings().ServerName()
	
	    self.SelectedAdministrators([]);	    
	    self.SelectedAdministrator(s);
	    $("#admin-dialog").modal({ 'backdrop': 'static'});
	}	
	
	self.ShowEditAdministrator = function() {
        self.LoadingAdmins(false);
	    $("#admin-dialog").modal({ 'backdrop': 'static'});
	}
	
	self.AddUpdateAdministrator = function() {
	    if (self.Settings().ServerAdministrators.indexOf(self.SelectedAdministrator()) < 0) {
            self.Settings().ServerAdministrators.push(self.SelectedAdministrator());
        }
        
        self.SaveAdministrators();
	}
	
	self.SaveAdministrators = function() {
	    self.LoadingAdmins(true);    
	    
	    $.ajax({
            url: "/api/jms/settings/administrators",
            type: "PUT",
            data: ko.toJSON(self.Settings().ServerAdministrators),
            success: function(settings) { 
                settings = JSON.parse(settings);
                self.LoadData(settings);  
	            question.Hide();
	            $("#admin-dialog").modal('hide');
            }, 
            error: function() {
                self.LoadingAdmins(false); 
	            question.ToggleLoading(false); 
            }
        });
        
	}
	
	self.DeleteAdministrator = function() {
	    question.Show("Delete Administrators?", "Are you sure you want to delete the selected administrators? This operation is irreversible.", function() {	        
	        question.ToggleLoading(true);
	        
	        $.each(self.SelectedAdministrators(), function(i, admin){
	            self.Settings().ServerAdministrators.remove(admin);
	        });
	        
	        self.SaveAdministrators();
	    });
	}
    
    //queue functions	
	
	self.ShowAddQueue = function() {
	    $("#queue-dialog").modal({
	        'backdrop':'static'
	    });
	    
        self.LoadingQueue(false); 
	}
	
	self.AddQueue = function() {
	    self.LoadingQueue(true);
	    
	    $.ajax({
            url: "/api/jms/settings/queues/" + $("#queue_name").val(),
            type: "POST",
            success: function(settings) { 
                settings = JSON.parse(settings);
                self.LoadData(settings); 
                
                $("#queue_name").val("");
                self.LoadingQueue(false); 
                $("#queue-dialog").modal('hide');
            }, 
            error: function() {
                self.LoadingQueue(false); 
            }
        });
	}
	
	self.SaveQueue = function() {
	    self.LoadingQueue(true);
	    
	    var queue_name = self.SelectedQueues()[0].QueueName()
	    
	    $.ajax({
            url: "/api/jms/settings/queues/" + queue_name,
            type: "PUT",
            data: ko.toJSON(self.SelectedQueue),
            success: function(settings) { 
                settings = JSON.parse(settings);
                self.LoadData(settings);
                
                $.each(self.Settings().Queues(), function(i, queue) {
                    if(queue_name == queue.QueueName()) {
                        self.SelectedQueues.push(queue);
                        return false;
                    }
                });
                
                self.LoadingQueue(false);   
            }, 
            error: function() {
                self.LoadingQueue(false);                
            }
        });
	}
	
	self.DeleteQueue = function() {	    
	    question.Show("Delete queues?", "Are you sure you want to delete the selected queues? This operation is irreversible.", function() {	        
	        question.ToggleLoading(true);
	        
	        $.ajax({
	            url: "/api/jms/settings/queues/" + self.SelectedQueues()[0].QueueName(),
	            type: "DELETE",
	            success: function(settings) { 
	                settings = JSON.parse(settings);
	                self.LoadData(settings);   
	                question.Hide();
	            }, 
	            error: function() {
	                
	            }
	        });
	    });
	}
	
	//node functions
	self.LoadNodes = function(nodes) {
	    self.Nodes([]);
        $.each(nodes, function(i, node) {
            self.Nodes.push(new Node(node.NodeName, node.State, node.NumProcessors, node.Properties));
        });
	}
	
	self.GetNodes = function() {
	    $.ajax({
	        url: "/api/jms/settings/nodes",
	        success: function(nodes) {
	            nodes = JSON.parse(nodes);
	            self.LoadNodes(nodes);
	            
	            self.LoadingNodes(false);
	        }
	    });
	}	
	
	self.ShowAddNode = function() {
        self.LoadingNodes(false);
        self.NewNode(new Node("", null, null, null, null));
	    $("#node-dialog").modal();
	}
	
	self.AddNode = function() {
	    self.LoadingNodes(true);
	    console.log(ko.toJSON(self.NewNode));
	    $.ajax({
            url: "/api/jms/settings/nodes",
            type: "POST",
            data: ko.toJSON(self.NewNode),
            success: function(nodes) { 
                nodes = JSON.parse(nodes);
                self.LoadNodes(nodes);
              
                $("#node-dialog").modal('hide');
                self.LoadingNodes(false);
            }, 
            error: function() {
                self.LoadingNodes(false);
            }
        });
	}
	
	self.EditNode = function() {
	    self.LoadingNodes(true);
	    
	    var node_name = self.SelectedNode().NodeName();
	    
	    $.ajax({
            url: "/api/jms/settings/nodes/" + node_name,
            type: "PUT",
            data: ko.toJSON(self.SelectedNode),
            success: function(nodes) { 
                nodes = JSON.parse(nodes);
                self.LoadNodes(nodes);
                
                $.each(self.Nodes(), function(i, node) {
                    if(node_name == node.NodeName()) {
                        self.SelectedNodes.push(node);
                        return false;
                    }
                });
                
	            self.LoadingNodes(false);
            }, 
            error: function() {
                self.LoadingNodes(false);
            }
        });
	}
	
	self.DeleteNode = function() {
	    question.Show("Delete node?", "Are you sure you want to delete the selected node?", function() {	        
	        question.ToggleLoading(true);
	        
	        $.ajax({
	            url: "/api/jms/settings/nodes/" + self.SelectedNodes()[0].NodeName(),
	            type: "DELETE",
	            success: function(nodes) { 
	                nodes = JSON.parse(nodes);
	                self.LoadNodes(nodes);
	              
	                question.Hide();
	            }, 
	            error: function() {
	                question.ToggleLoading(false);
	            }
	        });
	    });
	}
	
	self.ShowInstructions = function() {
	    $("#instructions-dialog").modal();
	}
}

var question = new QuestionModal("question-dialog");
	
var settings;
$(document).ready(function () {
	$("#settings-menu-item").addClass("active");
	$("#settings-menu-item > a").addClass("active-menu");
	
	settings = new SettingsViewModel();
	ko.applyBindings(settings, document.getElementById("page-wrapper"));
	
	settings.GetServerSettings();	
	settings.GetNodes();
});
