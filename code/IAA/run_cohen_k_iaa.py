import os
import sys

root_dir = sys.argv[1] # Dir above the annotator dirs with the tags
pfname = sys.argv[2] # pairs file
labels_name = sys.argv[3] # labels file
output_dir = sys.argv[4]

a_pairs = []
with open(pfname, "r") as fpi:
  for l in fpi:
    line = l.strip()
    if len(line) < 1:
      continue
    a_pairs.append(line)
    
for ap in a_pairs:
  print "AP:", ap
  annotators = ap.split("\t")
  sys_cmd = "python cohen_k_iaa.py "+labels_name+" "+root_dir+" "+output_dir+" "+annotators[0]+" "+annotators[1]
  print "\n",sys_cmd
  os.system(sys_cmd)
  