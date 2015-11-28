// This is the id of the HTML element(s), provided by a constant in the 
// python Field through a URLconf argument. 
var ID = "{{ id }}";
// This is the URL of a view that just returns a JSON blob of all the users in the 
// game. There is no logic that prevents you from inputting a user that isn't 
// playing on this floor. Maybe later. I'd have to read it from the URL though, 
// which might be ugly. Someday...
var PLAYER_URL = "{% url 'users' %}"; 
// This variable is just to expose a list of PlayerPickers to the global namespace
// so I can use them in other scripts. Nothing crazy. 
var playerPickers = [];
function PlayerPicker(inputElement){
    /*
     * This is the class that holds all the logic for the PlayerPicker
     * widget. I did it this way because doing it the procedural way 
     * makes it really hard to keep everything separate if you want to 
     * do stuff to them in other scripts. Doing it this way, combined with the
     * array above, lets you access everything together in a nice package from 
     * anwhere else in the JavaScript code for a page as long as this is executed 
     * before.
     */
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
    this.$box = $(inputElement);
    this.setURL = function(url){
        this.$box.typeahead("destroy");
        this.$box.typeahead({
            minLength: 1,
            highlight: false, 
            hint: false,
        }, { 
            name: "user_dataset", 
            source: jsonBloodhound(url), 
            templates: {
                pending: ". . .", 
                suggestion: function(obj) {
                    return "<div class=\"suggestion\">" + obj.username + "</div>";
                },
            },
            limit: 20,
            display: function(o){ return o.username; },
        });
    }
    this.setURL(PLAYER_URL);
    this.$box.keydown(function(event)
            {
                if(event.which === 13)
                {
                    event.preventDefault();
                }
            });
    var that = this;
    this.$box.bind("typeahead:select", function(event, suggestion)
            {
                that.runOnSelect(event, suggestion);
            });
}

$(document).ready(function(){
    var boxes = $("#" + ID);
    for(var i = 0; i < boxes.length; i++)
    {
        playerPickers.push(new PlayerPicker(boxes[i]));
    }
});
