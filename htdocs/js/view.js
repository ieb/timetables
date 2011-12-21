mercury.view = mercury.view || {};

// Object cache
mercury.c.$calendar_container = $("#calendar_container");
mercury.c.$calevent_text = $("#calevent_text");

mercury.c.$select_container = $("#cal_select_container");
mercury.c.$select_year = $("#select_year");
mercury.c.$select_tripos = $("#select_tripos");
mercury.c.$select_part = $("#select_part");
mercury.c.$select_course = $("#select_course");

(function($) {

    var fc = $.fullCalendar;
    var formatDate = fc.formatDate;
    var parseISO8601 = fc.parseISO8601;
    var addDays = fc.addDays;
    var applyAll = fc.applyAll;

})(jQuery);

mercury.view.cleantext = function(name,text) {
	return name+text;
};

mercury.view.clear_basic = function() {
	$('.head').html('');            	
	$('#hideshowlinks').css('display','none');
};

mercury.view.load_basics = function(ids) {
	var any = false;
	if(ids.length) {
		mercury.view.load_basic(ids[0],function(text_here) {
			any |= text_here;
			if(ids.length>1) {
				mercury.view.load_basics(ids.splice(1));
			} else {
				if(any) {
					$('#hideshowlinks').css('display','block');	
				}				
			}
		});
	}
}

mercury.view.load_basic = function(id,cont) {

    $.ajax({
        type: "GET",
        url: mercury.config.urlDetails,
        data: {
            "courseid": id
        },
        dataType: "json",
        success: function(data, textStatus, jqXHR) {
        	all = data.metadata.head + " " + data.metadata.foot;
			if(!$.trim(all)) {
				cont(false);
				return;
			}
			name = "<b>"+data.name+":</b> ";
            if (data !== null) {
            	$('.head').append(mercury.view.cleantext(name,all));            	
            } else {
                alert("The following data feed did not produce any data: "+mercury.config.urlDetails);
                mercury.data.top = {};
            }
            cont(true);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not load data from the feed!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            mercury.data.details = {};
        }
    });
};

mercury.view.feed_success = function(data) {                    
    var events = [];
    if (data.feed.entry) {
        $.each(data.feed.entry, function(i, entry) {
            var startStr = entry['gd$when'][0]['startTime'];
            var start = $.fullCalendar.parseISO8601(startStr, true);
            var end = $.fullCalendar.parseISO8601(entry['gd$when'][0]['endTime'], true);
            var allDay = startStr.indexOf('T') == -1;
            var url;
            $.each(entry.link, function(i, link) {
                if (link.type == 'text/html') {
                    url = link.href;
                }
            });
            if (allDay) {
                addDays(end, -1); // make inclusive
            }
            events.push({
                id: entry['gCal$uid']['value'],
                title: entry['title']['$t'],
                url: url,
                start: start,
                end: end,
                allDay: allDay,
                location: entry['gd$where'][0]['valueString'],
                description: entry['content']['$t']
            });
        });
    }
    var args = [events].concat(Array.prototype.slice.call(arguments, 1));
    var res = $.fullCalendar.applyAll(true, this, args);
    if ($.isArray(res)) {
        return res;
    }
    
    return events;
};

mercury.view.colour = function(id) {
	// We build indexes out of the last three digits as a number and a hash of the rest in the MSB.
	// That means in typical views, where it's the last three digits that vary, we guarantee
	// different colours.
	var suffix = parseInt(id.substr(id.length-3),10);
	var prefix = id.substr(0,id.length-3);
	// Simple hash function. We need not be the CIA here in our colour choices!
	var h = 0;
	for(var j=0;j<prefix.length;j++) {
		h = ((h * 40503) + prefix.charAt(j).charCodeAt()) % 65535;
	}
	h += suffix;
	return mercury.config.calendarColors[h%mercury.config.calendarColors.length];
};

mercury.view.calendar_data = function(id,cont) {

    $.ajax({
        type: "GET",
        url: mercury.config.urlCalendar,
        data: {
            "tripospartid": id
        },
        dataType: "json",
        success: function(data, textStatus, jqXHR) {
            if (data !== null) {
                cont(true,data);
            } else {
                cont(false,[]);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not load data from the feed!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            cont(false,[]);
        }
    });
};

mercury.view.convert_id_to_path = function(id,cont) {
	// XXX cache
	try {
		var cid = id.substr(0,14);
		var reversed = mercury.data.reverse_top[cid];
		mercury.view.calendar_data(cid,function(success,data) {
			if(success && data !== null) {
				var subj = false;
				if(id.length>14)
					subj = data.courses[id].name;
				cont(true,[reversed[0],reversed[1],reversed[2],cid,subj],data);
			} else {
				cont(false,[]);
			}
		});	
	} catch(err) {
		cont(false,[]);
	}
};

mercury.view.dropdown_update = function($selector,source,sel_in,data_cb,sel_cb) {
	if(typeof data_cb !== 'function') {
		data_cb = function(data,text) { return text; };
	}
	if(typeof sel_cb !== 'function') {
		sel_cb = function(value) { return value == sel_in; };
	}	
	var options = {};
    _.each(source, function(data, text){
        var selected = sel_cb(text) ? 'selected="true"' : "";
		var display = data_cb(data,text);
		options[display] = '<option value="'+text+'" '+selected+'>'+display+'</option>';
    });
    var keys = _.keys(options);
    keys.sort();
	var html = '';
	_.each(keys,function(x) {
		html += options[x];
	});    
    $selector.html(html);	
};

mercury.view.setup_multi = function($selector,what,minwidth,min_to_summary) {
    // Initialise multiselect for subjects
    $selector.multiselect({
        selectedText: "# of # "+what+" selected",
        noneSelectedText: "Select "+what,
        selectedList: min_to_summary,
        minWidth: minwidth
    });	
};

mercury.view.multi_change = function($what,callback) {
    $what.bind("multiselectclick multiselectcheckall multiselectuncheckall", function(e, ui){
    	callback();
	});	
};

mercury.view.single_change = function($what,callback) {
	$what.bind("change",function(e,ui) {
		callback();
	});
};

mercury.view.update_hash_from_course = function() {
    var selected = mercury.c.$select_course.multiselect("getChecked").map(function(){ return this.value; }).get();
	if(selected.length==0) {
		$.bbq.pushState({
			'part': mercury.c.$select_part.val()
		},2);
	} else {
	    var courses = selected.join(',');
	    $.bbq.pushState({
	    	'course': courses
		},2);
	}
	mercury.view.recompute();
};

mercury.view.render_path = function(sel_year,sel_tripos,sel_part,courses,ids) {
	mercury.view.dropdown_update(mercury.c.$select_year,mercury.data.selector,sel_year);
	mercury.view.dropdown_update(mercury.c.$select_tripos,mercury.data.selector[sel_year],sel_tripos);
	mercury.view.dropdown_update(mercury.c.$select_part,mercury.data.selector[sel_year][sel_tripos],sel_part,function(data,text) { return data.name; });
	mercury.view.dropdown_update(mercury.c.$select_course,courses,ids,function(data,text) { return data.name; },function(val) { return _.indexOf(ids,val) !== -1; });
    mercury.c.$select_course.multiselect("refresh");
};

mercury.view.choose_part = function(year,tripos) {
	var data = mercury.data.selector[year][tripos];
	for(var id in data)
		return id;
	return undefined;	
};

mercury.view.update_dropdowns = function() {
	// We might need to choose another part if it doesn't match our dropdowns (eg change year)
	var part_sel = mercury.c.$select_part.val();
	mercury.view.convert_id_to_path(part_sel,function(success,data,cal) {
		if(!success)
			return;
		var sel_year = mercury.c.$select_year.val();
		var sel_tripos = mercury.c.$select_tripos.val();
		if(sel_year != data[0] || sel_tripos != data[1]) {
			part_sel = mercury.view.choose_part(sel_year,sel_tripos);
		}
		//
		$.bbq.pushState({
			'part': part_sel
		},2);
		mercury.view.render_selectors_and_update();
	});
};

mercury.view.render_selectors_and_update = function() {
	var tc = mercury.view.cur_part_and_subjects();
	mercury.view.setup_multi(mercury.c.$select_course,'subjects',$(window).width()/2 - 100,4);	
	var src = tc[0];
	if(tc[1].length) {
		src = tc[1][0];
	}
	mercury.view.convert_id_to_path(src,function(success,data,cal) {
		if(!success)
			return;
		tc = mercury.view.cur_part_and_subjects();
		mercury.view.render_path(data[0],data[1],data[3],cal.courses,tc[1]);
		mercury.view.recompute();
	});
};

mercury.view.cur_part_and_subjects = function() {
    var hash = $.deparam.fragment();
	if(hash.course) {
		var courses = hash.course.split(/,/);
		var tripos = courses[0].substr(0,14);
		return [tripos,courses];
	} else {
		var tripos = hash.part;
		return [tripos,[]];		
	}
}

mercury.view.init = function() {
    var hash = $.deparam.fragment();    

	var right = 'month,agendaWeek,agendaDay';
	var weekends = true;
    if(hash.embed) {
    	right = '';
    	if(hash.nowe)
    		weekends = false;
    	$("html,body").css('overflow','auto');
	}
    
	$('#view_popup').dialog({
		'autoOpen': false
	});


	$('#embed_popup').dialog({
		'autoOpen': false,
		'width': '90%'
	});
	
	$('#embed_out a').click(function() {
		try {
			if (self.parent.frames.length != 0) {
			var here = document.location.href;
			here = here.replace('embed.html','view.html');
			self.parent.location=here;
			}
		}
		catch (Exception) {}
	});
	
	$('#embed').click(function() { $('#embed_popup').dialog('open'); return false; });

    // Init calendar
    mercury.data.calendarInstance = mercury.c.$calendar_container.fullCalendar({
        theme: false,
        aspectRatio: 1.4,
        firstDay: 1,
        minTime: 8,
        maxTime: 18,
        firstHour: 8,
        defaultView: 'agendaWeek',
        weekends: weekends,
        header: {
            left: 'prev,next today',
            center: 'title',
            right: right
        },
        firstHour: 8,
        allDaySlot: false,
        titleFormat: {
 		   month: 'MMMM yyyy',
    		week: "d MMM [ yyyy]{ '&#8212;'d  MMM  yyyy}",
		    day: 'dddd, d MMM, yyyy'
		},
		columnFormat: {
 		   month: 'ddd',    // Mon
 		   week: 'ddd d/M', // Mon 9/7
    		day: 'dddd d/M'  // Monday 9/7
		},
		eventClick: function(calEvent, jsEvent, view) {
			$('#view_popup').dialog('open');
			$('#view_details').html(calEvent.description);
			return false;
	    },
	    // Callback when hovering over an element
        eventMouseover: function(event, jsEvent, view) {
            mercury.c.$calevent_text.text(event.title);
        },

        eventMouseout: function(event, jsEvent, view) {
            mercury.c.$calevent_text.text("");
        },
        loading: function(isLoading,view) {
			if(isLoading)
				mercury.common.pause_on();
			else
				mercury.common.pause_off();			
        }    
    });

    $.ajax({
        type: "GET",
        url: mercury.config.urlTop,
        dataType: "json",
        success: function(data, textStatus, jqXHR) {

            if (data !== null) {
                // Save top data locally
                mercury.data.top = data;

                // Transform top data into a form which is easier to drive selectors from
                mercury.data.selector = mercury.processTopData(mercury.data.top);
				mercury.data.reverse_top = mercury.reverseTopData(mercury.data.top);

			    mercury.c.$select_container.hide(); // Prevent flash
				mercury.view.render_selectors_and_update();
			    mercury.c.$select_container.show();				
				mercury.view.single_change(mercury.c.$select_year,mercury.view.update_dropdowns);
				mercury.view.single_change(mercury.c.$select_tripos,mercury.view.update_dropdowns);
				mercury.view.single_change(mercury.c.$select_part,mercury.view.update_dropdowns);
				mercury.view.multi_change(mercury.c.$select_course,mercury.view.update_hash_from_course);

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

	$(window).bind("hashchange", function(event) {
		mercury.view.render_selectors_and_update();		
	});
	
	$('#headfoothide').click(function() {
		$('#headfoothide').css('display','none');
		$('#headfootshow').css('display','block');
		$('#headfootshy').css('display','none');
		return false;
	});
	$('#headfootshow').click(function() {
		$('#headfootshow').css('display','none');
		$('#headfoothide').css('display','block');
		$('#headfootshy').css('display','block');
		return false;
	});	
};

mercury.view.current_sources = [];

mercury.view.recompute = function() {
	mercury.view.recompute_calendar();
	mercury.view.recompute_embed();
};

mercury.view.recompute_embed = function() {
	var tc = mercury.view.cur_part_and_subjects();
	var ids = tc[1].join(',');
	var root = mercury.data.top.root;
	var rnd = Math.floor(Math.random()*100000000);
	var gcal = root + "php/gcal.php?rnd="+rnd+"&course="+ids;
	$('#embed_ical').attr('href',gcal+"&type=ical");
	$('#embed_ical').html(gcal+"&type=ical");
	$('#embed_gcal').attr('href',gcal);
	$('#embed_gcal').html(gcal);
	var frame = '<iframe src="'+root+'embed.html#course='+ids+'&embed=1" style="min-width: 600px; border: 0" width="100%" height="570"></iframe>';	
	$('#embed_embed').text(frame);
};

mercury.view.recompute_calendar = function() {
	var tc = mercury.view.cur_part_and_subjects();
	var courses = tc[1];
        
    
	toadd = {};
	togo = {};
	old = [];
	for(var i=0;i<mercury.view.current_sources.length;i++) {
		togo[mercury.view.current_sources[i].url] = 1;
		old.push(mercury.view.current_sources[i]);
	}	
	mercury.view.clear_basic();
	mercury.view.current_sources = [];
	mercury.view.load_basics(courses);
	for(var i=0;i<courses.length;i++) {
		var colours = mercury.view.colour(courses[i]);
		url = mercury.config.wcalFeedURL+"?course="+courses[i];
    	mercury.view.current_sources.push({
            url: url,
            success: mercury.view.feed_success,
            backgroundColor: colours.backgroundColour,
            borderColor: '#BDB219',
            textColor: '#222'			    		
    	});
    	if(!togo[mercury.view.current_sources[i].url]) {
    		toadd[mercury.view.current_sources[i].url] = 1;
    	}
		togo[mercury.view.current_sources[i].url] = 0;
	}
	for(var i=0;i<old.length;i++) {
		if(togo[old[i].url]) {
		    mercury.data.calendarInstance.fullCalendar('removeEventSource',old[i]);
		}
	}
	for(var i=0;i<mercury.view.current_sources.length;i++) {
		if(toadd[mercury.view.current_sources[i].url]) {
	    	mercury.data.calendarInstance.fullCalendar('addEventSource',mercury.view.current_sources[i]);
	   	}
	}	
    mercury.data.calendarInstance.fullCalendar('refetchEvents');	        
};



// Start with calling  page init function
$(document).ready(function() {
	mercury.view.init();
});