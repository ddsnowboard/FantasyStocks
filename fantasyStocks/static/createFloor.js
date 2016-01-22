// Find the submit button, and capture it's input. If it get's clicked, 
// check whether everything is good. If it is, let it run. If not, show 
// ConfirmationBox to make sure that the user is OK with what she's done, 
// and then send it. I'm not really feeling it at this point, but I should 
// do it later.

var EXAMPLE_NUMBER_OF_PLAYERS = 5;
$(document).ready(function() {
    $("#select").click(function(event){
        // The selectors that I'm using are tied to the names of the 
        // fields in the form, so I have to make sure that I change these
        // if I ever change those. 
        var permissiveness = $("#id_permissiveness").val();
        var num_players = parseInt($("#id_number_of_stocks").val());
        var num_stocks = stockWidgets[0].size();
        var max_stocks = $("#id_number_of_stocks").val();
        if(num_stocks < max_stocks * EXAMPLE_NUMBER_OF_PLAYERS && permissiveness == "closed")
        {
            $(document.body).append((new ConfirmationBox("You only have " + num_stocks +" stocks, so your floor will be unable to support " + EXAMPLE_NUMBER_OF_PLAYERS.toString() +" players unless you change the permissiveness. Are you sure you want to do this?", 
                            [{
                                text: "Yes",
                                func: function() {
                                $("#select").prop("disabled", false).unbind().click(); }
                            },
                            {
                                text: "No",
                                func: function() { this.destroy() }
                            }]).$holder));
            event.preventDefault();
        }
    });
});
