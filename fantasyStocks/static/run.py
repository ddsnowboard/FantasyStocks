import csv, json
with open("wholelist.csv") as f:
    reader = csv.reader(f)
    output = []
    for i in reader:
        output.append({"name": i[1], "symbol": i[0]})
    with open("out.json", "w") as w:
        w.write(json.dumps(output))
