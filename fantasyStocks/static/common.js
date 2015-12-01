"use strict"

function jsonBloodhound(url){
    var b = new Bloodhound({
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        datumTokenizer:  function(datum)
        {
            var out = [];
            for(var key in datum)
            {
                if(datum.hasOwnProperty(key)){
                    var curr = datum[key].split(" ");
                    for(var p = 0; p<curr.length; p++)
                    {
                        out.push(curr[p]);
                    }
                }
            }
            return out;
        },
        initialize: true,
        prefetch: {
            url: url,
            cache: false,
            transform: function(jsonObj)
            {
                return jsonObj;
            }, 
        }
    });
    b._get = b.get;
    var f = function(q, sync){
        if(q === "")
        {
            console.log("entered");
            return this.index.datums;
        }
        else
        {
            return this.search(q);
        }
    }
    b.get = f;
    console.log(b);
    return b;
}
