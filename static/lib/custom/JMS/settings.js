var Node = function(name, state, num_cores, busy_cores, num_jobs, other) {
	this.Name = ko.observable(name);
	this.State = ko.observable(state);
	this.NumCores = ko.observable(num_cores);
	this.BusyCores = ko.observable(busy_cores);
	this.FreeCores = ko.observable(num_cores - busy_cores);
	this.Jobs = ko.observable(num_jobs);
	this.Other = ko.observable(other)
}


var Setting = function(key, label, value, value_type, disabled){
    this.Key = ko.observable(key);
	this.Label = ko.observable(label);
	this.Value = ko.observable(value);
	this.ValueType = ko.observable(value_type);
	this.Disabled = ko.observable(disabled);
}
    

var SettingsSection = function(header, settings){
    this.SectionHeader = ko.observable(header);
	this.Settings = ko.observableArray(settings);
}
    

var Administrator = function(admin, sections){
    this.AdministratorName = ko.observable(admin);
	this.SettingsSections = ko.observableArray(sections);
}
    

var Queue = function(queue, sections){
    this.QueueName = ko.observable(queue);
	this.SettingsSections = ko.observableArray(sections);
}



function SettingsViewModel() {
	var self = this;
	
	//Setting types
	self.Text = 1
	self.Number = 2
	self.Checkbox = 3
	self.Label = 4
	self.Option = 5
	
	//Used to switch on/off loading animations
	self.Loading = ko.observable(true);
	self.LoadingServer = ko.observable(false);
	self.LoadingQueue = ko.observable(false);
	self.LoadingAdmins = ko.observable(false);
	self.LoadingNodes = ko.observable(true);
	
	//Actual data objects
	self.Settings = ko.observableArray();
	self.Administrators = ko.observableArray();
	self.Queues = ko.observableArray();
	self.Nodes = ko.observableArray();
	
	//Selected data objects
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
	            self.LoadSettings(settings);
	            self.Loading(false);
	        }
	    });
	}
	
	self.LoadSettings = function(settings){
	    var settings_sections = []
        $.each(settings.DataSections, function(i, section){
            var rs = new SettingsSection(section.SectionHeader, []);
           
            //add fields to sections
            $.each(section.DataFields, function(j, field){
                var s = new Setting(field.Key, field.Label, field.DefaultValue, field.ValueType, field.Disabled);
                
                //add setting values to fields
                $.each(settings.Data, function(k, setting_section){
                    if(setting_section.SectionHeader == section.SectionHeader) {
                        $.each(setting_section.Settings, function(l, setting){
                            if(setting.Name == field.Key){
                                //setting has been found
                                s.Value(setting.Value);
                                return false;
                            }
                        });
                        return false;
                    }  
                });
                rs.Settings.push(s);
            });
            settings_sections.push(rs);
        });
        self.Settings(settings_sections);
	}
	
	self.SaveServerSettings = function() {
	    self.LoadingServer(true);
        
        $.ajax({
            url: "/api/jms/settings",
            type: "POST",
            data: ko.toJSON(self.Settings),
            success: function(settings) {
                settings = JSON.parse(settings);
                self.LoadSettings(settings); 
            },
            error: function(http) {
                alert(http.responseText)
            },
            complete: function() {
	            self.LoadingServer(false);
	        }
        });
	}
	
	//administrator functions	
	self.GetAdministrators = function() {
	    $.ajax({
	        url: "/api/jms/settings/administrators",
	        success: function(admins) {
	            admins = JSON.parse(admins);
	            self.LoadAdministrators(admins);
	            self.Loading(false);
	        }
	    });
	}
	
	self.LoadAdministrators = function(admins) {
	    var administrators = []
        $.each(admins.Data, function(i, admin){
            var administrator = new Administrator(admin.AdministratorName, []);
            
            $.each(admins.DataSections, function(j, section) {
                var ss = new SettingsSection(section.SectionHeader, []);
                
                $.each(section.DataFields, function(j, field){
                    var s = new Setting(field.Key, field.Label, field.DefaultValue, field.ValueType, field.Disabled);
                    
                    //add setting values to fields
                    $.each(admin.SettingsSections, function(k, setting_section){
                        if(setting_section.SectionHeader == section.SectionHeader) {
                            
                            $.each(setting_section.Settings, function(l, setting){
                                if(setting.Name == field.Key){
                                    //setting has been found
                                    s.Value(setting.Value);
                                    return false;
                                }
                            })
                            
                            return false;
                        }  
                    });
                    ss.Settings.push(s);
                });
                administrator.SettingsSections.push(ss)
            });
            administrators.push(administrator);
        })
       
        self.Administrators(administrators);
	}
	
	self.ShowAddAdministrator = function() {
        self.LoadingAdmins(false);
        
	    var a = new Administrator("", []);
	
	    self.SelectedAdministrators([]);	    
	    self.SelectedAdministrator(a);
	    $("#admin-dialog").modal({ 'backdrop': 'static'});
	}	
	
	self.ShowEditAdministrator = function() {
        self.LoadingAdmins(false);
	    $("#admin-dialog").modal({ 'backdrop': 'static'});
	}
	
	self.AddUpdateAdministrator = function() {
	    if (self.SelectedAdministrators().length == 0) {
            self.SaveAdministrators("POST");
        }
        else {
            self.SaveAdministrators("PUT");
        }
	}
	
	self.SaveAdministrators = function(method) {
	    self.LoadingAdmins(true);    
	    
	    $.ajax({
            url: "/api/jms/settings/administrators",
            type: method,
            data: ko.toJSON(self.SelectedAdministrator),
            success: function(admins) { 
                admins = JSON.parse(admins);
                self.LoadAdministrators(admins);  
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
	        
	        admin = self.SelectedAdministrators()[0];
	        
	        $.ajax({
                url: "/api/jms/settings/administrators/" + admin.AdministratorName(),
                type: "DELETE",
                success: function(admins) { 
                    admins = JSON.parse(admins);
                    self.LoadAdministrators(admins);  
    	            question.Hide();
                }, 
                error: function() {
                    self.LoadingAdmins(false); 
    	            question.ToggleLoading(false); 
                }
            });
	    });
	}
    
    //queue functions
    
    self.GetQueues = function(){
        $.ajax({
	        url: "/api/jms/settings/queues",
	        success: function(queues) {
	            queues = JSON.parse(queues);
	            console.log(queues);
	            self.LoadQueues(queues);
	            self.Loading(false);
	        }
	    });
    }
    
    self.LoadQueues = function(qjson) {
	    var queues = []
        $.each(qjson.Data, function(i, queue){
            var q = new Queue(queue.QueueName, []);
            
            $.each(qjson.DataSections, function(j, section) {
                var ss = new SettingsSection(section.SectionHeader, []);
                
                $.each(section.DataFields, function(j, field){
                    var s = new Setting(field.Key, field.Label, field.DefaultValue, field.ValueType, field.Disabled);
                    
                    //add setting values to fields
                    $.each(queue.SettingsSections, function(k, setting_section){
                        if(setting_section.SectionHeader == section.SectionHeader) {
                            $.each(setting_section.Settings, function(l, setting){
                                if(setting.Name == field.Key){
                                    //setting has been found
                                    s.Value(setting.Value);
                                    return false;
                                }
                            })
                            return false;
                        }
                    });
                    ss.Settings.push(s);
                });
                q.SettingsSections.push(ss)
            });
            queues.push(q);
        })
       
        self.Queues(queues);
	}
	
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
            success: function(queues) { 
                queues = JSON.parse(queues);
                self.LoadQueues(queues); 
                
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
            success: function(queues) { 
                queues = JSON.parse(queues);
                self.LoadQueues(queues);
                
                $.each(self.Queues(), function(i, queue) {
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
	            success: function(queues) { 
	                queues = JSON.parse(queues);
	                self.LoadQueues(queues);   
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
            self.Nodes.push(new Node(node.name, node.state, node.num_cores, node.busy_cores, node.jobs, node.other));
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
        self.NewNode(new Node("", null, null, null, null, null));
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
	    var node_name = self.SelectedNode().Name();
	    self.LoadingNodes(true);
	    $.ajax({
            url: "/api/jms/settings/nodes/",
            type: "PUT",
            data: ko.toJSON(self.SelectedNode),
            success: function(nodes) { 
                nodes = JSON.parse(nodes);
                self.LoadNodes(nodes);
                
                $.each(self.Nodes(), function(i, node) {
                    if(node_name == node.Name()) {
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
	            url: "/api/jms/settings/nodes/" + self.SelectedNodes()[0].Name(),
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
	settings.GetAdministrators();
	settings.GetQueues();
	settings.GetNodes();
});
