/*
 * Mercury: List view
 *
 */

// Page namespace
mercury.list = {};

 
// Object cache
mercury.c.$header = $("#header");
mercury.c.$select_container = $("#select_container");
mercury.c.$select_year = $("#select_year");
mercury.c.$select_tripos = $("#select_tripos");
mercury.c.$select_part = $("#select_part");
mercury.c.$courselist_container = $("#list_container");
mercury.c.$page_title = $(".page-title");
mercury.c.$courselist = $("#courselist");
mercury.c.$static_timetable_container = $("#static_timetable_container");
mercury.c.$static_timetables = $("#static_timetables");


// Interactivity wireing
mercury.list.wire = function() {

    // When select fields are changed
    $("#select_year,#select_tripos,#select_part").bind("change", function(e){

        // Update selected state
        // If a new year is selected default to the first available tripos for that year. If a new tripos is selected default to the first avaiable part of that tripos
        mercury.data.selectedYear = mercury.c.$select_year.val();
        for (var firstTripos in mercury.data.selector[mercury.data.selectedYear]) { break; }
        mercury.data.selectedTripos = (mercury.data.selector[mercury.data.selectedYear][mercury.c.$select_tripos.val()]) ? mercury.c.$select_tripos.val() : firstTripos;
        for (var firstPartID in mercury.data.selector[mercury.data.selectedYear][mercury.data.selectedTripos]) { break; }
        mercury.data.selectedTriposPartID = (mercury.data.selector[mercury.data.selectedYear][mercury.data.selectedTripos][mercury.c.$select_part.val()]) ? mercury.c.$select_part.val() : firstPartID;

        // Reflect state change in URL
        mercury.list.pushState();

        // Re-render based on new selection
        mercury.list.renderSelectors();
        mercury.list.renderCourseList();

    });


    // When there is a change in the URL hash
    $(window).bind("hashchange", function(event) {

        // Get previous state
        var hash_str = event.fragment;
        var hash = event.getState();

        if (hash_str !== "") {
            // Restore selection state
            mercury.data.selectedYear = hash.year;
            mercury.data.selectedTripos = hash.tripos;
            mercury.data.selectedTriposPartID = hash.tripospartid;

            // Re-render based on new selection
            mercury.list.renderSelectors();
            mercury.list.renderCourseList();
        }
    });

};

// (re)Renders the selectors in the top section, based on mercury.data.top
mercury.list.renderSelectors = function() {

    // Render year
    var yhtml = '';
    _.each(mercury.data.selector, function(ydata, year){
        var selected = (mercury.data.selectedYear === year) ? 'selected="true"' : "";
        yhtml += '<option value="'+year+'" '+selected+'>'+year+'</option>';
    });
    mercury.c.$select_year.html(yhtml);

    // Render tripos select
    var thtml = '';
    _.each(mercury.data.selector[mercury.data.selectedYear], function(tdata, tripos){
        var selected = (mercury.data.selectedTripos === tripos) ? 'selected="true"' : "";
        thtml += '<option value="'+tripos+'" '+selected+'>'+tripos+'</option>';
    });
    mercury.c.$select_tripos.html(thtml);

    // Render part select
    var phtml = '';
    _.each(mercury.data.selector[mercury.data.selectedYear][mercury.data.selectedTripos], function(part, partid){
        var selected = (mercury.data.selectedTriposPartID === partid) ? 'selected="true"' : "";
        phtml += '<option value="'+partid+'" '+selected+'>'+part.name+'</option>';
    });
    mercury.c.$select_part.html(phtml);

};

mercury.list.cached_calendars = {};
mercury.list.calendar_load = function(partid,cont) {
	var out = mercury.list.cached_calendars[partid]; 
	if(out === true) {
		return; // In progress
	} else if(out) {
		cont(mercury.list.cached_calendars[partid]);
	} else {
		mercury.list.cached_calendars[partid] = true; // loading
		mercury.common.pause_on();
		$.ajax({
	    	type: "GET",
	        url: mercury.config.urlCalendar,
	        dataType: "json",
	        data: {
	            "tripospartid": partid
	        },
	        success: function(data, textStatus, jqXHR) {
				mercury.list.cached_calendars[partid] = data;
				mercury.common.pause_off();
	        	cont(data);
			},
	        error: function(jqXHR, textStatus, errorThrown) {
				mercury.list.cached_calendars[partid] = undefined;
	            var error_msg = "Could not load data from the feed!";
	            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
	            mercury.data.calendar = {};
	        }
		});
	}
};

// Loads and (re)Renders the course list

mercury.list.renderCourseList = function() {

    mercury.common.get_user(function(user_data) {
        // Get course list based on selection
		var partid = mercury.data.selectedTriposPartID;
		mercury.list.calendar_load(partid,function(data) {
                // Store data
                mercury.data.calendar = data;
                // If this selection has a top level static URL to a PDF timetable stop here and just display that
                if (mercury.data.calendar.staticurls && mercury.data.calendar.staticurls.length > 0) {
    
                    var sulhtml = "";
                    _.each(mercury.data.calendar.staticurls, function(linkUrl){
                        var linkName = linkUrl.replace(/\\/g,'/').replace( /.*\//, '' );
                        sulhtml += '<li><a class="course-static-link" href="'+linkUrl+'">'+linkName+'</a></li>';
                    });
                    mercury.c.$static_timetables.html(sulhtml);
                    mercury.c.$static_timetable_container.show();
    
                } else if (mercury.data.calendar.courses) {
    
                    // If it's normal, render courses if data
                    var chtmls = {};
                    var courseids = [];
                    for(var k in mercury.data.calendar.courses) { courseids.push(k); }
                    
                    mercury.common.audit(courseids,function(audit_data) {
                        _.each(mercury.data.calendar.courses, function(cdata,cID){
                            var chtml = '<li class="course-list-item-container">';
        
                            // If this particular module has a static timetable display the link for it, otherwise display normal links to the clendar page
                            if (cdata.staticurls && cdata.staticurls.length > 0) {
        
                                chtml += ' <div class="course-list-coursename">'+cdata.name+'</div>';
                                chtml += ' <div class="course-list-staticurlmsg">Only static timetable available, please click on the link(s) below</div>';
                                _.each(cdata.staticurls, function(linkUrl){
                                    var linkName = linkUrl.replace(/\\/g,'/').replace(/\/$/,'').replace( /.*\//, '' );
                                    chtml += '<a class="course-static-link" href="'+linkUrl+'">'+linkName+'</a>';
                                });
        
                            } else {
                                chtml += ' <a class="course-list-courselink" href="view.html#course='+cID+'">'+cdata.name+'</a>';
                                chtml += ' <div class="course-list-termlink-container">';
                                
                                
    
    	                        termhtml = "&year="+mercury.data.selectedYear;
    	                        _.each(mercury.config.terms, function(term){
    	                            termhtml += "&terms[]="+term;
    	                        });                                
    	  
    
        						// view
        						chtml += '<a class="course-list-termlink" href="view.html#course='+cID+'">view as timetable</a>'; // XXX temporary hack by dan
        						chtml += '<a class="course-list-termlink" href="report.html#tripospartid='+mercury.data.selectedTriposPartID+'&courseids[]='+cID+termhtml+'">view as report</a>';
                                
                                if(user_data.all || user_data.triposes[cID.substr(0,14)]) {                            
            						// edit
            						chtml += "<br/>";
                                    chtml += '<a class="course-list-termlink" href="calendar.html#tripospartid='+mercury.data.selectedTriposPartID+'&courseids[]='+cID+termhtml+'">edit online</a>';
                                    chtml += '<a class="course-list-termlink" href="php/download.php?id='+cID+'">download as spreadsheet</a>';
                                    chtml += '<a class="course-list-upload course-list-termlink" data-id="'+cID+'" href="javascript:;">upload new spreadsheet</a><br/><br/>';
                                    var shtml = audit_data[cID].status+" (changed by "+audit_data[cID].who+", "+audit_data[cID].time+')';                        
                                    chtml += 'audit status: <em id="status_id_'+cID+'">'+ shtml +'</em> <a class="status_update course-list-termlink" data-id="'+cID+'">[update status]</a>';
                                }
                                chtml += ' </div>';
        
                            }
                            chtml += '</li>';
                            chtmls[cdata.name]=chtml;
                        });
                        var finalchtml = _.reduce(_.keys(chtmls).sort(),function(m,v) { return m+chtmls[v]; },"");
                        mercury.c.$courselist.html(finalchtml);

                        jQuery('.status_update').click(function() {
                            id = jQuery(this).data('id');
                            mercury.common.audit([id],function(data) {
                                jQuery('#status_id').attr('value',id);
                                jQuery('#status_status').attr('value',data[id].status);
                                jQuery('#status_update').dialog('open'); 
                            });                    
                        });
		                jQuery('.course-list-upload').click(function() {
		                    var id = jQuery(this).data('id');
		                    jQuery('#upload_id').attr('value',id);
		                    jQuery('#upload_spreadsheet').dialog('open');
		                });

                    });                    
    
                } else {
                    alert("There is no course information available in the course feed!");
                }
    
                // Update page title
                mercury.c.$page_title.html(mercury.data.selectedTripos+" &raquo; "+$("option[value='"+mercury.data.selectedTriposPartID+"']").html()+" in "+mercury.data.selectedYear);

                jQuery('#upload_spreadsheet').dialog({ 'autoOpen': false, 'width': 600, 'modal': true });    
                // Upload dialog

                // Audit update
                jQuery('#status_update').dialog({ 'autoOpen': false, 'width': 600, 'modal': true });

                jQuery('#status_update_button').click(function() {
                    var id = jQuery('#status_id').attr('value');
                    var status = jQuery('#status_status').attr('value');
                    mercury.common.audit_update(id,status,function(data) {
                        var html = data.status+" (changed by "+data.who+", "+data.time+')';                        
                        jQuery('#status_id_'+id).html(html);
                        jQuery('#status_update').dialog('close');
                    });
                });			
		});
    });
};

mercury.list.upload_done = function(success) {
    if(success) {
        alert("ERROR! "+success);    
    } else {
        alert("upload successful");        
    }
    jQuery('#upload_spreadsheet').dialog('close');
};

// Saves current state of the app and pushes current selection into the URL hash
mercury.list.pushState = function() {

    // Push a new state and alter URL
    $.bbq.pushState({
        "year": mercury.data.selectedYear,
        "tripos": mercury.data.selectedTripos,
        "tripospartid": mercury.data.selectedTriposPartID
    });

    // Store selection in a cookie/local storage too
    $.jStorage.set("mercury-list-selection", {
        "year": mercury.data.selectedYear,
        "tripos": mercury.data.selectedTripos,
        "tripospartid": mercury.data.selectedTriposPartID
    });

};


// Page init function
mercury.list.init = function() {

    // Fetch top feed
    $.ajax({
        type: "GET",
        url: mercury.config.urlTop,
        dataType: "json",
        success: function(data, textStatus, jqXHR) {

            if (data !== null) {
                // Save data in memory
                mercury.data.top = data;

                // Transform top data into a form which is easier to drive selectors from
                mercury.data.selector = mercury.processTopData(mercury.data.top);

                // Read URL hash
                var hash = $.deparam.fragment();

                // Read state stored in local storage
                var storedState = ($.jStorage.get("mercury-list-selection") || false);

                // Use state from URL if exists, then see if we have a state saved in cookie, otherwise use defaults
                var selection = {
                    "selectedYear": (hash.year || storedState.year || data.years[0]["name"]),
                    "selectedTripos": (hash.tripos || storedState.tripos || mercury.config.defaultTripos),
                    "selectedTriposPartID": (hash.tripospartid || storedState.tripospartid || "")
                };
                
                // Check storedstate is ok or you can lock yourself out
                if(!mercury.data.selector[selection.selectedYear]) {
                	mercury.common.abort();
                }
                if(!mercury.data.selector[selection.selectedYear][selection.selectedTripos]) {
                	selection.selectedTripos = "";
				}
                if (selection.selectedTripos === "") {
                    for (var tid in mercury.data.selector[selection.selectedYear]) {
                        selection.selectedTripos = tid ;
                        break;
                    }
                }				
                if(!mercury.data.selector[selection.selectedYear][selection.selectedTripos][selection.selectedTriposPartID]) {
					selection.selectedTriposPartID = "";
				}
                if (selection.selectedTriposPartID === "") {
                    for (var tpid in mercury.data.selector[selection.selectedYear][selection.selectedTripos]) {
                        selection.selectedTriposPartID = tpid ;
                        break;
                    }
                }
                if(!mercury.data.selector[selection.selectedYear][selection.selectedTripos][selection.selectedTriposPartID]) {
					mercury.common.abort();            	
                }

                // Set up selections for the first time
                mercury.data.selectedYear = selection.selectedYear;
                mercury.data.selectedTripos = selection.selectedTripos;
                mercury.data.selectedTriposPartID = selection.selectedTriposPartID;

                mercury.list.pushState();

                // Wire up
                mercury.list.wire();

                // Render selector area
                mercury.list.renderSelectors();
                mercury.list.renderCourseList();
                mercury.c.$select_container.show();


            } else {
                alert("The following data feed did not produce any data: "+mercury.config.urlTop);
                mercury.data.top = {};
            }

        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not load data from the feed!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            mercury.data.top = {};
        }
    });

	mercury.common.login_link();
	
};

// Start with calling  page init function
$(document).ready(mercury.list.init());
