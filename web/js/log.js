var mercury = mercury || {};
mercury.log = {};

mercury.log.get = function(cont) {
    $.ajax({
        type: "GET",
        url: mercury.config.urlLog,
        dataType: "json",
        success: function(data, textStatus, jqXHR) {
            cont(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not retrieve log";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
        }
    });
};

mercury.log.delegations = function(cont) {
    $.ajax({
        type: "GET",
        url: mercury.config.urlDelegations,
        dataType: "json",
        success: function(data, textStatus, jqXHR) {
            cont(data);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            var error_msg = "Could not retrieve delegation list";
            ajaxError.apply(this, [null, jqXHR, $.ajaxSettings, errorThrown, error_msg]);
        }
    });
};

mercury.log.display = function() {
    mercury.log.get(function(data) {
        var text = data['text'];
        text = '<li>'+text.replace(/[\r\n]+/g,'</li><li>')+'</li>';
        text = text.replace(/<li><\/li>/g,'');
        jQuery('#logfill').html(text);
    });
    mercury.log.delegations(function(data) {
        var out = '';
        for(var row in data['data']) {
            out += "<li>"+data['data'][row]+"</li>";
        }
        jQuery('#delfill').html(out);
    });
};

mercury.log.init = function() {
    mercury.common.login_link();
    mercury.log.display();  
};

jQuery(function() { mercury.log.init(); });
