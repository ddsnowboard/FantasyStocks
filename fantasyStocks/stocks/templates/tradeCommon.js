var OTHER_USER_STOCKS_NAME = "other_stocks";
var USER_STOCKS_NAME = "user_stocks";
var USER_NAMEBOX_ID = "username";
var OTHER_NAMEBOX_ID = "playerChoiceWidget";
var floor;
var otherStockbox;
var userStockbox;
var name;
var $username;
var otherUsername;
function getUserURL(username, floor)
{
    var NAME_REPLACEMENT = "replacement";
    // This has to be numbers so it matches the regex.
    var FLOOR_REPLACEMENT = "12345";
    return "{% url 'prefetch' user='replacement' pkFloor=12345 %}"
        .replace(NAME_REPLACEMENT, username).replace(FLOOR_REPLACEMENT, floor);
}
function getFloorPlayersURL(floor){
    var FLOOR_REPLACEMENT = "124512352354";
    return "{% url "floorPlayers" pkFloor=124512352354 %}".replace(FLOOR_REPLACEMENT, floor);
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
    sb.setURL(getUserURL(username, floor));
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
    otherStockbox.minLength = 0;
    otherStockbox.setTypeahead();
    userStockbox.minLength = 0;
    userStockbox.setTypeahead();
    for(var i = 0; i < playerPickers.length; i++)
    {
        var w = playerPickers[i];
        var currName = w.$box.attr("id");
        if(currName === OTHER_NAMEBOX_ID)
        {
            otherUsername = w;
        }
    }
    otherUsername.setURL(getFloorPlayersURL(floor));
    $username = $("#" + USER_NAMEBOX_ID);
    var max_stocks = parseInt($("#maxStocks").html());
    var remainingStocks = max_stocks - (userNumberOfStocks + otherStockbox.size() - userStockbox.size());
    $("#currStocks").html(remainingStocks);

    var onChangeFunction = function() {
        remainingStocks = max_stocks - (userNumberOfStocks + otherStockbox.size() - userStockbox.size());
        $("#currStocks").html(remainingStocks);
        if(remainingStocks < 0){
            $("#count").css("color", "red");
        }
        else
        {
            $("#count").css("color", "black");
        }
    }
    userStockbox.onChange(onChangeFunction);
    otherStockbox.onChange(onChangeFunction);
});
