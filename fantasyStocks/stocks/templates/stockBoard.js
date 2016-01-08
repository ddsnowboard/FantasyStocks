// Apparently this line gets run over and over. God only knows why. 
// Anyway, because of that, I have to do this or else it's always empty. 
var stockChanges = stockChanges || {};
function setPrice(el, price)
{
    var klass;
    var sign;
    if(price > 0)
    {
        klass = "green";
        sign = "+";
    }
    else if(price < 0)
    {
        klass = "red";
        sign = "";
    }
    else
    {
        klass = "blue";
        sign = "";
        // No one else has to know about this...
    }
    $(el).addClass(klass).removeClass("loadingPrice").html(sign + price.toFixed(2));
}
function getPriceCallback(el, xhr)
{
    return function(){
        var DONE = 4;
        if(xhr.readyState === DONE)
        {
            var jsonObj = JSON.parse(xhr.response);
            setPrice(el, jsonObj.change);
            stockChanges[jsonObj.symbol] = jsonObj.change;
        }
    };
}
function loadPrices(){
    var loadingPrices = $(".loadingPrice");
    var STOCK_PRICE_URL = "{% url "stockPrice" symbol="ZZZ" %}";
    var xhrs = [];
    for(var i = 0; i < loadingPrices.length; i++)
    {
        var price = loadingPrices[i];
        var symbol = price.id;
        if(stockChanges[symbol] === undefined)
        {
            xhrs.push(new XMLHttpRequest());
            xhrs[i].onreadystatechange = getPriceCallback(price, xhrs[i]);
            xhrs[i].open("GET", STOCK_PRICE_URL.replace("ZZZ", symbol));
            xhrs[i].send();
        }
        else
        {
            xhrs[i] = null;
            setPrice(price, stockChanges[symbol]);
        }
    }
}

$(document).ready(function() {
    loadPrices();
});
