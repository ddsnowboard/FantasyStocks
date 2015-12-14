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
    var $username = $("#" + USER_NAMEBOX_ID);
    if($username.val() !== "")
    {
        setUserStockbox($username.val(), floor);
    }
    if(otherUsername.$box.val() !== "")
    {
        setOtherStockbox(otherUsername.$box.val(), floor);
        otherUsername.name = otherUsername.$box.val();
    }
    // This makes sure that the JavaScript prevents you from putting in a bunch of stocks for a person who doesn't have them. 
    otherUsername.onSelect(function(event, suggestion)
            {
                if(otherStockbox.selectedStocks.length !== 0 && suggestion !== otherUsername.name)
                {
                    $(document.body).append(new ConfirmationBox("If you change the user, all the stocks that you already selected will disappear.",
                                [{text: "Ok", 
                                    func: function(){ 
                                        otherStockbox.clear();
                                        setOtherStockbox(otherUsername.$box.val(), floor);
                                        otherUsername.name = otherUsername.$box.val();
                                        this.destroy();
                                    }
                                }, {text: "Cancel",
                                    func: function(){ 
                                        otherUsername.$box.typeahead("val", otherUsername.name);
                                        this.destroy();
                                    }, 
                                }
                                ]).$holder);
                }
                else
                {
                    setOtherStockbox(otherUsername.$box.val(), floor);
                    otherUsername.name = suggestion;
                }
            });
});
