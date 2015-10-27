import csv

with open("wholelist.csv") as f:
    reader = csv.reader(f)
    d = {}
    for i in reader:
        d[i[0]] = {k: l for k in ['symbol', 'name', 'lastsale', 'marketcap', 'ipoyear', 'sector', 'industry', 'summary quote'] for l in i[1:]}
    print(d["SF"])
