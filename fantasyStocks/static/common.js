"use strict"

function jsonBloodhound(url){
    var b = new Bloodhound({
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        datumTokenizer:  function(datum)
        {
            var out = [];
            for(var key in datum)
            {
                if(datum.hasOwnProperty(key)){
                    var curr = datum[key].split(" ");
                    for(var p = 0; p<curr.length; p++)
                    {
                        out.push(curr[p]);
                    }
                }
            }
            return out;
        },
        initialize: true,
        prefetch: {
            url: url,
            cache: false,
            transform: function(jsonObj)
            {
                return jsonObj;
            }, 
        }
    });
    return function(q, sync)
    {
        if(q === "")
        {
            return sync(b.index.all());
        }
        else
        {
            return b.search(q, sync);
        }
    };
}

function ConfirmationBox(text, buttons)
{
    // Buttons is an array of objects of the form {text: "button text", func: function() { console.log("Do stuff"); }}
    this.buttons = buttons;
    this.text = text;
    this.$holder = $("<div class=\"confirmationBox\"></div>");
    this.$holder.html(text + "<br />");
    for(var i = 0; i < buttons.length; i++)
    {
        var $currButton = $("<div class=\"confirmationButton\"></div>");
        $currButton.html(buttons[i].text);
        $currButton.click(buttons[i].func.bind(this));
        this.$holder.append($currButton);
    }
    this.destroy = function() 
    {
        this.$holder.remove();
    };
}
