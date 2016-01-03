$(document).ready(function() {
    for(var i = 0; i < stockWidgets.length; i++)
    {
        stockWidgets[i].disable();
    }
    for(var i = 0; i < playerPickers.length; i++)
    {
        playerPickers[i].disable();
    }
    if($(".errorlist").length > 0)
    {
        $("#acceptButton").attr("disabled", "disabled").attr("title", "There is an error with this trade; you can't accept it.");
    }
});
