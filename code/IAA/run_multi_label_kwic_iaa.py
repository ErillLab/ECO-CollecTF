import os
import sys


root_dir = sys.argv[1]
pfname = sys.argv[2] # pairs file
labels_name = sys.argv[3] # labels -- eco or rz
sub_dir = sys.argv[4] # Example: rzhetsky
use_no_term_ic = sys.argv[5]


data_dir = os.path.join(root_dir, "data")
data_dir = os.path.join(data_dir, sub_dir)
rss_dir = os.path.join(root_dir, "raw_stats_split")
rss_dir = os.path.join(rss_dir, sub_dir)

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
  sys_cmd = "python multi_label_kw_ic.py "+labels_name+" "+data_dir+" "+rss_dir+" ic "+use_no_term_ic+" "+annotators[0]+" "+annotators[1]

  print "\n",sys_cmd
  os.system(sys_cmd)
  