"use strict"
$(document).ready(function() {
    $("tr").click(function(event) {
        if(event.target.nodeName !== "TH")
        {
            window.location = $(this).find("a").attr("href");
        }
    });
});
