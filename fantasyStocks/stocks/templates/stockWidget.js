"use strict"
var PREFETCH_URL = "{% url 'prefetch' %}";
var CLASS_NAME = "{{ class_name }}";
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
var StockWidget = function(id)
{
    this.$value = $("input." + CLASS_NAME);
    if(this.$value.val())
    {
        var DONE = 4;
        var initValues = this.$value.val().split(",");
        var request = new XMLHttpRequest();
        request.onreadystatechange = function(){
            console.log(this.readyState);
            if(this.readyState === DONE)
            {
                var response = JSON.parse(this.responseText);
                var curr;
                for(var i = 0; i<initValues.length; i++)
                {
                    curr = initValues[i];
                    for(var j = 0; j<response.length; j++)
                    {
                        if(response[j].symbol === curr)
                        {
                            this.pushStock(response[j], true);
                            break;
                        }
                    }
                }
            }
        }
        request.open("GET", PREFETCH_URL, true);
        request.send();
    }
    this.id = id;
    this.TEXTBOX_CLASS = "inputBox";
    this.selected_stocks = [];

    this.$holder = $("<div class=\"holder\"></div>");
    var that = this;
    this.$holder.on("mousedown", ".selection", function() {
        that.selected_stocks.splice(that.selected_stocks.indexOf($(this).attr('id')), 1);
        that.setBox(that.selected_stocks);
        $(this).remove();
    })
    .on("mouseenter", ".selection", function() {
        $(this).addClass("redBackground");
    })
    .on("mouseleave", ".selection", function() {
        $(this).removeClass("redBackground");
    });

    this.$box = $("<input type=\"text\" />");
    this.$box.addClass(this.TEXTBOX_CLASS);
    this.$box.attr("id", this.id);
    this.$box.keydown(function(event) {
        if(event.which === 13)
            event.preventDefault();
    });

    this.setBox = function(arr)
    {
        this.$value.val(arr.join(","));
    }
    this.pushStock = function(stock, addToArray)
    {
        var WARNING_DURATION = 2000;
        // The JavaScript eqivalent of a default argument. Brilliant.
        if(addToArray === undefined)
        {
            addToArray = true;
        }
        if(this.selected_stocks.indexOf(stock.symbol) === -1)
        {
            that.$holder.append("<div class=\"selection\" id=\"" + stock.symbol + "\"><span class=\"name\">" + stock.name + "</span><span class=\"symbol\"> (" + stock.symbol + ") </span></div>");
            if(addToArray){
                that.selected_stocks.push(stock.symbol);
                that.setBox(that.selected_stocks);
            }
        }
        else
        {
            that.$holder.append("<div class=\"redBackground selection warning\">You can't include a stock twice!</div>");
            setTimeout(function(){ $(".warning").fadeOut() }, WARNING_DURATION);
        }
    }
    this.$value.parent().append(this.$holder).append(this.$box);
    this.$box.typeahead({
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

    this.$box.bind("typeahead:select", function(event, suggestion)
            {
                that.$box.typeahead("val", "");
                that.pushStock(suggestion);
            });
}

$(document).ready(function(){
    if(boxes !== undefined)
    {
        boxes.push(new StockWidget("{{ id }}"));
    }
    else
    {
        var boxes = [new StockWidget("{{ id }}")];
    }
});
