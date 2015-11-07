from pprint import pprint
import json
import re
REGEXP = re.compile("(?P<symbol>[A-Z]{1,4}).*")
with open("stocks.json") as f:
    l = json.loads(f.read())
    out = []
    for i in l:
        if not "^" in i["symbol"]:
            out.append(i)
    with open("newStocks.json", "w") as w:
        w.write(json.dumps(out))
