function QuestionModal(modal_id) {
    qm = this;
    
    qm.modal_id = modal_id;
	qm.dialog = $("#" + modal_id);
	qm.dialog.css("z-index", 9000);
	
    qm.dialog_html = '<div class="modal-dialog">' +
        '<div class="modal-content">' +
            '<div class="modal-header" id="question-header">' +
                '<img src="/assets/img/question.png" style="padding-left:5px;" />' +
                '<span class="modal-title" style="font-weight:bold;font-size:16pt;" id="question-heading"></span>' +
	        '</div>' +
	        '<div class="modal-body" style="overflow:hidden;">' +
	          	'<div>' +
			        '<div class="tab-pane">' +
				        '<span id="question-content"></span>' +
				    '</div>' +
			    '</div>' +
			    '<div style="text-align:center;display:none;" id="question-loading">' +
				    '<img src="/assets/img/big_red_loader.gif" style="height:100px;"/>' +
				    '<br/>' +
				    '<img src="/assets/img/text_loader.gif" style="height:30px;"/>' +	
			    '</div>' +
			    '<div id="question-error">' +
			    '</div>' +
	        '</div>' +
	        '<div class="modal-footer" id="question-footer">' +
	            '<button type="button" class="btn btn-success" id="question-yes-btn">Yes</button>' +
	            '<button type="button" class="btn btn-danger" id="question-close-btn">No</button>' +
	        '</div>' +
	    '</div>' +
	'</div>';
	
	qm.dialog.html(qm.dialog_html);
        
    $("#question-close-btn").on('click', function() {
        qm.No();
    });
    
    $("#question-yes-btn").on('click', function() {
        qm.Yes();
    });
    
    qm.ToggleLoading = function(loading) {
        if (loading) {
            $("#question-footer").hide();
            $("#question-content").hide();
            $("#question-header").hide();
            $("#question-loading").show();
        } else {
            $("#question-footer").show();
            $("#question-content").show();
            $("#question-header").show();
            $("#question-loading").hide();
        }
    }
    
    qm.Show = function(heading, question, yes_action, no_action) {
        $("#question-content").html(question);
        $("#question-heading").html(heading);
        
        qm.dialog.modal({ 
		    "backdrop": "static"
		});
		
		qm.Yes = yes_action;
		
		if(typeof no_action != "undefined") {
		    qm.No = no_action;
		}
		
        qm.ToggleLoading(false);       
    }
    
    qm.ShowError = function(message) {
        AppendAlert("danger", message, "#question-error");
    }
    
    qm.Yes = function() {
        console.log('No Yes function');
    }
    
    qm.No = function() {
        qm.Hide();
    }
    
    qm.Hide = function() {
        qm.dialog.modal('hide');
        
        qm.Yes = function() {
            console.log('No Yes function');
        }
        
        qm.No = function() {
            qm.Hide();
        }
    }
}
