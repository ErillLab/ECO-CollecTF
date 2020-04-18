import os
import sys
import csv

fname = sys.argv[1]

with open(fname, "rb") as infile:
  reader = csv.reader(infile)
  for row in reader:
    if len(row) < 1:
      continue
    if len(row[1]) >=6:
      pmc_str = row[1][3:] # remove PMC
      pmid = row[0]
      print pmid+","+pmc_str
      