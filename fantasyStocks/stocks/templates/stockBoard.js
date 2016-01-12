// Apparently this line gets run over and over. God only knows why. 
// Anyway, because of that, I have to do this or else it's always empty. 
var stockChanges = stockChanges || {};

var owners = {};
function calculateOwners(){
    owners = {};
    var players = $(".playerLine");
    for(var i = 0; i < players.length; i++)
    {
        var stocks = players[i].dataset.stocks.split(",");
        for(var s = 0; s < stocks.length; s++)
        {
            owners[stocks[s]] = players[i];
        }
    }
}
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
    var STOCK_URL_PLACEHOLDER = "ZZZ";
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
            xhrs[i].open("GET", STOCK_PRICE_URL.replace(STOCK_URL_PLACEHOLDER, symbol));
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
    $(".stock").mouseover(function(){
        $(owners[this.id]).addClass("highlighted");
    })
    .mouseout(function(){
        $(owners[this.id]).removeClass("highlighted");
    });
    $(".playerLine").mouseover(function() {
        var stocks = this.dataset.stocks.split(",");
        for(var i = 0; i < stocks.length; i++){
            $("#" + stocks[i]).addClass("highlighted");
        }
    }).mouseout(function() {
        var stocks = this.dataset.stocks.split(",");
        for(var i = 0; i < stocks.length; i++){
            $("#" + stocks[i]).removeClass("highlighted");
        }
    });
    calculateOwners();
    onTabClick = calculateOwners;
});
