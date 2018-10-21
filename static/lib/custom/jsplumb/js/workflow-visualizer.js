var Tool = function(id, name, category, description, user, public_ind) {
    this.ToolID = ko.observable(id);
    this.ToolName = ko.observable(name);
    this.Category = ko.observable(category);
    this.ToolDescription = ko.observable(description);
    this.User = ko.observable(user);
    this.PublicInd = ko.observable(public_ind);
    this.ToolVersions = ko.observableArray();
    
    this.SelectedVersion = ko.observable();
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
	this.OptionalInd = ko.observable(optional);
	
	this.ToolVersion = ko.observable();
}

var ExpectedOutput = function(id, label, file, type) {
    this.ExpectedOutputID = ko.observable(id);
    this.OutputName = ko.observable(label);
    this.FileName = ko.observable(file);
    this.FileType = ko.observable(type);
    
    this.DeleteInd = ko.observable(false);
    
    this.ToolVersion = ko.observable();
}

var Stage = function(id, toolversion, workflowversion, checkpoint, left, top, level, params, iteration) {
    this.StageID = ko.observable(id);
    this.ToolVersion = ko.observable(toolversion);
    this.WorkflowVersion = ko.observable(workflowversion);
    if(toolversion != null && workflowversion == null) {
        this.StageType = ko.observable(1); //tool
    } else if (toolversion == null && workflowversion != null) {
        this.StageType = ko.observable(2); //workflow
    }
    this.Checkpoint = ko.observable(checkpoint);
    this.StageLevel = ko.observable(level);
    
    this.StageParameters = ko.observableArray(params);
    this.Iteration = ko.observable(iteration);
    
    this.left_co_ord = ko.observable(left);
    this.top_co_ord = ko.observable(top);
}

var StageParameter = function(id, param, type, value) {
    this.StageParameterID = ko.observable(id);
    this.Parameter = ko.observable(param);
    this.StageParameterType = ko.observable(type);
    this.Value = ko.observable(value)
}

var StageParameterType = function(id, name) {
    this.StageParameterTypeID = ko.observable(id);
    this.StageParameterTypeName = ko.observable(name);
}

var StageDependency = function(id, stage, dependency, condition, exit_code, c){
    this.StageDependencyID = ko.observable(id);
    this.StageOI = ko.observable(stage);
    this.DependantOn = ko.observable(dependency);
    this.Condition = ko.observable(condition);
    this.ExitCodeValue = ko.observable(exit_code);
    
    this.connection = c;
}

var StageIteration = function(id, stage, iteration_type, iteration_value) {
    this.StageIteration = ko.observable(id);
    this.Stage = ko.observable(stage);
    this.IterationType = ko.observable(iteration_type); //1 - Number, 2 - Parameter
    this.Value = ko.observable(iteration_value);
}


function VisualizerViewModel() {
    var self = this;
    
    self.loading = ko.observable(true);
    
    self.WorkflowID;
    
    self.Tools = ko.observableArray();
	self.SelectedTools = ko.observableArray();
	self.GetTools = function() {
	    $.ajax({
	        url: "/api/jms/tools",
	        success: function(tools) {
	            self.LoadTools(tools);
	            self.loading(false);
	        }
	    });
	}
	
	self.LoadTools = function(tools) {
        self.Tools([]);
            
	    //loop through tools
	    $.each(tools, function(i, tool) {
            var t = new Tool(tool.ToolID, tool.ToolName, tool.Category, 
            tool.ToolDescription, null, tool.PublicInd, []);
            
            $.each(tool.ToolVersions, function(j, version) {
                t.ToolVersions.push(new ToolVersion(version.ToolVersionID, tool.ToolID, version.ToolVersionNum))
            })
            
            self.Tools.push(t);
	    });
	}
	
	self.loading_stages = ko.observable(true);
    self.Stages = ko.observableArray();
    self.GetStages = function(workflow_id) { 
	    self.WorkflowID = workflow_id;
	    
	    $.ajax({
	        url: "/api/jms/workflows/" + workflow_id + "/versions/dev/stages/",
	        type: "GET",
	        success: function(s){
	            self.Stages([]);
	            var deps = [];
	            $.each(s, function(i, stage){
	                var s = self.LoadStage(stage);
	                self.Stages.push(s);
	                self.redraw(s);
	                
	                $.each(stage.StageDependencies, function(j, dep){
	                    deps.push(new StageDependency(dep.StageDependencyID,
	                        s, dep.DependantOn, dep.Condition, dep.ExitCodeValue)
	                    );
	                });
	            });
	            
	            self.LoadStageDependencies(deps);
	            self.loading_stages(false);
	        },
	        error: function(http) {
	            AppendAlert("danger", "Something went wrong while fetching tool details.", "#edit-workflow-error");
	        },
	        complete: function() {
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
	
    self.GetStage = function(stage_id) { 
	    $.ajax({
	        url: "/api/jms/stages/" + stage_id,
	        type: "GET",
	        success: function(stage){
	            $.each(self.Stages(), function(i, s){
	                if(s.StageID() == stage.StageID) {
	                    s.ToolVersion().ToolVersionNum(s.ToolVersion.ToolVersionNum);
	                    self.redraw(s);
	                }
	            });
	            self.loading_stages(false);
	        },
	        error: function(http) {
	            AppendAlert("danger", "Something went wrong while fetching tool details.", "#edit-workflow-error");
	        },
	        complete: function() {
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
	self.MoveStage = function(stage) {
	    console.log(stage);
	    
	    var data = new Object();
	    data.Left = stage.left_co_ord();
	    data.Top = stage.top_co_ord();
	    
	    $.ajax({
	        url: "/api/jms/stages/" + stage.StageID() + "/position",
	        type: "PUT",
			contentType: 'application/json',
	        data: JSON.stringify(data),
	        success: function(s) { },
	        error: function(http) { }
	    });
	}
	
	self.CreateToolStage = function(tool) {
	    var v = tool.ToolVersions()[tool.ToolVersions().length-1];
	    v.Tool(tool); 
	    
	    var left = 10*self.count+30;
	    var right = 10*self.count+30;
	    var temp_id = "temp" + self.count;
	    
	    var stage = new Stage(temp_id, v, null, false, left,
	        right, [], null);
	       
	    var data = new Object();
	    data.ID = tool.ToolID();
	    data.VersionNum = v.ToolVersionNum();
	    data.StageType = 1;
	    data.Left = stage.left_co_ord();
	    data.Top = stage.top_co_ord();
	    
 
	    $.ajax({
	        url: "/api/jms/workflows/" + self.WorkflowID + "/versions/dev/stages",
	        type: "POST",
			contentType: 'application/json',
	        data: JSON.stringify(data),
	        success: function(s) {
	            stage = self.LoadStage(s);
	            
	            $.each(self.Stages(), function(i, se) {
	                if(se.StageID() == temp_id) {
	                    self.Stages.remove(se);
	                    self.Stages.push(stage);
	                    self.redraw(stage);
	                    return false;
	                }
	            });
	        },
	        error: function(http) {
	            console.log(http.responseText);
	        }
	    });
	    
	    return stage;
	}
	
	self.LoadStage = function(stage) {
	    var t = new Tool(stage.ToolVersion.Tool.ToolID, 
            stage.ToolVersion.Tool.ToolName);
        t.ToolVersions([]);
        $.each(stage.ToolVersion.Tool.ToolVersions, function(i, v){
            version = new ToolVersion(v.ToolVersionID, t, v.ToolVersionNum)
            t.ToolVersions.push(version);
        });
        
        var tv = new ToolVersion(stage.ToolVersion.ToolVersionID, 
            t, stage.ToolVersion.ToolVersionNum);
        
        $.each(stage.ToolVersion.ToolParameters, function(i, param) {
            var p = new Parameter(param.ParameterID, param.ParameterName, null, 
                null, param.ParameterType);
            p.ToolVersion(tv);
            
            tv.ToolParameters.push(p);
        });
        
        $.each(stage.ToolVersion.ExpectedOutputs, function(i, out) {
            var e = new ExpectedOutput(out.ExpectedOutputID, out.OutputName);
            e.ToolVersion(tv);
            
            tv.ExpectedOutputs.push(e);
        });
        
        var temp_stage = new Stage(stage.StageID, tv, null, 
            stage.Checkpoint, stage.left_co_ord, stage.top_co_ord, stage.StageLevel);
        
        $.each(stage.StageParameters, function(i, param) {
            var s = new StageParameter(param.StageParameterID, param.Parameter,
                param.StageParameterType, param.Value);
            
            temp_stage.StageParameters.push(s);
        });
        
        return temp_stage;
	}
	
	self.previous_parameters = ko.observableArray();
	self.previous_outputs = ko.observableArray();
	
	self.Stage = ko.observable();
	self.Stage.subscribe(function(stage){
	    self.previous_parameters([]);
	    self.previous_outputs([]);
	    $.each(self.StageDependencies(), function(i, dep){
	        if(dep.StageOI().StageID() == stage.StageID()){
	            self.previous_parameters(
	                self.previous_parameters().concat(dep.DependantOn().ToolVersion().ToolParameters())
	            );
	            self.previous_outputs(
	                self.previous_outputs().concat(dep.DependantOn().ToolVersion().ExpectedOutputs())
	            );
	        }
	    });
	});
	
	self.ToolParameters = ko.observableArray();
	self.ShowEditStage = function(stage) {
	    //self.GetStage(stage.StageID());
	    self.Stage(stage);
	    $("#stage-dialog").modal({'backdrop':'static'})
	}
	
	self.GetParameters = function(tool_id) {
	    $.ajax({
	        url: "/api/jms/tools/" + tool_id + "/parameters/",
	        success: function(parameters) {
	            parameter = self.LoadParameter(parameters);
	            self.Parameter(parameter);
	            
	            $("#loading-dialog").modal('hide');
	        },
	        error: function(http) {
	            $("#loading-dialog").modal('hide');
	        }
	    });
	}
	
	self.EditStage = function(stage) {
	    var data = new Object();
	    data.VersionNum = stage.ToolVersion().ToolVersionNum();
	    data.Checkpoint = stage.Checkpoint();
	    data.StageParameters = [];
	    $.each(stage.StageParameters(), function(i, param) {
	        var p = new Object();
	        p.ParameterID = param.Parameter();
	        p.StageParameterTypeID = param.StageParameterType();
	        p.Value = param.Value();
	        
	        data.StageParameters.push(p);
	    })
	    
	    $.ajax({
	        url: "/api/jms/stages/" + stage.StageID(),
	        type: "PUT",
			contentType: 'application/json',
	        data: JSON.stringify(data),
	        success: function() {
        	    $("#stage-dialog").modal('hide');
	        }
	    });
	}
	
	self.DeleteStage = function(data) {
	    
	    $.ajax({
	        url: "/api/jms/stages/" + data.StageID(),
	        type: "DELETE",
	        success: function() {
        	    instance.detachAllConnections($("#stage_" + data.StageID()));
        	    self.Stages.remove(data);
        	    $("#stage-dialog").modal('hide');
	            
	        }
	    });
	}
	
	self.loading_dependency = ko.observable(false);
	self.StageDependencies = ko.observableArray();
	
	$('#dependency-dialog').on('hidden.bs.modal', function () {
	    if(self.Dependency().StageDependencyID() == 0) {
            instance.detach(self.Dependency().connection);
	    }
    });
    
	self.Conditions = ko.observableArray([
	    { ConditionID: 1, ConditionName: "Stage completed successfully" },
	    { ConditionID: 2, ConditionName: "Stage failed" },
	    { ConditionID: 3, ConditionName: "Stage completed" },
	    { ConditionID: 4, ConditionName: "Exit code value" },    
	]);
	
	self.LoadStageDependencies = function(deps) {
	    
	    $.each(deps, function(i, dep){
	        $.each(self.Stages(), function(j, stage){
	            if(dep.DependantOn() == stage.StageID()){
	                dep.DependantOn(stage);
	                dep.connection = instance.connect({ 
	                    source: "stage_" + dep.DependantOn().StageID(), 
	                    target: "stage_" + dep.StageOI().StageID(),
                        anchor: "Continuous"
	                });
	                
	                dep.connection.Dependency = dep;
	                self.StageDependencies.push(dep);
	                return false;
	            }
	        });
	    });
	}
	
	self.Dependency = ko.observable();
	self.ShowAddDependency = function(c) {
	    self.Dependency(c.Dependency);
	    $("#dependency-dialog").modal({'backdrop':'static'})
	}
	
	self.AddDependency = function() {
	    var data = new Object();
	    data.DependantOn = self.Dependency().DependantOn().StageID();
	    data.Condition = self.Dependency().Condition();
	    data.ExitCodeValue = self.Dependency().ExitCodeValue();
	    
	    $.ajax({
	        url: "/api/jms/stages/" + self.Dependency().StageOI().StageID() + "/dependencies",
	        type: "POST",
			contentType: 'application/json',
	        data: JSON.stringify(data),
	        success: function(dependency) {
	            self.StageDependencies.push(self.Dependency());
	            self.Dependency().StageDependencyID(dependency.StageDependencyID);
	            
	            //Get the updated levels for the stages
        	    $.ajax({
        	        url: "/api/jms/workflows/" + self.WorkflowID + "/versions/dev/stages/levels",
        	        type: "GET",
        	        success: function(stages){
        	            self.UpdateStageLevels(stages);
        	        },
        	        error: function(http) {
        	            AppendAlert("danger", "Something went wrong while fetching stage levels.", "#edit-workflow-error");
        	        },
        	        complete: function() {
	                    $("#dependency-dialog").modal('hide');
        	        }
        	    });
	        }, 
	        error: function(http) {
	            
	        }
	    });
	}
	
	self.ShowEditDependency = function(c) {
	    self.Dependency(c.Dependency);
	    $("#edit-dependency-dialog").modal({'backdrop':'static'})
	}

	self.EditDependency = function(dep) {
	    var data = new Object();
	    data.Condition = dep.Condition();
	    data.ExitCodeValue = dep.ExitCodeValue();
	    
	    $.ajax({
	        url: "/api/jms/stages/dependencies/" + dep.StageDependencyID(),
	        type: "PUT",
			contentType: 'application/json',
	        data: JSON.stringify(data),
	        success: function() {
	            $("#edit-dependency-dialog").modal('hide');
	        }
	    });
	}
	
	self.DeleteDependency = function(dep) {
	    $.ajax({
	        url: "/api/jms/stages/dependencies/" + dep.StageDependencyID(),
	        type: "DELETE",
	        success: function(stages) {
	            $("#edit-dependency-dialog").modal('hide');
                self.StageDependencies.remove(dep);
                instance.detach(dep.connection);
                $("#edit-dependency-dialog").modal('hide');
                
                self.UpdateStageLevels(stages);
	        }
	    });
	}
	
	self.UpdateStageLevels = function(stages){
	    $.each(stages, function(i, new_s){
	        $.each(self.Stages(), function(j, old_s){
	            if(new_s.StageID == old_s.StageID()) {
	                old_s.StageLevel(new_s.StageLevel);
	                return false;
	            }
	        });
	    });
	}
	
	
	self.StageParameterTypes = ko.observableArray([
	    new StageParameterType(1, "Value"),
	    new StageParameterType(2, "Parameter from another stage"),
	    new StageParameterType(3, "Output from a previous stage")
	]);
	
	self.AddStageParameter = function(stage){
	    var sp = new StageParameter();
	    stage.StageParameters.push(sp);
	}
	
	self.DeleteStageParameter = function(sp) {
	    self.Stage().StageParameters.remove(sp);
	}
	
	self.count = 0;
	self.AddTool = function(tool) {
	    self.count++;
	    
	    var s = self.CreateToolStage(tool);
	    self.Stages.push(s);
	    
	    var windows = $(".visualizer .w")
	    
	    var el = $("#stage_" + s.StageID())
	    
        //initializer the connector - allow it to be a source of new connections
        instance.makeSource(windows, {
            filter: ".ep",
            anchor: "Continuous",
            connector: [ "StateMachine", { curviness: 20 } ],
            connectorStyle: { strokeStyle: "#5c96bc", lineWidth: 2, outlineColor: "transparent", outlineWidth: 4 }
        });
        
        //make the element a target for a connection
        instance.makeTarget(windows, {
            dropOptions: { hoverClass: "dragHover" },
            anchor: "Continuous",
            allowLoopback: true
        });
        
        //make the element draggable
        instance.draggable(windows, {
          containment: 'parent'
        });
        
	    instance.repaint("stage_" + s.StageID(), { left: s.left_co_ord(), top: s.top_co_ord()});
        
	}
	
	self.redraw = function(stage) {
	    //var windows = $(".visualizer .w")
	    
	    var id = "stage_" + stage.StageID();
	    var el = $("#" + id)
	    
	    //initializer the connector - allow it to be a source of new connections
        instance.makeSource(el, {
            filter: ".ep",
            anchor: "Continuous",
            connector: [ "StateMachine", { curviness: 20 } ],
            connectorStyle: { strokeStyle: "#5c96bc", lineWidth: 2, outlineColor: "transparent", outlineWidth: 4 }
        });
        
        //make the element a target for a connection
        instance.makeTarget(el, {
            dropOptions: { hoverClass: "dragHover" },
            anchor: "Continuous",
            allowLoopback: true
        });
        
        //make the element draggable
        instance.draggable(el, {
            containment: 'parent',
            stop: function(e){
                var left = parseInt(el.css('left'));
                var top = parseInt(el.css('top'));
                
                stage.left_co_ord(left);
                stage.top_co_ord(top);
                
                self.MoveStage(stage);
            }
        });
        
	    instance.repaint(id, { 
	        left: stage.left_co_ord(), 
	        top: stage.top_co_ord()
	    });
	}
	
	self.AddTools = function() {
	    $.each(self.SelectedTools(), function(i, tool){
	        self.AddTool(tool);
	    });
	}
}


var visualizer;
var instance;
var question = new QuestionModal("question-dialog");

$(document).ready(function () {
	$("#workflow-menu-item").addClass("active");
	$("#workflow-menu-item > a").addClass("active-menu");	
	
	visualizer = new VisualizerViewModel();
	ko.applyBindings(visualizer, document.getElementById("visualization"));
	
	visualizer.GetTools();

    // setup some defaults for jsPlumb.
    instance = jsPlumb.getInstance({
        Endpoint: ["Dot", {radius: 2}],
        HoverPaintStyle: {strokeStyle: "#1e8151", lineWidth: 2 },
        ConnectionOverlays: [
            [ "Arrow", {
                location: 1,
                id: "arrow",
                length: 14,
                foldback: 0.8
            } ]
        ],
        Container: "visualizer"
    });

    window.jsp = instance;

    // bind a click listener to each connection; the connection is deleted. you could of course
    // just do this: jsPlumb.bind("click", jsPlumb.detach), but I wanted to make it clear what was
    // happening.
    instance.bind("click", function (c) {
        visualizer.ShowEditDependency(c);
    });

    // bind a connection listener. note that the parameter passed to this function contains more than
    // just the new connection - see the documentation for a full list of what is included in 'info'.
    // this listener sets the connection's internal
    // id as the label overlay's text.
    instance.bind("connection", function (info) {
        //info.connection.getOverlay("label").setLabel(info.connection.id);
        //instance.detach(info.connection)
        if(visualizer.loading_stages() == false) {
    	    source = document.getElementById(info.connection.sourceId);
    	    target = document.getElementById(info.connection.targetId);
    	    
    	    source_id = info.connection.sourceId.split("_")[1];
    	    target_id = info.connection.targetId.split("_")[1];
    	    
    	    var stage, dependency;
    	    $.each(visualizer.Stages(), function(i, s) {
    	        if(s.StageID() == source_id) {
    	            dependency = s;
    	        } 
    	        if (s.StageID() == target_id) {
    	            stage = s;
    	        }
    	    });
    	    
    	    var dep = new StageDependency(0, stage, dependency, 1, 0, info.connection);
    	    info.connection.Dependency = dep;
            visualizer.ShowAddDependency(info.connection);
        }
    });

    jsPlumb.fire("jsPlumbLoaded", instance);

    // initialize the application
	var app = Sammy(function() {
		this.get('#:workflow_id', function() {
		    visualizer.GetStages(this.params.workflow_id);
		});
	});

	// start the application
	app.run('/workflows/visualize/#');
});


