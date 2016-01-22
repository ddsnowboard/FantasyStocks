"use strict"
var main;
var pk;
var tabFunctions = [];
var onTabClick = function(func){
    tabFunctions.push(func)
};
var runTabFunctions = function(domObject) {
    for(var i = 0; i < tabFunctions.length; i++) {
        tabFunctions[i](domObject);
    } 
};
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
$(document).ready(function(){
    main = $(".floorContainer");
    pk = $(".selected")[0].id;
    main.html(floors[pk]);
    $(".tabs li").click(function() {
        if(this.className.indexOf("selected") == -1)
        {
            $(".tabs li").removeClass("selected");
            $(this).addClass("selected");
            main.html(floors[this.id]);
            runTabFunctions(this);
        }
    });
    $($(".tabs li")[0]).removeClass("selected").click();
});
