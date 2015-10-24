"use strict"


$(document).ready(function(){
    var $box = $("." + CLASS_NAME);

    var stocks_bloodhound = new Bloodhound({
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        initialize: true,
        remote: {
            url: STOCK_API_URL, 
            wildcard: WILDCARD, 
            transform: function(jsonObj)
            {
                return jsonObj;
            }
        }, 
    });

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
    });
});
