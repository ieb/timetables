mercury.report = {};

mercury.report.init = function() {
	mercury.common.login_link();
	$('#report_select a').click(function() {
		$.bbq.pushState({
			'collate': $(this).attr('id')
		});
	});
};

mercury.report.update_from_hash = function() {
	var hash = $.deparam.fragment();
	var collation = hash.collate || 'collate_standard';
	$.ajax({
		type: "GET",
		url: mercury.config.urlReport,
		dataType: "html",
		data: {
			'id': hash.courseids,
			'collate': collation
		},
        success: function(data, textStatus, jqXHR) {
        	jQuery('#report').html(data);
        	$('.selected').removeClass('selected');
        	$('#'+collation).parent('li').addClass('selected');
        },
        error: function(jqXHR, textStatus, errorThrown) {
        }
	});
};

$(window).bind("hashchange", function(event) {
	mercury.report.update_from_hash();
});

jQuery(function() {
	try {
		mercury.report.init();
		mercury.report.update_from_hash();
	} catch(err) {
	    var error = 'Javascript error on page caught by report init try/catch  :' + err;
    	mercury.common.report_error('error',error);
    	alert("An error occurred loading this page. Perhaps you are using an unsupported browser? I suggest the basic javascript-free version, linked below.");
	}

});
