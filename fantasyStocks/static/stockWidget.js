"use strict"

var TEXTBOX_CLASS = "inputBox";
var selected_stocks = [];

function setBox($box, arr)
{
    $box.val(arr.join(","));
}
$(document).ready(function(){
    var $value = $("." + CLASS_NAME);
    var $box = $("<input type=\"text\" />");
    $box.addClass(TEXTBOX_CLASS);
    $box.keydown(function(event) {
        if(event.which === 13)
            event.preventDefault();
    });
    var $holder = $("<div class=\"holder\"></div>");
    $holder.on("mousedown", ".selection", function() {
        selected_stocks.splice(selected_stocks.indexOf($(this).attr('id')), 1);
        setBox($value, selected_stocks);
        $(this).remove();
    })
    .on("mouseenter", ".selection", function() {
        $(this).addClass("redBackground");
    })
    .on("mouseleave", ".selection", function() {
        $(this).removeClass("redBackground");
    });
    $value.parent().append($holder).append($box);
    var stocks_bloodhound = new Bloodhound({
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        datumTokenizer:  function(datum)
        {
            return [datum.name, datum.symbol];
        },
        initialize: true,
        prefetch: {
            url: PREFETCH_URL,
            cache: false,
            transform: function(jsonObj)
            {
                return jsonObj;
            }, 
        }
    });
    stocks_bloodhound.initialize();


    $box.typeahead({
        minLength: 1,
        highlight: false,
        hint: false,
    }, {
        name: "stocks_dataset", 
        source: stocks_bloodhound,
        templates: {
            pending: " . . . ", 
            suggestion: function(obj)
            {
                return "<div class=\"suggestion\"><span class=\"name\">" + obj.name + "</span><span class=\"symbol\"> (" + obj.symbol + ") </span></div>"
            }, 
        }, 
        limit: 20,
        rateLimitBy: "throttle",
        rateLimitWait: 600,
        display: function(o){ return o.name; }, 
    });

    $box.bind("typeahead:select", function(event, suggestion)
            {
                $box.typeahead("val", "");
                $holder.append("<div class=\"selection\" id=\"" + suggestion.symbol + "\"><span class=\"name\">" + suggestion.name + "</span><span class=\"symbol\"> (" + suggestion.symbol + ") </span></div>");
                selected_stocks.push(suggestion.symbol);
                setBox($value, selected_stocks);
            });
});
