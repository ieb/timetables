/*
 * Mercury: Details view
 *
 */

// Page namespace
mercury.details = {};
mercury.data.courseNames = []; // This will hold a cached copy of course names coming from a full autocomplete dump

// Object cache
mercury.c.$header = $("#header");
mercury.c.$details_tabs = $("#details_tab_container");
mercury.c.$basic_cancel_button = $("#det_basic_cancel_button");
mercury.c.$basic_save_button = $("#det_basic_save_button");
mercury.c.$basic_back_button = $("#det_basic_back_button");
mercury.c.$advanced_cancel_button = $("#det_advanced_cancel_button");
mercury.c.$advanced_save_button = $("#det_advanced_save_button");
mercury.c.$advanced_back_button = $("#det_advanced_back_button");

mercury.c.$eventgroup_container = $("#eventgroup_container");

mercury.c.$add_eventgroup_dialog = $("#add_eg_dialog");
mercury.c.$course_name_dialog = $("#course_name_dialog_container");
mercury.c.$course_organiser_dialog =  $("#course_organiser_dialog_container");
mercury.c.$course_location_dialog =  $("#course_location_dialog_container");



// Initialise basic edit tab
mercury.details.basicEditInit = function() {

    // Populate input fields with data
    $(".det-data").each(function(element, i) {

        var dataKey = $(this).data("manipulates");
        if (mercury.data.details[dataKey]) {
            $(this).val(mercury.data.details[dataKey]);
        }

    });

    // Initialise tinyMCE for metadata edits
    // XXX Tabfocus does not work for some reason - will need to look at it later
    tinyMCE.init({
        mode : "textareas",
        theme: "advanced",
        skin : "o2k7",
        plugins : "spellchecker,iespell,paste,tabfocus",
        tabfocus_elements: ":prev,:next",
		content_css: 'css/tinymce.css',

        theme_advanced_buttons1 : "bold,italic,underline,strikethrough",
        theme_advanced_buttons2 : "",
        theme_advanced_buttons3 : "",
        theme_advanced_toolbar_location : "top",
        theme_advanced_toolbar_align : "left",
        theme_advanced_statusbar_location : "bottom",
        theme_advanced_resizing : false,

        init_instance_callback: function(editor) {
            // Populate editor content with course data
            var dataKey = $("#"+editor.editorId).data("manipulates");
            if (mercury.data.details.metadata[dataKey]) {
            	mercury.data.details.metadata[dataKey] = mercury.data.details.metadata[dataKey].replace(/<\/p><p>/g,'');
                editor.setContent(mercury.data.details.metadata[dataKey]);
            }
        }

    });


    // Set up autocompletes
    mercury.details.setupAutocompletes();

    // Trigger autocomplete on click for course name input
    $("#det_name").click(function(e){
        $(this).autocomplete("search","");
    })

    //
    $("#det_name").change(function(e){
        // Confirmation if user is creating a new module
        // Check against an array of courses coming from a full autocomplete dump
        if (_.indexOf(_.pluck(mercury.data.courseNames,"label"),$("#det_name").val()) === -1) {

            mercury.c.$course_name_dialog.dialog({
                modal: true,
                title: "Creating a new module",
                buttons: {
                    "No": function() {
                        $("#det_name").val("").click();
                        $(this).dialog("close");
                    },
                    "Yes": function() {
                        $(this).dialog("close");
                    }
                }

            });
        }
    });



    // Check person uniqueness
    $("#det_organiser").change(function(e){
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
                                $("#det_organiser").val("").click();
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
    $("#det_location").change(function(e){
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
                                $("#det_location").val("").click();
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



    // Basic details 'Cancel' click handler
    mercury.c.$basic_cancel_button.bind("click", function(e){
        window.history.go(-1);
    });

    // Basic details 'Save' click handler
    mercury.c.$basic_save_button.bind("click", function(e){

        // Gether normal text inputs and update local data
        $(".det-data").each(function(element, i){

            var dataKey = $(this).data("manipulates");
            if (mercury.data.details[dataKey]) {
                mercury.data.details[dataKey] = $(this).val();
            }

        });

        // Gather metadata and update local data
        $(".det-metadata").each(function(element, i){

            var editorID = $(this).attr("id");
            var dataKey = $(this).data("manipulates");
            mercury.data.details.metadata[dataKey] = tinyMCE.editors[editorID].getContent();

        });

        // Save local data back to the server
		mercury.common.spin_on();
        $.ajax({
            type: "POST",
            url: mercury.config.urlDetails,
            data: {
                "payload": JSON.stringify(mercury.data.details)
            },
            dataType: "json",
            success: function(data, textStatus, jqXHR) {
				mercury.common.spin_off();

                // Refresh local copy
                mercury.data.details = data;

                // Let users know that the save has been successful
                $.gritter.add({
                    title: 'Mercury basic details save',
                    text: 'Basic course details has been successfuly saved.',
                    time: mercury.config.messageTimeToLive
                });

            },
            error: function(jqXHR, textStatus, errorThrown) {
				mercury.common.spin_off();
                var error_msg = "Could not save data to the server!";
                ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            }
        });
    });

    // Back to calendar button click handler
    mercury.c.$basic_back_button.bind("click", function(e){

        // Go back to the calendar screen with the stored hash (we need to reload the claendar data - hence navigating and not going back in history)
        window.location = "calendar.html#"+$.jStorage.get("mercury-calendar-hash","");

    });

};



// Initialise basic edit tab
mercury.details.advancedEditInit = function() {

    // Render event groups
    var eghtml = '';

    // Group by term
    for (var termNumber = 0, terms = mercury.config.terms.length; termNumber < terms; termNumber++) {

        var term = mercury.config.terms[termNumber];
        var currentCourseTypes = [];

        eghtml += '<li class="eg-term-container" data-term="'+term+'" data-termnumber="'+termNumber+'">';
        eghtml += ' <h2 class="eg-term">'+term+'</h2>';

        // Get each event group for this term
        _.each(mercury.data.details.groups, function(group,groupNumber){

            if (group.term === term) {

                // Event group
                eghtml += '<div class="eg" data-name="'+group.name+'">';
                eghtml += ' <div class="eg-name">'+group.name+'</div>';

                // Save module type to later know what types we already have (to help adding)
                if ($.inArray(group.name,currentCourseTypes) === -1) {
                    currentCourseTypes.push(group.name);
                }

                eghtml += ' <label class="eg-label">Default days and times</label>';
                eghtml += ' <input type="text" class="eg-data eg-code" data-manipulates="code" value="'+group.code+'">';

                // Elements within the event group
                eghtml += ' <table class="eg-elements-container">';
                eghtml += '  <thead><tr><th>Person responsible</th><th>Title</th><th>Location</th><th>Days and times</th><th class="merge-head">Merge</th><th></th><th></th></tr></thead>';
                eghtml += '  <tbody>';

                    // Render event elements
                    _.each(group.elements, function(element,elementNumber){
                        eghtml += '<tr class="eg-element">';

                        // Handle non-existing keys
                        var who = element.who || "";
                        var name = element.what || "";
                        var location = element.where || "";
                        var code = element.code || "";
                        var merge = (element.merge === 1) ? 'checked="true"' : "";
                        var eid = element.eid || "";

                        hidden = '<input type="hidden" class="eg-elementdata" data-manipulates="eid" value="'+eid+'"/>';
                        eghtml += ' <td>'+hidden+'<input type="text" class="eg-elementdata eg-elementdata-organiser" data-manipulates="who" value="'+who+'" /></td>';
                        eghtml += ' <td><input type="text" class="eg-elementdata eg-elementdata-name" data-manipulates="what" value="'+name+'" /></td>';
                        eghtml += ' <td><input type="text" class="eg-elementdata eg-elementdata-location" data-manipulates="where" value="'+location+'" /></td>';
                        eghtml += ' <td><input type="text" class="eg-elementdata eg-elementdata-code" data-manipulates="code" value="'+code+'" /></td>';
                        eghtml += ' <td class="force-center"><input type="checkbox" class="eg-elementdata eg-elementdata-merge" data-manipulates="merge" '+merge+'/></td>';
                        eghtml += ' <td><a class="eg-element-delete-button ui-icon ui-icon-trash" href="javascript:;" title="Click to delete this event"></a></td>';
                        eghtml += ' <td><a class="eg-element-reorderhandle ui-icon ui-icon-arrowthick-2-n-s" href="javascript:;" title="Drag event to re-arrange"></a></td>';
                        eghtml += '</tr>';
                    });

                eghtml += '   <tr><td><a class="eg-element-add-button" href="javascript:;" title="Add another event"><span class="ui-icon ui-icon-plus"></span>Add event</a></td></tr>';
                eghtml += '  </tbody>';
                eghtml += ' </table>';

                eghtml += '</div>';

            }
        });

        // Add "Add element group" button
        eghtml += '<a href="javascript:;" class="add_eg_button" data-term="'+term+'" data-termnumber="'+termNumber+'" data-cctypes="'+currentCourseTypes.join("|")+'"><span class="ui-icon ui-icon-plusthick"></span>Add event group</a>';

        eghtml += '</li>';
    }

    // Add rendered html string to the DOM
    mercury.c.$eventgroup_container.html(eghtml);

    // Set up reorderer
    $(".eg-elements-container tbody").each(function() {
        $(this).sortable({
            containment: $(this).parents(".eg-elements-container"),
            items: "tr"
        });
    });

    // Set up element delete
    $(".eg-element-delete-button", $(".eg-elements-container")).live("click",function(e) {
        var $numberOfElements = $(".eg-element", $(this).parents(".eg-element").parent()).length;
        if ($numberOfElements > 1) {
            $(this).parents(".eg-element").remove();
        } else {
            // Let users know that the save has been successful
            $.gritter.add({
                title: 'Removing an an event',
                text: 'You can\'t remove the last event from the module type',
                time: mercury.config.messageTimeToLive
            });
        }
    });

    // Set up autocompletes
    mercury.details.setupAutocompletes();

    // Set up add element
    $(".eg-element-add-button", $(".eg-elements-container")).bind("click", function(e) {
        $(this).parents("tr").prev(".eg-element").clone().insertBefore($(this).parents("tr"));
        mercury.details.setupAutocompletes();
    });

    // Set up add event group button
    $(".add_eg_button").bind("click", function(e){

        var cctypes = $(this).data("cctypes");
        cctypes = cctypes.split("|");
        var term = $(this).data("term");

        mercury.c.$add_eventgroup_dialog.dialog({
            modal: true,
            title: "Add event group",
            buttons: {
                "Cancel": function() {
                    // Close the dialog
                    $(this).dialog("close");
                },
                "Add": function() {

                    var groupname = $("#add_eg_type_exact").val();

                    // Gather data
                    mercury.details.gatherEditorData();

                    // Add new group into mercury.data.details
                    var groupObject = {
                        "code": "",
                        "elements": [{
                            "code": "",
                            "what": "",
                            "where": "",
                            "who": "",
                            "merge": 0
                        }],
                        "name": groupname,
                        "term": term
                    };
                    mercury.data.details.groups.push(groupObject);

                    // Re-render advanced edit
                    mercury.details.advancedEditInit();

                    // Close the dialog
                    $(this).dialog("close");
                }
            },
            open: function() {

                var $eg_type_select = $("#add_eg_type_predefined_select");
                var $eg_type_exact = $("#add_eg_type_exact");

                // Offer course types for selection which are not yet displayed
                var cthtml = '';
                _.each(mercury.config.courseTypes, function(courseType){
                    if ($.inArray(courseType,cctypes) === -1) {
                        cthtml += '<option value="'+courseType+'">'+courseType+'</option>';
                    }
                });
                $eg_type_select.html(cthtml);

                // Set up type selector behaviour
                $eg_type_exact.val($eg_type_select.val());
                $eg_type_select.bind("change", function(e){
                    if ($(this).val() === "Other") {
                        $eg_type_exact.val("").show();
                    } else {
                        $eg_type_exact.val($(this).val()).hide();
                    }
                });


            }
        });

    });


    // Set up 'Cancel' click event
    mercury.c.$advanced_cancel_button.unbind().bind("click", function(e) {
        window.history.go(-1);
    });

    // Set up 'Save' click event
    mercury.c.$advanced_save_button.unbind().bind("click", function(e) {

        // Gather data
        mercury.details.gatherEditorData();

        // Save local data back to the server
		mercury.common.spin_on();
        $.ajax({
            type: "POST",
            url: mercury.config.urlDetails,
            data: {
                "payload": JSON.stringify(mercury.data.details)
            },
            dataType: "json",
            success: function(data, textStatus, jqXHR) {
				mercury.common.spin_off();
                // Update local copy of details data with a fresh one from the server
                mercury.data.details = data;

                // Let users know that the save has been successful
                $.gritter.add({
                    title: 'Mercury advanced details save',
                    text: 'Advanced course details has been successfuly saved.',
                    time: mercury.config.messageTimeToLive
                });

            },
            error: function(jqXHR, textStatus, errorThrown) {
				mercury.common.spin_off();
                var error_msg = "Could not save data to the server!";
                ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            }
        });

    });

    // Back to calendar button click handler
    mercury.c.$advanced_back_button.bind("click", function(e){

        // Go back to the calendar screen with the stored hash (we need to reload the claendar data - hence navigating and not going back in history)
        window.location = "calendar.html#"+$.jStorage.get("mercury-calendar-hash","");

    });

};


mercury.details.gatherEditorData = function() {

        // Reset local groups data
        mercury.data.details.groups = [];

        // Gather all event groups - here we are reconstructing the groups object array entirely from the DOM state and send back the recreated data to the server
        $(".eg").each(function(groupelement, groupelementNumber){

            var $eventGroup = $(this);
            var $termContainer = $eventGroup.parents(".eg-term-container");
            var term = $termContainer.data("term");
            var $elements = $(".eg-element", $eventGroup);

            // Construct new event group object
            var egObject = {};
            egObject.name = $eventGroup.data("name");
            egObject.term = term;
            egObject.code = $(".eg-code", $eventGroup).val();
            egObject.elements = [];

            $elements.each(function(element, elementNumber){
                var elementObject = {};
                $(".eg-elementdata", $(this)).each(function(eData,eDataNumber){
                    var key = $(this).data("manipulates");
                    var value = "";
                    if ($(this).attr("type") === "checkbox") {
                        value = ($(this).is(":checked")) ? 1 : 0;
                    } else {
                        value = $(this).val();
                    }
                    elementObject[key] = value;
                });
                egObject.elements.push(elementObject);
            });

            mercury.data.details.groups.push(egObject);

        });

}



// Sets up autocompletes
mercury.details.setupAutocompletes = function() {

    // Set up autocompletes
    $(".eg-elementdata-name").autocomplete({
        source: mercury.config.urlAutocompleteCourseTitles
    });

    $("#det_name").autocomplete({
        source: function(request, response) {

            // Custom data source so that we can cache a full course list array
            $.ajax({
                type: "GET",
                url: mercury.config.urlAutocompleteCourseTitles,
                dataType: "json",
                data: {
                    "term": request.term
                },
                success: function(data, status, xhr) {
                    var result = data;

                    // Cache a full result set
                    if (request.term === "") {
                        mercury.data.courseNames = data;
                    }

                    response(result);
                },
                error: function() {
                    // Quiet...
                    var result = [];
                    response(result);
                }
            });

        },
        minLength: 0,
        select: function(e, ui) {
            $(this).autocomplete("close");
        }
    });
    $(".eg-elementdata-organiser, #det_organiser").autocomplete({
        source: mercury.config.urlAutocompletePeople
    })
    $(".eg-elementdata-location, #det_location").autocomplete({
        source: mercury.config.urlAutocompleteLocations
    })

};

mercury.details.pushState = function(history) {
	if(history) {

	    // Push a new state and alter URL
	    $.bbq.pushState({
	        "courseid": mercury.data.selectedCourseID,
	        "tab": mercury.data.selectedTab
	    });
	} else {
		window.location.replace(window.location.href+"#courseid="+mercury.data.selectedCourseID+"&tab="+mercury.data.selectedTab);
	}

    // Store selection in a cookie/local storage too
    $.jStorage.set("mercury-details-selection", {
        "courseid": mercury.data.selectedCourseID,
        "tab": mercury.data.selectedTab
    });
};

// Page init function
mercury.details.init = function() {

	mercury.common.login_link();

    // Read URL hash
    var hash = $.deparam.fragment();

    // Read cookie
    var storedState = ($.jStorage.get("mercury-details-selection") || false);

    // Set up state
    mercury.data.selectedCourseID = (hash.courseid || storedState.courseid || "");
    mercury.data.selectedTab = (hash.tab || storedState.tab || 0);

    if (mercury.data.selectedCourseID === "") {
        alert("No course ID has been provided, I don't know which course's details should I display...");
    }

	setInterval(function() { mercury.common.lock(mercury.data.selectedCourseID.substr(0,14),120); },60*1000);
	mercury.common.lock(mercury.data.selectedCourseID.substr(0,14),120);

    // Fetch details feed from server
    $.ajax({
        type: "GET",
        url: mercury.config.urlDetails,
        data: {
            "courseid": mercury.data.selectedCourseID
        },
        dataType: "json",
        success: function(data, textStatus, jqXHR) {

            if (data !== null) {

                // Store loaded data
                mercury.data.details = data;

                // Init tabs
                mercury.c.$details_tabs.tabs({
                    selected: mercury.data.selectedTab,
                     select: function(event, ui) {
                        mercury.data.selectedTab = ui.index;
                        mercury.details.pushState(true);
                        if (ui.index === 0) {
                            $("#det_name").focus();
                        }
                     }
                });

                // Init buttons
                $("button", $(".buttonbar")).button();

                // Init basic edit
                mercury.details.basicEditInit();

                // Init advanced edit
                mercury.details.advancedEditInit();

                // Push initial state
                mercury.details.pushState(false);


            } else {
                alert("The following data feed did not produce any data: "+mercury.config.urlDetails);
                mercury.data.top = {};
            }

        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not load data from the feed!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
            mercury.data.details = {};
        }
    });


};

// Start with calling  page init function
$(document).ready(function() {
	mercury.details.init(); 
	mercury.common.idle_init();

});
