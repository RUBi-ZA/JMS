var Setting = function(key, label, value, value_type, disabled){
    this.Key = ko.observable(key);
	this.Label = ko.observable(label);
	this.Value = ko.observable(value);
	this.ValueType = ko.observable(value_type);
	this.Disabled = ko.observable(disabled);
	
	this.clone = function() {
	    var copy = new Setting(this.Key(), this.Label(), this.Value(), 
	        this.ValueType(), this.Disabled());
	    return copy;
	}
}
    
var SettingsSection = function(header, settings){
    this.SectionHeader = ko.observable(header);
	this.Settings = ko.observableArray(settings);
}
   
var Queue = function(queue, sections){
    this.QueueName = ko.observable(queue);
	this.SettingsSections = ko.observableArray(sections);
}

var User = function(id, name) {
    this.UserID = ko.observable(id);
    this.Username = ko.observable(name);
    
    this.clone = function() {
        var copy = new User(this.UserID(), this.Username());
        return copy;
    }
}

var Category = function(id, name, tools) {
    this.CategoryID = ko.observable(id);
    this.CategoryName = ko.observable(name);
    this.Tools = ko.observableArray(tools);
    
    this.Visible = ko.observable(false);
}

var Tool = function(id, name, category, description, user, public_ind) {
    this.ToolID = ko.observable(id);
    this.ToolName = ko.observable(name);
    this.Category = ko.observable(category);
    this.ToolDescription = ko.observable(description);
    this.User = ko.observable(user);
    this.PublicInd = ko.observable(public_ind);
    this.ToolVersions = ko.observableArray();
    this.UserToolPermissions = ko.observableArray();
}

var UserToolPermission = function(user, run, edit, publish, exp, admin){
    this.User = ko.observable(user);
    this.Run = ko.observable(run);
    this.Edit = ko.observable(edit);
    this.Publish = ko.observable(publish);
    this.Export = ko.observable(exp);
    this.Admin = ko.observable(admin);
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
    this.DefaultResources = ko.observableArray(resources);
    
    this.Files = ko.observableArray();
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

var ParameterType = function(param_type_id, param_type_name) {
	this.ParameterTypeID = ko.observable(param_type_id);
	this.ParameterTypeName = ko.observable(param_type_name);
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

var FileType = function(id, name) {
    this.FileTypeID = ko.observable(id);
    this.FileTypeName = ko.observable(name);
}

var ExpectedOutput = function(id, label, file, type) {
    this.ExpectedOutputID = ko.observable(id);
    this.OutputName = ko.observable(label);
    this.FileName = ko.observable(file);
    this.FileType = ko.observable(type);
    
    this.DeleteInd = ko.observable(false);
}

var File = function(name) {
    this.FileName = ko.observable(name);
    this.Content = ko.observable(null);
}
    

function ToolViewModel() {
	var self = this;
	
	self.loading_queues = ko.observable(false);
	self.loading = ko.observable(true);
	self.creating_tool = ko.observable(false);
	self.creating_category = ko.observable(false);
	self.creating_parameter = ko.observable(false);
	self.creating_file_type = ko.observable(false);
	
	self.Queues = ko.observableArray();
	self.Queue = ko.observable();
	
	//self.Categories = ko.observableArray();
	
	self.Categories = ko.observableArray();
	self.Tool = ko.observable()
	self.ToolVersion = ko.observable()
	
	self.ToolVersions = ko.observableArray([]);
	
	self.Parameter = ko.observable();
	self.SelectedParameters = ko.observableArray();
	
    self.FileTypes = ko.observableArray();
    
    self.SelectedFile = ko.observable();
    
    self.SelectedFiles = ko.observableArray();
    self.SelectedFiles.subscribe(function(files){
        if(files.length > 0) {
            self.SelectedFile(files[0]);
            self.GetFileContent(files[0]);
        } else {
            self.SelectedFile(null);
        }
    });
	
	self.ParameterTypes = ko.observableArray([
    	new ParameterType(1, "Text"),
    	new ParameterType(2, "Number"),
    	new ParameterType(3, "True/False"),
    	new ParameterType(4, "Options"),
    	new ParameterType(5, "File"),
    	new ParameterType(6, "Complex object"),
    	new ParameterType(7, "Related object")
    ]);
    
    
    self.GetFileTypes = function() {
        $.ajax({
            url: "/api/jms/files/types",
            success: function(types){
                $.each(types, function(i, type){
                    self.FileTypes.push(new FileType(type.FileTypeID, type.FileTypeName));
                });
            }
        });
    }
    
    self.new_file_type = ko.observable();
    self.ShowAddFileType = function() {
        self.new_file_type("");
	    $("#add-file-type-dialog").modal({ 'backdrop': 'static'})
    }
    
    self.AddFileType = function() {
        self.creating_file_type(true);
        
        $.ajax({
            url: "/api/jms/files/types",
            type: "POST",
            data: self.new_file_type(),
            success: function(type){
                self.FileTypes.push(new FileType(type.FileTypeID, type.FileTypeName));
                $("#add-file-type-dialog").modal('hide');
            },
            error: function(http) {
                console.log(http.responseText);
                AppendAlert("danger", "Something went wrong. Check that you have a valid file type name.", "#add-file-type-error");
            },
            complete: function() {
                self.creating_file_type(false);
            }
        });
    }
	
	self.GetQueues = function(){
        $.ajax({
	        url: "/api/jms/settings/queues",
	        success: function(queues) {
	            queues = JSON.parse(queues);
	            self.LoadQueues(queues);
	        }
	    });
    }
    
    self.LoadQueues = function(qjson) {
	    var queues = [];
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
                            });
                            return false;
                        }
                    });
                    ss.Settings.push(s);
                });
                q.SettingsSections.push(ss);
            });
            queues.push(q);
        });
       
        self.Queues(queues);
	}
	
	self.GetCategories = function() {
	    $.ajax({
	        url: "/api/jms/tools/categories",
	        success: function(categories) {
	            self.LoadCategories(categories);
	            self.GetTools();
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
	            
	            if(self.Tool() != null)
    	            self.Tool().Category(category.CategoryID);
	        },
	        error: function(http) {
	            console.log(http.responseText);
	            self.creating_category(false);
	            AppendAlert("danger", "Something went wrong. Check that you have a valid category name.", "#add-category-error");
	        }
	    })
	}
	
	self.DeleteCategory = function(category) {
	    question.Show("Delete tool category?", "Are you sure you want to delete this category? You will not be able to reverse this process.", function() {
			question.ToggleLoading(true);
		    $.ajax({
			    url: "/api/jms/tools/categories/" + category.CategoryID(),
			    type: 'DELETE',
			    success: function(result) {			
				    self.Categories.remove(category);
			        question.Hide();
			    },
			    error: function(http) {
			        console.log(http.responseText);
			        question.ToggleLoading(false);
			        question.ShowError("Something went wrong. Are there tools in this category?")
			    }
		    });
		});	
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
	
	self.GetTools = function() {
	    $.ajax({
	        url: "/api/jms/tools",
	        success: function(tools) {
	            self.LoadTools(tools);
	            self.loading(false);
	        }
	    });
	}
	
	self.NumTools = ko.observable(0);
	self.LoadTools = function(tools) {
	    var num_tools = 0;
	    
	    //loop through tools
	    $.each(tools, function(i, tool) {
            num_tools++;
                
            var t = new Tool(tool.ToolID, tool.ToolName, tool.Category, 
            tool.ToolDescription, null, tool.PublicInd, []);
        
            //loop through each version of tool
            $.each(tool.ToolVersions, function(i, version){
                var v = new ToolVersion(version.ToolVersionID, tool.ToolID, 
                    version.ToolVersionNum, null, null, version.DatePublished);
                
                t.ToolVersions.push(v);
            });
            
            $.each(self.Categories(), function(j, cat){
                if(cat.CategoryID() == tool.Category) {
	                cat.Tools.push(t);
	                return false;
                }
            });
	    });
	        
        self.NumTools(num_tools);
	}
	
	self.ShowAddTool = function() {
	    self.Tool(new Tool(0, "", 1, "", new User(0, '')));
	    $("#tool-dialog").modal({ 'backdrop': 'static'});
	}
	
	self.AddTool = function(data) {
	    self.creating_tool(true);
	    
	    $.ajax({
	        url: "/api/jms/tools",
	        type: "POST",
	        data: ko.toJSON(data),
	        success: function(toolversion){
	            console.log(toolversion);
	            self.GetCategories();
	            
	            self.creating_tool(false);
	            $("#tool-dialog").modal('hide');
	        },
	        error: function(http) {
	            console.log(http.responseText);
	            self.creating_tool(false);
	            AppendAlert("danger", "Something went wrong. Check that you have entered valid data.", "#add-tool-error");
	        }
	    });
	}
	
	self.loading_perms = ko.observable(false);
	self.ShowToolPermissions = function(data) {
	    $("#permissions-dialog").modal({'backdrop':'static'});
	    self.GetToolPermissions(data.ToolID());
	}
	
	self.UpdateToolAvailability = function(data) {
	    console.log(data.PublicInd());
	    var method = "PUT";
	    var message = "Are you sure you want to make this tool available to all users on the system?"
	    if(data.PublicInd() == true) {
	        method = "DELETE"
	        message = "Are you sure you want to make this tool private?"
	    }
	    
	    question.Show("Update availability?", message, function() {
			question.ToggleLoading(true);
		    $.ajax({
			    url: "/api/jms/tools/" + data.ToolID() + "/public",
			    type: method,
			    success: function(tool) {				
				    var t = new Tool(tool.ToolID, tool.ToolName);
                    t.User(new User(tool.User.id, tool.User.username));
                    t.UserToolPermissions([]);
                    t.PublicInd(tool.PublicInd);
                    
                    $.each(tool.UserToolPermissions, function(i, perm){
                        var user = new User(perm.User.id, perm.User.username);
                        var p = new UserToolPermission(user, perm.Run, perm.Edit, 
                            perm.Publish, perm.Export, perm.Admin);
                        
                        t.UserToolPermissions.push(p);
                    });
                    
                    self.Tool(t);
			        question.Hide();
			        
			        
    	            var found = false;
    	            $.each(self.Categories(), function(i, cat) {
    	                $.each(cat.Tools(), function(j, tool) {
    	                    if(tool.ToolID() == t.ToolID()) {
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
			        question.ShowError("Something went wrong while updating the tool.")
			    }
		    });
		});	
	}
	
	self.GetToolPermissions = function(tool_id) {
	    self.loading_perms(true);
	    $.ajax({
	        url: '/api/jms/tools/' + tool_id + '/share',
	        success: function(tool) {
	            var t = new Tool(tool.ToolID, tool.ToolName);
                t.User(new User(tool.User.id, tool.User.username));
	            t.UserToolPermissions([]);
	            t.PublicInd(tool.PublicInd);
	            
	            $.each(tool.UserToolPermissions, function(i, perm){
	                var user = new User(perm.User.id, perm.User.username);
	                var p = new UserToolPermission(user, perm.Run, perm.Edit, 
	                    perm.Publish, perm.Export, perm.Admin);
	                
	                t.UserToolPermissions.push(p);
	            });
	            
	            self.Tool(t);
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
	self.ShowShareTool = function() {
	    self.NewShare(new UserToolPermission(new User(0, ""), true, false, false, false, false))
	    $("#share-dialog").modal({'backdrop':'static'});
	}
	
	self.EditShare = function(data) {
	    self.NewShare(data)
	    $("#share-dialog").modal({'backdrop':'static'});
	}
	
	self.ShareTool = function() {
	    self.sharing(true);
	    
	    var data = new Object();
	    data.Run = self.NewShare().Run();
	    data.Edit = self.NewShare().Edit();
	    data.Export = self.NewShare().Export();
	    data.Publish = self.NewShare().Publish();
	    data.Admin = self.NewShare().Admin();
	    
	    $.ajax({
	        url: "/api/jms/tools/" + self.Tool().ToolID() + "/share/" + self.NewShare().User().Username(),
	        type: "PUT",
	        data: JSON.stringify(data),
	        success: function() {
	            self.GetToolPermissions(self.Tool().ToolID());
	            $("#share-dialog").modal('hide');
	        },
	        error: function() {
	            AppendAlert("danger", "Something went wrong while sharing the tool. Make sure the username you entered is a valid user on the system.", "#share-error");
	        },
	        complete: function() {
	            self.sharing(false);
	        }
	    })
	}
	
	self.UnshareTool = function(data) {
	    self.loading_perms(true);
	    
	    $.ajax({
	        url: "/api/jms/tools/" + self.Tool().ToolID() + "/share/" + data.User().Username(),
	        type: "DELETE",
	        success: function() {
	            self.GetToolPermissions(self.Tool().ToolID());
	        },
	        error: function() {
	            self.loading_perms(false);
	            AppendAlert("danger", "Something went wrong while attempting to remove permissions. If the problem persists, contact an administrator.", "#permissions-error");
	        }
	    })
	    
	}
	
	self.DeleteTool = function(data, parent) {
	    question.Show("Delete tool?", "Are you sure you want to delete this tool? You will not be able to reverse this process.", function() {
			question.ToggleLoading(true);
		    $.ajax({
			    url: "/api/jms/tools/" + data.ToolID(),
			    type: 'DELETE',
			    success: function(result) {				
				    parent.Tools.remove(data);	
			        question.Hide();
			    },
			    error: function() {
			        question.ToggleLoading(false);
			        question.ShowError("Something went wrong. Tool not deleted.")
			    }
		    });
		});	
	}
	
	
	self.RevertVersion = function(data) {
	    question.Show("Revert to version " + data.ToolVersionNum() + "?", "Are you sure you want to revert to version " + data.ToolVersionNum() + 
	        "?<br/><br/>If you continue, any changes you have made to the development version since the last time you published this tool will be lost.", function() {
			question.ToggleLoading(true);
			
		    $.ajax({
			    url: "/api/jms/tools/" + self.ToolVersion().Tool().ToolID() + "/versions",
			    type: 'PUT',
			    data: data.ToolVersionNum(),
			    success: function(v) {	
			        self.GetDevVersion(self.ToolVersion().Tool().ToolID());
				    
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
	
	
	self.major = ko.observable();
	self.minor = ko.observable();
	self.patch = ko.observable();
	self.ShowPublishVersion = function() {
	    //get latest version
	    if(self.ToolVersions().length > 1) {
	        var latest_version = self.ToolVersions()[0];
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
	    question.Show("Publish tool?", "Are you sure you are ready to publish an official version of this tool?", function() {
			question.ToggleLoading(true);
			
			var version = new Object();
			version.Major = self.major();
			version.Minor = self.minor();
			version.Patch = self.patch();
			
		    $.ajax({
			    url: "/api/jms/tools/" + self.ToolVersion().Tool().ToolID() + "/versions",
			    type: 'POST',
			    data: JSON.stringify(version),
			    success: function(v) {				
				    var version = new ToolVersion(v.ToolVersionID, null, 
				        v.ToolVersionNum)
				    
				    self.ToolVersions.unshift(version);
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
    	        url: "/api/jms/tools/" + self.ToolVersion().Tool().ToolID() + "/versions/" + version.ToolVersionNum(),
    	        type: "GET",
    	        success: function(v){
    	            var tool = new Tool(v.Tool.ToolID, v.Tool.ToolName, 
    	                v.Tool.Category);
    	                
    	            version.Tool(tool);
    	            version.ShortDescription(v.ShortDescription)
    	            version.LongDescription(v.LongDescription)
    	            version.DatePublished(v.DatePublished)
    	            
    	            version.ToolParameters(self.LoadParameters(v.ToolParameters))
    	            
    	            version.ExpectedOutputs([]);
    	            $.each(v.ExpectedOutputs, function(i, output){
    	                version.ExpectedOutputs.push(
    	                    new ExpectedOutput(
    	                        output.ExpectedOutputID,
    	                        output.OutputName,
    	                        output.FileName,
    	                        output.FileType
    	                    )    
    	                );
    	            });
    	            
    	            //set the values to the defaults for this specific tool
    	            version.DefaultResources([]);
    	            $.each(v.Resources, function(i, tr){
    	                var r = new Setting(tr.Key, tr.Label, tr.Value, null, null);
    	                version.DefaultResources.push(r)
    	            });
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
	
	self.loading_versions = ko.observable(false);
	self.GetToolVersions = function(tool_id) {
	    self.loading_versions(true);
	    $.ajax({
	        url: "/api/jms/tools/" + tool_id + "/versions",
	        success: function(versions) {
	            self.ToolVersions([]);
	            $.each(versions, function(i, version){
	                console.log(version)
	                self.ToolVersions.push(new ToolVersion(version.ToolVersionID, null, 
	                    version.ToolVersionNum))
	            });
	        }
	    });
	}
	
	self.GetDevVersion = function(tool_id) {
	    $("#loading-dialog").modal({ 'backdrop': 'static'});
	    
	    $.ajax({
	        url: "/api/jms/tools/" + tool_id + "/versions/dev",
	        type: "GET",
	        success: function(v){
	            var tool = new Tool(v.Tool.ToolID, v.Tool.ToolName, 
	                v.Tool.Category);
	                
	            var version = new ToolVersion(v.ToolVersionID, tool, 
	                v.ToolVersionNum, v.ShortDescription, v.LongDescription, 
	                v.DatePublished, v.Command, 
	                self.LoadParameters(v.ToolParameters), [], []
	            );
	            
	            $.each(v.ExpectedOutputs, function(i, output){
	                version.ExpectedOutputs.push(
	                    new ExpectedOutput(
	                        output.ExpectedOutputID,
	                        output.OutputName,
	                        output.FileName,
	                        output.FileType
	                    )    
	                );
	            });
	            
	            //load the default resources for a tool
	            $.each(self.DefaultResources(), function(i, resource) {
	                version.DefaultResources.push(resource.clone());
	            });
	            
	            //set the values to the defaults for this specific tool
	            $.each(v.Resources, function(i, tr){
	                $.each(version.DefaultResources(), function(i, dr){
    	                if(tr.Key == dr.Key()) {
    	                    dr.Value(tr.Value);
    	                    return false;
    	                }
    	            });
	            });
	            
	            self.ToolVersion(version);
	            self.GetFiles(tool_id);
	        },
	        error: function(http) {
	            AppendAlert("danger", "Something went wrong while fetching tool details.", "#edit-tool-error");
	        },
	        complete: function() {
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
	self.GetFiles = function(tool_id) {
	    $.ajax({
	        url: "/api/jms/tools/" + tool_id + "/files",
	        type: "GET",
	        success: function(files){
	            self.ToolVersion().Files([]);
	            $.each(files, function(i, file) {
	                self.ToolVersion().Files.push(new File(file));
	            });
	        },
	        error: function(http) {
	            AppendAlert("danger", "Something went wrong while fetching tool details.", "#edit-tool-error");
	        },
	        complete: function() {
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
	self.GetFileContent = function(file) {
	    var content = file.Content();
	    if(content != null) {
	        $("#ace-editor").val(content);
    	    make_editor($("#ace-editor"));
	    } else {
    	    $.ajax({
    	        url: "/api/jms/tools/" + self.ToolVersion().Tool().ToolID() + "/files/" + file.FileName(),
    	        type: "GET",
    	        success: function(content) {
    	            file.Content(content);
    	            $("#ace-editor").val(content)
    	            make_editor($("#ace-editor"));
    	        }
    	    });
	    }
	}
	
	self.UploadFiles = function() {
		//upload scripts/files
		var files = $('#file_upload').prop('files');
		if(files.length > 0) {	
					
			sendFiles(files, "/api/jms/tools/" + self.ToolVersion().Tool().ToolID() + "/files", "file",
				function(files) {
					self.ToolVersion().Files([]);
					$.each(files, function(i, f) {
						self.ToolVersion().Files.push(new File(f));
					});						
						
					AppendAlert("success", "Files uploaded successfully.", "#upload_alert-container");
				},
				function(message) {
					AppendAlert("danger", message, "#upload_alert-container");
				},
				function() {
					$("#upload_file_btn > i").show();
					$("#upload_file_btn > img").hide();
					$("#upload_file_btn > span").hide();
				},
				function(progress) {
					$("#upload_file_btn > span").text(progress + "%");
				}						
			);	
		}	
	}
	
	self.new_file_name = ko.observable();
	self.creating_file = ko.observable(false);
	self.ShowAddFile = function() {
	    self.new_file_type("");
	    $("#add-file-dialog").modal({ 'backdrop': 'static'});
	}
	
	self.AddFile = function() {
	    self.creating_file(true);
	    var filename = self.new_file_name();
	    $.ajax({
	        url: "/api/jms/tools/" + self.ToolVersion().Tool().ToolID() + "/files/" + filename,
	        type: "POST",
	        success: function() {
	            var f = new File(filename);
	            self.ToolVersion().Files.push(f);
	            self.SelectedFiles([f])
	            $("#add-file-dialog").modal('hide');
	        },
	        error: function(http) {
	            console.log(http.responseText);
	            AppendAlert("danger", http.responseText, "#add-file-error");
	        },
	        complete: function() {
	            self.creating_file(false);
	        }
	    });
	}
	
	self.saving_file = ko.observable(false);
	self.SaveFile = function(file) {
	    self.saving_file(true);
	    $.ajax({
	        url: "/api/jms/tools/" + self.ToolVersion().Tool().ToolID() + "/files",
	        type: "PUT",
	        data: ko.toJSON(file),
	        success: function() { },
	        error: function(http) {
	            console.log(http.responseText);
	            AppendAlert("danger", http.responseText, "#save-file-error");
	        },
	        complete: function() {
	            self.saving_file(false);
	        }
	    });
	}
	
	self.DeleteFile = function() {
	    var f = self.SelectedFile()
	    
	    question.Show("Delete file?", "Are you sure you want to delete this file (" + f.FileName() + ")? You will not be able to reverse this process.", function() {
			question.ToggleLoading(true);
		    $.ajax({
			    url: "/api/jms/tools/" + self.ToolVersion().Tool().ToolID() + "/files/" + f.FileName(),
			    type: 'DELETE',
			    success: function() {	
				    self.SelectedFiles.remove(f);
			        self.ToolVersion().Files.remove(f);
			        question.Hide();
			    },
			    error: function(http) {
			        question.ToggleLoading(false);
			        question.ShowError(http.responseText)
			    }
		    });
		});	
	}
	
	self.GetParameter = function(param_id) {
	    $.ajax({
	        url: "/api/jms/tools/parameters/" + param_id,
	        success: function(parameters) {
	            parameter = self.LoadParameter(parameters);
	            self.Parameter(parameter);
	            
	            $("#loading-dialog").modal('hide');
	        },
	        error: function(http) {
	            console.log(http.responseText);
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
	
	self.LoadParameters = function(parameters) {
	    params = []
	    
	    //load parameters
	    $.each(parameters, function(i, param){
    	    
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
    		    if(param.ParameterType == 7) {
        			var related = self.FindParameter(params, param.Value);
        			p.related_parameter(related);
    		    }
    		    
    		    //find parent parameter and add this parameter as a child
    			var parent = self.FindParameter(params, param.ParentParameter);
    		    parent.parameters.push(p);
    	    }
	    });
	    
	    return params;
	}
	
	self.AddParameter = function(version) {
	    $("#loading-dialog").modal({ 'backdrop': 'static'});
	    
	    $.ajax({
	        url: "/api/jms/tools/" + version.Tool().ToolID() + "/parameters",
	        type: "POST",
	        data: "New Parameter",
	        success: function(param) {
	            var p = self.LoadParameters([param])[0];
                
                self.ToolVersion().ToolParameters.push(p);
	            self.SelectedParameters([p]);
	            
	            $("#loading-dialog").modal('hide');
	        },
	        error: function(http) {
	            console.log(http.responseText);
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
	self.DeleteParameter = function(){
	    $("#loading-dialog").modal({ 'backdrop': 'static'});
	    
	    var parameter = self.SelectedParameters()[0];
	    
	    $.ajax({
	        url: "/api/jms/parameters/" + parameter.ParameterID(),
	        type: "DELETE",
	        success: function(param) {
	            self.SelectedParameters.remove(parameter)
	            self.ToolVersion().ToolParameters.remove(parameter);
	            
	            $("#loading-dialog").modal('hide');
	        },
	        error: function(http) {
	            console.log(http.responseText);
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
	self.AddSubParameter = function(parameters, parent_id) {
	    parameters.push(new Parameter(null, "", "", "user", 1, false, "", null, null, parent_id, false));		
	}
	
	self.DeleteSubParameter = function(parameters, data) {
	    if(data.ParameterID() == null) {
		    parameters.remove(data);
	    } else {
	        data.DeleteInd(true);
	    }
	}
	
	self.AddParameterOption = function() {
		self.SelectedParameters()[0].ParameterOptions.push(new ParameterOption(0, "", ""));
	}
	
	self.DeleteParameterOption = function(data) {
	    if(data.ParameterOptionID() == 0) {
		    self.SelectedParameters()[0].ParameterOptions.remove(data);
	    } else {
	        data.DeleteInd(true);
	    }
	}
	
	self.CreateParameterObject = function(param) {
		var p = new Object();
		p.ParameterID = param.ParameterID();
		p.ParameterName = param.ParameterName();
		p.Context = param.Context();
		p.InputBy = param.InputBy();
		p.ParameterType = param.Type();
		p.Multiple = param.Multiple();
		p.Optional = param.OptionalInd();
		p.Value = param.Value();
		p.Delimiter = param.Delimiter();	
		p.ParentParameterID = param.ParentParameterID();
		p.DeleteInd = param.DeleteInd();
			
		p.ParameterOptions = [];
		$.each(param.ParameterOptions(), function(i, option) {
			//create parameter option to be serialized
			var o = new Object();
			o.ParameterOptionID = option.ParameterOptionID();
			o.ParameterOptionText = option.ParameterOptionText();
			o.ParameterOptionValue = option.ParameterOptionValue();
			o.DeleteInd = option.DeleteInd();
			
			p.ParameterOptions.push(o);
		});
		
		//create sub-parameters
		p.parameters = []		
		$.each(param.parameters(), function(i, sub_param) {
			p.parameters.push(self.CreateParameterObject(sub_param));
		});
		
		return p;
	}
	
	self.AddExpectedOutput = function() {
	    self.ToolVersion().ExpectedOutputs.push(
	        new ExpectedOutput(null, "", "", 1)
	    );
	}
	
	self.DeleteExpectedOutput = function(data) {
	    if(data.ExpectedOutputID() == null) {
	        self.ToolVersion().ExpectedOutputs.remove(data);
	    } else {
	        data.DeleteInd(true);
	    }
	}
	
	self.UpdateTool = function() {
	    $("#loading-dialog").modal({ 'backdrop': 'static'});
	    
	    //create version object to be serialized
		var v = new Object();
		v.ToolVersionID = self.ToolVersion().ToolVersionID();
		v.Command = self.ToolVersion().Command();
		v.ShortDescription = self.ToolVersion().ShortDescription();
		v.LongDescription = self.ToolVersion().LongDescription();
		
		v.Tool = new Object();
		v.Tool.ToolName = self.ToolVersion().Tool().ToolName();
		v.Tool.CategoryID = self.ToolVersion().Tool().Category();
		
		v.ExpectedOutputs = [];
		
		$.each(self.ToolVersion().ExpectedOutputs(), function(j, output) {
			//create output object to be serialized
			var o = new Object();
			o.ExpectedOutputID = output.ExpectedOutputID()
			o.OutputName = output.OutputName();
			o.FileName = output.FileName();
			o.FileTypeID = output.FileType();
			o.DeleteInd = output.DeleteInd();
			
			v.ExpectedOutputs.push(o);
		});
		
		v.Parameters = [];
		
		$.each(self.ToolVersion().ToolParameters(), function(j, param) {
			//create parameter object to be serialized
			var p = self.CreateParameterObject(param);
			v.Parameters.push(p);
		});
		
		v.Resources = [];
		
		$.each(self.ToolVersion().DefaultResources(), function(j, resource) {
		    var r = new Object();
		    r.Key = resource.Key();
		    r.Value = resource.Value();
		    r.Label = resource.Label();
		    
		    v.Resources.push(r);
		});
		
		data = JSON.stringify(v);
		
		$.ajax({
		    url: "/api/jms/tools/" + self.ToolVersion().Tool().ToolID(),
		    type: "PUT",
		    data: data,
		    success: function() {
		        $("#loading-dialog").modal('hide');
		    },
		    error: function(http) {
		        AppendAlert("danger", http.responseText, "#edit-tool-error");
		        $("#loading-dialog").modal('hide');
		    }
		});
	}
	
	self.DefaultResources = ko.observableArray();
	self.GetDefaultResources = function() {
	    $.ajax({
	        url: "/api/jms/settings/resources",
	        success: function(section) {
	            section = JSON.parse(section);
	            
	            self.LoadResources(section.DataFields);
	        }
	    });
	}
	
	self.LoadResources = function(resources) {
	    var r = [];
	    $.each(resources, function(i, resource) {
	        var s = new Setting(resource.Key, resource.Label, 
	            resource.DefaultValue, resource.ValueType, resource.Disabled);
	        //alert(resource.Key);
	        r.push(s);
	    });
	        
	    console.log(r);
	    
	    self.DefaultResources(r);
	}
	
	self.ObjectMode = ko.observable();
	self.ClonedParameter = ko.observable();
	self.NewObjects = ko.observableArray();
	self.AddComplexObject = function(data) {
	    self.Parameter(data);
		self.ClonedParameter(data.clone());
		
		console.log(data.related_parameter())
		
		self.NewObjects.push(data);
		var len = self.NewObjects().length;		
		
		self.ObjectMode("add");
		
		$("#object-dialog-" + String(len - 1)).modal();
		$('#object-dialog-' + String(len - 1)).on('hidden.bs.modal', function () {
			self.NewObjects.pop();
			var len = self.NewObjects().length;
			
			if(len > 0) {
				self.Parameter(self.NewObjects()[len-1]);
				self.ClonedParameter(self.NewObjects()[len-1].clone());
			} else {
				self.Parameter(new Parameter());
			}
		}) 
	}
	
	self.SaveComplexObject = function(param) {
		var complex_object = new ComplexObject(param.clone());
		self.Parameter().complex_objects.push(complex_object);
		
		var len = self.NewObjects().length;
		$("#object-dialog-" + String(len - 1)).modal('hide');
	}
	
	self.EditComplexObject = function(param) {
		self.NewObjects.push(param.selected_parameters()[0].Parameter());
		var len = self.NewObjects().length;
		
		self.ClonedParameter(param.selected_parameters()[0].Parameter());
		
		self.ObjectMode("edit");
		
		$("#object-dialog-" + String(len - 1)).modal();
		$('#object-dialog-' + String(len - 1)).on('hidden.bs.modal', function () {
			self.NewObjects.pop();
			var len = self.NewObjects().length;
			
			if(len > 0) {
				self.Parameter(self.NewObjects()[len-1]);
				self.ClonedParameter(self.NewObjects()[len-1].clone());
			} else {
				self.Parameter(new Parameter());
			}
		}) 
	}
	
	self.DeleteComplexObject = function(param) {
		$.each(param.selected_parameters(), function(i, p) {
			param.complex_objects.remove(p);
		});
	}
	
	self.AddValue = function(data) {
		data.value_items.push(new ValueItem("", data));
	}
	
	self.RemoveValue = function(parent, data) {
		parent.value_items.remove(data);
	}
	
    self.job_id = ko.observable();
    self.submitting = ko.observable(false);
    self.submit_success = ko.observable(true);
	self.RunCustomJob = function() {
	    var form = $("form#custom-job");
	    
	    try 
        {
            $("#submit-dialog").modal({ backdrop: "static"});
            
    		tool.submitting(true);
    		
    		var formData = new FormData(form[0]);
		    formData.append('Settings', ko.toJSON(tool.DefaultResources));
    		
    		$.ajax({
    		    url: "/api/jms/jobs/custom",
    		    type: "POST",
    		    data: formData,
    		    success: function(id) {
    		        //Set the job ID so that the "Go to Job" button works
    		        self.job_id(id);
    		        
    		        tool.submit_success(true);
    		    }, 
    		    error: function() {
    		        tool.submit_success(false);
    		    },
    		    complete: function() {
    		        tool.submitting(false);
    		    },
                cache: false,
                contentType: false,
                processData: false
    		});
    		
        } catch(err) {
            tool.submit_success(false);
    		tool.submitting(false);
            console.log(err);   
        }
	}
	
	self.tool_job_name = ko.observable()
	self.tool_job_desc = ko.observable()
	self.RunTool = function() {
	    var form = $("form#tool-form");
	    
	    try 
        {
            $("#submit-dialog").modal({ backdrop: "static"});
            
    		tool.submitting(true);
    		
    		var formData = new FormData(form[0]);
    		
    		var Parameters = []
    		$.each(self.ToolVersion().ToolParameters(), function(i, p) {
    		    if(p.InputBy() == "user" && p.ParentParameterID() == null) {
				    var param = new Object();
				    param.ParameterID = p.ParameterID();
					    
    		        if(p.Type() == 5) {				
					    var temp_files = $('input[name="param_' + p.ParameterID() + '"]').prop('files');
						param.Value = "";
					    $.each(temp_files, function(k, f) {
						    param.Value += f.name + ",";
					    });
					    param.Value = param.Value.substring(0, param.Value.length - 1);
    		        } else if(p.Type() == 6) {
					    param.Value = p.get_JSON();
					    console.log(param.Value);
				    } else if(p.Type() == 7) {
					    param.Value = p.related_parameter().get_JSON();					
				    } else {
					    param.Value = p.Value();
				    }
        		    
        		    Parameters.push(param);
    		    }
    		});
    		
    		formData.append('JobName', tool.tool_job_name());
    		formData.append('Description', tool.tool_job_desc());
		    formData.append('Parameters', JSON.stringify(Parameters));
    		
    		$.ajax({
    		    url: "/api/jms/jobs/tool/versions/" + tool.ToolVersion().ToolVersionID(),
    		    type: "POST",
    		    data: formData,
    		    success: function(id) {
    		        //Set the job ID so that the "Go to Job" button works
    		        self.job_id(id);
    		        
    		        tool.submit_success(true);
    		    }, 
    		    error: function() {
    		        tool.submit_success(false);
    		    },
    		    complete: function() {
    		        tool.submitting(false);
    		    },
                cache: false,
                contentType: false,
                processData: false
    		});
    		
        } catch(err) {
            tool.submit_success(false);
    		tool.submitting(false);
            console.log(err);   
        }
	}
	
	
	self.ShowImportTool = function() {
	    alert("clicked");
	}
	
	self.selected_version = ko.observable();
	self.selected_version.subscribe(function(version){
	    console.log(version)
	    if(self.ToolVersion() != null && version != self.ToolVersion().ToolVersionNum()) {
	        self.GetVersion(self.ToolVersion().Tool().ToolID(), version);
	    }
	})
	
	self.GetVersion = function(tool_id, version) {
	    $("#loading-dialog").modal({ 'backdrop': 'static'});
	    
	    $.ajax({
	        url: "/api/jms/tools/" + tool_id + "/versions/" + version,
	        type: "GET",
	        success: function(v){
	            var tool = new Tool(v.Tool.ToolID, v.Tool.ToolName, 
	                v.Tool.Category);
	            
	            $.each(v.Tool.ToolVersions, function(i, version) {
	                tool.ToolVersions.push(new ToolVersion(version.ToolVersionID, 
	                    tool, version.ToolVersionNum)
	                );
	            })
	            
	            var version = new ToolVersion(v.ToolVersionID, tool, 
	                v.ToolVersionNum, v.ShortDescription, v.LongDescription, 
	                v.DatePublished, v.Command, 
	                self.LoadParameters(v.ToolParameters), [], []
	            );
	            
	            $.each(v.ExpectedOutputs, function(i, output){
	                version.ExpectedOutputs.push(
	                    new ExpectedOutput(
	                        output.ExpectedOutputID,
	                        output.OutputName,
	                        output.FileName,
	                        output.FileType
	                    )    
	                );
	            });
	            
	            //load the default resources for a tool
	            $.each(self.DefaultResources(), function(i, resource) {
	                version.DefaultResources.push(resource.clone());
	            });
	            
	            //set the values to the defaults for this specific tool
	            $.each(v.Resources, function(i, tr){
	                $.each(version.DefaultResources(), function(i, dr){
    	                if(tr.Key == dr.Key()) {
    	                    dr.Value(tr.Value);
    	                    return false;
    	                }
    	            });
	            });
	            
	            self.ToolVersion(version);
	        },
	        error: function(http) {
	            AppendAlert("danger", "Something went wrong while fetching tool details.", "#run-tool-error");
	        },
	        complete: function() {
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
}

var make_editor = function(textarea) {      
    var modelist = ace.require('ace/ext/modelist');
    mode = modelist.getModeForPath(tool.SelectedFile().FileName()).mode;
    
    var langauge_tools = ace.require("ace/ext/language_tools");
    
    var editDiv = $('<div>', {
        position: 'absolute',
        width: $("#page").width(),
        height: "650px",
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
        tool.SelectedFile().Content(content);
    });
} 

var tool;
var question = new QuestionModal("question-dialog");

$(document).ready(function () {
	$("#tool-menu-item").addClass("active");
	$("#tool-menu-item > a").addClass("active-menu");	
	
	tool = new ToolViewModel();
	ko.applyBindings(tool, document.getElementById("tools"));
	
	tool.GetCategories();
	tool.GetDefaultResources();
	tool.GetFileTypes();
	
	$(window).bind('keydown', function(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (String.fromCharCode(event.which).toLowerCase()) {
                case 's':
                    event.preventDefault();
                    
                    tool.SaveFile(tool.SelectedFile());
                        
                    break;
            }
        }
    });
	
	// initialize the application
	var app = Sammy(function() {

		// define a 'route'
		this.get('#run/:tool', function() {
		    $("#tools-list").fadeOut(200);
		    $("#tool-editor").fadeOut(200);
		    $("#custom-job").fadeOut(200);
		    setTimeout(function() {
		        $("#tool-runner").fadeIn();	
		    }, 300);
		    
		    tool.GetVersion(this.params.tool, "latest");
		});
		
		this.get('#edit/:tool', function() {
		    $("#tools-list").fadeOut(200);
		    $("#tool-runner").fadeOut(200);
		    $("#custom-job").fadeOut(200);
		    setTimeout(function() {
		        $("#tool-editor").fadeIn();	
		    }, 300);
		    tool.GetDevVersion(this.params.tool);
		    tool.GetToolVersions(this.params.tool);
		});
		
		this.get('#custom', function() {
		    $("#tools-list").fadeOut(200);
		    $("#tool-runner").fadeOut(200);
		    $("#tool-editor").fadeOut(200);
		    setTimeout(function() {
		        $("#custom-job").fadeIn();	
		    }, 300);
		});
		
		this.get('/tools/', function() {
		    $("#tool-runner").fadeOut(200);
		    $("#tool-editor").fadeOut(200);
		    $("#custom-job").fadeOut(200);
		    $("#loading-dialog").modal('hide')
		    
		    setTimeout(function() {
		        $("#tools-list").fadeIn();	
		    }, 300);
		});
	});

	// start the application
	app.run('/tools/#');
});