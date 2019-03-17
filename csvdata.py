import csv
import json

output = []

with open("journallist.csv", newline="") as csvfile:
    data = csv.reader(csvfile)
    for row in data:
        try:
            english = row[32][:7].lower()
            if english == "english":
                _ = row[32][
                    7
                ]  # do this to throw an index error if the field is longer than 'english'
        except IndexError:
            if row[4]:
                output.append(row[4])
            elif row[3]:
                output.append(row[3])
            else:
                print("no issn")

with open("issnlist.txt", "w") as issnfile:
    issnfile.write(json.dumps(output))
