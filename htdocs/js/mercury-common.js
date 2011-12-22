/*
 * MERCURY: Common JS
 * Functionality which is general, used across many pages within the app
 */

if(!$) {
	alert("Your browser is too old to use this applicaiton. It is probably at risk from attacks on the internet to, so it's a good idea to upgrade. Otherwise, why not try a different browser on this computer?");
}

// Namespaces
var mercury = window.mercury || {};         // Root namespace
mercury.data = {};                          // Data - calendar data in memory, state, etc...
mercury.c = {};                             // jQuery object cache
mercury.config = {};


// Config

// Config > URLs
mercury.config.urlTop = "php/top.php";
mercury.config.urlCalendar = "php/calendar.php";
mercury.config.urlDetails = "php/details.php";
mercury.config.urlAuth = "php/auth.php";
mercury.config.urlLog = "php/log.php";
mercury.config.urlDelegations = "php/delegations.php";
mercury.config.urlAutocompleteCourseTitles = "php/autocomplete_coursetitles.php";
mercury.config.urlAutocompletePeople = "autocomplete_people.php";
mercury.config.urlAutocompleteLocations = "autocomplete_locations.php";
mercury.config.urlCheckPersonUniqueness = "php/check_person_uniqueness.php";
mercury.config.urlCheckLocationUniqueness = "php/check_location_uniqueness.php";
mercury.config.urlUser = "php/user.php";
mercury.config.urlDelegate = "php/delegate.php";
mercury.config.urlRescind = "php/rescind.php";
mercury.config.urlPing = "php/ping.php";
mercury.config.urlLock = "php/lock.php";
mercury.config.urlList = "list.html";
mercury.config.urlAbort = "list.html";
mercury.config.urlLogin = "login.html";
mercury.config.urlReport = "php/report.php";
mercury.config.urlAudit = "php/audit.php";


// Config > Calendar
mercury.config.calendarBaseYear = 2000;     // Date needs to be chosen carefully - Baseday should fall on the starting day of the calendar
mercury.config.calendarBaseMonth = 4;       // Date needs to be chosen carefully - Baseday should fall on the starting day of the calendar
mercury.config.calendarBaseDay = 11;        // Date needs to be chosen carefully - Baseday should fall on the starting day of the calendar
mercury.config.calendarBackgroundColor = "#aaccdd";
mercury.config.calendarTextColor = "#333333";
mercury.config.weekDays = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
mercury.config.weekDaysOrder = [3,4,5,6,0,1,2];
mercury.config.firstHour = 8;
mercury.config.minTime = 8;
mercury.config.maxTime = 20;

// Config > Defaults
mercury.config.defaultTripos = "AMES";
mercury.config.defaultNumberOfWeeks = 10;
mercury.config.defaultEventDataTemplate = {
    "day": 0,
    "starttime": [0,0],
    "endtime": [0,0],
    "cid": "",
    "cname": "",
    "text": "",
    "what": "",
    "organiser": "",
    "where": "",
    "when": "",
    "type": "Lecture",
    "terms": [1,1,1]
};

// Config > Lookups
mercury.config.terms = ["Michaelmas","Lent","Easter"];
mercury.config.courseTypes = ["Lecture","Lab","Field trip","Examples class", "Other"];
mercury.config.calendarColors = [
    {"backgroundColour":"#6c8cd5","textColour":"#222222","borderColour":"#4671d5"},
    {"backgroundColour":"#e667af","textColour":"#222222","borderColour":"#e6399b"},
    {"backgroundColour":"#ffdc73","textColour":"#222222","borderColour":"#ffcf40"},
    {"backgroundColour":"#ffc373","textColour":"#222222","borderColour":"#ffad40"},
    {"backgroundColour":"#876ed7","textColour":"#222222","borderColour":"#6a48d7"},
    {"backgroundColour":"#c9f76f","textColour":"#222222","borderColour":"#b9f73e"},
    {"backgroundColour":"#ff9d73","textColour":"#222222","borderColour":"#ff7940"},
    {"backgroundColour":"#5ccccc","textColour":"#222222","borderColour":"#33cccc"},
    {"backgroundColour":"#ff7373","textColour":"#222222","borderColour":"#ff4040"},
    {"backgroundColour":"#7373d9","textColour":"#222222","borderColour":"#4f4fd9"},
    {"backgroundColour":"#ffe773","textColour":"#222222","borderColour":"#ffde40"},
    {"backgroundColour":"#66a3d2","textColour":"#222222","borderColour":"#3f92d2"},
    {"backgroundColour":"#a9f16c","textColour":"#222222","borderColour":"#8ef13c"},
    {"backgroundColour":"#cf5fd3","textColour":"#222222","borderColour":"#cd35d3"},
    {"backgroundColour":"#996ad6","textColour":"#222222","borderColour":"#8243d6"},
    {"backgroundColour":"#f16c97","textColour":"#222222","borderColour":"#f13d76"},
    {"backgroundColour":"#ad66d5","textColour":"#222222","borderColour":"#9f3ed5"},
    {"backgroundColour":"#e1fa71","textColour":"#222222","borderColour":"#d8fa3f"},
    {"backgroundColour":"#61d7a4","textColour":"#222222","borderColour":"#36d792"},
    {"backgroundColour":"#ffd073","textColour":"#222222","borderColour":"#ffbf40"},
    {"backgroundColour":"#fffd73","textColour":"#222222","borderColour":"#fffd40"},
    {"backgroundColour":"#fff273","textColour":"#222222","borderColour":"#ffee40"},
    {"backgroundColour":"#67e667","textColour":"#222222","borderColour":"#39e639"}
];

// Config > UI things
mercury.config.messageTimeToLive = 4000; // Time for how long the Growl like messages appear in msec

// Config > Student view
mercury.config.gcalFeedURL = "php/gcal.php";
mercury.config.wcalFeedURL = "php/wcal.php";


// Console object declaration for browsers which don't support it
if (!window.console) {
    window.console = {};
    window.console.log = function(){};
    window.console.dir = function(){};
    window.console.time = function(){};
    window.console.timeEnd = function(){};
};


// global to prevent error cascade on abort
var aborting = false;

// Transforms top data into a form which is more suitable to drive the selectors from
mercury.processTopData = function(rawTop) {
    var selector = {};
    _.each(rawTop.years, function(yeardata, yearindex){

        selector[yeardata.name] = {};

        _.each(yeardata.triposes, function(triposdata, triposindex){

            selector[yeardata.name][triposdata.name] = {};

            _.each(triposdata.parts, function(partdata, partindex){
                var p = {};
                p.name = partdata.name;
                selector[yeardata.name][triposdata.name][partdata.id] = p;
            });
        });
    });
    return selector;
};

mercury.reverseTopData = function(rawTop) {
	var out = {};
    _.each(rawTop.years, function(yeardata, yearindex){
        _.each(yeardata.triposes, function(triposdata, triposindex){
            _.each(triposdata.parts, function(partdata, partindex){
				out[partdata.id] = [yeardata.name,triposdata.name,partdata.name];
            });
        });
    });	
    return out;
};

// General ajax error handler
function ajaxError(event, jqXHR, ajaxSettings, thrownError, error_msg){

    // The local error handler passes the local context, so 'this' refers to the originating $.ajax object

    if (jqXHR.status == 409) {
		if(!aborting)
			alert("Unfortunately, someone updated this data before you had a chance: please reload this page to get the most recent version and then make your changes again.");
    } else {
        // Display an error message, provided by the local ajax error handler
        var serverMsg = (jqXHR.responseText) ? jqXHR.responseText : "An undescribed error occurred";
        if(!aborting)
	        alert(serverMsg);
    }

};

mercury.common = {};

// Stuff common to every page
mercury.common.get_user = function(cont) {
	if(mercury.common.user) {
		cont(mercury.common.user);
	}
    // Fetch top feed
    $.ajax({
        type: "GET",
        url: mercury.config.urlUser,
        dataType: "json",
        success: function(data, textStatus, jqXHR) {
			mercury.common.user = data;
			if(data['colour'])
				jQuery('#header').css('background',data['colour']);
			
			cont(mercury.common.user);			
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not load username!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
        }
    });

};

mercury.common.delegate = function(whom,what,cont) {
	$.ajax({
		type: "POST",
		url: mercury.config.urlDelegate,
		dataType: "json",
		data: {
			'whom': whom,
			'what': what
		},
        success: function(data, textStatus, jqXHR) {
			if(!data.success) {
				if(!aborting)
		            alert("Could not delegate!");
			}
        	cont(data.success);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not delegate!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            cont(false);
        }
	});
}

mercury.common.rescind = function(whom,what,cont) {
    $.ajax({
        type: "POST",
        url: mercury.config.urlRescind,
        dataType: "json",
        data: {
            'whom': whom,
            'what': what
        },
        success: function(data, textStatus, jqXHR) {
            if(!data.success) {
				if(!aborting)
	                alert("Could not rescind!");
            }
            cont(data.success);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not rescind!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            cont(false);
        }
    });
}

mercury.common.login_link = function() {

	// Populate login etc
	mercury.common.get_user(function(user) {

		// TITLE BAR

		var out = '';
		var home = "<a href='list.html'>home</a>";
		if(/list.html($|#)/.test(document.URL)) {
			home = "";
		}
		if(user.loggedin) {
			out = "Hello "+user.user+". <a href='index.html'>intro</a> "+home+" <a href='php/logout.php'>logout</a>"+
			      " <a class='user_delegate' href='javascript:;'>delegate</a>"+
			      " <a class='user_rescind' href='javascript:;'>rescind</a>"+
			      " <a href='log.html'>log</a>";
		} else {
			out = "<a href='index.html'>intro</a> "+home+" <a href='php/login.php'>admin login</a>";
		}

        // dialog common
        function dialog(name,options) {
            out = '<div id="<<_dialog" title="<>"><p>Which tripos: <select name="which" id="<<_which">'+options+'</select></p><p>Whom: <input type="text" id="<<_whom" name="whom"></p><button id="<<_button"><>!</button></div>';
            name = name.toLowerCase();
            out = out.replace(/<</g,name);
            uname = name.charAt(0).toUpperCase() + name.substr(1);
            out = out.replace(/<>/g,uname);
            return out;
        }
        
        function post_dialog(name,cont) {
            jQuery('#'+name+'_dialog').dialog({ 'autoOpen': false, 'width': 600, 'modal': true});

            jQuery('.user_'+name).click(function() {         
                jQuery('#'+name+'_dialog').dialog('open');
            });
                        
            jQuery('#'+name+'_button').click(function() {
                jQuery('#'+name+'_dialog').dialog('close');
                cont(jQuery('#'+name+'_whom').val(),jQuery('#'+name+'_which').val());
            });
        }

		// PREPARE DIALOGS

		var options = '';
		// Sorted list
		var tkeys = [];
		for(var k in user.triposes) { tkeys.push(k) };
		tkeys = tkeys.sort(function(a,b) {
			if(user.triposes[a]<user.triposes[b]) return -1;
			return user.triposes[a]>user.triposes[b];	
		});
		for(var i=0;i<tkeys.length;i++) {
			k = tkeys[i];
			options += '<option value="'+k+'">'+user.triposes[k]+'</option>';
		}
		out += dialog('delegate',options);		
        out += dialog('rescind',options);
		
        // INSERT
        jQuery('#link_login').html(out);

        post_dialog('delegate',function(whom,which) {
            mercury.common.delegate(whom,which,function(success) {
                if(success) {
                    jQuery.gritter.add({'title':'Success','text':'Delegation successful', time: 1000});
                }
            });            
        });
        post_dialog('rescind',function(whom,which) {
            mercury.common.rescind(whom,which,function(success) {
                if(success) {
                    jQuery.gritter.add({'title':'Success','text':'Rescinding successful', time: 1000});
                }
            });            
        });
	});
};

mercury.common.print_messages = function(data) {
	for(var k in data) {
		var v = data[k];
		var sk = 'message-'+k;
		if($.jStorage.get(sk))
		  continue;
		$.jStorage.set(sk,true);
		alert(v);
	}
};

mercury.common.ping_interval = 60;

mercury.common.ping = function() {
	$.ajax({
		type: "GET",
		url: mercury.config.urlPing,
		dataType: "json",
		// Treat those two imposters just the same
        success: function(data, textStatus, jqXHR) {
        	if(data.messages)
	        	mercury.common.print_messages(data.messages);
			mercury.common.ping_interval = data.ping || 60;
        },
        error: function(jqXHR, textStatus, errorThrown) {
        }
	});	
};

mercury.common.lock_blase = false;
mercury.common.lock_steal = false;


mercury.common.lock_init = function(tripos,seconds) {
	var lock_dia_body = "<p><span id='lock_dialog_who'></span> seems to be currently editing this tripos (or has finished doing so in the last couple of minutes). There is a risk, if you are working on the same subjects, of attempting to "+
						"overwrite each other's data. At this point out-of-date updates will be rejected. If you believe this could be an issue, "+
						"to avoid frustration, we recommend you  edit this tripos later.</p><p>If you think it will be safe click <b>'Take that risk'</b>. "+
						"If you are pretty sure they are not working on it click <b>'steal lock'</b> to take it away from them. To leave this screen"+
						"click <b>'leave here'</b>.</p>";
	var lock_dia = jQuery("<div></div>").append(lock_dia_body);
	lock_dia.attr('id','lock_dialog')
	lock_dia.attr('title','Someone else is using the system');
	lock_dia.dialog({
		'autoOpen': false, 
		'modal': true,
		'width': 400,
		'buttons': [
			{
				'text': 'Leave here',
				'click': function() {
					window.location.href = mercury.config.urlList;
 		       		jQuery('#lock_dialog').dialog('close');
				}
			},
			{
				'text': 'Take that risk',
				'click': function() {
					mercury.common.set_blase();
 		       		jQuery('#lock_dialog').dialog('close');
				}
			},
			{
				'text': 'Steal lock',
				'click': function() {
 		       		jQuery('#lock_dialog').dialog('close');
 		       		mercury.common.lock_steal = true;
					mercury.common.lock(jQuery('#lock_dialog').data('tripos'),jQuery('#lock_dialog').data('time'));
				}
			}
		]
	});
};

mercury.common.set_blase = function() {
	mercury.common.lock_blase = true;
	$.jStorage.set("blase",new Date().getTime()+10*60*1000); // 10 minutes of peace
};

mercury.common.is_blase = function() {
	if(mercury.common.lock_blase)
	  return true;
	timeout = $.jStorage.get("blase");
	if(new Date().getTime() < timeout)
		return true;
	return false;
};

mercury.common.lock = function(tripos,seconds) {
	$.ajax({
		type: "POST",
		url: mercury.config.urlLock,
		dataType: "json",
		data: {
			'tripos': tripos,
			'time': seconds,
			'steal': mercury.common.lock_steal?'true':'false'
		},
        success: function(data, textStatus, jqXHR) {
        	if(!data.success) {
        		if(!aborting) {
        			if(!mercury.common.is_blase()) {
        				jQuery('#lock_dialog_who').html(data.user);
        				jQuery('#lock_dialog').data('tripos',tripos);
        				jQuery('#lock_dialog').data('time',seconds);
 		       			jQuery('#lock_dialog').dialog('open');
 		       		}
	        	}
        	}
        },
        error: function(jqXHR, textStatus, errorThrown) {
        }
	});	
	mercury.common.lock_steal = false;
};

mercury.common.spinner_init = function() {
	var spinner_text = "<p>working...</p><p><img src='images/ajax-loader.gif'/></p>";
	var spinner_box = jQuery('<div></div>').append(spinner_text);
	spinner_box.attr('style','text-align: center; margin: auto; width: 130px');
	var spinner = jQuery('<div></div>').append(spinner_box);
	spinner.attr('id','spinner');
	spinner.dialog({
		'autoOpen': false, 
		'modal': true,
		'width': 150,
		'height': 120	
	});
};

mercury.common.spin_on = function() {
	jQuery('#spinner').dialog('open');
};

mercury.common.spin_off = function() {
	jQuery('#spinner').dialog('close');
};

mercury.common.pause_count = 0;

mercury.common.pause_on = function() {
	if(mercury.common.pause_count)
		return;
	var $loader = $('<div></div>');
	$loader.attr('id','loader');
	$loader.text("Loading...");
    $loader.css("position","absolute");
    $loader.css("top", (($(window).height() - $loader.outerHeight()) / 2) + $(window).scrollTop() + "px");
    $loader.css("left", (($(window).width() - $loader.outerWidth()) / 2) + $(window).scrollLeft() + "px");
	$loader.css('background','red');
	$('body').append($loader);
	mercury.common.pause_count++;
};

mercury.common.pause_off = function() {
	mercury.common.pause_count--;
	if(!mercury.common.pause_count)
		jQuery('#loader').remove();
};

mercury.common.ping_loop = function() {
	mercury.common.ping();
	setTimeout(mercury.common.ping_loop,mercury.common.ping_interval*1000);
};

mercury.common.periodic_ping = function() {
	mercury.common.ping_loop();
};

mercury.common.audit = function(courses,cont) {
    $.ajax({
        type: "GET",
        url: mercury.config.urlAudit,
        dataType: "json",
        data: {
            'id': courses
        },
        success: function(data, textStatus, jqXHR) {
            cont(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
			if(!aborting)
	            alert("Cannot retrieve statuses "+errorThrown);
        }
    });     
};

mercury.common.audit_update = function(course,status,cont) {
    $.ajax({
        type: "POST",
        url: mercury.config.urlAudit,
        dataType: "json",
        data: {
            'id': course,
            'status': status
        },
        success: function(data, textStatus, jqXHR) {
            cont(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
			if(!aborting)
	            alert("Cannot update status");
        }
    });         
};

mercury.common.abort = function() {
	var index = $.jStorage.index();
	for(k in index) {
		$.jStorage.deleteKey(index[k]);
	}
	aborting = true;	
	window.location.href = mercury.config.urlAbort;
	//throw new Error('halt');
};

mercury.common.idle_init = function() {
	$.idleTimer(60*60*1000);

	$(document).bind("idle.idleTimer", function(){
		$.jStorage.set('idle',true);
		window.location.href = mercury.config.urlList;
	});
};

mercury.common.idle_note = function() {
	
	if($.jStorage.get('idle')) {
		$.jStorage.set('idle',false);
		var dia_in = "<p>You were taken back to this page because you did not use the timetable edit view for an hour. This could have prevented others using it.</p>";
		var dialog = jQuery("<div></div>");
		dialog.append(dia_in);
		dialog.dialog({ buttons: { 'OK': function() { dialog.dialog('close'); }}});
	} 
};

mercury.common.note = function() {
};

jQuery(function() { 
	mercury.common.lock_init();
	mercury.common.idle_note();
	mercury.common.spinner_init();
	mercury.common.periodic_ping();
	mercury.common.note();
	$('.product_title').click(function() { window.location.href = 'list.html' });
});
