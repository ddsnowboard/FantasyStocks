"use strict"

var TEXTBOX_CLASS = "inputBox";
var selected_stocks = [];
var $holder;
var $value;
function setBox($box, arr)
{
    $box.val(arr.join(","));
}

function pushStock(stock, addToArray)
{
    var WARNING_DURATION = 2000;
    // The JavaScript eqivalent of a default argument. Brilliant.
    if(addToArray === undefined)
    {
        addToArray = true;
    }
    if(selected_stocks.indexOf(stock.symbol) === -1)
    {
        $holder.append("<div class=\"selection\" id=\"" + stock.symbol + "\"><span class=\"name\">" + stock.name + "</span><span class=\"symbol\"> (" + stock.symbol + ") </span></div>");
        if(addToArray){
            selected_stocks.push(stock.symbol);
            setBox($value, selected_stocks);
        }
    }
    else
    {
        $holder.append("<div class=\"redBackground selection warning\">You can't include a stock twice!</div>");
        setTimeout(function(){ $(".warning").fadeOut() }, WARNING_DURATION);
    }
}
$(document).ready(function(){
    $value = $("." + CLASS_NAME);
    if($value.val())
    {
        var DONE = 4;
        var initValues = $value.val().split(",");
        var request = new XMLHttpRequest();
        request.onreadystatechange = function(){
            console.log(this.readyState);
            if(this.readyState === DONE)
            {
                var response = JSON.parse(this.responseText);
                var curr;
                for(var i = 0;i<initValues.length;i++)
                {
                    curr = initValues[i];
                    for(var j = 0; j<response.length;j++)
                    {
                        if(response[j].symbol === curr)
                        {
                            pushStock(response[j], true);
                            break;
                        }
                    }
                }
            }
        }
        request.open("GET", PREFETCH_URL, true);
        request.send();
    }
    var $box = $("<input type=\"text\" />");
    $box.addClass(TEXTBOX_CLASS);
    $box.keydown(function(event) {
        if(event.which === 13)
            event.preventDefault();
    });
    $holder = $("<div class=\"holder\"></div>");
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
            var out = [];
            var FIELDS = [datum.name, datum.symbol];
            for(var i = 0;i < FIELDS.length;i++)
            {
                var curr = FIELDS[i].split(" ");
                for(var p = 0;p<curr.length;p++)
                {
                    out.push(curr[p]);
                }
            }
            return out;
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
                pushStock(suggestion);
            });
});
