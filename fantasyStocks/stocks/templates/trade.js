$(document).ready(function() {
    if($username.val() !== "")
    {
        setUserStockbox($username.val(), floor);
    }
    if(otherUsername.$box.val() !== "")
    {
        setOtherStockbox(otherUsername.$box.val(), floor);
        otherUsername.name = otherUsername.$box.val();
    }
    // This makes sure that the JavaScript prevents you from putting in a bunch of stocks 
    // for a person who doesn't have them. 
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
                    otherUsername.name = suggestion.username;
                }
            });
});
