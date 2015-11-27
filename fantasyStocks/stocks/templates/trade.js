var OTHER_USER_STOCKS_NAME = "other_stocks";
var USER_STOCKS_NAME = "user_stocks";
var USER_NAMEBOX_ID = "username";
var OTHER_NAMEBOX_ID = "playerChoiceWidget";
var floor;
var otherStockbox;
var userStockbox;
var name;

function getUserURL(username, floor)
{
    var NAME_REPLACEMENT = "replacement";
    // This has to be numbers so it matches the regex.
    var FLOOR_REPLACEMENT = "12345";
    return "{% url 'prefetch' user='replacement' floor=12345 %}"
        .replace(NAME_REPLACEMENT, username).replace(FLOOR_REPLACEMENT, floor);
}
function getFloor()
{
    var parts = window.location.pathname.split('/');
    for(var i = 0; i < parts.length; i++)
    {
        if(parts[i] === "floor")
            return parts[i + 1];
    }
}
function setStockbox(sb, username, floor)
{
    sb.changeURL(getUserURL(username, floor));
}
function setUserStockbox(username, floor)
{
    setStockbox(userStockbox, username, floor);
}
function setOtherStockbox(username, floor)
{
    setStockbox(otherStockbox, username, floor);
}
$(document).ready(function() {
    // I guess here is as good a place as any to do some design. 
    // So what I'm going to do is first get the name of each
    // StockWidget's value box, from the StockWidgets list
    // that I put in the stockWidget.js file. I'll have variables that hold 
    // the HTML class names of all the things in question, either hard-coded 
    // or with template variables, and I'll use those variables to figure out
    // which stock box is which. Then I'll read the usernames from the user
    // boxes and call the changeURL() methods on the corresponding 
    // StockWidgets with the usernames and floor number as properly-positioned 
    // arguments so that the server will send back the JSON for that user's stocks. 
    // I'll get the floor number from the URL of the trade page.
    floor = getFloor();
    for(var i = 0; i < stockWidgets.length; i++)
    {
        name = stockWidgets[i].$value.attr("name");
        if(name === OTHER_USER_STOCKS_NAME)
        {
            otherStockbox = stockWidgets[i];
        }
        else if(name === USER_STOCKS_NAME)
        {
            userStockbox = stockWidgets[i];
        }
    }
    var otherUsername;
    for(var i = 0; i < playerPickers.length; i++)
    {
        var w = playerPickers[i];
        var currName = w.$box.attr("id");
        if(currName === OTHER_NAMEBOX_ID)
        {
            otherUsername = w;
        }
    }
    var username = $("#" + USER_NAMEBOX_ID);
    if(username.val() !== "")
    {
        setUserStockbox(username.val(), floor);
    }
    if(otherUsername.$box.val() !== "")
    {
        setOtherStockbox(otherUsername.$box.val(), floor);
    }
    otherUsername.onSelect = function(event, suggestion)
    {
        setOtherStockbox(otherUsername.$box.val(), floor);
        // TODO: Clear stockbox if you change the name, or, better yet, make it ask you if you really want to do this. 
    };
});
