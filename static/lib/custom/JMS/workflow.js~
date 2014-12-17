ko.observableArray.fn.insertAt = function(index, value) {
    this.valueWillMutate();
    this.splice(index, 0, value);
    this.valueHasMutated();
}

ko.observableArray.fn.swap = function(index1, index2) {
	this.valueWillMutate();
	
	var temp = this()[index1];
	this()[index1] = this()[index2];
	this()[index2] = temp;
	
    this.valueHasMutated();
}

var Job = function(job_id, job_name, description, wf) {
	this.JobID = ko.observable(job_id);
	this.JobName = ko.observable(job_name);
	this.Description = ko.observable(description);
	this.Workflow = ko.observable(wf);
	
	this.InputProfile = ko.observable();
	this.InputProfile.subscribe(function(value) {
	    if(value.InputProfileID() > 0){
	        workflow.InputProfileName(value.InputProfileName());
    	    workflow.GetInputProfile();
    	} else {
    	    workflow.InputProfileName("");
    	}
	});
	
	this.JobType = ko.observable(1);
	
	this.clone = function() {
		var copy = new Job(this.JobID(), this.JobName(), this.Description(), this.Workflow().clone());
		return copy();
	}
}

var Workflow = function(workflow_id, workflow_name, description, stages, publicInd) {
	var self = this;
	
	self.WorkflowID = ko.observable(workflow_id);
	self.WorkflowName = ko.observable(workflow_name);
	self.Description = ko.observable(description);
	
    self.Accessibility = ko.observable();
    self.PublicInd = ko.observable();    
    self.PublicInd.subscribe(function(value) {
        if(value) {
            self.Accessibility("Public");
        } else {
    	    self.Accessibility("Private");
    	}
	});
	self.PublicInd(publicInd);
	self.UserAccessRights = ko.observableArray();
	self.GroupAccessRights = ko.observableArray();
	
	self.InputProfiles = ko.observableArray();
	
	self.Stages = ko.observableArray(stages);
	
	self.files = ko.observableArray();
	self.clone = function() {
		var copy = new Workflow(self.WorkflowID(), self.WorkflowName(), self.Description(), [], self.PublicInd());
		$.each(self.Stages(), function(i, stage) {
			copy.Stages.push(stage.clone());
		});
		
		return copy;
	}
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

var UserWorkflowAccessRight = function(user, access_right) {
    self = this;
    
    self.User = ko.observable(user);
    self.AccessRight = ko.observable(access_right);
    
    this.clone = function() {
        var copy = new UserWorkflowAccessRight(this.User().clone(), this.AccessRight().clone());
        return copy;
    }
}

var GroupWorkflowAccessRight = function(group, access_right) {
    self = this;
    
    self.Group = ko.observable(group);
    self.AccessRight = ko.observable(access_right);
    
    this.clone = function() {
        var copy = new GroupWorkflowAccessRight(self.Group().clone(), self.AccessRight.clone());
        return copy;
    }
}

var ScriptFile = function(file_name) {
	this.FileName = ko.observable(file_name);	
	this.Content = ko.observable();
	this.ExistsOnServer = ko.observable(true);
}

var InputProfile = function(id, name, description) {
    this.InputProfileID = ko.observable(id);
    this.InputProfileName = ko.observable(name);
    this.Description = ko.observable(description);
    
    this.clone = function() {
        var copy = new InputProfile(this.InputProfileID(), this.InputProfileName(), this.Description(), []);
        
        return copy;
    }
}

var Stage = function(stage_id, stage_name, dependencies, type, scripts, command, parameters, outputs, queue, nodes, cores, memory, walltime) {
	this.StageID = ko.observable(stage_id);
	this.StageName = ko.observable(stage_name);    
	this.StageDependencies = ko.observableArray(dependencies);
	this.StageType = ko.observable(type);
	this.Scripts = ko.observableArray(scripts);
	this.Command = ko.observable(command);			
	this.Parameters = ko.observableArray(parameters);
	this.ExpectedOutputs = ko.observableArray(outputs);
	this.RequiresEdit = ko.observable(false);
	this.StageIndex = ko.observable();
	
	//default resources
	this.Queue = ko.observable(queue);
	this.Nodes = ko.observable(nodes);
	this.MaxCores = ko.observable(cores);
	this.Memory = ko.observable(memory);
	this.Walltime = ko.observable(walltime);
	
	this.available = ko.observable(false);
	this.clone = function() {
		var copy = new Stage(this.StageID(), this.StageName(), [], this.StageType(), [], this.Command(), [], [], this.Queue(), this.Nodes(). this.MaxCores(), this.Memory(), this.Walltime());
		
		$.each(this.StageDependencies(), function(i, dep) {
			copy.StageDependencies.push(dep.clone());
		});
		
		$.each(this.Scripts(), function(i, script) {
			copy.ReferencedScripts.push(script);
		});
		
		$.each(this.Parameters(), function(i, params) {
			copy.Parameters.push(params.clone());
		});
		
		$.each(this.ExpectedOutputs(), function(i, output) {
			copy.ExpectedOutputs.push(output.clone());
		});
		
		return copy;
	}
}

var StageType = function(type_id, type_name) {
	this.StageTypeID = ko.observable(type_id);
	this.StageTypeName = ko.observable(type_name);
}

var StageDependency = function(stage_id, condition_id, value) {
	this.StageID = ko.observable(stage_id);
	this.ConditionID = ko.observable(condition_id);
	this.Value = ko.observable(value);
	
	this.StageName = ko.computed(function() {
		self = this;
		
		if(workflow != null) {
			var name = "n/a";
			$.each(workflow.Workflow().Stages(), function(i, stage) {
				if(stage.StageID() == self.StageID()) {
					name = stage.StageName();
					return false
				}
			});
			
			return name;
		}
			
		return self.StageID;		
	}, this);
	
	this.editing = ko.observable(false);
	
	this.clone = function() {
		var copy = new StageDependency(this.StageID(), this.ConditionID(), this.Value());		
		return copy;
	}
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
	this.Optional = ko.observable(optional);
	
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
			this.Multiple(), this.Value(), [], this.Delimiter(), this.ParentParameterID(), this.Optional());
		
		
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
		if(this.Type() == 7) {
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
		} else if(this.Type() == 8) {
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
	
	this.clone = function() {
		var copy = new ParameterOption(this.ParameterOptionID(), this.ParameterOptionText(), this.ParameterOptionValue());
		
		return copy;
	}
}

var ExpectedOutput = function(output_id, name) {
	this.ExpectedOutputID = ko.observable(output_id);
	this.ExpectedOutputFileName = ko.observable(name);
	
	this.clone = function() {
		var copy = new ExpectedOutput(this.ExpectedOutputID(), this.ExpectedOutputFileName());
		
		return copy;
	}
}

/*=============================
  WorkflowViewModel
===============================*/
function WorkflowViewModel() {
	var self = this;
	
	//Data
	self.Workflows = ko.observableArray();	
    
    //Interface
    self.VisibleWindow = ko.observable("workflows");
    self.ObjectMode = ko.observable();
	self.Loading = ko.observable(true);   
	self.Importing = ko.observable(false);
	
	self.Submitting = ko.observable(true);
	self.SubmitStatus = ko.observable(0);
	self.SubmitSuccess = ko.observable();
	self.SubmitMessage = ko.observable("");
    
    //Filters			
	self.WorkflowFilter = ko.observable("");
    
    //Utilities
    self.ParameterTypes = ko.observableArray([
    	new ParameterType(1, "Text"),
    	new ParameterType(2, "Number"),
    	new ParameterType(3, "True/False"),
    	new ParameterType(4, "Options"),
    	new ParameterType(5, "File"),
    	new ParameterType(6, "Parameter value from previous stage"),
    	new ParameterType(7, "Complex object"),
    	new ParameterType(8, "Related object")
    ]);
    
    self.StageTypes = ko.observableArray([
    	new StageType(1, "Comand-line utility"),
    	new StageType(2, "Custom script")
    ]);
    
    self.AccessRights = ko.observableArray([
    	new AccessRight(2, "Admin"),
    	new AccessRight(3, "View & Use"),
    	new AccessRight(4, "View"),
    ]);
    
    self.PreviousParameters = ko.observableArray([]);
    self.PreviousObjects = ko.observableArray([]);
    
	self.StageSeed = 1; 
	self.ParameterSeed = 1;
        
	//Selected items
	self.Job = ko.observable(new Job(-1, "", "", new Workflow(-1, "", "", null, false)));	
	self.Workflow = ko.observable(new Workflow(-1, "", "", null, false));	
	self.Stage = ko.observable(new Stage(-1, "", null, "", null, "", [], []));    
    self.StageDependency = ko.observable(new StageDependency());
    
	self.SelectedDependencies = ko.observableArray();	
	self.SelectedDependencies.subscribe(function(value) {
		if(value.length > 0) {
			self.StageDependency(value[0]);
		}
    });
    
    self.ClonedParameter = ko.observable(new Parameter(1, "", "", "user", 1, false, "", null));
    self.Parameter = ko.observable(new Parameter(1, "", "", "user", 1, false, "", null));
    self.Parameter.subscribe(function() {    	
    	var params = [];
    	var objs = [];
    	$.each(self.Workflow().Stages(), function(i, stage) {
    		if(stage.StageID() > self.Stage().StageID()) {
    			return false;
    		}
    		
    		$.each(stage.Parameters(), function(j, param) {
    			if(stage.StageID() < self.Stage().StageID()) {
    				params.push(param);
    			}
    			
    			if(param.Type() == 7) {
    				objs.push(param);	
    			} 
    		});
    	});
    	self.PreviousParameters(params);
    	self.PreviousObjects(objs);
    });
    
	self.SelectedStages = ko.observableArray();	
	self.SelectedStages.subscribe(function(value) {
		if(value.length > 0) {
			self.SelectedFiles([]);
			self.Stage(value[0]);
			$('input[name="type"]').val([self.Stage().StageType()]);
			
			var val = true;
			$.each(self.Workflow().Stages(), function(i, stage) {
				if(stage.StageID() == self.Stage().StageID()) 
					val = false;
				
				stage.available(val);
			});
		}
    });
    
    self.File = ko.observable(null);    
    self.SelectedFiles = ko.observableArray();	
    self.SelectedFiles.subscribe(function(value) {
		if(value.length > 0) {
			self.SelectedStages([]);
			self.File(value[0]);
			
			if(value[0].ExistsOnServer()) {
				self.GetWorkflowFileContent(value[0]);
			} else {
			    make_editor();
			}
		}
    });
    
    
	self.UserAccessRight = ko.observable(null);	
	
	self.InputProfileName = ko.observable("");
	self.InputProfileDescription = ko.observable("");
	self.InputProfileLoading = ko.observable(false);
    
    
    //Functions   
	self.LoadData = function() {
		self.Workflows([]);
		
		$.ajax({
			url: '/api/jms/workflows',
			success: function(data) {
				$.each(data, function(i, wf) {
					//add workflow
					self.Workflows.push(self.LoadWorkflowObservable(wf));					
				});
				self.Loading(false);
			},
			error: function() {
				self.Loading(false);			
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
	
	self.LoadWorkflowObservable = function(wf) {
		var workflow = new Workflow(wf.WorkflowID, wf.WorkflowName, wf.Description, [], wf.PublicInd);
	    
	    if(typeof wf.Stages != "undefined") {		
		    //add workflow stages
		    $.each(wf.Stages, function(j, stage) {
			    workflow.Stages.insertAt(stage.StageIndex -1, new Stage(stage.StageID, stage.StageName, [], stage.StageType, null, stage.Command, null, null, stage.Queue, stage.Nodes, stage.MaxCores, stage.Memory, stage.Walltime));
			    self.StageSeed = stage.StageID + 1;
												
			    //add stage dependencies
			    $.each(stage.StageDependencies, function(k, dep) {
				    $.each(workflow.Stages(), function(l, s) {
					    if(dep.DependantOn == s.StageID()) {
						    workflow.Stages()[j].StageDependencies.push(new StageDependency(s.StageID(), dep.Condition, dep.ExitCodeValue));
					    }
				    });							
			    });						
					
			    //add stage parameters
			    $.each(stage.Parameters, function(k, param) {
				    if(param.ParentParameter == null) {
					    //add parameter to root parameters
					    workflow.Stages()[j].Parameters.push(new Parameter(param.ParameterID, param.ParameterName, param.Context, param.InputBy, param.ParameterType, 
						    param.Multiple, param.Value, [], param.Delimiter, null, param.Optional));
				    } else {
					    //else find parent parameter and add this parameter as a child					
					    var p = new Parameter(param.ParameterID, param.ParameterName, param.Context, param.InputBy, param.ParameterType, 
						    param.Multiple, param.Value, [], param.Delimiter, param.ParentParameter, param.Optional)
											
					    var parent = self.FindParameter(workflow.Stages()[j].Parameters(), param.ParentParameter);
					    if(param.ParameterType == 8) {
						    related = self.FindParameter(workflow.Stages()[j].Parameters(), param.Value);
						    //console.log(parent.ParameterName() + " - " + p.ParameterName() + " - " + related.ParameterName());
						    p.related_parameter(related);
					    }
					
					    parent.parameters.push(p);
				    }
				    self.ParameterSeed = param.ParameterID + 1;
				
				    //add parameter options
				    $.each(param.ParameterOptions, function(l, option) {
					    workflow.Stages()[j].Parameters()[k].ParameterOptions.push(new ParameterOption(option.ParameterOptionID, 
						    option.ParameterOptionText, option.ParameterOptionValue));
				    });
			    });
			
			    //add expected outputs
			    $.each(stage.ExpectedOutputs, function(k, output) {
				    workflow.Stages()[j].ExpectedOutputs.push(new ExpectedOutput(output.ExpectedOutputID, output.ExpectedOutputFileName));
			    });
			
		    });
		}
		
		//add workflow input profiles
		if(typeof wf.InputProfiles != "undefined") {   
		    workflow.InputProfiles.push(new InputProfile(0, "None", []));
		     
		    $.each(wf.InputProfiles, function(i, profile) {
		        workflow.InputProfiles.push(new InputProfile(profile.InputProfileID, profile.InputProfileName, profile.Description, []));
		    });
		}
		
		return workflow;
	}
	
	self.GetInputProfile = function() {
	    profile_id = self.Job().InputProfile().InputProfileID();
	    if(profile_id > 0) {
	        $.ajax({
	            url: "/api/jms/inputprofiles/" + profile_id,
	            success: function(profile) {
	                var complex_params = {}
	                $.each(profile.InputProfileParameters, function(i, input_param) {
	                    $.each(self.Job().Workflow().Stages(), function(j, stage) {
	                        if(stage.StageID() == input_param.Parameter.Stage) {
    	                        var parameter = self.FindParameter(stage.Parameters(), input_param.Parameter.ParameterID);
    	                        if(parameter != false) {
        	                        switch(parameter.Type()) {
            	                        case 1:
            	                        case 2:
            	                        case 3:
            	                        case 4:
            	                            if(parameter.Multiple()) {
            	                                parameter.value_items([]);
            	                                var values = input_param.Value.split(parameter.Delimiter());
            	                                $.each(values, function(k, value) {
            	                                    parameter.value_items.push(new ValueItem(value, parameter));
            	                                });
            	                            } else {
                	                            parameter.Value(input_param.Value);
                	                        }
                	                        break;
            	                        case 5:
            	                            //Not yet implemented
            	                            break;
            	                        case 6:
            	                            //Not yet implemented
            	                            break;
            	                        case 7:
            	                            //Not yet implemented
            	                            break;
            	                        case 8:
            	                            //Not yet implemented
            	                            break;
        	                        }
        	                    }
    	                    }
	                    });
	                });
	            }
	        });
	    }
	}
	
	self.ClearInput = function() {
	
	}
	
	self.SaveInputProfile = function() {
	    if(self.Job().InputProfile().InputProfileID() == 0) {
	        self.ShowCreateInputProfile();
	    } else {
	        question.Show(
	            "Overwrite input profile?", 
	            "Would you like to overwrite the input profile, '" + self.Job().InputProfile().InputProfileName() + "'?", 
	            self.UpdateInputProfile, 
	            function() {
	                question.Hide();
	                self.ShowCreateInputProfile();
	            }
	        );
	    }
	}
	
	self.ShowCreateInputProfile = function() {
	    $("#input-profile-dialog").modal();
	}
	
	self.CreateInputProfile = function() {
	    self.InputProfileLoading(true);
	
	    var profile = self.DetermineInputProfile();
	    data = JSON.stringify(profile);
	    
	    $.ajax({
	        url: "/api/jms/inputprofiles",
	        type: "POST",
	        data: data,
	        success: function(id) {
	            self.Job().Workflow().InputProfiles.push(new InputProfile(id, profile.InputProfileName, []));
	            $("#input-profile-dialog").modal('hide');
	        },
	        error: function() {
	        
	        },
	        complete: function() {
	            self.InputProfileLoading(false);
	        }
	    });
	    
	}
	
	self.UpdateInputProfile = function() {
	    question.ToggleLoading(true);
	    
	    var profile = self.DetermineInputProfile();
	    data = JSON.stringify(profile);
	    
	    $.ajax({
	        url: "/api/jms/inputprofiles/" + profile.InputProfileID,
	        type: "PUT",
	        data: data,
	        success: function() {
	            question.Hide();
	        },
	        error: function() {
	        },
	        complete: function() {
	            question.ToggleLoading(false);
	        }
	    });
	}
	
	self.DetermineInputProfile = function() {
	    try {
	        var profile = new Object();
	        profile.InputProfileID = self.Job().InputProfile().InputProfileID();
	        profile.InputProfileName = self.InputProfileName();
	        profile.Description = self.InputProfileDescription();
	        profile.WorkflowID = self.Job().Workflow().WorkflowID();
	        profile.InputProfileParameters = new Array();
		
			var files = [];
		
			$.each(self.Job().Workflow().Stages(), function(i, s) {
			
				$.each(s.Parameters(), function(j, p) {
				    if(p.Type() == 5) {				
						var temp_files = $('input[name="param_' + p.ParameterID() + '"]').prop('files');
						$.each(temp_files, function(k, f) {
							var param = new Object();
							param.ParameterID = p.ParameterID();
							param.Value = f.name;
				
							profile.InputProfileParameters.push(param);
						});
					
						files.push({ value: "param_" + p.ParameterID(), files: temp_files});
					} else if(p.Type() == 7 || p.Type() == 8) {
						var param = new Object();
						param.ParameterID = p.ParameterID();
						param.Value = p.get_JSON();
						param.Type = p.Type();
				
						profile.InputProfileParameters.push(param); 					
					} else {
						var param = new Object();
						param.ParameterID = p.ParameterID();
						param.Value = p.Value();
						param.Type = p.Type();
				
						profile.InputProfileParameters.push(param);
					}
				});			
			});	    
	    
	        return profile;
	        
	    } catch(err) {
			self.InputProfileLoading(false);
		}
	}
	
	self.FilterWorkflow = function(workflow) {
		if(self.WorkflowFilter().length > 0) {
			if(workflow.WorkflowName().toLowerCase().indexOf(self.WorkflowFilter().toLowerCase()) >= 0) {
			   	return true;
		    } else if (workflow.Description().toLowerCase().indexOf(self.WorkflowFilter().toLowerCase()) >= 0) {
			   	return true;
		    }
		    
		    return false;
        }                
        return true;
	}
	
	self.AddWorkflow = function() {
		self.StageSeed = 1;
		self.ParameterSeed = 1;
		
		self.Workflow(new Workflow(-1, "", "", null, false));
		self.Stage(new Stage(-1, "", null, "", null, "", [], []));
		self.ShowCreateWorkflow();
	}
	
	self.DetermineParameterIndices = function(params) {
		$.each(params, function(i, param) {
			param.ParameterIndex(i+1);
			
			self.DetermineParameterIndices(param.parameters());
		});
	}
	
	self.CreateParameterObject = function(param) {
		var p = new Object();
		p.ParameterID = param.ParameterID();
		p.ParameterName = param.ParameterName();
		p.Context = param.Context();
		p.InputBy = param.InputBy();
		p.Type = param.Type();
		p.Multiple = param.Multiple();
		p.Optional = param.Optional();
		p.Value = param.Value();
		p.Delimiter = param.Delimiter();	
		p.ParameterIndex = param.ParameterIndex();
		p.ParentParameterID = param.ParentParameterID();
			
		p.ParameterOptions = [];
		$.each(param.ParameterOptions(), function(i, option) {
			//create parameter option to be serialized
			var o = new Object();
			o.ParameterOptionID = option.ParameterOptionID();
			o.ParameterOptionText = option.ParameterOptionText();
			o.ParameterOptionValue = option.ParameterOptionValue();
			
			p.ParameterOptions.push(o);
		});
		
		//create sub-parameters
		p.parameters = []		
		$.each(param.parameters(), function(i, sub_param) {
			p.parameters.push(self.CreateParameterObject(sub_param));
		});
		
		return p;
	}
	
	self.GetWorkflow = function(workflow) {
	    $.ajax({
	        url: "/api/jms/workflows/" + workflow.WorkflowID(),
	        success: function(wf) {
	            self.Workflow(self.LoadWorkflowObservable(wf));
		        self.GetWorkflowFiles();
	            self.Loading(false);
	        },
	        error: function() {
	            self.VisibleWindow("workflows");
	            self.Loading(false);
	        }
	    });
	}
	
	self.SaveWorkflow = function() {
	
		$("#save_workflow_btn > i").hide();
		$("#save_workflow_btn > img").show();
		
		//create workflow object to be serialized
		var workflow = new Object();
		workflow.WorkflowID = self.Workflow().WorkflowID();
		workflow.WorkflowName = self.Workflow().WorkflowName();
		workflow.Description = self.Workflow().Description();
		workflow.Stages = [];
		
		$.each(self.Workflow().Stages(), function(i, stage) {
			//determine stage and parameter indices
			stage.StageIndex(i+1);			
			self.DetermineParameterIndices(stage.Parameters());
			
			//create stage object to be serialized
			var s = new Object();
			s.StageID = stage.StageID();
			s.StageName = stage.StageName();
			s.StageType = stage.StageType();
			s.Command = stage.Command();
			s.StageIndex = stage.StageIndex();
			
			s.Queue = stage.Queue();
			s.Nodes = stage.Nodes();
			s.MaxCores = stage.MaxCores();
			s.Memory = stage.Memory();
			s.Walltime = stage.Walltime();
			
			s.ExpectedOutputs = [];
			s.Parameters = [];
			s.StageDependencies = [];
			
			$.each(stage.ExpectedOutputs(), function(j, output) {
				//create output object to be serialized
				var o = new Object();
				o.ExpectedOutputID = output.ExpectedOutputID()
				o.ExpectedOutputFileName = output.ExpectedOutputFileName();
				
				s.ExpectedOutputs.push(o);
			});
			
			$.each(stage.Parameters(), function(j, param) {
				//create parameter object to be serialized
				var p = self.CreateParameterObject(param);
				
				s.Parameters.push(p);
			});
			
			$.each(stage.StageDependencies(), function(j, dep) {
				//create dependency object to be serialized
				var d = new Object();
				d.StageID = dep.StageID();
				d.ConditionID = dep.ConditionID();
				d.Value = dep.ConditionID();
				
				s.StageDependencies.push(d);
			});
				
			workflow.Stages.push(s);
		});		
		
		data = JSON.stringify(workflow);	
		
		$.ajax({
			url: "/api/jms/workflows",
			type: 'POST',
			data: data,
			success: function(wf) {	
				w = self.LoadWorkflowObservable(wf)
				w.files(self.Workflow().files());
				
				self.Workflow(w);	
						
				if(workflow.WorkflowID < 0) {
					//add new workflow to workflow list	
					self.Workflows.push(self.Workflow());	
				} else {
					//update workflow in workflow list					
					$.each(self.Workflows(), function(i, w) {
						if(w.WorkflowID() == self.Workflow().WorkflowID()) {
							self.Workflows.replace(w, self.Workflow());
						}
					});
				}	
				
				if(self.File() != null) {
					self.SaveWorkflowFile();
				}
				
				self.UploadWorkflowFiles();
				
				$("#save_workflow_btn > i").show();
				$("#save_workflow_btn > img").hide();
				
				AppendAlert("success", "Workflow saved successfully.", "#workflow_name-container");			
			},
			error: function() {
				$("#save_workflow_btn > i").show();
				$("#save_workflow_btn > img").hide();
				AppendAlert("danger", "Something went wrong. Workflow not saved.", "#workflow_name-container");
			}
		});
	}
	
	self.EditWorkflow = function(data) {
	    self.Loading(true);
		self.GetWorkflow(data);
		
		$.each(data.Stages(), function(i, s) {
			if(s.StageID() >= self.StageSeed)
				self.StageSeed = s.StageID() + 1;
		
			$.each(s.Parameters(), function(j, p) {
				if(p.ParameterID() >= self.ParameterSeed)
					self.ParameterSeed = p.ParameterID() + 1
			});
		});
		
		self.ShowCreateWorkflow();
	}
	
	self.DeleteWorkflow = function(data) {
	    question.Show("Delete workflow?", "Are you sure you want to delete this workflow? You will not be able to reverse this process.", function() {
			question.ToggleLoading(true);
		    $.ajax({
			    url: "/api/jms/workflows/" + data.WorkflowID(),
			    type: 'DELETE',
			    success: function(result) {				
				    self.Workflows.remove(data);			
			    },
			    error: function() {
				    AppendAlert("danger", "Something went wrong. Workflow not deleted.", "#workflows-container");
			    },
			    complete: function() {
			        question.Hide();
			    }
		    });
		});	
	}
	
	self.ShowImportWorkflow = function() {
	    self.Importing(false);
	    $("#import-dialog").modal();
	}
	
	self.ImportWorkflow = function() {
	    error = false;
	    self.Importing(true);
	    
	    files = $("#import-file").prop('files');
	    console.log(files)
	    sendFiles(files, "/api/jms/workflows/import", "file",
		    function(files) {
			    //success
			    console.log("success");
		    },
		    function(message) {
			    //error
			    alert(message);
			    self.Importing(false);
			    error = true;
		    },
		    function() {
			    //complete
			    self.LoadData();
	            $("#import-dialog").modal();
			    $("#import-dialog").modal('hide');
			    self.Importing(false);
			},
		    function(progress) {
			    //progress								
		    }						
	    );
	}
	
	self.CreateJob = function() {
		try {
			self.Submitting(true);
			self.SubmitStatus(0);
		
			$("#submit-dialog").modal({ 
				"backdrop": "static"
			})
		
			var job = new Object();
			job.JobName = self.Job().JobName();
			job.Description = self.Job().Description();
			
			if(self.Job().JobType() == 1) {
			    //Normal job
			    
			    job.WorkflowID = self.Job().Workflow().WorkflowID();
			    job.Stages = [];
		
			    var files = [];
		
			    $.each(self.Job().Workflow().Stages(), function(i, s) {
				    var stage = new Object();
				    stage.StageID = s.StageID();
				    stage.Parameters = [];
			
				    $.each(s.Parameters(), function(j, p) {
					    //if parameter is a file
					    if(p.Type() == 5) {				
						    var temp_files = $('input[name="param_' + p.ParameterID() + '"]').prop('files');
						    $.each(temp_files, function(k, f) {
							    var param = new Object();
							    param.ParameterID = p.ParameterID();
							    param.Value = f.name;
				
							    stage.Parameters.push(param);
						    });
					
						    files.push({ value: "param_" + p.ParameterID(), files: temp_files});
					    } else if(p.Type() == 7) {
						    var param = new Object();
						    param.ParameterID = p.ParameterID();
						    param.Value = p.get_JSON();
						    param.Type = p.Type();
				
						    stage.Parameters.push(param);	
					    } else if(p.Type() == 8) {
						    var param = new Object();
						    param.ParameterID = p.ParameterID();
						    param.Value = p.related_parameter().get_JSON();
						    param.Type = p.Type();
					
						    stage.Parameters.push(param);					
					    } else {
						    var param = new Object();
						    param.ParameterID = p.ParameterID();
						    param.Value = p.Value();
						    param.Type = p.Type();
				
						    stage.Parameters.push(param);
					    }
				    });
			
				    job.Stages.push(stage);
			    });
		
			    var data = JSON.stringify(job);
		
			    $.ajax({
				    url: "/api/jms/jobs",
				    type: "POST",
				    data: data,
				    success: function (job_id) {
					    self.Job().JobID(job_id);
								
					    if(files.length > 0) {
						    //upload job files
						    var num_sent = 0;
						    var num_completed = 0;
						    var error = false;
					
						    self.SubmitStatus(1);
					
						    $.each(files, function(i, f) {
						
							    if(f.files.length > 0) {
								    num_sent++;
								    sendFiles(f.files, "/api/jms/files/jobs/" + job_id, f.value,
									    function(files) {
										    //success
									    },
									    function(message) {
										    //error
										    error = true;
										    self.SubmitSuccess(false);
										    self.Submitting(false);
									    },
									    function() {
										    //complete
										    num_completed++;
									
										    if(!error && num_completed == num_sent) {
											    //all files uploaded without error
											    self.RunJob();
										    }
									    },
									    function(progress) {
										    //progress								
									    }						
								    );							
							    } 
						    });
					
						    if(num_sent == 0) {
							    self.RunJob();
						    }
					    } else {
						    self.RunJob();				
					    }
				    },
				    error: function () {
					    self.SubmitSuccess(false);
					    self.Submitting(false);
				    }
			    });
			} else {
			    //Batch job
			    $.ajax({
			        url: "/api/jms/jobs/batch",
			        type: "POST",
			        data: JSON.stringify(job),
			        success: function(job_id) {
			            self.Job().JobID(job_id);
			            //upload job files
						
						var error = false;
						
			            var batch_file = $('#batch_file').prop('files');
			            sendFiles(batch_file, "/api/jms/jobs/batch/" + job_id + "/files/batch", "file",
						    function(files) {
							    //success
						    },
						    function(message) {
							    //error
							    error = true;
							    self.SubmitSuccess(false);
							    self.Submitting(false);
						    },
						    function() {
							    //complete						
							    if(!error) {
							        var input_files = $('#input_files').prop('files');
							        sendFiles(input_files, "/api/jms/jobs/batch/" + job_id + "/files/input", "file",
						                function(files) {
							                //success
						                },
						                function(message) {
							                //error
							                error = true;
							                self.SubmitSuccess(false);
							                self.Submitting(false);
						                },
						                function() {
							                //complete
							                var num_sent = 0;
						                    var num_completed = 0;
						
							                if(!error) {							                    
								                //all files uploaded without error
								                self.RunJob();
							                }
						                },
						                function(progress) {
							                //progress								
						                }						
					                );
							    }
						    },
						    function(progress) {
							    //progress								
						    }						
					    );
			        },
			        error: function() {
			            self.SubmitSuccess(false);
					    self.Submitting(false);
			        }
			    });
			}
		} catch(err) {
			self.SubmitSuccess(false);
			self.Submitting(false);
		}
	}
	
	self.RunJob = function() {
		self.SubmitStatus(2);
		batch = "";
		if(self.Job().JobType() == 2) {
		    batch = "batch/";
		}
		
		$.ajax({
			url: "/api/jms/jobs/" + batch + self.Job().JobID(),
			type: "PUT",
			success: function() {
				self.SubmitSuccess(true);
				self.SubmitStatus(3);
			},
			error: function() {
				self.SubmitSuccess(false);		
			},
			complete: function() {
				self.Submitting(false);
			}
		});
			
	}
	
	self.AddStage = function() {
		self.ParameterSeed += 1;
		self.StageSeed += 1;
		
		var stage = new Stage(self.StageSeed, "New Stage", null, 1, null, "", [], [], "batch", 1, 1, 1, "02:00:00");
		
		self.Workflow().Stages.push(stage);
		self.SelectedStages([stage]);
	}	
	
	self.UploadWorkflowFiles = function() {
		
		var id = self.Workflow().WorkflowID();
		var file = self.File();
		
		if(id > 0) {
			//upload scripts/files
			var files = $('#files').prop('files');
			if(files.length > 0) {	
				
				$("#upload_file_btn > span").text("0%");
		
				$("#upload_file_btn > i").hide();
				$("#upload_file_btn > img").show();
				$("#upload_file_btn > span").show();
						
				sendFiles(files, "/api/jms/files/workflows/" + id, "file",
					function(files) {
						self.Workflow().files([]);
						$.each(files, function(i, f) {
							self.Workflow().files.push(new ScriptFile(f));
							
							if(file != null && f == file.FileName()) {
								self.SelectedFiles.push(self.Workflow().files()[i]);
							}
						});						
							
						AppendAlert("success", "Files uploaded successfully.", "#workflow_options-container");
					},
					function(message) {
						AppendAlert("danger", message, "#workflow_options-container");
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
		} else {
			self.SaveWorkflow();
		}
	}
	
	self.GetWorkflowFiles = function() {
		var file = self.File();
		
		$.ajax({
			url: "/api/jms/files/workflows/" + self.Workflow().WorkflowID(),
			success: function(files) {
				self.Workflow().files([]);
				$.each(files, function(i, f) {
					self.Workflow().files.push(new ScriptFile(f));
						
					if(file != null && f == file.FileName()) {
						self.SelectedFiles.push(self.Workflow().files()[i]);
					}
				});
			}
		});
	}
	
	self.GetWorkflowFileContent = function(file) {
		$.ajax({
			url: "/api/jms/files/workflows/" + self.Workflow().WorkflowID() + "/" + file.FileName(),
			success: function(content) {
				file.Content(content);
				make_editor();
			},
			error: function() {
				AppendAlert("danger", "Something went wrong while fetching file content.", "#workflow_options-container");
				make_editor();
			}
		});
	}
	
	self.DeleteWorkflowFiles = function() {
		$.each(self.SelectedFiles(), function(i, file){
			if(file.ExistsOnServer()) {
				$.ajax({
					url: "/api/jms/files/workflows/" + self.Workflow().WorkflowID() + "/" + file.FileName(),
					type: "DELETE",
					success: function() {
						self.Workflow().files.remove(file);
					},
					error: function() {
						AppendAlert("danger", "Something went wrong. File not deleted.", "#workflow_options-container");
					}
				});
			} else {
				self.Workflow().files.remove(file);
			}
		});
	}
	
	self.AddWorkflowFile = function() {
		var f = new ScriptFile("New_File.txt");
		f.ExistsOnServer(false);
		
		self.Workflow().files.push(f);
		self.SelectedFiles([f]);
	}
	
	self.SaveWorkflowFile = function() {
					
		$("#save_workflow_file_btn > i").hide();
		$("#save_workflow_file_btn > img").show();
		
		if(self.Workflow().WorkflowID() > 0) {
			var file = self.File();
			
			$.ajax({
				url: "/api/jms/files/workflows/" + self.Workflow().WorkflowID() + "/" + file.FileName(),
				type: "PUT",
				data: file.Content(),
				success: function(files) {
					self.Workflow().files([]);
					$.each(files, function(i, f) {
						self.Workflow().files.push(new ScriptFile(f));
						
						if(f == file.FileName()) {
							self.SelectedFiles.push(self.Workflow().files()[i]);
						}
					});
					
					$("#save_workflow_file_btn > i").show();
					$("#save_workflow_file_btn > img").hide();
				},
				error: function() {
					AppendAlert("danger", "Something went wrong. File not saved.", "#workflow_options-container");
				
					$("#save_workflow_file_btn > i").show();
					$("#save_workflow_file_btn > img").hide();
				}
			});
		} else {
			self.SaveWorkflow();
		}
	}
	
	self.DeleteStage = function() {
		$.each(self.SelectedStages(), function(i, stage) {
			//remove dependencies
			$.each(self.Workflow().Stages(), function(j, s){
				$.each(s.StageDependencies(), function(k, dep) {
					if(dep.StageID() == stage.StageID()) {
						s.StageDependencies.remove(dep);
					}
				});
			});
			
			self.Workflow().Stages.remove(stage);
		});
	}
	
	self.ShiftStageDown = function() {
		var index = self.Workflow().Stages.indexOf(self.Stage());
		var last_index = self.Workflow().Stages().length-1;		
		
		if(index < last_index) {
			self.Workflow().Stages.swap(index+1, index);
		}		
	}
	
	self.ShiftStageUp = function() {
		var index = self.Workflow().Stages.indexOf(self.Stage());
		
		if(index > 0) {
			self.Workflow().Stages.swap(index-1, index);
		}
	}
	
	self.ViewAddStageDependency = function() {
		self.StageDependency(new StageDependency(null, 1, null));
		$("#dependency-dialog").modal();
	}		
	
	self.ViewEditStageDependency = function(data) {
		var dep = new StageDependency(self.SelectedDependencies()[0].StageID(), self.SelectedDependencies()[0].ConditionID(), self.SelectedDependencies()[0].Value());
		self.StageDependency(dep);
		self.StageDependency().editing(true);
		$("#dependency-dialog").modal();
	}
	
	self.SaveStageDependency = function() {			
		if(self.StageDependency().editing() == true) {
			self.SelectedDependencies()[0].StageID(self.StageDependency().StageID());
			self.SelectedDependencies()[0].ConditionID(self.StageDependency().ConditionID());
			self.SelectedDependencies()[0].Value(self.StageDependency().Value());
		} else {
			var dep = new StageDependency(self.StageDependency().StageID(), self.StageDependency().ConditionID(), self.StageDependency().Value());
			self.Stage().StageDependencies.push(dep);
		}
		
		$("#dependency-dialog").modal('hide');
	}
	
	self.DeleteStageDependency = function() {
		$.each(self.SelectedDependencies(), function(i, dependency) {			
			self.Stage().StageDependencies.remove(dependency);
		});
	}
	
	self.AddParameter = function() {
		self.ParameterSeed += 1;
		self.Stage().Parameters.push(new Parameter(self.ParameterSeed, "", "", "user", 1, false, "", null, null, null, false));		
	}
	
	self.AddSubParameter = function(parameters, parent_id) {
		self.ParameterSeed += 1;
		
		parameters.push(new Parameter(self.ParameterSeed, "", "", "user", 1, false, "", null, null, parent_id, false));		
	}
	
	self.DeleteParameter = function(parameters, data) {
		parameters.remove(data);
	}
	
	self.NewObjects = ko.observableArray();
	self.AddComplexObject = function(data) {
		self.Parameter(data);
		self.ClonedParameter(data.clone());
		
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
	
	self.ParameterOptions = function(data) {
		self.Parameter(data);
		$("#param-dialog").modal();
	}
	
	self.AddParameterOption = function() {
		self.Parameter().ParameterOptions.push(new ParameterOption(0, "", ""));
	}
	
	self.DeleteParameterOption = function(data) {
		self.Parameter().ParameterOptions.remove(data);
	}
	
	self.AddExpectedOutput = function() {
		self.Stage().ExpectedOutputs.push(new ExpectedOutput(-1, ""));
	}
	
	self.DeleteExpectedOutput = function(data) {
		self.Stage().ExpectedOutputs.remove(data);
	}
	
	self.AddValue = function(data) {
		data.value_items.push(new ValueItem("", data));
	}
	
	self.RemoveValue = function(parent, data) {
		parent.value_items.remove(data);
	}
	
	self.edit_mode = false;
	
	self.SaveUserAccessRight = function() {
	    $.ajax({
	        url: "/api/jms/workflows/" + self.Workflow().WorkflowID() + "/permissions/users",
	        type: "POST",
	        data: { Username: self.UserAccessRight().User().Username(), AccessRightID: self.UserAccessRight().AccessRight().AccessRightID() },
	        success: function(data) {
	            access = new AccessRight(data.AccessRight.AccessRightID, data.AccessRight.AccessRightName);
	            
	            if(self.edit_mode) {
	                self.temp_share().AccessRight(access);
	            } else {
        	        user = new User(data.User.id, data.User.username);
    	            self.Workflow().UserAccessRights.push(new UserWorkflowAccessRight(user, access, true));
	            }
	            
	            $("#user-share-dialog").modal('hide');
	        },
	        error: function() {
	        
	        }
	    });
	}
	
	self.ShowAddUserAccessRight = function() {
	    self.edit_mode = false;
	    self.UserAccessRight(new UserWorkflowAccessRight(new User(0, ""), self.AccessRights()[2]));
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
	        url: "/api/jms/workflows/" + self.Workflow().WorkflowID() + "/permissions/groups",
	        type: "POST",
	        data: { GroupID: self.GroupAccessRight().Group().GroupID(), AccessRightID: self.UserAccessRight().AccessRight().AccessRightID() },
	        success: function(data) {
	            group = new Group(data.Group.id, data.Group.name);
	            access = new AccessRight(data.AccessRight.AccessRightID, data.AccessRight.AccessRightName);
	                
	            self.Workflow().GroupAccessRights.push(new GroupWorkflowAccessRight(group, access, true));
	            
	            $("#group-share-dialog").modal('hide');
	        },
	        error: function() {
	        
	        }
	    });
	}
	
	self.ShowAddGroupAccessRight = function() {
	    self.GroupAccessRight(new GroupWorkflowAccessRight(new Group(0, ""), self.AccessRights()[2]));
	    $("#group-share-dialog").modal();
	}
	
	self.ShowEditGroupAccessRight = function(data) {
	    console.log(data.AccessRight().AccessRightID());
	    self.GroupAccessRight(data);
	    $("#group-share-dialog").modal();
	}
	
	self.DeleteUserAccessRight = function(data) {	    
	    question.Show("Remove user access?", "Are you sure you want to remove " + data.User().Username() + "'s access to this workflow?", function() {
			question.ToggleLoading(true);
			$.ajax({
			    url: "/api/jms/workflows/" + self.Workflow().WorkflowID() + "/permissions/users/" + data.User().UserID(),
			    type: "DELETE",
    	        success: function() {
    	            self.Workflow().UserAccessRights.remove(data);
    	        },
    	        complete: function() {
    	            question.Hide();
    	        }
    	    });
	    });
	}
	
	self.DeleteGroupAccessRight = function(data) {
	    question.Show("Remove group access?", "Are you sure you want to remove " + data.Group().GroupName() + "'s access to this workflow?", function() {
			question.ToggleLoading(true);
			$.ajax({
			    url: "/api/jms/workflows/" + self.Workflow().WorkflowID() + "/permissions/groups/" + data.Group().GroupID(),
			    type: "DELETE",
    	        success: function() {
    	            self.Workflow().GroupAccessRights.remove(data);
    	        },
    	        complete: function() {
    	            question.Hide(false);
    	        }
    	    });
	    });
	}
	
	self.ShowShareWorkflow = function(workflow) {
	    self.Workflow(workflow);
	    
	    $.ajax({
	        url: "/api/jms/workflows/" + workflow.WorkflowID() + "/permissions",
	        success: function(data) {
	            self.Workflow().UserAccessRights([]);
	            self.Workflow().GroupAccessRights([]);
	            
	            $.each(data.UserWorkflowAccessRights, function(i, access_right) {
	                user = new User(access_right.User.id, access_right.User.username);
	                access = new AccessRight(access_right.AccessRight.AccessRightID, access_right.AccessRight.AccessRightName);
	                
	                self.Workflow().UserAccessRights.push(new UserWorkflowAccessRight(user, access, true));
	            });
	            
	            $.each(data.GroupWorkflowAccessRights, function(i, access_right) {
	                group = new Group(access_right.group.id, access_right.group.groupname);
	                access = new AccessRight(access_right.AccessRight.AccessRightID, access_right.AccessRight.AccessRightName);
	                
	                self.Workflow().GroupAccessRights.push(new GroupWorkflowAccessRight(group, access, true));
	            });
	        },
	        error: function() {
	        
	        }
	    });
	    
	    $("#share-dialog").modal();
	}
	
	self.ShowWorkflows = function() {
		self.VisibleWindow("workflows");			
	}
	
	self.ShowCreateWorkflow = function() {	
		self.VisibleWindow("create_workflow");			
	}
	
	self.ShowRunWorkflow = function(data) {
	    self.Loading(true);
	     
	    $.ajax({
	        url: "/api/jms/workflows/" + data.WorkflowID(),
	        success: function(wf) {
		        self.Job(new Job(-1, "", "", self.LoadWorkflowObservable(wf)));
	            self.Loading(false);
	        },
	        error: function() {
	            self.VisibleWindow("workflows");
	            self.Loading(false);
	        }
	    });
			
		self.VisibleWindow("run_workflow");		
	}
	
	self.hideOption = function(option, item) {
        ko.applyBindingsToNode(option, { visible: item.available }, item);
    }
}

var question = new QuestionModal("question-dialog");
	
var workflow;
$(document).ready(function () {
	$("#workflow-menu-item").addClass("active");
	$("#workflow-menu-item > a").addClass("active-menu");
	
	workflow = new WorkflowViewModel();
	ko.applyBindings(workflow, document.getElementById("workflows"));
		
	workflow.LoadData();	
});
