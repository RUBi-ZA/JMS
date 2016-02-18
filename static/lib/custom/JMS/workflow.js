var Tool = function(id, name, category, description, user, public_ind) {
    this.ToolID = ko.observable(id);
    this.ToolName = ko.observable(name);
    this.Category = ko.observable(category);
    this.ToolDescription = ko.observable(description);
    this.User = ko.observable(user);
    this.PublicInd = ko.observable(public_ind);
    this.ToolVersions = ko.observableArray();
}

var ToolVersion = function(id, tool, version, short_desc, long_desc, date, command, params, outputs, resources) {
    this.ToolVersionID = ko.observable(id);
    this.Tool = ko.observable(tool);
    this.ToolVersionNum = ko.observable(version);
    this.ShortDescription = ko.observable(short_desc);
    this.LongDescription = ko.observable(long_desc);
    this.DatePublished = ko.observable(date);
    this.Command = ko.observable(command);
    this.ToolParameters = ko.observableArray(params);
    this.ExpectedOutputs = ko.observableArray(outputs);
}

var Parameter = function(param_id, name, context, input_by, type, multiple, value, options, delimiter, parent_id, optional) {
	var self = this;
		
	this.ParameterID = ko.observable(param_id);
	this.ParameterName = ko.observable(name);
	this.Context = ko.observable(context);
	this.InputBy = ko.observable(input_by);
	this.Type = ko.observable(type);
	this.Multiple = ko.observable(multiple);
	this.Value = ko.observable(value);
	this.ParameterOptions = ko.observableArray(options);
	this.Delimiter = ko.observable(delimiter);	
	this.ParameterIndex = ko.observable();
	this.ParentParameterID = ko.observable();
	if(parent_id != null) {
		this.ParentParameterID(parent_id);
	}
	this.OptionalInd = ko.observable(optional);
	
	this.DeleteInd = ko.observable(false);
	
	//if parameter type is "Text" or "Number"
	this.value_items = ko.observableArray([new ValueItem("", self)]);
	
	//if parameter type is "Options"
	this.selected_values = ko.observableArray([]);
	this.selected_values.subscribe(function(values) {	
		var value = "";		
		$.each(values, function(i, val) {
			if(i > 0) {
				value += self.Delimiter();
			}
			value += val;
		});
		self.Value($.trim(value));
	});
	
	//if parameter type is "Complex object"
	this.parameters = ko.observableArray(null);
	this.complex_objects = ko.observableArray(null);
	this.selected_parameters = ko.observableArray();
	
	//if parameter type is "Related object"
	this.related_parameter = ko.observable();
	this.related_objects = ko.observableArray();
	
	this.clone = function() {
		var copy = new Parameter(this.ParameterID(), this.ParameterName(), this.Context(), this.InputBy(), this.Type(), 
			this.Multiple(), this.Value(), [], this.Delimiter(), this.ParentParameterID(), this.OptionalInd());
		
		
		$.each(this.ParameterOptions(), function(i, option) {
			copy.ParameterOptions.push(option.clone());
		});
		
		$.each(this.parameters(), function(i, param) {
			copy.parameters.push(param.clone());
		});
		
		$.each(this.complex_objects(), function(i, obj) {
			copy.complex_objects.push(obj.clone());
		});
		
		copy.related_parameter(this.related_parameter());
		
		$.each(this.related_objects(), function(i, obj) {
			copy.related_objects.push(obj);
		});
		
		return copy;
	}
	
	this.get_JSON = function() {
		json = "{ " + this.get_complex_objects_JSON() + " }";
		return json;
	}
	
	this.get_complex_objects_JSON = function() {
		var json = "";
		if(this.Type() == 6) {
			if(this.Multiple()) {
				$.each(this.complex_objects(), function(i, obj) {
					var obj_json = obj.get_complex_object_JSON();
				
					if(i > 0) {
						json += ", ";
					}
					json += "{ " + obj_json + " }";
				});		
			
				json = '"' + this.ParameterName() + '": [ ' + json + ' ]';	
			} else {
				var param_json = '';
				$.each(this.parameters(), function(i, param) {
					if(i > 0) {
						param_json += ", ";
					}
					param_json += param.get_complex_objects_JSON();
				});

				json += '"' + this.ParameterName() + '": { ' + param_json + ' }';
			}
		} else if(this.Type() == 7) {
			if(this.Multiple()) {
				$.each(this.related_objects(), function(i, obj) {
					var obj_json = obj.get_complex_object_JSON();

					if(i > 0) {
						json += ", ";
					}
					json += "{ " + obj_json + " }";
				});	
				json = '"' + this.ParameterName() + '": [ ' + json + ' ]';	
			} else {
				json = '"' + this.ParameterName() + '": { ' + this.related_objects().get_complex_object_JSON() + ' }';
			}			
		} else {	
				
			json += '"' + this.ParameterName() + '": "' + this.Value() + '"';			
		}
		
		return json;
	}
}

var ParameterOption = function(param_option_id, option_text, option_value) {
	this.ParameterOptionID = ko.observable(param_option_id);
	this.ParameterOptionText = ko.observable(option_text);
	this.ParameterOptionValue = ko.observable(option_value);
	this.DeleteInd = ko.observable(false);
	
	this.clone = function() {
		var copy = new ParameterOption(this.ParameterOptionID(), 
		    this.ParameterOptionText(), this.ParameterOptionValue());
		
		return copy;
	}
}

var ComplexObject = function(parameter) {
	this.Parameter = ko.observable(parameter);
	
	this.clone = function() {
		var copy = new ComplexObject(this.Parameter());
		return copy;
	}
	
	this.get_complex_object_JSON = function() {
		var json = "";
		$.each(this.Parameter().parameters(), function(i, param) {
			if(i>0) {
				json += ", "
			}
			json += param.get_complex_objects_JSON();
		});
		return json;
	}
}

var ValueItem = function(value, parent) {
	this.value = ko.observable(value);
	this.value.subscribe(function() {	
		var value = "";		
		$.each(parent.value_items(), function(i, val) {
			if(i > 0) {
				value += parent.Delimiter();
			}
			console.log(val);
			value += val.value();
		});
		parent.Value($.trim(value));
	});
}

var ExpectedOutput = function(id, label, file, type) {
    this.ExpectedOutputID = ko.observable(id);
    this.OutputName = ko.observable(label);
    this.FileName = ko.observable(file);
    this.FileType = ko.observable(type);
    
    this.DeleteInd = ko.observable(false);
}

var User = function(id, name) {
    this.UserID = ko.observable(id);
    this.Username = ko.observable(name);
    
    this.clone = function() {
        var copy = new User(this.UserID(), this.Username());
        return copy;
    }
}

var Category = function(id, name, workflows) {
    this.CategoryID = ko.observable(id);
    this.CategoryName = ko.observable(name);
    this.Workflows = ko.observableArray(workflows);
    
    this.Visible = ko.observable(false);
}

var Workflow = function(id, name, category, description, user, public_ind) {
    this.WorkflowID = ko.observable(id);
    this.WorkflowName = ko.observable(name);
    this.Category = ko.observable(category);
    this.Description = ko.observable(description);
    this.User = ko.observable(user);
    this.PublicInd = ko.observable(public_ind);
    
    this.WorkflowVersions = ko.observableArray();
    this.UserWorkflowPermissions = ko.observableArray();
}

var UserWorkflowPermission = function(user, run, edit, publish, exp, admin){
    this.User = ko.observable(user);
    this.Run = ko.observable(run);
    this.Edit = ko.observable(edit);
    this.Publish = ko.observable(publish);
    this.Export = ko.observable(exp);
    this.Admin = ko.observable(admin);
}

var WorkflowVersion = function(id, workflow, version, short_desc, long_desc, date, stages) {
    this.WorkflowVersionID = ko.observable(id);
    this.Workflow = ko.observable(workflow);
    this.WorkflowVersionNum = ko.observable(version);
    this.ShortDescription = ko.observable(short_desc);
    this.LongDescription = ko.observable(long_desc);
    this.DatePublished = ko.observable(date);
    
    this.Stages = ko.observableArray(stages);
}    

var Stage = function(id, tool) {
    this.StageID = ko.observable(id);
    this.ToolVersion = ko.observable(tool);
}


function WorkflowViewModel() {
    var self = this;
    
    self.loading = ko.observable(true);
    
    self.Categories = ko.observableArray();
    
    self.GetCategories = function() {
	    $.ajax({
	        url: "/api/jms/tools/categories",
	        success: function(categories) {
	            self.LoadCategories(categories);
	            self.GetWorkflows();
	        }
	    });
	}
	
	self.LoadCategories = function(categories) {
	    self.Categories([]);
	    $.each(categories, function(i, category){
	        self.Categories.push(new Category(category.CategoryID, 
	            category.CategoryName));
	    });
	}
	
	self.new_category_name = ko.observable();
	self.ShowAddCategory = function() {
	    self.new_category_name("");
	    $("#add-category-dialog").modal({ 'backdrop': 'static'})
	}
	
	self.creating_category = ko.observable(false);
	self.AddCategory = function() {
	    self.creating_category(true);
	    
	    $.ajax({
	        url: "/api/jms/tools/categories",
	        type: "POST",
	        data: self.new_category_name(),
	        success: function(category){
	            var cat = new Category(category.CategoryID, category.CategoryName);
	            self.Categories.push(cat);
	            $("#add-category-dialog").modal('hide');
	            self.creating_category(false);
	            if(self.Workflow() != null) {
	                self.Workflow().Category(category.CategoryID);
	            }
	        },
	        error: function(http) {
	            console.log(http.responseText);
	            self.creating_category(false);
	            AppendAlert("danger", "Something went wrong. Check that you have a valid category name.", "#add-category-error");
	        }
	    })
	}
	
	self.Category = ko.observable();
	self.ShowUpdateCategory = function(category) {
	    self.Category(category);
	    self.new_category_name(category.CategoryName());
	    
	    $("#edit-category-dialog").modal({ 'backdrop': 'static'})
	}
	
	self.UpdateCategory = function(category) {
	    self.creating_category(true);
	    
	    $.ajax({
	        url: "/api/jms/tools/categories/" + category.CategoryID(),
	        type: "PUT",
	        data: self.new_category_name(),
	        success: function(category){
	            $("#edit-category-dialog").modal('hide');
	            self.creating_category(false);
	            self.Category().CategoryName(self.new_category_name());
	        },
	        error: function(http) {
	            console.log(http.responseText);
	            self.creating_category(false);
	            AppendAlert("danger", "Something went wrong. Check that you have a valid category name.", "#edit-category-error");
	        }
	    })
	}
	
	self.ToggleVisible = function(category) {
	    $("#category_" + category.CategoryID()).slideToggle();
	    category.Visible(!category.Visible());
	}
	
	self.GetWorkflows = function() {
	    $.ajax({
	        url: "/api/jms/workflows",
	        success: function(workflows) {
	            self.LoadWorkflows(workflows);
	            self.loading(false);
	        }
	    });
	}
	
	self.NumWorkflows = ko.observable(0);
	self.LoadWorkflows = function(workflows) {
	    var num_workflows = 0;
	    
	    //loop through tools
	    $.each(workflows, function(i, workflow) {
            num_workflows++;
                
            var t = new Workflow(workflow.WorkflowID, workflow.WorkflowName, workflow.Category, 
                workflow.Description, null, workflow.PublicInd, []);
        
            //loop through each version of tool
            $.each(workflow.WorkflowVersions, function(i, version){
                var v = new WorkflowVersion(version.WorkflowVersionID, workflow.WorkflowID, 
                    version.WorkflowVersionNum, version.ShortDescription, null/*, version.DatePublished*/);
                
                t.WorkflowVersions.push(v);
            });
            
            $.each(self.Categories(), function(j, cat){
                if(cat.CategoryID() == workflow.Category) {
	                cat.Workflows.push(t);
	                return false;
                }
            });
	    });
	        
        self.NumWorkflows(num_workflows);
	}
	
	self.Workflow = ko.observable(null);
	self.ShowAddWorkflow = function() {
	    self.Workflow(new Workflow(0, "", 1, "", new User(0, '')));
	    $("#workflow-dialog").modal({ 'backdrop': 'static'});
	}
	
	self.creating_workflow = ko.observable(false);
	self.AddWorkflow = function(data) {
	    self.creating_workflow(true);
	    
	    $.ajax({
	        url: "/api/jms/workflows",
	        type: "POST",
	        data: ko.toJSON(data),
	        success: function(version){
	            self.GetCategories();
	            
	            $("#workflow-dialog").modal('hide');
	        },
	        error: function(http) {
	            console.log(http.responseText);
	            AppendAlert("danger", "Something went wrong. Check that you have entered valid data.", "#add-workflow-error");
	        },
	        complete: function() {
	            self.creating_workflow(false);
	        }
	    });
	}
	
	self.UpdateWorkflow = function(version) {
	    $("#loading-dialog").modal({ 'backdrop': 'static'});
	    
	    var data = Object();
	    data.WorkflowName = version.Workflow().WorkflowName();
	    data.Category = version.Workflow().Category();
	    data.ShortDescription = version.ShortDescription();
	    data.LongDescription = version.LongDescription();
	    
	    $.ajax({
		    url: "/api/jms/workflows/" + self.WorkflowVersion().Workflow().WorkflowID(),
		    type: "PUT",
		    data: JSON.stringify(data),
		    success: function() {
		        $("#loading-dialog").modal('hide');
		    },
		    error: function(http) {
		        AppendAlert("danger", http.responseText, "#edit-workflow-error-error");
		        $("#loading-dialog").modal('hide');
		    }
		});
	}
	
	self.DeleteWorkflow = function(data, parent) {
	    question.Show("Delete workflow?", "Are you sure you want to delete this workflow? You will not be able to reverse this process.", function() {
			question.ToggleLoading(true);
		    $.ajax({
			    url: "/api/jms/workflows/" + data.WorkflowID(),
			    type: 'DELETE',
			    success: function(result) {				
				    parent.Workflows.remove(data);
				    self.NumWorkflows(self.NumWorkflows()-1);
			        question.Hide();
			    },
			    error: function() {
			        question.ToggleLoading(false);
			        question.ShowError("Something went wrong. Workflow not deleted.")
			    }
		    });
		});	
	}
	
	self.loading_perms = ko.observable(false);
	self.ShowWorkflowPermissions = function(data) {
	    $("#permissions-dialog").modal({'backdrop':'static'});
	    self.GetWorkflowPermissions(data.WorkflowID());
	}
	
	self.UpdateWorkflowAvailability = function(data) {
	    
	    var method = "PUT";
	    var message = "Are you sure you want to make this workflow available to all users on the system?"
	    if(data.PublicInd() == true) {
	        method = "DELETE"
	        message = "Are you sure you want to make this workflow private?"
	    }
	    
	    question.Show("Update availability?", message, function() {
			question.ToggleLoading(true);
		    $.ajax({
			    url: "/api/jms/workflows/" + data.WorkflowID() + "/public",
			    type: method,
			    success: function(tool) {				
				    var t = new Workflow(tool.WorkflowID, tool.WorkflowName);
                    t.User(new User(tool.User.id, tool.User.username));
                    t.UserWorkflowPermissions([]);
                    t.PublicInd(tool.PublicInd);
                    
                    $.each(tool.UserWorkflowPermissions, function(i, perm){
                        var user = new User(perm.User.id, perm.User.username);
                        var p = new UserWorkflowPermission(user, perm.Run, perm.Edit, 
                            perm.Publish, perm.Export, perm.Admin);
                        
                        t.UserWorkflowPermissions.push(p);
                    });
                    
                    self.Workflow(t);
			        question.Hide();
			        
    	            var found = false;
    	            $.each(self.Categories(), function(i, cat) {
    	                $.each(cat.Workflows(), function(j, tool) {
    	                    if(tool.WorkflowID() == t.WorkflowID()) {
    	                        found = true;
    	                        tool.PublicInd(t.PublicInd())
    	                        return false;
    	                    }
    	                });
    	                
    	                if(found) {
    	                    return false;
    	                }
    	            });
			    },
			    error: function() {
			        question.ToggleLoading(false);
			        question.ShowError("Something went wrong while updating the workflow.")
			    }
		    });
		});	
	}
	
	self.GetWorkflowPermissions = function(workflow_id) {
	    self.loading_perms(true);
	    $.ajax({
	        url: '/api/jms/workflows/' + workflow_id + '/share',
	        success: function(tool) {
	            var t = new Workflow(tool.WorkflowID, tool.WorkflowName);
                t.User(new User(tool.User.id, tool.User.username));
	            t.UserWorkflowPermissions([]);
	            t.PublicInd(tool.PublicInd);
	            
	            $.each(tool.UserWorkflowPermissions, function(i, perm){
	                var user = new User(perm.User.id, perm.User.username);
	                var p = new UserWorkflowPermission(user, perm.Run, perm.Edit, 
	                    perm.Publish, perm.Export, perm.Admin);
	                
	                t.UserWorkflowPermissions.push(p);
	            });
	            
	            self.Workflow(t);
	        },
	        error: function() {
	            $("#permissions-dialog").modal('hide');
	        },
	        complete: function() {
	            self.loading_perms(false);
	        }
	    });
	}
	
	self.sharing = ko.observable(false);
	self.NewShare = ko.observable();
	self.ShowShareWorkflow = function() {
	    self.NewShare(new UserWorkflowPermission(new User(0, ""), true, false, false, false, false))
	    $("#share-dialog").modal({'backdrop':'static'});
	}
	
	self.EditShare = function(data) {
	    self.NewShare(data)
	    $("#share-dialog").modal({'backdrop':'static'});
	}
	
	self.ShareWorkflow = function() {
	    self.sharing(true);
	    
	    var data = new Object();
	    data.Run = self.NewShare().Run();
	    data.Edit = self.NewShare().Edit();
	    data.Export = self.NewShare().Export();
	    data.Publish = self.NewShare().Publish();
	    data.Admin = self.NewShare().Admin();
	    
	    $.ajax({
	        url: "/api/jms/workflows/" + self.Workflow().WorkflowID() + "/share/" + self.NewShare().User().Username(),
	        type: "PUT",
	        data: JSON.stringify(data),
	        success: function() {
	            self.GetWorkflowPermissions(self.Workflow().WorkflowID());
	            $("#share-dialog").modal('hide');
	        },
	        error: function() {
	            AppendAlert("danger", "Something went wrong while sharing the workflow. Make sure the username you entered is a valid user on the system.", "#share-error");
	        },
	        complete: function() {
	            self.sharing(false);
	        }
	    })
	}
	
	self.UnshareWorkflow = function(data) {
	    self.loading_perms(true);
	    
	    $.ajax({
	        url: "/api/jms/workflows/" + self.Workflow().WorkflowID() + "/share/" + data.User().Username(),
	        type: "DELETE",
	        success: function() {
	            self.GetWorkflowPermissions(self.Workflow().WorkflowID());
	        },
	        error: function() {
	            self.loading_perms(false);
	            AppendAlert("danger", "Something went wrong while attempting to remove permissions. If the problem persists, contact an administrator.", "#permissions-error");
	        }
	    })
	    
	}
	
	self.GetVersion = function(workflow_id, version) { 
	    $("#loading-dialog").modal({ 'backdrop': 'static'});
	    
	    $.ajax({
	        url: "/api/jms/workflows/" + workflow_id + "/versions/" + version,
	        type: "GET",
	        success: function(v){
	            
	            var workflow = new Workflow(v.Workflow.WorkflowID, 
	                v.Workflow.WorkflowName, v.Workflow.Category);
	            
	            workflow.WorkflowVersions([]);
	            $.each(v.Workflow.WorkflowVersions, function(i, version) {
	                workflow.WorkflowVersions.push(
	                    new WorkflowVersion(version.WorkflowVersionID, workflow, 
	                        version.WorkflowVersionNum
	                    )
	                );
	            });
	           
	            
	            
	            var version = new WorkflowVersion(v.WorkflowVersionID, workflow, 
	                v.WorkflowVersionNum, v.ShortDescription, v.LongDescription, 
	                v.DatePublished
	            );
	            
	            $.each(v.WorkflowVersionStages, function(i, stage) {
	                var tool = new Tool(stage.ToolVersion.Tool.ToolID, 
	                    stage.ToolVersion.Tool.ToolName, 
	                    stage.ToolVersion.Tool.Category
	                );
	                    
	                var toolversion = new ToolVersion(
	                    stage.ToolVersion.ToolVersionID, tool, 
    	                stage.ToolVersion.ToolVersionNum, 
    	                stage.ToolVersion.ShortDescription, 
    	                stage.ToolVersion.LongDescription, 
    	                stage.ToolVersion.DatePublished, 
    	                stage.ToolVersion.Command, 
    	                self.LoadParameters(stage.ToolVersion.ToolParameters, stage.StageParameters), 
    	                [], []
    	            );
    	            
    	            var s = new Stage(stage.StageID, toolversion);
    	            version.Stages.push(s);
	            });
	            
	            self.WorkflowVersion(version);
	        },
	        error: function(http) {
	            AppendAlert("danger", "Something went wrong while fetching tool details.", "#edit-workflow-error");
	        },
	        complete: function() {
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
	self.FindParameter = function(params, parent_id) {
		p = false;
		$.each(params, function(i, param) {
			if(param.ParameterID() == parent_id) {	
				p = param;		
				return false;
			} else {
				p = self.FindParameter(param.parameters(), parent_id);
				if(p != false) {
					return false;
				}
			}
		});
		return p;
	}
	
	self.LoadParameters = function(parameters, stage_params) {
	    params = []
	    
	    //load parameters
	    $.each(parameters, function(i, param){
	        
	        //set flag to true if the workflow will automatically populate a field
	        var flag = false;
	        $.each(stage_params, function(j, stage_param) {
	            if(param.ParameterID == stage_param.Parameter){
	                flag = true;
	                return false;
	            }
	        })
	        
    	    if(param.InputBy == "user" && !flag) {
        	    if(param.ParentParameter == null) {
        	        //this is a parent parameter
        	        
        		    //add parameter
        		    var parameter = new Parameter(param.ParameterID, param.ParameterName, param.Context, param.InputBy, param.ParameterType, 
        			    param.Multiple, param.Value, [], param.Delimiter, null, param.Optional);
        	
            	    //add parameter options
            	    $.each(param.ParameterOptions, function(l, option) {
            		    parameter.ParameterOptions.push(
            		        new ParameterOption(
                		        option.ParameterOptionID, option.ParameterOptionText, 
                		        option.ParameterOptionValue
                		    )
                		);
            	    });
            	    
            	    params.push(parameter);
        	    } else {
        	        //this is a child parameter
        	        					
        		    var p = new Parameter(param.ParameterID, param.ParameterName, param.Context, param.InputBy, param.ParameterType, 
        			    param.Multiple, param.Value, [], param.Delimiter, param.ParentParameter, param.Optional)
        			
        			//if the parameter is a related object, find the related parameter
        		    if(param.ParameterType == 8) {
            			var related = self.FindParameter(params, param.Value);
            			p.related_parameter(related);
        		    }
        		    
        		    //find parent parameter and add this parameter as a child
        			var parent = self.FindParameter(params, param.ParentParameter);
        		    parent.parameters.push(p);
        	    }
    	    }
	    });
	    
	    return params;
	}
	
	
	self.WorkflowVersion = ko.observable();
	self.GetDevVersion = function(workflow_id) { 
	    self.GetVersion(workflow_id, "dev");
	}
	
	
	self.major = ko.observable();
	self.minor = ko.observable();
	self.patch = ko.observable();
	self.ShowPublishVersion = function() {
	    //get latest version
	    var versions = self.WorkflowVersion().Workflow().WorkflowVersions();
	    if(versions.length > 1) {
	        var latest_version = versions()[0];
	        version_nums = latest_version.ToolVersionNum().split(".");
	        self.major(version_nums[0]);
        	self.minor(version_nums[1]);
        	self.patch(Number(version_nums[2]) + 1);
	        
	    } else {
	        self.major(0);
        	self.minor(1);
        	self.patch(0);
	    }
	    
	    $("#publish-dialog").modal();
	}
	
	
	self.PublishVersion = function() {
	    question.Show("Publish workflow?", "Are you sure you are ready to publish an official version of this workflow?", function() {
			question.ToggleLoading(true);
			
			var versions = self.WorkflowVersion().Workflow().WorkflowVersions();
			
			var version = new Object();
			version.Major = self.major();
			version.Minor = self.minor();
			version.Patch = self.patch();
			
		    $.ajax({
			    url: "/api/jms/workflows/" + self.WorkflowVersion().Workflow().WorkflowID() + "/versions",
			    type: 'POST',
			    data: JSON.stringify(version),
			    success: function(v) {				
				    var version = new WorkflowlVersion(v.WorkflowVersionID, 
				        self.WorkflowVersion().Workflow(), v.WorkflowVersionNum)
				    
				    versions.unshift(version);
				    self.SelectedVersions([version]);
				    
	                $("#publish-dialog").modal('hide');
			        question.Hide();
			    },
			    error: function() {
			        question.ShowError("Something went wrong. Tool not deleted.")
			    }, complete: function() {
			        question.ToggleLoading(false);
			    }
		    });
		});	
	}
	
	
	self.SelectedVersion = ko.observable();
	self.SelectedVersion.subscribe(function(version){
	    if(version != null) {
	        $.ajax({
    	        url: "/api/jms/workflows/" + self.WorkflowVersion().Workflow().WorkflowID() + "/versions/" + version.WorkflowVersionNum(),
    	        type: "GET",
    	        success: function(v){
    	            var workflow = new Workflow(v.Workflow.WorkflowID, 
	                v.Workflow.WorkflowName, v.Workflow.Category);
    	                
    	            version.Workflow(workflow);
    	            version.ShortDescription(v.ShortDescription);
    	            version.LongDescription(v.LongDescription);
    	            version.DatePublished(v.DatePublished);
    	        },
    	        error: function(http) {
    	            AppendAlert("danger", "Something went wrong while fetching tool details.", "#version-tool-error");
    	        },
    	        complete: function() {
    	        }
    	    });
	    }
	});
	
	self.SelectedVersions = ko.observableArray();
	self.SelectedVersions.subscribe(function(versions){
	    if(versions.length > 0){
	        self.SelectedVersion(versions[0]);
	    } else {
	        self.SelectedVersion(null);
	    }
	});
	
	self.job_id = ko.observable();
	self.loading_stages = ko.observable(false);
	self.workflow_job_name = ko.observable();
	self.workflow_job_desc = ko.observable();
	self.submitting = ko.observable(false);
	self.submit_success = ko.observable(false);
	self.RunWorkflow = function() {
	    var form = $("form#workflow-form");
	    
	    try 
        {
            $("#submit-dialog").modal({ backdrop: "static"});
            
    		self.submitting(true);
    		
    		var formData = new FormData(form[0]);
    		
    		var Stages = [];
    		
    		$.each(self.WorkflowVersion().Stages(), function(i, stage){
    		    var s = new Object();
    		    s.StageID = stage.StageID();
        		s.Parameters = []
        		
        		$.each(stage.ToolVersion().ToolParameters(), function(i, p) {
        		    if(p.InputBy() == "user") {
        		        
            		    var param = new Object();
            		    param.ParameterID = p.ParameterID();
            		    
            		    if(p.Type() == 5) {
                		    var temp_files = $('#param_' + p.ParameterID()).prop('files');
    						param.Value = "";
    					    $.each(temp_files, function(k, f) {
    						    param.Value += f.name + ",";
    					    });
					        param.Value = param.Value.substring(0, param.Value.length - 1);
            		    }
            		    else {
            		        param.Value = p.Value();
            		    }
            		    
            		    s.Parameters.push(param);
        		    }
        		});
        		
        		Stages.push(s);
    		});
    		
    		formData.append('JobName', self.workflow_job_name());
    		formData.append('Description', self.workflow_job_desc());
		    formData.append('Stages', JSON.stringify(Stages));
    		
    		$.ajax({
    		    url: "/api/jms/jobs/workflow/versions/" + self.WorkflowVersion().WorkflowVersionID(),
    		    type: "POST",
    		    data: formData,
    		    success: function(id) {
    		        //Set the job ID so that the "Go to Job" button works
    		        self.job_id(id);
    		        
    		        self.submit_success(true);
    		    }, 
    		    error: function() {
    		        self.submit_success(false);
    		    },
    		    complete: function() {
    		        self.submitting(false);
    		    },
                cache: false,
                contentType: false,
                processData: false
    		});
    		
        } catch(err) {
            self.submit_success(false);
    		self.submitting(false);
            console.log(err);   
        }
	}
}



var workflow;
var question = new QuestionModal("question-dialog");

$(document).ready(function () {
	$("#workflow-menu-item").addClass("active");
	$("#workflow-menu-item > a").addClass("active-menu");	
	
	workflow = new WorkflowViewModel();
	ko.applyBindings(workflow, document.getElementById("workflows"));
	
	workflow.GetCategories();
	
	// initialize the application
	var app = Sammy(function() {

		// define a 'route'
		this.get('#run/:workflow', function() {
		    $("#workflow-list").fadeOut(200);
		    $("#workflow-editor").fadeOut(200);
		    setTimeout(function() {
		        $("#workflow-runner").fadeIn();	
		    }, 300);
		    
		    workflow.GetVersion(this.params.workflow, "latest");
		});
		
		this.get('#edit/:workflow', function() {
		    $("#workflow-list").fadeOut(200);
		    $("#workflow-runner").fadeOut(200);
		    setTimeout(function() {
		        $("#workflow-editor").fadeIn();	
		    }, 300);
		    
		    workflow.GetDevVersion(this.params.workflow);
		    workflow.GetWorkflowVersions(this.params.workflow);
		});
		
		this.get('/workflows/', function() {
		    $("#workflow-runner").fadeOut(200);
		    $("#workflow-editor").fadeOut(200);
		    setTimeout(function() {
		        $("#workflow-list").fadeIn();	
		    }, 300);
		});
	});

	// start the application
	app.run('/workflows/#');
});



