/*
 * Mercury: List view
 *
 */

// Page namespace
mercury.calendar = {};

// Object cache
mercury.c.$header = $("#header");

mercury.c.$select_container = $("#cal_select_container");
mercury.c.$select_year = $("#select_year");
mercury.c.$select_tripos = $("#select_tripos");
mercury.c.$select_part = $("#select_part");
mercury.c.$select_course = $("#select_course");
mercury.c.$select_terms = $("#select_terms");
mercury.c.$calevent_text = $("#calevent_text");


mercury.c.$calendar_container = $("#calendar_container");

mercury.c.$quickedit_container = $("#quickedit_container");
mercury.c.$qe_subevent_selector_container = $("#qe_subevent_selector_container");
mercury.c.$qe_course_title = $("#qe_course_title");
mercury.c.$qe_course_what = $("#qe_course_what");
mercury.c.$qe_course_organiser = $("#qe_course_organiser");
mercury.c.$qe_course_location = $("#qe_course_location");
mercury.c.$qe_course_when = $("#qe_course_when");
mercury.c.$qe_ctype_predefined_selector = $("#qe_course_type_predefined");
mercury.c.$qe_ctype = $("#qe_course_type_exact");
mercury.c.$qe_edit_course_button = $("#qe_edit_course_button");
mercury.c.$qe_delete_course_button = $("#qe_delete_course_button");
mercury.c.$qe_edit_course_button = $("#qe_edit_course_button");

mercury.c.$delete_course_dialog = $("#delete_course_dialog_container");
mercury.c.$course_name_dialog = $("#course_name_dialog_container");
mercury.c.$course_organiser_dialog =  $("#course_organiser_dialog_container");
mercury.c.$course_location_dialog =  $("#course_location_dialog_container");


// Interactivity wireing
mercury.calendar.wire = function() {

    // When select fields are changed
    $("#select_year,#select_tripos,#select_part").bind("change", function(e){
        $(window).trigger("calendarredraw");
    });

    // Handler for the calendardraw event - which will read in selections, load in calendar data from the server and re-render the calendar view
    $(window).bind("calendarredraw", function(e){

        // Update selected state
        // If a new year is selected default to the first available tripos for that year. If a new tripos is selected default to the first avaiable part of that tripos
        mercury.data.selectedYear = mercury.c.$select_year.val();
        for (var firstTripos in mercury.data.selector[mercury.data.selectedYear]) { break; }
        mercury.data.selectedTripos = (mercury.data.selector[mercury.data.selectedYear][mercury.c.$select_tripos.val()]) ? mercury.c.$select_tripos.val() : firstTripos;
        for (var firstPartID in mercury.data.selector[mercury.data.selectedYear][mercury.data.selectedTripos]) { break; }
        mercury.data.selectedTriposPartID = (mercury.data.selector[mercury.data.selectedYear][mercury.data.selectedTripos][mercury.c.$select_part.val()]) ? mercury.c.$select_part.val() : firstPartID;

		mercury.calendar.lock();

        // Get new calendar data based on selectors
        mercury.calendar.loadCalendarData(mercury.data.selectedTriposPartID, function(success){

            // Select no courses by default
            mercury.data.selectedCourses = [];

            // Re-render based on new selection
            mercury.calendar.renderSelectors();

            // Re-render calendar view
            mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);

            // Reflect state in URL hash
            mercury.calendar.pushState();
        });

    });

    // When term filter is clicked
    mercury.c.$select_terms.bind("multiselectclick multiselectcheckall multiselectuncheckall", function(e, ui){


        // Update selected state
        var termnos = mercury.c.$select_terms.multiselect("getChecked").map(function(){ return this.value; }).get();
        mercury.data.selectedTerms = [];
        _.each(termnos, function(termno){
            mercury.data.selectedTerms.push(mercury.config.terms[termno]);
        });

        // Re-render calendar view
        mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);

        // Reflect state in URL hash
        mercury.calendar.pushState();

    });


    // When course filter is clicked
    mercury.c.$select_course.bind("multiselectclick multiselectcheckall multiselectuncheckall", function(e, ui){

        // Update selected state
        mercury.data.selectedCourses = [];
        mercury.data.selectedCourses = mercury.c.$select_course.multiselect("getChecked").map(function(){ return this.value; }).get();

        // Re-render calendar view
        mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);


        // Reflect state in URL hash
        mercury.calendar.pushState();

    });


    // When there is a change in the URL hash
    $(window).bind("hashchange", function(event) {

        // Load previous selected state
        var hash_str = event.fragment;
        var hash = event.getState();
        if (hash_str !== "") {

            var triposPartIDChanged = (mercury.data.selectedTriposPartID === hash.tripospartid) ? false : true;
            mercury.data.selectedTriposPartID = hash.tripospartid;

            mercury.data.selectedCourses = hash.courseids;
            mercury.data.selectedTerms = hash.terms;

			mercury.calendar.lock();

            // Re-render selectors
            mercury.calendar.renderSelectors();

            // Redraw calendar if there is a chaneg in tripospartID (otherwise is just a filter change, only redraw is needed)
            if (triposPartIDChanged) {

                // Get new calendar data based on selectors
                mercury.calendar.loadCalendarData(mercury.data.selectedTriposPartID, function(success){

                    // Re-render calendar view
                    mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);

                    // Reflect state in URL hash
                    mercury.calendar.pushState();

                });

            } else {
                // Re-render calendar view
                mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);
            }
        }

    });

};

// (re)Renders the selectors in the top section, based on mercury.data.top
mercury.calendar.renderSelectors = function() {

    // Hide container
    mercury.c.$select_container.hide();

    // Initialise multiselect for subjects
    mercury.c.$select_course.multiselect({
        selectedText: "# of # subjects selected",
        noneSelectedText: "Select subjects",
        selectedList: 4,
        minWidth: ($(window).width() - 400)
    });

    // Initialise multiselect for terms
    mercury.c.$select_terms.multiselect({
        selectedText: "# of # terms selected",
        noneSelectedText: "Select terms",
        selectedList: 3
    });

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

    // Render terms select
    var tehtml = '';
    for (var i=0,il=mercury.config.terms.length; i<il; i++) {
        var selected = (_.indexOf(mercury.data.selectedTerms, mercury.config.terms[i]) !== -1) ? 'selected="true"' : "";
        tehtml += '<option value="'+i+'" '+selected+'>'+mercury.config.terms[i]+'</option>';
    }
    mercury.c.$select_terms.html(tehtml);
    mercury.c.$select_terms.multiselect("refresh");

    // Render course select
    var chtml = '';
    var courses = mercury.data.selector[mercury.data.selectedYear][mercury.data.selectedTripos][mercury.data.selectedTriposPartID]["courses"];
    _.each(_.sortBy(courses,function(val) { return val.name }), function(course, courseid){
        var selected = (_.indexOf(mercury.data.selectedCourses, course.id) !== -1) ? 'selected="true"' : "";
        chtml += '<option value="'+course.id+'" '+selected+'>'+course.name+'</option>';
    });
    mercury.c.$select_course.html(chtml);
    mercury.c.$select_course.multiselect("refresh");

    // Show container
    mercury.c.$select_container.show();

};

// Fetches the calendar data form the server
mercury.calendar.loadCalendarData = function(tripospartid, callback) {

    $.ajax({
        type: "GET",
        url: mercury.config.urlCalendar,
        data: {
            "tripospartid": tripospartid
        },
        dataType: "json",
        success: function(data, textStatus, jqXHR) {

            if (data !== null) {
                // Save calendar data
                mercury.data.calendar = data;
				mercury.data.orig_calendar = jQuery.extend({},mercury.data.calendar);

                // Inject course info into selector data
                mercury.data.selector[mercury.data.selectedYear][mercury.data.selectedTripos][mercury.data.selectedTriposPartID]["courses"] = data.courses;

                // Call callback function if specified
                if (typeof callback === "function") {
                    callback(true);
                }
            } else {
                alert("The following data feed did not produce any data: "+mercury.config.urlCalendar);
                mercury.data.calendar = {};

                // Call callback function if specified
                if (typeof callback === "function") {
                    callback(false);
                }
            }

        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not load data from the feed!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            mercury.data.calendar = {};

            // Call callback function if specified
            if (typeof callback === "function") {
                callback(false);
            }
        }
    });

};


// Saves local calendar data to the server
mercury.calendar.saveCalendarData = function(tripospartid, callback) {

    // POST data to the server
	mercury.common.spin_on();
    $.ajax({
        type: "POST",
        url: mercury.config.urlCalendar,
        data: {
            "payload": JSON.stringify(mercury.data.calendar)
        },
        dataType: "json",
        success: function(data, textStatus, jqXHR) {
			mercury.common.spin_off();

            // Update calendar data with a fresh copy from the server
            mercury.data.calendar = data;
			mercury.data.orig_calendar = jQuery.extend({},mercury.data.calendar);

            // Call callback function if specified
            if (typeof callback === "function") {
                callback(true);
            }

        },
        error: function(jqXHR, textStatus, errorThrown) {
			mercury.common.spin_off();
            var error_msg = "Could not save calendar data!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            mercury.data.calendar = {};

            // Call callback function if specified
            if (typeof callback === "function") {
                callback(false);
            }
        }
    });

};


// Renders the calendar view based on mercury.data.calendar
mercury.calendar.renderCalendar = function(selected_courses, selected_terms) {

	var calendarjson = mercury.data.orig_calendar;

    // Transform calendar data into a form which is readable by fullCalendar
    var newCalendarData = mercury.calendar.processCalendarData(calendarjson, selected_courses, selected_terms);

    // Update calendar view
    mercury.data.calendarInstance.fullCalendar('removeEvents');
    mercury.data.calendarInstance.fullCalendar('addEventSource', newCalendarData);

};


// Initialises calendar display for the first time
mercury.calendar.initCalendar = function(calendarjson, selected_courses, selected_terms) {

    // Transform calendar data into a form which is readable by fullCalendar
    var calendarData = mercury.calendar.processCalendarData(calendarjson, selected_courses, selected_terms);

    // Create a fullCalendar instance
    mercury.data.calendarInstance = mercury.c.$calendar_container.fullCalendar({

        // Calendar config
        editable: true,
        theme: true,
        header: {
            left: '',
            center: '',
            right: ''
        },
        aspectRatio: 1.4,
        firstDay: (mercury.config.weekDaysOrder[0] + 1),
        weekends: true,
        selectable: true,
        selectHelper: true,
        unselectAuto: false,
        ignoreTimezone: true,
        allDaySlot: true,
        columnFormat: "dddd",
        defaultView: "agendaWeek",
        allDayText: "No time",
        dayNames: ['Sundays', 'Mondays', 'Tuesdays', 'Wednesdays','Thursdays', 'Fridays', 'Saturdays'],
        year: mercury.config.calendarBaseYear,
        month: mercury.config.calendarBaseMonth,
        date: mercury.config.calendarBaseDay,
        minTime: mercury.config.minTime,
        maxTime: mercury.config.maxTime,
        firstHour: mercury.config.firstHour,
        defaultEventMinutes: 60,
        events: calendarData,

        // Callback when an new calendar event is created
        select: function(startDate, endDate, allDay, jsEvent, view) {

            // Create a new event
            var event = $.extend({},mercury.config.defaultEventDataTemplate);

            // Create a random ID for it
            event.cid = _.uniqueId("createdseries_");
            event.rid = _.uniqueId("createdseries_");

            // Set day and times
            if (startDate.getDay() === 0) {
                event.day = 6;
            } else {
                event.day = startDate.getDay() - 1;
            }
            event.starttime[0] = startDate.getHours();
            event.starttime[1] = startDate.getMinutes();
            event.endtime[0] = endDate.getHours();
            event.endtime[1] = endDate.getMinutes();

            // Save new event data locally
            var rArray = [event];
            mercury.data.calendar.rectangles.push(rArray);

            // Init quickedit for the new event
            mercury.calendar.initQuickedit(event, jsEvent, view, "create");

        },

        // Callback when calendar event is moved
        eventDrop: function(event, dayDelta, minuteDelta, allDay, revertFunc, jsEvent, calUI, calView ) {

            // Most likely a bug in Fullcalendar.js - puts in source in the calendar event object which recurses infinitely
            // Freaks out jQuery.extend - will die with too much recursion
            if (event.source) {
                delete event.source;
            }

            // Update mercury.data.calendar day and time values based on the day and time delta after the move
            _.detect(mercury.data.calendar.rectangles,function(e,i){
                if (($.isArray(e) && e[0].rid === event.rid) || (e.rid && e.rid === event.rid)) {

                    var newStartTimeMinutes = (event["starttime"][0] * 60) + event["starttime"][1] + minuteDelta;
                    var newEndTimeMinutes = (event["endtime"][0] * 60) + event["endtime"][1] + minuteDelta;

                    // If it is a compound event adjust all subevents
                    if (event.hasSubEvents) {

                        // Adjust compound event details
                        mercury.data.calendar.rectangles[i][0]["day"] = mercury.config.weekDaysOrder[mercury.config.weekDaysOrder.indexOf(event.subEvents[0].day) + dayDelta];
                        mercury.data.calendar.rectangles[i][0]["starttime"][0] = Math.floor(newStartTimeMinutes / 60);
                        mercury.data.calendar.rectangles[i][0]["starttime"][1] = (newStartTimeMinutes % 60);
                        mercury.data.calendar.rectangles[i][0]["endtime"][0] = Math.floor(newEndTimeMinutes / 60);
                        mercury.data.calendar.rectangles[i][0]["endtime"][1] = (newEndTimeMinutes % 60);

                        for (var sen = 0, sel = event.subEvents.length; sen < sel; sen++) {
                            mercury.data.calendar.rectangles[i][sen+1]["day"] = mercury.config.weekDaysOrder[mercury.config.weekDaysOrder.indexOf(event.subEvents[sen].day) + dayDelta];
                            mercury.data.calendar.rectangles[i][sen+1]["starttime"][0] = Math.floor(newStartTimeMinutes / 60);
                            mercury.data.calendar.rectangles[i][sen+1]["starttime"][1] = (newStartTimeMinutes % 60);
                            mercury.data.calendar.rectangles[i][sen+1]["endtime"][0] = Math.floor(newEndTimeMinutes / 60);
                            mercury.data.calendar.rectangles[i][sen+1]["endtime"][1] = (newEndTimeMinutes % 60);
                        }

                    } else {

                        // Adjust normal event details
                        mercury.data.calendar.rectangles[i]["day"] = mercury.config.weekDaysOrder[mercury.config.weekDaysOrder.indexOf(event.day) + dayDelta];
                        mercury.data.calendar.rectangles[i]["starttime"][0] = Math.floor(newStartTimeMinutes / 60);
                        mercury.data.calendar.rectangles[i]["starttime"][1] = (newStartTimeMinutes % 60);
                        mercury.data.calendar.rectangles[i]["endtime"][0] = Math.floor(newEndTimeMinutes / 60);
                        mercury.data.calendar.rectangles[i]["endtime"][1] = (newEndTimeMinutes % 60);

                    }

                    return;
                }
            });

            // Save calendar data to the server and refresh local copy
			mercury.common.spin_on();
            $.ajax({
                type: "POST",
                url: mercury.config.urlCalendar,
                data: {
                    'payload': JSON.stringify(mercury.data.calendar)
                },
                dataType: "json",
                success: function(data, textStatus, jqXHR) {
					mercury.common.spin_off();
                    // Update calendar data
                    mercury.data.calendar = data;
					mercury.data.orig_calendar = jQuery.extend({},mercury.data.calendar);

                    // Re-render calendar view
                    mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);

                    // Let users know that the move has been successful
                    $.gritter.add({
                        title: 'Editing course day and time',
                        text: 'New course day and time has been successfuly saved.',
                        time: mercury.config.messageTimeToLive
                    });

                },
                error: function(jqXHR, textStatus, errorThrown) {
                	mercury.common.spin_off();
                    var error_msg = "Could not update calendar data on the server";
                    ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
                }
            });

        },

        // Callback when calendar event is resized
        eventResize: function(event, dayDelta, minuteDelta, allDay, revertFunc, jsEvent, calUI, calView ) {

            // Most likely a bug in Fullcalendar.js - puts in source in the calendar event object which recurses infinitely
            // Freaks out jQuery.extend - will die with too much recursion
            if (event.source) {
                delete event.source;
            }

            // Update mercury.data.calendar day and time values based on the day and time delta after the move
            _.detect(mercury.data.calendar.rectangles,function(e,i){
                if (($.isArray(e) && e[0].rid === event.rid) || (e.rid && e.rid === event.rid))  {

                    //Calculate new end time in minutes
                    var newEndTimeMinutes = (event["endtime"][0] * 60) + event["endtime"][1] + minuteDelta;

                    // If event is a compound event adjust all subevents
                    if (event.hasSubEvents) {
                        // Save it back as hours and mins
                        mercury.data.calendar.rectangles[i][0]["endtime"][0] = Math.floor(newEndTimeMinutes / 60);
                        mercury.data.calendar.rectangles[i][0]["endtime"][1] = (newEndTimeMinutes % 60);

                        for (var sen = 0, sel = event.subEvents.length; sen < sel; sen++) {
                            mercury.data.calendar.rectangles[i][sen+1]["endtime"][0] = Math.floor(newEndTimeMinutes / 60);
                            mercury.data.calendar.rectangles[i][sen+1]["endtime"][1] = (newEndTimeMinutes % 60);
                        }
                    } else {
                        // Save it back as hours and mins
                        mercury.data.calendar.rectangles[i]["endtime"][0] = Math.floor(newEndTimeMinutes / 60);
                        mercury.data.calendar.rectangles[i]["endtime"][1] = (newEndTimeMinutes % 60);
                    }

                    return;
                }
            });

            // POST the new calendar data to the server (when implemented on the server)
			mercury.common.spin_on();
            $.ajax({
                type: "POST",
                url: mercury.config.urlCalendar,
                data: {
                    'payload': JSON.stringify(mercury.data.calendar)
                },
                dataType: "json",
                success: function(data, textStatus, jqXHR) {
					mercury.common.spin_off();
                    // Update calendar data
                    mercury.data.calendar = data;
					mercury.data.orig_calendar = jQuery.extend({},mercury.data.calendar);

                    // Re-render calendar view
                    mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);

                    // Let users know that the move has been successful
                    $.gritter.add({
                        title: 'Editing course time',
                        text: 'New course time has been successfuly saved.',
                        time: mercury.config.messageTimeToLive
                    });

                },
                error: function(jqXHR, textStatus, errorThrown) {
    				mercury.common.spin_off();
                    var error_msg = "Could not update calendar data on the server!";
                    ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
                }
            });
        },

        // Callback when an event is clicked
        eventClick: function(event, jsEvent, view) {

            // Init quickedit
            mercury.calendar.initQuickedit(event, jsEvent, view, "edit");
        },

        // Callback when hovering over an element
        eventMouseover: function(event, jsEvent, view) {
            mercury.c.$calevent_text.html(event.text);
        },

        eventMouseout: function(event, jsEvent, view) {
            mercury.c.$calevent_text.html("");
        }

    });

};

// Constructs, displays and sets up the quickedit dialog
mercury.calendar.initQuickedit = function(event, jsEvent, view, action) {

    var quickEditWidth = 300;
    var quickEditHeight = 440;

    // If dialog is already open do nothing
    if (mercury.c.$quickedit_container.hasClass("ui-dialog-content")) {
        return;
    }

    // Create dialog title
    var dTitle = (action === "edit") ? "Quick edit": "Creating new course entry...";

    // Gathers and stores the current data entered into the Quickedit window
    var commitQEData = function(i_senumber) {
        var senumber = i_senumber || 0;
        var rid = mercury.c.$quickedit_container.data("rid");
        var courseid = mercury.c.$quickedit_container.data("courseid");

        // Gather basic data
        $("input.qe-data[type=text],input.qe-data[type=textarea]").each(function(i, element){

            var key = $(this).data("manipulates");
            var value = $(this).val();

            // Update values in mercury.data.calendar which will be POSTed back to the server
            _.detect(mercury.data.calendar.rectangles,function(e,i){
                if (e[0] && e[0].rid === rid) {
					if(senumber == 1 && e.length == 1)
						index = 0;
					else
						index = senumber;
                    _.detect(mercury.data.calendar.rectangles[i], function(se,sen){
                        if (sen === index) {
                            mercury.data.calendar.rectangles[i][sen][key] = value;
                            return;
                        }
                    });
                    return;
                } else if (e.rid && e.rid === rid) { // Make it work on legacy data layout as well, when rectangles are just single valued
                    mercury.data.calendar.rectangles[i][key] = value;
                    return;
                }
            });

        });
    };

    // Populates the Quickedit window with current, local event data
    var pullQEData = function(i_rid, i_sen) {

        var currentEventNumber = 0;
        var currentSubEventNumber = i_sen || 1;

        // Get path to data element which we are quickediting - ie current event and sub-event number
        _.detect(mercury.data.calendar.rectangles,function(e,i){
            if (e[0] && e[0].rid === i_rid) {
                currentEventNumber = i;
                return;
            } else if (e.rid && e.rid === i_rid) { // Make it work on legacy data layout as well, when rectangles are just single valued
                currentEventNumber = i;
                return;
            }
        });

        // Populate data
        var currentEvent = ($.isArray(mercury.data.calendar.rectangles[currentEventNumber])) ? mercury.data.calendar.rectangles[currentEventNumber][currentSubEventNumber] : mercury.data.calendar.rectangles[currentEventNumber];
        mercury.c.$qe_course_title.val(currentEvent.cname);
        mercury.c.$qe_course_what.val(currentEvent.what);
        mercury.c.$qe_course_organiser.val(currentEvent.organiser);
        mercury.c.$qe_course_location.val(currentEvent.where);
        mercury.c.$qe_course_when.val(currentEvent.when);

        // Render course type selector
        mercury.c.$qe_ctype_predefined_selector.html(mercury.calendar.renderCourseTypes(mercury.config.courseTypes, currentEvent.type, "qe"));
        mercury.c.$qe_ctype.val(currentEvent.type).hide();

        // Return current for convenience
        return currentEventNumber;

    };


    // Create a dialog for quickedit
    mercury.c.$quickedit_container.dialog({
        width: quickEditWidth,
        height: quickEditHeight,
        resizable: false,
        title: dTitle,
        buttons: {
            // Quickedit: When dialog Cancel button is pressed
            "Cancel": function() {

                // Restore original state
                mercury.data.calendar.rectangles = mercury.data.qe_original_rectangles;

                // Close the dialog
                $(this).dialog("close");
            },
            // Quickedit: When dialog Save button is pressed
            "Save": function() {

                // Gather and commit QE data to local storage
                commitQEData(parseInt(mercury.c.$quickedit_container.data("currentsubeventnumber"),10));

                // POST the new calendar data to the server
				mercury.common.spin_on();
                $.ajax({
                    type: "POST",
                    url: mercury.config.urlCalendar,
                    data: {
                        'payload': JSON.stringify(mercury.data.calendar)
                    },
                    dataType: "json",
                    success: function(data, textStatus, jqXHR) {
						mercury.common.spin_off();
                        // Update local copy with a fresh one from the server
                        mercury.data.calendar = data;
						mercury.data.orig_calendar = jQuery.extend({},mercury.data.calendar);

                        // Re-render calendar view
                        mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);

                        // Remove temp calendar item
                        mercury.data.calendarInstance.fullCalendar("unselect");

                        // Close dialog
                        mercury.c.$quickedit_container.dialog("close");

                        // Let users know that the action was successful
                        if (action === "create") {
                            $.gritter.add({
                                title: 'Creating a new course',
                                text: 'New course entry has been successfully created.',
                                time: mercury.config.messageTimeToLive
                            });

                            // Re-render selectors
                            mercury.calendar.renderSelectors();

                            // Re-render calendar
                            mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);
                        } else {
                            $.gritter.add({
                                title: 'Mercury quickedit course',
                                text: 'Course details has been successfuly saved.',
                                time: mercury.config.messageTimeToLive
                            });
                        }


                    },
                    error: function(jqXHR, textStatus, errorThrown) {
        				mercury.common.spin_off();
                        if (action === "create") {
                            // Remove temp calendar item
                            mercury.data.calendarInstance.fullCalendar("unselect");
                        }
                        var error_msg = "Could not update calendar data on the server!";
                        ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
                    }
                });


            }
        },
        // Quickedit: When dialog opens
        open: function() {

            // Store original rectangles state, so that we can revert if user Cancles the Quickedit
            mercury.data.qe_original_rectangles = $.extend(true, {}, mercury.data.calendar.rectangles); // Stores original calendar data state
            mercury.c.$quickedit_container.data("courseid", event.cid);
            mercury.c.$quickedit_container.data("rid", event.rid);
            mercury.c.$quickedit_container.data("currentsubeventnumber","1");

            // Populate quickedit with current data if we are not creating a new event
            if (action !== "create") {
                var currentEventNumber = pullQEData(event.rid);
            }

            // Show sub-event selector if needed and populate it with sub event data
            if (event.hasSubEvents) {
                var sehtml = '<label class="qe-label">Sub-event</label>';
                sehtml += '<select id="qe_subevents_selector" name="qe_subevents_selector">';
                _.each(mercury.data.calendar.rectangles[currentEventNumber], function(subEvent, subEventNumber) {
                    if (subEventNumber !== 0) {
                        sehtml += '<option value="'+subEventNumber+'">'+subEvent.text+'</option>';
                    }
                });
                sehtml += '</select>';
                mercury.c.$qe_subevent_selector_container.html(sehtml).show();
            } else {
                mercury.c.$qe_subevent_selector_container.html("").hide();
            }

            // Set up Quickedit event handlers - here rather than wire for better code readability


            // Select sub event (proxying to retain context of the mercury.calendar.initQuickedit function)
            // changed live to bind: when we select a new box we want to replace the binding or pullQEData gets
            // called multiple times (one for each lvie binding) and data gets overwritten. -- s dan
            $("#qe_subevents_selector").bind("change",$.proxy(function(e){

                // Commit current state
                commitQEData(parseInt(mercury.c.$quickedit_container.data("currentsubeventnumber"),10));

                // Get current sub-event number
                var csen = parseInt($("#qe_subevents_selector").val(),10);

                // Update current sub-event number
                mercury.c.$quickedit_container.data("currentsubeventnumber",csen);

                // Load subevent data
                pullQEData(event.rid, csen);

            },this));


            // Close Quickedit if going to the detailed edit page
            mercury.c.$qe_edit_course_button.bind("click", function(){
                // Make this dialog cease to be
                $(this).dialog("destroy");

                // Save current hash so that we can reload it later when we come back
                $.jStorage.set("mercury-calendar-hash", $.param.fragment());

                // Go to the edit page
                var storedState = ($.jStorage.get("mercury-details-selection") || false);
                var tab = (storedState.tab || 0);
                window.location = "details.html#courseid="+event.cid+"&tab="+tab;

            });

            // Show text input when user selects other for a course type | Also every time selector changes copy value to the text field since saving will pick up course type from the text field rather t
            mercury.c.$qe_ctype_predefined_selector.bind("change", function(e){

                if ($(e.currentTarget).val() === "Other") {
                    mercury.c.$qe_ctype.show().val("");
                } else {
                    mercury.c.$qe_ctype.attr("value", $(e.currentTarget).val()).hide();
                }

            });

            // Set up autocompletes
            mercury.c.$qe_course_title.autocomplete({
                source: mercury.config.urlAutocompleteCourseTitles+"/"+mercury.data.selectedTriposPartID,
                minLength: 0,
                select: function(e, ui) {
                    $(this).autocomplete("close");
                }
            });
            mercury.c.$qe_course_organiser.autocomplete({
                source: mercury.config.urlAutocompletePeople
            });
            mercury.c.$qe_course_location.autocomplete({
                source: mercury.config.urlAutocompleteLocations
            });

            // Check person uniqueness
            mercury.c.$qe_course_organiser.change(function(e){
                $.ajax({
                    type: "GET",
                    url: mercury.config.urlCheckPersonUniqueness,
                    dataType: "json",
                    data: {
                        "q": $(e.target).val()
                    },
                    success: function(data) {
                        if (data.unique && data.unique === 1) {
                            mercury.c.$course_organiser_dialog.dialog({
                                modal: true,
                                title: "Adding a new organiser",
                                buttons: {
                                    "No": function() {
                                        mercury.c.$qe_course_organiser.val("").click();
                                        $(this).dialog("close");
                                    },
                                    "Yes": function() {
                                        $(this).dialog("close");
                                    }
                                }
                            });
                        }
                    }
                });
            });


            // Check location uniqueness
            mercury.c.$qe_course_location.change(function(e){
                $.ajax({
                    type: "GET",
                    url: mercury.config.urlCheckLocationUniqueness,
                    dataType: "json",
                    data: {
                        "q": $(e.target).val()
                    },
                    success: function(data) {
                        if (data.unique && data.unique === 1) {
                            mercury.c.$course_location_dialog.dialog({
                                modal: true,
                                title: "Adding a new location",
                                buttons: {
                                    "No": function() {
                                        mercury.c.$qe_course_location.val("").click();
                                        $(this).dialog("close");
                                    },
                                    "Yes": function() {
                                        $(this).dialog("close");
                                    }
                                }
                            });
                        }
                    }
                });
            });


            // Stuff which needs to be done on creation
            if (action === "create") {

                // Render course type selector
                mercury.c.$qe_ctype_predefined_selector.html(mercury.calendar.renderCourseTypes(mercury.config.courseTypes, mercury.config.courseTypes[0], "qe"));
                mercury.c.$qe_ctype.val(mercury.config.courseTypes[0]).hide();

                // Show course/module name input on create
                 $("#qe_cname_input_container").show();
                 mercury.c.$qe_course_title.autocomplete("enable");

                // Hide edit and delete buttons
                mercury.c.$qe_edit_course_button.hide();
                mercury.c.$qe_delete_course_button.hide();

                // Trigger autocomplete on focus for course name input
                mercury.c.$qe_course_title.click(function(e){
                    $(this).autocomplete("search","");
                }).focus().autocomplete("search","");

                // Course title mockery
                mercury.c.$qe_course_title.blur(function(e){

                    // Pupulate specific event name automatically from the module name
                    if (!event.what || event.what === "") {
                        mercury.c.$qe_course_what.val($(this).val());
                    }

                }).change(function(e){

                    // Confirmation if user is creating a new module
                    if (_.indexOf((_.pluck(_.values(mercury.data.calendar.courses),"name")), mercury.c.$qe_course_title.val()) === -1) {

                        mercury.c.$course_name_dialog.dialog({
                            modal: true,
                            title: "Creating a new subject",
                            buttons: {
                                "No": function() {
                                    mercury.c.$qe_course_title.val("").click();
                                    $(this).dialog("close");
                                },
                                "Yes": function() {
                                    $(this).dialog("close");
                                }
                            }

                        });
                    }

                });

                // Set OK button label
                $('.ui-dialog-buttonpane button:contains(Save) span').html('Create');


            } else {

                // Hide course/module name input on edit
                $("#qe_cname_input_container").hide();
                mercury.c.$qe_course_title.unbind().autocomplete("disable");

                // Show edit button
                mercury.c.$qe_edit_course_button.button({
                    icons: {
                        primary: "ui-icon-wrench"
                    }
                }).css({"display": "inline-block"}).show();

                // Show delete course button
                mercury.c.$qe_delete_course_button.button({
                    icons: {
                        primary: "ui-icon-trash"
                    }
                }).bind("click",function(e){
                    mercury.calendar.deleteCourse(mercury.c.$quickedit_container.data("courseid"));
                }).css({"display": "inline-block"}).show();
            }

        },
        // Quickedit: When dialog closes
        close: function() {

            // Clean up orphan event data in mercury.data.calendar if the user does a U-turn and decides does not want the event anymore
            if (action==="create") {

                var courseid = mercury.c.$quickedit_container.data("courseid");
                _.detect(mercury.data.calendar.rectangles,function(e,i){
                    if (e[0].cid === courseid && e[0].text === "" && e[0].organiser === "" && e[0].where === "") {
                        mercury.data.calendar.rectangles.splice(i,1);
                        return;
                    }
                });
            }

            // Restore original state
            mercury.data.calendar.rectangles = mercury.data.qe_original_rectangles;

            // Remove temp calendar item
            mercury.data.calendarInstance.fullCalendar("unselect");

            // Remove name autocomplete
            mercury.c.$qe_course_title.autocomplete("destroy");

            // Obliterate this dialog
            $(this).dialog("destroy");
        }

    });

};


// Render course type selector
mercury.calendar.renderCourseTypes = function(ctypes, selected, prefix) {

    // Deal with course types which are not in the predefined set - make sure "Other" is the last option if exists
    if ($.inArray(selected,ctypes)) {
        var oLoc = _.indexOf(ctypes,"Other");
        if (oLoc !== -1) {
            ctypes[oLoc] = selected;
            ctypes.push("Other");
        } else {
            ctypes.push(selected);
        }
    }

    var html = '';
    _.each(ctypes, function(ctype,i) {
        var sel = '';
        if (ctype === selected) { sel  = 'selected="true"'; } else { sel = ''; }
        html += '<option value="'+ctype+'" '+sel+'>'+ctype+'</option>';
    });
    return html;

};

// Generate tripos list from raw top data
mercury.calendar.generateTriposList = function(rawTop) {
    var triposes = {};
    _.each(rawTop.years,function(yeardata,yearindex) {
        _.each(yeardata.triposes, function(triposdata,triposindex) {
            _.each(triposdata.parts, function(partdata, partindex){
                triposes[partdata['id']] = triposdata['name'];
            });
        });
    });
    return triposes;
};


// Transform calendar data into a form which is readable by fullCalendar
mercury.calendar.processCalendarData = function(calendarjson, selected_courses, selected_terms) {

    var calendarData = [];
    var availableColourObjects = $.extend(true,[],mercury.config.calendarColors);
    var pickedColourObjects = {};

    for (var i=0, il=calendarjson.rectangles.length; i<il; i++) {

        var hasSubEvents = false;
        var calevent = {};
        var subEvents = [];

        // Check if server sends arrays of calevents,and see if we are dealing with a compound event
        if ($.isArray(calendarjson.rectangles[i])) {
            if (calendarjson.rectangles[i].length > 1) {
                hasSubEvents = true;
                subEvents = _.rest(calendarjson.rectangles[i], 1);
            }
            // Use the first event to display in calendar
            calevent = calendarjson.rectangles[i][0];
        } else {
            calevent = calendarjson.rectangles[i];
        }

        // Apply course and term filters
        var in_selected_terms = false;
        _.detect(selected_terms, function(term){
            termNumber = _.indexOf(mercury.config.terms, term);
            if (calevent.termweeks[termNumber].length !== 0 || (calevent.terms && calevent.terms[termNumber] === 1)) {
                in_selected_terms = true;
                return;
            }
        });

        if ($.inArray(calevent.cid,selected_courses) !== -1 && in_selected_terms) {
            // Day
            var sDay = mercury.config.calendarBaseDay + $.inArray((calevent.day), mercury.config.weekDaysOrder);
            var start = "";
            var end = "";
            var sHours = 0;
            var sMinutes = 1;
            var eHours = 23;
            var eMinutes = 59;
            var allDay = false;
            if (calevent.fullday && calevent.fullday === 1) {
                // If this is a full day event - mark it as a full day event for fullCalendar and use the default times
                allDay = true;
            } else {
                // If this is a normal event

                // First check if event start and end times are actually supplied
                if ($.isArray(calevent.starttime) && calevent.starttime.length == 2 && $.isArray(calevent.endtime) && calevent.endtime.length == 2) {
                    sHours = calevent.starttime[0];
                    sMinutes = calevent.starttime[1];
                    eHours = calevent.endtime[0];
                    eMinutes = calevent.endtime[1];
                } else {
                    // If not display it as an all day event
                    allDay = true;
                }
            }

            // Start time - normalised to a base date and taking into account the calendar start day delta too
            var sY = mercury.config.calendarBaseYear;
            var sM = mercury.config.calendarBaseMonth;
            var sDate = new Date(sY, sM, sDay, sHours, sMinutes, 0, 0);
            var start = sDate.toString();

            // End time - normalised to a base date and taking into account the calendar start day delta too
            var eY = mercury.config.calendarBaseYear;
            var eM = mercury.config.calendarBaseMonth;
            var eDate = new Date(eY, eM, sDay, eHours, eMinutes, 0, 0);
            var end = eDate.toString();

            // Colours
            var selectedDolourObject = {};
            if (!pickedColourObjects[calevent.cname]) {
            	// We build indexes out of the last three digits as a number and a hash of the rest in the MSB.
            	// That means in typical views, where it's the last three digits that vary, we guarantee
            	// different colours.
				var suffix = parseInt(calevent.cid.substr(calevent.cid.length-3),10);
				var prefix = calevent.cid.substr(0,calevent.cid.length-3);
				// Simple hash function. We need not be the CIA here in our colour choices!
				hash = 0;
				for(var j=0;j<prefix.length;j++) {
					hash = ((hash * 40503) + prefix[j].charCodeAt()) % 65535;
				}
				hash += suffix;
                pickedColourObjects[calevent.cname] = availableColourObjects[hash%availableColourObjects.length];
            }
            selectedColourObject = pickedColourObjects[calevent.cname];


            // Create fullCalendar event object (from the calendar server object + some additional helper info)
            var eventObject = $.extend({}, calevent, {
                "title": calevent.text,
                "allDay": allDay,
                "start": start,
                "end": end,
                "textColor": selectedColourObject.textColour,
                "borderColor": selectedColourObject.borderColour,
                "backgroundColor": selectedColourObject.backgroundColour,
                "hasSubEvents": hasSubEvents,
                "subEvents": subEvents
            });

            calendarData.push(eventObject);
        }

    }

    return calendarData;
};


// Deletes a specific course with "Are you sure" dialog
mercury.calendar.deleteCourse = function(courseid) {

    // Init dialog
    mercury.c.$delete_course_dialog.dialog({
        title: ("Delete event(s)?"),
        resizable: false,
        modal: true,
        buttons: {
            "Cancel": function() {
                $(this).dialog( "close" );
            },
            "Delete": function() {

                // Remove event(s) from mercury.data.calendar
                var eventNumbers = [];
                var deletedEventsMsg = "";
                _.each(mercury.data.calendar.rectangles,function(ev,ei){
                    if (($.isArray(ev) && ev[0].cid === courseid) || (ev.cid === courseid)) {
                        eventNumbers.push(ei);
                        deletedEventsMsg += ev.text+"<br />";
                    }
                });
                _.each(eventNumbers, function(en){
                    mercury.data.calendar.rectangles.splice(en,1);
                });


                // POST the new calendar data to the server
                $.ajax({
                    type: "DELETE",
                    url: mercury.config.urlCalendar,
                    data: {
                        "calendardata": JSON.stringify(mercury.data.calendar),
                        "deletedcourseid": courseid
                    },
                    dataType: "json",
                    success: function(data, textStatus, jqXHR) {

                        // Let users know that the move has been successful
                        $.gritter.add({
                            title: 'Deleting events',
                            text: 'The following events were successfuly deleted: <br/> '+deletedEventsMsg,
                            time: mercury.config.messageTimeToLive
                        });

                        // Update local copy with a fresh one from the server
                        mercury.data.calendar = data;
						mercury.data.orig_calendar = jQuery.extend({},mercury.data.calendar);

                        // Send Quickedit dialog to meet its maker
                        mercury.c.$quickedit_container.dialog("destroy");

                        // Shut this one down
                        mercury.c.$delete_course_dialog.dialog("close");

                        // Re-render calendar view
                        mercury.calendar.renderCalendar(mercury.data.selectedCourses, mercury.data.selectedTerms);

                    },
                    error: function(jqXHR, textStatus, errorThrown) {
                        var error_msg = "Could not delete calendar data on the server!";
                        ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
                    }
                });


            }
        }
    });
};

// Saves current state of the app and pushes current selection into the URL hash
mercury.calendar.pushState = function() {
    $.bbq.pushState({
        "year": mercury.data.selectedYear,
        "tripospartid": mercury.data.selectedTriposPartID,
        "courseids": mercury.data.selectedCourses,
        "terms": mercury.data.selectedTerms,
        "tripos": mercury.data.selectedTripos
    });

    // Store selection in a cookie/local storage too
    $.jStorage.set("mercury-calendar-selection", {
        "year": mercury.data.selectedYear,
        "tripospartid": mercury.data.selectedTriposPartID,
        "courseids": mercury.data.selectedCourses,
        "terms": mercury.data.selectedTerms,
        "tripos": mercury.data.selectedTripos
    });
};


// Page init function
mercury.calendar.init = function() {

	mercury.common.login_link();

    // Read URL hash
    var hash = $.deparam.fragment();

    // Read state stored in local storage
    var storedState = ($.jStorage.get("mercury-calendar-selection") || false);

    // Fetch top feed from server which drives selectors
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
                mercury.data.triposid_to_name = mercury.calendar.generateTriposList(mercury.data.top);

                // Set tripospartID from URL if exists, or from cookie if exists, or the first one
                mercury.data.selectedTriposPartID = (hash.tripospartid || storedState.tripospartid || mercury.data.top.years[0]["triposes"][0]["parts"][0]["id"]);

                // Set up state
                mercury.data.selectedYear = (hash.year || storedState.year || mercury.data.top.years[0]["name"]);
                mercury.data.selectedTripos = mercury.data.triposid_to_name[mercury.data.selectedTriposPartID];
                mercury.data.selectedCourses = (hash.courseids || storedState.courseids || [""]);
                mercury.data.selectedTerms = (hash.terms || storedState.terms || mercury.config.terms); // If there is term specified use it otherwise assume all terms
                if (mercury.data.selectedTerms.length === 1 && mercury.data.selectedTerms[0] === "") {
                    mercury.data.selectedTerms = mercury.config.terms;
                }

				mercury.calendar.lock();

                mercury.calendar.pushState();

                // Get calendar data
                mercury.calendar.loadCalendarData(mercury.data.selectedTriposPartID, function(success){

                    // Wire up
                    mercury.calendar.wire();

                    // Render selectors for the first time
                    mercury.calendar.renderSelectors();

                    // Recalculate multiselect width when window is resized
                    $(window).resize(function(e){
                        mercury.c.$select_course.multiselect("option", "minWidth", $(window).width() - 400);
                    });

                    // Render calendar for the first time
                    mercury.calendar.initCalendar(mercury.data.calendar, mercury.data.selectedCourses, mercury.data.selectedTerms);

                    // Show select container
                    mercury.c.$select_container.show();

                });

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
	setInterval(function() { mercury.calendar.lock(); },60*1000);
};

mercury.calendar.lock = function(tripos) {
	mercury.common.lock(mercury.data.selectedTriposPartID,120);
};


// Start with calling  page init function
$(document).ready(function() {
	mercury.calendar.init();
	mercury.common.idle_init();
});
