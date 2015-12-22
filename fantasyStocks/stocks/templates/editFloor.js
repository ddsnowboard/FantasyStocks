$(document).ready(function() {
    $("#deleteButton").click(function () {
        $(document.body).append(new ConfirmationBox("Are you sure you want to delete floor {{ floor.name }}?",
                    [ {text: "Yes", func: function(){ window.location.href = "{% url "deleteFloor" pkFloor=floor.pk %}";} },
                    {text: "No", func: function(){ this.destroy(); } } ]).$holder);
    });
});
