/* JSLint */
/* jslint browser: true */
/* global $, jQuery */


TODO, add map for content.sub_key to type (string, table, etc) add to config.js

var AJAX_SNOOZE = 2000,
    ATTEMPT_LIMIT = 4,
    FADE_DELAY = 1000;


function load_content(content_key, data) {
    'use strict';

    var key, 
        content = data['content'], 
        content_type = data['content_type'];

    for (key in content) {
        var key_string = "#" + content_key + "-" + key;
        // console.log("   " + key_string);
        // console.log(key);

        switch (content_type[key]) {
            case 'string':
                $(key_string).append(content[key]).fadeIn(FADE_DELAY);
                break;

            case 'list':
                for (var i = 0; i < content[key].length; i++) {
                    $(key_string).append(content[key][i]).fadeIn(FADE_DELAY);
                }
                break;

            case 'table':

                break;

        }
    }
}


// remove loader image, display sad face, display error notification
function handle_timeout(content_key, message) {
    'use strict';
    console.log("in handle_timeout: " + content_key);
    console.log(message);
}


function dispatch(resource, content_key, attempt, page) {
    'use strict';

    var params = {
        'resource': resource,
        'content_key': content_key
    }

    if (page) {
        params['page'] = page;
    }

    $.ajax({
        url: "/ajax/retrieval/",
        data: params,
        dataType: 'json',
        type: 'GET',
        success: function(data, stat, o) {
            switch (data['status']) {
                case 'success':
                    load_content(content_key, data[content_key]);

                    break;

                case 'pending':
                    if (attempt > ATTEMPT_LIMIT) {
                        handle_timeout(content_key, o);
                    }
                    else {
                        setTimeout(function() {
                                dispatch(resource, content_key, ++attempt, page);
                            }
                        , AJAX_SNOOZE);
                    }

                    break;
            }
        }
        // ,
        // error: function(o, stat, er) {},
        // complete: function(o, stat) {}
    });
}



