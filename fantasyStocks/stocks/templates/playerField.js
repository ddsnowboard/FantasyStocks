var ID = "{{ id }}";
var PLAYER_URL = "{% url 'users' %}"; 
var playerPickers = [];
function PlayerPicker(inputElement){
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
                    return "<div class=\"suggestion\">" + obj.username + " (" + obj.email + ")</div>";
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
}

$(document).ready(function(){
    var boxes = $("#" + ID);
    for(var i = 0; i < boxes.length; i++)
    {
        playerPickers.push(new PlayerPicker(boxes[i]));
    }
});
