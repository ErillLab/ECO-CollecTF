import os
import sys

ofname = sys.argv[1] # output name for the log of the multi run
which = sys.argv[2]

val_pos = -1
values = []
  
with open(ofname, "r") as fpi:
  for l in fpi:
    line = l.strip()
    if line.find(which) > -1:
      items = line.split()
      values.append(float(items[val_pos]))

print values
sum_vals = sum(values)
print "sum:", sum_vals
avg_val = sum(values)/len(values)
print which, avg_val

  