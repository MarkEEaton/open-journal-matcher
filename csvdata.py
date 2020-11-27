""" extract issns from journallist.csv """

import csv
import json
import regex

output = []

with open("journallist-June2020.csv", newline="") as csvfile:
    data = csv.reader(csvfile)
    for row in data:
        try:
            if "english" in row[30].lower():
                if row[4]:
                    if regex.match(r'^[0-9]{4}-[0-9]{3}[0-9xX]$', row[4]):
                        output.append(row[4])
                    else:
                        print(row[4], 'regex does not match')
                elif row[3]:
                    if regex.match(r'^[0-9]{4}-[0-9]{3}[0-9Xx]$', row[3]):
                        output.append(row[3])
                    else:
                        print(row[3], 'regex does not match')
                else:
                    print("no issn")
        except:
            pass

with open("issnlist-multilingual.txt", "w") as issnfile:
    issnfile.write(json.dumps(output))
