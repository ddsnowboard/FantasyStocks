"use strict"
$(document).ready(function() {
    $("td").click(function() {
        window.location = $(this).find("a").attr("href");
    });
});
