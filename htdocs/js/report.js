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
	$.ajax({
		type: "GET",
		url: mercury.config.urlReport,
		dataType: "html",
		data: {
			'id': hash.courseids,
			'collate': hash.collate || 'collate_standard'
		},
        success: function(data, textStatus, jqXHR) {
        	jQuery('#report').html(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
        }
	});	
};

$(window).bind("hashchange", function(event) {
	mercury.report.update_from_hash();
});

jQuery(function() {
	mercury.report.init();
	mercury.report.update_from_hash();
});
