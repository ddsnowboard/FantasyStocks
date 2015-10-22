"use strict"
$(document).ready(function() {
    $("tr").click(function() {
        window.location = $(this).find("a").attr("href");
    });
});
