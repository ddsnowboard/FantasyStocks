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
    return function(q, sync)
    {
        if(q === "")
        {
            return sync(b.index.all());
        }
        else
        {
            return b.search(q, sync);
        }
    };
}
