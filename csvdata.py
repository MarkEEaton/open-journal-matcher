""" extract issns from journallist.csv """

import csv
import json
import regex

MONTH = "2021-09"
output = []

with open("journallist-" + MONTH + ".csv", newline="") as csvfile:
    data = csv.reader(csvfile)
    for row in data:
        try:
            print(row[7].lower())
            if "english" == row[7].lower():
                if row[4]:
                    if regex.match(r'^[0-9]{4}-[0-9]{3}[0-9xX]$', row[4]):
                        output.append(row[4])
                    else:
                        print(row[4], 'regex does not match')
                elif row[5]:
                    if regex.match(r'^[0-9]{4}-[0-9]{3}[0-9Xx]$', row[5]):
                        output.append(row[5])
                    else:
                        print(row[5], 'regex does not match')
                else:
                    print("no issn")
        except:
            pass

with open("issnlist-" + MONTH + ".txt", "w") as issnfile:
    issnfile.write(json.dumps(output))
