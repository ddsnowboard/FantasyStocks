"use strict"

/* 
 * I had repeated this code all over the place, so I decided to 
 * Not Repeat Myself and put it here. I also wanted to localize some of 
 * the below documented complexity. 
 */
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
    /*
     * This ugly bit is here so that I can let have something for the 
     * typeahead to show when it is active but empty. Apparently, they didn't
     * think of this when they were writing Bloodhound. Oh well. 
     */
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
    /* Buttons is an array of objects of the form {text: "button text", func: function() { console.log("Do stuff"); }}
     * Note that the functions are run with the actual ConfirmationBox as the context (ie, when you use `this`, you'll get the ConfirmationBox object). 
     * Bit of fanciness I did there. 
     */
    this.destroy = function() 
    {
        this.$holder.remove();
        $("body > *:not(.confirmationBox)").css("opacity", 1);
        $(":submit").prop("disabled", false);
    };

    this.buttons = buttons;
    this.text = text;
    this.$holder = $("<div class=\"confirmationBox\"></div>");
    this.$holder.html(text + "<br />");
    // Make everything else on the page hard to see so the user might not click on it. 
    $("body > *:not(.confirmationBox)").css("opacity", .1);
    $(":submit").prop("disabled", true);
    for(var i = 0; i < buttons.length; i++)
    {
        var $currButton = $("<div class=\"confirmationButton\"></div>");
        $currButton.html(buttons[i].text);
        $currButton.click(buttons[i].func.bind(this));
        this.$holder.append($currButton);
    }
}
