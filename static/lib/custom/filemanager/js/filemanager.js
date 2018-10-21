function DirectoryObject(name, path, type) {
    this.name = ko.observable(name);
    this.fullpath = ko.observable(path);
    this.type = ko.observable(type);
}

var tab_id = 0;
function Tab(file) {
    var self = this;
    self.id = ko.observable(tab_id);
    self.file = ko.observable(file);
    self.file_content = ko.observable();
    self.type = ko.observable();
    
    self.tab_class = ko.observable();
    self.display = ko.observable();
    
    self.editor = null;
    self.mode = null;
    
    tab_id++;
    
    self.make_editor = function(textarea) {      
            
        var modelist = ace.require('ace/ext/modelist');
        self.mode = modelist.getModeForPath(self.file().name()).mode;
        var editDiv = $('<div>', {
            position: 'absolute',
            width: $("#page").width(),
            height: $("#page").height() - 43,
            'class': textarea.attr('class')
        }).insertBefore(textarea);
        textarea.css('visibility', 'hidden');
        self.editor = ace.edit(editDiv[0]);
        self.editor.getSession().setValue(textarea.val());
        self.editor.getSession().setMode(self.mode);
        self.editor.setAutoScrollEditorIntoView(true);
        self.editor.setTheme("ace/theme/" + webinal.filemanager_settings().theme()); 
        self.editor.setOptions({
          fontSize: webinal.filemanager_settings().font_size() + "pt"
        });                 
        
        self.editor.getSession().on('change', function(){
            self.file_content(self.editor.getSession().getValue());
        });
    }   
}

var FileManagerViewModel = function() {
    var self = this;
    
    self.cwd = ko.observableArray();
    self.directories = ko.observableArray();
    self.files = ko.observableArray();
    self.tabs = ko.observableArray();
    self.selected_tab = ko.observable();
    self.clipboard = ko.observable();
    self.errors = ko.observableArray();
    
    self.file_menu = ko.observableArray([
        { 
            text: "<i class='fa fa-file'></i> Open", 
            action: function(data) { self.getFile(data); }
        }, {
            text: "<i class='fa fa-download'></i> Download",
            action: function(data) { self.downloadFile(data); }
        }, {
            text: "<i class='fa fa-edit'></i> Rename",
            action: function(data) { self.showRenameModal(data); }
        }, {
            separator: true
        }, {
            text: "<i class='fa fa-copy'></i> Copy",
            action: function(data) { self.copy(data); }
        }, {
            text: "<i class='fa fa-cut'></i> Cut",
            action: function(data) { self.cut(data); }
        }, {
            separator: true
        }, {
            text: "<i class='fa fa-trash-o'></i> Delete",
            action: function(data) { self.delete(data) }
        }, {
            separator: true
        }, {
            text: "<i class='fa fa-sliders'></i> Properties",
            action: function(data) { self.delete(data) }
        }     
    ]);
        
    self.dir_menu = ko.observableArray([
        { 
            text: "<i class='fa fa-file'></i> Open", 
            action: function(data) { self.getDirectory(data.fullpath()); }
        }, {
            text: "<i class='fa fa-edit'></i> Rename",
            action: function(data) { self.showRenameModal(data); }
        }, {
            separator: true
        }, {
            text: "<i class='fa fa-copy'></i> Copy",
            action: function(data) { self.copy(data); }
        }, {
            text: "<i class='fa fa-cut'></i> Cut",
            action: function(data) { self.cut(data); }
        }, {
            text: "<i class='fa fa-paste'></i> Paste Into Folder",
            action: function(data) { self.paste(data); }
        }, {
            text: "<i class='fa fa-trash-o'></i> Delete",
            action: function(data) { self.delete(data) }
        }, {
            separator: true
        }, {
            text: "<i class='fa fa-sliders'></i> Properties",
            action: function(data) { self.delete(data) }
        }    
    ]);
    
    self.tab_menu = ko.observableArray([
        { 
            text: "<i class='fa fa-folder-open-o'></i> Open Directory", 
            action: function(data) { 
                path = data.file().fullpath();
                
                // windows
                if (path.indexOf("/") == -1) { 
                    path = path.substring(0, path.lastIndexOf('\\'));
                }
                // unix
                else { 
                    path = path.substring(0, path.lastIndexOf('/'));
                }
                
                self.getDirectory(path);
            }
        }, {
            separator: true
        }, {
            text: "<i class='fa fa-times-circle'></i> Close",
            action: function(data) { self.closeTab(data) }
        }
    ]);
    
    self.creating = ko.observable(false);
    self.create_error = ko.observable(new ErrorMessage());
    self.new_directory_object = ko.observable();
    
    self.createFile = function() {
        self.create_error(new ErrorMessage());
        
        var path = self.cwd()[self.cwd().length - 1].fullpath();
        self.new_directory_object(new DirectoryObject("", path, "file"));
        console.log(self.new_directory_object());
        $("#create-modal").modal();
    }
    
    
    self.createDirectory = function() {
        self.create_error(new ErrorMessage());
        
        var path = self.cwd()[self.cwd().length - 1].fullpath();
        self.new_directory_object(new DirectoryObject("", path, "directory"));
        $("#create-modal").modal();
    }
    
    self.createDirectoryObject = function() { 
        self.creating(true);
              
        $.ajax({
            url: "/files/operation/create",
            type: "POST",
            data: { 
                name: self.new_directory_object().name(), 
                fullpath: self.new_directory_object().fullpath(), 
                type: self.new_directory_object().type()
            },
            success: function() {
                self.reloadDirectory();
                $("#create-modal").modal('hide');
            },
            error: function(http) {
                self.create_error().error(true);
                self.create_error().message(http.responseText);
            },
            complete: function() {
                self.creating(false);
            }
        });
    }
    
    
    self.uploading = ko.observable(false);
    self.upload_error = ko.observable(new ErrorMessage());
    self.upload_path = ko.observable();    
    
    self.showUploadModal = function() {
        self.upload_error(new ErrorMessage()); 
        self.upload_path(self.cwd()[self.cwd().length - 1].fullpath());
        $("#upload-modal").modal();
    }
    
    self.upload = function() {
        $("form#upload").submit();
    }
    
    
    self.getDirectory = function(path){
    
        $("#refresh_dir").addClass("faa-spin animated");
                
        var url = "/files/directory";
        if (path != null) {
            url += "?path=" + path
        }
        
        $.ajax({
            url: url,
            success: function(data) {
                self.cwd([]);
                self.directories([]);
                self.files([]);
                
                data = JSON.parse(data);
                $.each(data.cwd, function(i, dir){
                    self.cwd.push(new DirectoryObject(dir.name, dir.fullpath, dir.type));
                });
                
                $.each(data.dir_contents, function(i, dir){
                    if(dir.type == "directory") {
                        self.directories.push(new DirectoryObject(dir.name, dir.fullpath, dir.type));
                    } else {
                        self.files.push(new DirectoryObject(dir.name, dir.fullpath, dir.type));
                    }                        
                });
                
                self.directories.sort(function(left, right) {
                    var left_name = left.name().toLowerCase();
                    var right_name = right.name().toLowerCase();
                    return left_name == right_name ? 0 : (left_name < right_name ? -1 : 1);
                });
                
                self.files.sort(function(left, right) {
                    var left_name = left.name().toLowerCase();
                    var right_name = right.name().toLowerCase();
                    return left_name == right_name ? 0 : (left_name < right_name ? -1 : 1); 
                });
            },
            error: function(http) {
                self.addError(http.responseText);
            },
            complete: function() {
                $("#refresh_dir").removeClass("faa-spin animated");
            }
        });
    }
    
    
    self.reloadDirectory = function() {
        path = self.cwd()[self.cwd().length - 1].fullpath();
        self.getDirectory(path);
    }
    
    
    self.getFile = function(data) {
        var url = "/files/file?path=" + data.fullpath();
        
        //send a HEAD request to check the content type of the file
        $.ajax({
            url: url,
            type: "HEAD",
            success: function(result, status, xhr){                
                var tab = new Tab(data);  
                self.tabs.push(tab);
                self.selectTab(tab);
                
                //do something based on the content type
                var ct = xhr.getResponseHeader("content-type");
                if(ct.startsWith("image")) {
                    tab.type("image");
                    
                    var img = new Image();
                    img.src = url;
                    img.className = "tab-image";
                    $("#tab_" + tab.id()).append(img);
                } else if (ct == "application/pdf") {
                    tab.type("pdf");
                    
                    var pdf = document.createElement("object");
                    pdf.type = "application/pdf";
                    pdf.value = "Adobe Reader is required for Internet Explorer."
                    pdf.data = url;
                    pdf.className = "tab-pdf";
                    $("#tab_" + tab.id()).append(pdf);
                } else if(ct.startsWith("video")) {
                    tab.type("video");
                    
                    var video = "<video class='tab-video' controls>";
                    video += "<source src='" + url + "' />";
                    video += "</video>"
                    $("#tab_" + tab.id()).append(video);
                } else if(ct.startsWith("audio")) {
                    tab.type("audio");
                    
                    var audio = "<audio class='tab-audio' controls>";
                    audio += "<source src='" + url + "' />";
                    audio += "</audio>"
                    $("#tab_" + tab.id()).append(audio);
                } else { 
                    $.ajax({
                        url: url,
                        success: function(result) {
                            tab.type("text");
                            tab.file_content(result);
                    
                            var txt = document.createElement("textarea");
                            txt.value = result;
                            txt.className = "tab-text";
                            $("#tab_" + tab.id()).append(txt);
                            
                            tab.make_editor($(txt));
                        }
                    });
                }
            },
            error: function(http) {
                self.addError(http.responseText);
            }
        });        
    }
    
    
    self.downloadFile = function(data) {
        var url = "/files/transfer?path=" + data.fullpath();
        window.location = url;
    }    
    
    
    self.renamed_object = ko.observable();
    self.rename_error = ko.observable(new ErrorMessage());
    
    self.showRenameModal = function(data) {
        self.rename_error(new ErrorMessage());        
        self.renamed_object(new DirectoryObject(data.name(), data.fullpath(), data.type()));
        $("#rename-modal").modal();
    }
    
    self.renaming = ko.observable(false);
    self.rename = function() {
        self.renaming(true);
        
        var data = new Object();
        data.name = self.renamed_object().name();
        data.fullpath = self.renamed_object().fullpath();
        data.type = self.renamed_object().type();
        
        $.ajax({
            url: "/files/operation/rename",
            type: "PUT",
			contentType: 'application/json',
            data: JSON.stringify(data),
            success: function() {
                self.reloadDirectory();
                $("#rename-modal").modal('hide');
            },
            error: function(http) {
                self.rename_error().error(true);
                self.rename_error().message(http.responseText);
            },
            complete: function() {
                self.renaming(false);
            }
        });
    }
    
    
    self.copy = function(data) {
        self.clipboard({ data: data, op: 'copy'});
    }
    
    
    self.cut = function(data) {
        self.clipboard({ data: data, op: 'move'});
    }
    
    
    self.paste = function(data) {
        var destination = data.fullpath();
        
        data = new Object();
        data.name = self.clipboard().data.name();
        data.fullpath = self.clipboard().data.fullpath();
        data.type = self.clipboard().data.type();
        data.destination = destination;
        
        var op = self.clipboard().op;
        
        $.ajax({
            url: "/files/operation/" + op,
            type: "PUT",
			contentType: 'application/json',
            data: JSON.stringify(data),
            success: function() {
                self.reloadDirectory();
            },
            error: function(http) {
                self.addError(http.responseText);
            },
            complete: function() {
                self.clipboard(null);
            }
        });
    }
    
    
    self.delete = function(data) {
        $.ajax({
            url: "/files/operation/delete",
            type: "DELETE",
            data: {
                name: data.name(),
                fullpath: data.fullpath(),
                type: data.type()
            },
            success: function() {
                self.reloadDirectory();
            },
            error: function(http) {
                self.addError(http.responseText);
            }
        });
    }
    
    
    self.saveFile = function(data) {
        if(data.type() == "text") {
            $.ajax({
                url: "/files/file",
                type: "POST",
                data: { path: data.file().fullpath(), contents: data.file_content() },
                success: function() {
                    alert("File saved successfully");
                }
            });
        } else {
            self.addError("Webinal can only save text files.");
        }
    }
    
    
    self.selectTab = function(tab) {
        $.each(self.tabs(), function(i, t){
            if(t == tab) {
                t.tab_class("active");
                t.display("block");
            } else {
                t.tab_class("");
                t.display("none");
            }
        });
    }
    
    
    self.closeTab =function(data){
        self.tabs.remove(data);
    }
    
    
    self.addError = function(message) {       
        var e = new ErrorMessage();
        e.error(true);
        e.message(message);
        
        self.errors.push(e);
        
        $("#error-icon").addClass("faa-ring animated");
        setTimeout(function() {
            $("#error-icon").removeClass("faa-ring animated");
        }, 500);
    }
    
    
    self.showErrors = function() {
        $("#error-modal").modal();
    }
    
    
    self.clearError = function(data) {
        self.errors.remove(data);
    }
    
    
    self.clearErrors = function() {
        self.errors([]);
        $("#error-modal").modal('hide');
    }
}

$(window).resize(function() {
    $(".tab-page .ace_editor").each(function() {
        $(this).height($("#page").height() - 43);
        $(this).width($("#page").width());
    }) 
    $.each(filemanager.tabs(), function(i, tab){
        if(tab.type() == "text")
            tab.editor.resize(true);
    })
});

$("#max_footer").click(function() { 
    $(window).trigger('resize', function(){});
});

$("#min_footer").click(function() { 
    $(window).trigger('resize', function(){});
});

$("#hide-nav").click(function() { 
    $(window).trigger('resize', function(){});
});

$("form#upload").submit(function(){
    
    filemanager.uploading(true);
    
    var formData = new FormData($(this)[0]);

    $.ajax({
        url: "/files/transfer",
        type: 'POST',
        data: formData,
        success: function (data) {
            filemanager.reloadDirectory();
            $("#upload-modal").modal('hide');
        },
        error: function (http) {
            filemanager.upload_error().error(true);
            filemanager.upload_error().message(http.responseText);
        },
        complete: function() {
            filemanager.uploading(false);
        },
        cache: false,
        contentType: false,
        processData: false
    });

    return false;
});

$(window).bind('keydown', function(event) {
    if (event.ctrlKey || event.metaKey) {
        switch (String.fromCharCode(event.which).toLowerCase()) {
        case 's':
            event.preventDefault();
            
            var success = false;
            $.each(filemanager.tabs(), function(index, tab) {
                if(tab.tab_class() == "active") {
                    filemanager.saveFile(tab);
                    success = true;
                    return false;
                }
            });
            
            if(!success) {
               filemanager.addError("There was no active page to save.");
            }
                
            break;
        }
    }
});
        
var filemanager = new FileManagerViewModel();
ko.applyBindings(filemanager, document.getElementById("page-container"));
