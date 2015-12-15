"use strict"
// This is the default URL that will give you all the stocks.
var PREFETCH_URL = "{% url 'prefetch' %}";
var CLASS_NAME = "{{ class_name }}";
var stockWidgets = [];


var StockWidget = function(inputElement)
{
    // Defaults
    this.minLength = 1;
    this.highlight = false;
    this.hint = false;
    this.url = PREFETCH_URL;
    this.pending = ". . .";
    this.enabled = false;
    this.suggestionFunc = function(obj)
    {
        return "<div class=\"suggestion\"><span class=\"name\">" + obj.name + "</span><span class=\"symbol\"> (" + obj.symbol + ") </span></div>"
    }
    this.limit = 20;
    this.displayFunc = function(o){ return o.name; }
    this.enable = function() {
        this.enabled = true;
        var that = this; 
        this.$holder.on("mousedown", ".selection:not(.warning)", function() {
            that.remove($(this).attr("id"));
        })
        .on("mouseenter", ".selection:not(.warning)", function() {
            $(this).addClass("redBackground");
        })
        .on("mouseleave", ".selection:not(.warning)", function() {
            $(this).removeClass("redBackground");
        });
        this.$box.removeAttr("disabled");
    }
    this.disable = function() {
        this.enabled = false;
        this.$holder.unbind();
        this.$box.attr("disabled", "disabled");
    }

    this.$value = $(inputElement);
    if(this.$value.val())
    {
        var DONE = 4;
        var initValues = this.$value.val().split(",");
        var request = new XMLHttpRequest();
        var that = this;
        request.onreadystatechange = function(){
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
                            that.pushStock(response[j], true);
                            break;
                        }
                    }
                }
            }
        }
        request.open("GET", PREFETCH_URL, true);
        request.send();
    }
    this.TEXTBOX_CLASS = "inputBox";
    this.selectedStocks = [];

    this.$holder = $("<div class=\"holder\"></div>");
    var that = this;

    this.$box = $("<input type=\"text\" />");
    this.$box.addClass(this.TEXTBOX_CLASS);
    this.$box.keydown(function(event) {
        if(event.which === 13)
            event.preventDefault();
    });

    this.setBox = function(arr)
    {
        this.$value.val(arr.join(","));
    };

    this.pushStock = function(stock, addToArray)
    {
        var WARNING_DURATION = 2000;
        // The JavaScript eqivalent of a default argument. Brilliant.
        if(addToArray === undefined)
        {
            addToArray = true;
        }
        if(this.selectedStocks.indexOf(stock.symbol) === -1)
        {
            that.$holder.append("<div class=\"selection\" id=\"" 
                    + stock.symbol + "\"><span class=\"name\">" 
                    + stock.name + "</span><span class=\"symbol\"> (" 
                    + stock.symbol + ") </span></div>");
            if(addToArray){
                this.selectedStocks.push(stock.symbol);
                this.setBox(that.selectedStocks);
            }
        }
        else
        {
            that.$holder.append("<div class=\"redBackground selection warning\">You can't include a stock twice!</div>");
            setTimeout(function(){ $(".warning").fadeOut() }, WARNING_DURATION);
        }
    }

    this.$value.parent().append(this.$holder).append(this.$box);

    this.onSelectFunctions = [];

    this.runOnSelect = function(event, suggestion)
    {
        for(var i = 0; i < this.onSelectFunctions.length; i++)
        {
            this.onSelectFunctions[i](event, suggestion);
        }
    }

    this.onSelect = function(func)
    {
        this.onSelectFunctions.push(func);
    }

    this.$box.bind("typeahead:select", function(event, suggestion)
            {
                that.$box.typeahead("val", "");
                that.pushStock(suggestion);
                that.runOnSelect(event, suggestion);
            });

    this.changeURL = function(url) 
    {
        this.url = url;
        this.setTypeahead();
    };

    this.setTypeahead = function()
    {
        this.$box.typeahead("destroy");
        this.$box.typeahead({
            minLength: this.minLength,
            highlight: this.highlight,
            hint: this.hint,
        }, {
            name: "stocks_dataset", 
            source: jsonBloodhound(this.url),
            templates: {
                pending: this.pending, 
                suggestion: this.suggestionFunc, 
            }, 
            limit: this.limit,
            rateLimitBy: "throttle",
            rateLimitWait: 600,
            display: this.displayFunc, 
        });
    };

    this.remove = function(symbol)
    {
        this.selectedStocks.splice(this.selectedStocks.indexOf(symbol));
        this.setBox(this.selectedStocks);
        $(".selection:not(.warning)#" + symbol.toUpperCase()).remove();
    };

    this.clear = function()
    {
        var stocksCopy = this.selectedStocks.slice();
        for(var i = 0; i < stocksCopy.length; i++)
        {
            this.remove(stocksCopy[i]);
        }
    };


    this.setTypeahead();
    this.enable();
}

$(document).ready(function(){
    var $inputs = $("." + CLASS_NAME);
    for(var i = 0; i < $inputs.length; i++)
    {
        stockWidgets.push(new StockWidget($inputs[i]));
    }
});
