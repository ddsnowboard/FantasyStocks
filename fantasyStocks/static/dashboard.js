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
function rebind()
{
    $(".acceptButton").click(function(event)
            {
                var that = this;
                var url = $(that).attr("href");
                $(document.body).append((new ConfirmationBox("Do you want to add the stock " + this.id + " to this floor?", 
                        [{text: "Yes", func: function() { window.location = url; }},
                        {text: "No", func: function(){ window.location = url + "del/"; }},
                        {text: "Cancel", func: function() { this.destroy(); }}])).$holder);
                event.preventDefault();
            }); 
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
            rebind();
        }
    });
    $($(".leftTabs li")[0]).removeClass("selected").click();
    $(".tradeTab").click(function() {
        if(this.className.indexOf("selected") == -1)
        {
            $(".tradeTab").removeClass("selected");
            $(this).addClass("selected");
            setTradeBox(tradeInbox, currentTradeSet[this.id]);
            rebind();
        }
    });
    $(".deleteButton").click(function(event)
            {
                if(confirm("Are you sure you want to leave " + this.id + "?"))
                {}
                else
                {
                    event.preventDefault();
                }
            });
});

