"use strict"
var main;
$(document).ready(function() {
    main = $(".dashboardMain");
    main.html(floors[$(".selected")[0].id]);
    $(".leftTabs li").click(function() {
        if(this.className.indexOf("selected") == -1)
        {
            $(".leftTabs li").removeClass("selected");
            $(this).addClass("selected");
            main.html(floors[this.id]);
        }
    });
}); 

