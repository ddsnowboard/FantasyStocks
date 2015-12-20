"use strict"
var currentTradeSet;
var received;
var sent;
var tradeInbox;
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
    received = $("#received");
    sent = $("#sent");
    tradeInbox = $(".tradeInbox");
    currentTradeSet = trades[pk];
    setTradeBox(tradeInbox, currentTradeSet.received);
    onTabClick = function(that) {
        received.addClass("selected");
        sent.removeClass("selected");
        currentTradeSet = trades[that.id];
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
    };

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
