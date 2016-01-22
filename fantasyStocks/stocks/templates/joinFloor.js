"use strict"
$(document).ready(function() {
    $("#id_floor_name").typeahead({
        minLength: 0,
        highlight: false, 
        hint: false,
    }, {
        name: "floors", 
        templates: {
            suggestion: function(floorObj)
            {
                return "<div class=\"suggestion\">" + floorObj["name"] + "</div>";
            }, 
            pending: ". . .", 
        }, 
        source: jsonBloodhound("{% url "floorsJson" %}"), 
        display: function(floorObj)
        {
            return floorObj["name"];
        },
    })
});
