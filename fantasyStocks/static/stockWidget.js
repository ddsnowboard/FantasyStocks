"use strict"

$(document).ready(function(){
    var $box = $("." + CLASS_NAME);
    var $holder = $("<div class=\"holder\"></div>");
    $box.before($holder);
    var stocks_bloodhound = new Bloodhound({
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        datumTokenizer:  function(datum)
        {
            return [datum.Name, datum.Symbol];
        },
        initialize: true,
        remote: {
            url: STOCK_API_URL, 
            wildcard: WILDCARD, 
            transform: function(jsonObj)
            {
                return jsonObj;
            }
        }, 
        prefetch: {
            url: PREFETCH_URL,
            cache: false,
            transform: function(jsonObj)
            {
                console.log(jsonObj);
                return jsonObj;
            }, 
        }
    });
    stocks_bloodhound.initialize();


    $box.typeahead({
        minLength: 1,
        highlight: false,
    }, {
        name: "stocks_dataset", 
        source: stocks_bloodhound,
        templates: {
            pending: " . . . ", 
            suggestion: function(obj)
            {
                return "<div class=\"suggestion\"><span class=\"name\">" + obj.Name + "</span><span class=\"symbol\"> (" + obj.Symbol + ") </span></div>"
            }, 
        }, 
        limit: 20,
        rateLimitBy: "throttle",
        rateLimitWait: 600,
    });

    // This isn't working. So that's interesting. 
    $box.bind("typeahead:autocomplete", function(event, suggestion)
            {
                console.log(suggestion);
            });
});

