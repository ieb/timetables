/*
 * Mercury: Login
 *
 */

// Page namespace
mercury.login = {};

// Object cache
mercury.c.$login_dialog = $("#login_dialog_container");

// Attempt logging in
mercury.login = function(username, password) {

    mercury.c.$login_dialog.dialog("disable");

    $.ajax({
        type: "POST",
        url: mercury.config.urlAuth,
        data: {
            "u": username,
            "p": password
        },
        success: function(data, textStatus, jqXHR) {

            mercury.c.$login_dialog.dialog("enable");

            // See if login was successful
            if (data.success === true) {
                $("#login_error").hide();
                mercury.c.$login_dialog.dialog("close");
                window.location = mercury.config.urlList;
            } else {

                // Reset form
                $("#login_username").val("");
                $("#login_password").val("");

                // Display error message from server if any
                if (data.error && data.error !== "") {
                    mercury.c.$login_dialog.dialog("option", "height", 300);
                    $("#login_error").html(data.error).show();
                }
            }

        },
        error: function(jqXHR, textStatus, errorThrown) {
            mercury.c.$login_dialog.dialog("enable");
            var error_msg = "Something went wrong while connecting to the authentication service!";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
        }
    });

};


// Init
mercury.login.init = function() {

    // Create login window
    mercury.c.$login_dialog.dialog({
        title: "Sign in to Mercury",
        width: 400,
        modal: true,
        resizable: false,
        buttons: {
            "Sign in": function() {
                mercury.login($("#login_username").val(), $("#login_password").val());
            }
        }
    });

    // Set up Enter button
    $(window).keypress(function(e){
        if (e.keyCode === 13) {
            mercury.login($("#login_username").val(), $("#login_password").val());
        }

    });

};




// Start with calling page init function
$(document).ready(mercury.login.init());
