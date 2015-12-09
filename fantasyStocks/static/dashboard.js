"use strict"
var main;
var currentTradeSet;
var received;
var sent;
var tradeInbox;
function setTradeBox($box, text)
{
    if(text === "" || /^\s*$/.test(text))
    {
        $box.html("<tr><td>There doesn't seem to be anything here...</td></tr>")
    }
    else
    {
        $box.html(text);
    }
}
$(document).ready(function() {
    main = $(".dashboardMain");
    received = $("#received");
    sent = $("#sent");
    tradeInbox = $(".tradeInbox");
    var pk = $(".selected")[0].id;
    main.html(floors[pk]);
    currentTradeSet = trades[pk];
    setTradeBox(tradeInbox, currentTradeSet.received);
    $(".leftTabs li").click(function() {
        if(this.className.indexOf("selected") == -1)
        {
            $(".leftTabs li").removeClass("selected");
            $(this).addClass("selected");
            main.html(floors[this.id]);
            received.addClass("selected");
            sent.removeClass("selected");
            currentTradeSet = trades[this.id];
            setTradeBox(tradeInbox, currentTradeSet.received);
            if(currentTradeSet.requests == undefined)
            {
                $("#requests").css("visibility", "hidden");
            }
            else
            {
                $("#requests").css("visibility", "visible");
            }
        }
    });
    $($(".leftTabs li")[0]).removeClass("selected").click();
    $(".tradeTab").click(function() {
        if(this.className.indexOf("selected") == -1)
        {
            $(".tradeTab").removeClass("selected");
            $(this).addClass("selected");
            setTradeBox(tradeInbox, currentTradeSet[this.id]);
        }
    });
}); 

