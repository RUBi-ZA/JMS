function ErrorMessage() {
    this.error = ko.observable(false);
    this.message = ko.observable("");
}

function Notification(notification, type) {
    this.viewed = ko.observable(false);
    this.notification = ko.observable(notification);
    this.type = ko.observable(type);
}

function FileManagerSettings(home_directory, theme, font_size) {
    this.home_directory = ko.observable(home_directory);
    this.theme = ko.observable(theme);
    this.font_size = ko.observable(font_size)
}

var WebinalViewModel = function() {
    self = this;
        
    self.notifications = ko.observableArray();
    
    self.filemanager_settings = ko.observable();
    self.updating_settings = ko.observable(false);
    self.settings_error = ko.observable(new ErrorMessage());
    
    self.showSettingsModal = function() {
        self.settings_error(new ErrorMessage());
        $("#settings-modal").modal();
    }
    
    self.load = function() {
        self.settings_error(new ErrorMessage());
        self.updating_settings(true);
        
        $.ajax({
            url: "/files/settings",
            success: function(data) {
                data = JSON.parse(data);
                self.filemanager_settings(new FileManagerSettings(data.home_directory, data.theme, data.font_size));
                
                filemanager.getDirectory(data.home_directory);
            },
            error: function(http) {
                self.settings_error().error(true);
                self.settings_error().message(http.responseText);
            },
            complete: function() {
                self.updating_settings(false);
            }
        });
        
    }
    
    self.saveSettings = function() {
        self.settings_error(new ErrorMessage());
        self.updating_settings(true);
        
        $.ajax({
            url: "/files/settings",
            type: "POST",
            data: {
                home_directory: self.filemanager_settings().home_directory(),
                theme: self.filemanager_settings().theme(),
                font_size: self.filemanager_settings().font_size()
            },
            success: function() {
                $.each(filemanager.tabs(), function(i, tab) {
                    tab.editor.setTheme("ace/theme/" + self.filemanager_settings().theme())
                    tab.editor.setOptions({
                      fontSize: self.filemanager_settings().font_size() + "pt"
                    });   
                });
            },
            error: function(http) {
                self.settings_error().error(true);
                self.settings_error().message(http.responseText);
            },
            complete: function() {
                self.updating_settings(false);
            }
        });
    }
}


var webinal = new WebinalViewModel();
ko.applyBindings(webinal, document.getElementById("navbar"));

$(function() {
    webinal.load();

    $('#side-menu').metisMenu();

	$(window).bind("load resize", function() {
        topOffset = 50;
        width = (this.window.innerWidth > 0) ? this.window.innerWidth : this.screen.width;
        if (width < 768) {
            $('div.navbar-collapse').addClass('collapse');
            topOffset = 100; // 2-row-menu
        } else {
            $('div.navbar-collapse').removeClass('collapse');
        }

        height = (this.window.innerHeight > 0) ? this.window.innerHeight : this.screen.height;
        height = height - topOffset;
        if (height < 1) height = 1;
        if (height > topOffset) {
            $("#page-wrapper").css("min-height", (height) + "px");
        }
    });
	
	
});

var nav_hidden = false;
var footer_level = 1;

$("#max_footer").click(function() {
    if(footer_level < 2) {
        footer_level++;
        if(footer_level == 2) {
            $("#footer").removeClass("level_1");
            $("#footer").addClass("level_2");
        } else if (footer_level == 1) {
            $("#footer").removeClass("level_0");
            $("#page-container").removeClass("page-container_0");
            
            $("#page-container").addClass("page-container_1");
            $("#footer").addClass("level_1");
        } 
    }        
});

$("#min_footer").click(function() {
    if(footer_level > 0) {
        footer_level--;
        if(footer_level == 0) {
            $("#footer").removeClass("level_1");
            $("#page-container").removeClass("page-container_1");
            
            $("#page-container").addClass("page-container_0");
            $("#footer").addClass("level_0");
        } else if (footer_level == 1) {
            $("#footer").removeClass("level_2");
            $("#footer").addClass("level_1");
        }
    }
});

$("#hide-nav").bind("click", function() {
    if(nav_hidden) {
        $("#nav-wrapper").removeClass("nav-hidden");
        $("#page").removeClass("full-page");
        $("#page").addClass("part-page");
        nav_hidden = false;
    } else {
        $("#nav-wrapper").addClass("nav-hidden");
        $("#page").addClass("full-page");
        $("#page").removeClass("part-page");
        nav_hidden = true;
    }
});

$("#min_footer").click();

function confirmExit()
{
    return "You are attempting to leave this page.  Any unsaved changes will be lost.";
}
window.onbeforeunload = confirmExit;


setupAjax();
