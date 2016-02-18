


/*=============================================================
    Authour URI: www.binarycart.com
    License: Commons Attribution 3.0

    http://creativecommons.org/licenses/by/3.0/

    100% To use For Personal And Commercial Use.
    IN EXCHANGE JUST GIVE US CREDITS AND TELL YOUR FRIENDS ABOUT US
   
    ========================================================  */

/*===================================
			CUSTOM METHODS
======================================*/
if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str){
        return this.slice(0, str.length) == str;
    };
}

function sendFiles(files, url, name, success_callback, error_callback, complete_callback, progress_callback) {
	try {	
		var percentComplete = 0;
		
		var client = new XMLHttpRequest();	
		var formData = new FormData();
	
		$.each(files, function(i, file) {
			formData.append(name, file, file.name);
		});
	
	  	client.open("post", url, true);
	  	client.setRequestHeader("X-CSRFToken", csrftoken);
		
		//transfer complete event listener
		client.addEventListener("load", function() {
		  	if (client.status === 200) {
		  	    try {
				    success_callback(JSON.parse(client.responseText));
				} catch (err) {
				    console.log(err);
				}				
		  	} else {
				error_callback("Something went wrong. An error occurred while uploading files.");
		  	}
		  	complete_callback();
		}, false);		
		
		//error event listener
	    client.addEventListener("error", function() {
	    	error_callback("Something went wrong. An error occurred while uploading files.");
		  	complete_callback();
	    }, false);	    
	   	
	   	//progress event listener
	   	client.upload.addEventListener('progress', function(e){
			percentComplete = Math.floor((e.loaded / e.total)*100);
			
			progress_callback(percentComplete);
		}, false);
	   	
		client.send(formData);
	}
	catch (err) {
		error_callback(err);
	}
}

function searchTable(table_id, search_term) {
    rows = $("#" + table_id + " tbody tr");
    rows.hide(); //hide all rows

    rows.each(function() { //loop over each row
		if($(this).find("td").text().toLowerCase().indexOf(search_term.toLowerCase()) >= 0) { //check value of TD
	       	$(this).show(); //show the row 
        }
    });
}

var alert_index = 0;
function AppendAlert(msg_class, msg, html_selector) {
	var html = '<div id="alert_' + alert_index + '" class="col-lg-12 alert alert-' + msg_class + ' alert-dismissable"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>' + msg + '</div>';
	
	$(html_selector).append(html);
	setTimeout(function() {
		$("#alert_" + alert_index).remove()
	}, 5000);
}

function TransitionDivs(hide, show, duration) {	
	$(hide).fadeOut(duration);
	
	setTimeout(function() { 
    	$(show).fadeIn(); 
    }, duration);
}

function sleep(millis, callback) {
    setTimeout(function() { 
    	callback(); 
    }, millis);
}

var csrftoken;

function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
		    var cookie = jQuery.trim(cookies[i]);
		    // Does this cookie string begin with the name we want?
		    if (cookie.substring(0, name.length + 1) == (name + '=')) {
		        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		        break;
		    }
		}
	}
	return cookieValue;
}
	
function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
		
function sameOrigin(url) {
	// test that a given url is a same-origin URL
	// url could be relative or scheme relative or absolute
	var host = document.location.host; // host + port
	var protocol = document.location.protocol;
	var sr_origin = '//' + host;
	var origin = protocol + sr_origin;
	// Allow absolute or scheme relative URLs to same origin
	return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
		(url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
		// or any other URL that isn't scheme relative or absolute i.e relative.
		!(/^(\/\/|http:|https:).*/.test(url));
}
		
function setupAjax() {
	csrftoken = getCookie('csrftoken');
	
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
				// Send the token to same-origin, relative URLs only.
				// Send the token only if the method warrants CSRF protection
				// Using the CSRFToken value acquired earlier
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});
}

setupAjax();

/*====================================
            LOAD LAYOUT
=======================================*/

         
(function ($) {
    "use strict";
    var mainApp = {

        main_fun: function () {
            /*====================================
            METIS MENU 
            ======================================*/
            $('#main-menu').metisMenu();

            /*====================================
              LOAD APPROPRIATE MENU BAR
           ======================================*/
            $(window).bind("load resize", function () {
                if ($(this).width() < 768) {
                    $('div.sidebar-collapse').addClass('collapse')
                } else {
                    $('div.sidebar-collapse').removeClass('collapse')
                }
            });
     
        },

        initialization: function () {
            mainApp.main_fun();

        }

    }
    // Initializing ///

    $(document).ready(function () {
        mainApp.main_fun();
    });

}(jQuery));
