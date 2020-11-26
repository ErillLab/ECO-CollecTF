# Run in anaconda window
import os
import sys
import pandas as pd

def get_data(fname):
  # this has the values in the first line, separated by commas.
  num_params = 4
  num_at_end_to_skip = 3 # the min, max, and avg

  with open(fname, "r") as fpi:
    dlines = fpi.readlines()
  
  ditems = dlines[0].strip().split(",")[num_params:-1*num_at_end_to_skip]
  #print "Len items:", len(ditems), ditems[0],ditems[-1]
  return ditems

def output_data(dfname, out_fname):
  print "Output to", out_fname
  dfname.to_csv(out_fname, index=False)
  
#####################################
in_fname = sys.argv[1] # file with list of subdirs to process
hop_pos = int(sys.argv[2]) # simplistic -- place in the subdir name with the p/hop value
out_prefix = sys.argv[3] 

k_fname = "summary_sent_iaa_k.txt"
kw_fname = "summary_kw_stats_no1.txt"


dfk = pd.DataFrame()
dfkw = pd.DataFrame()

with open(in_fname, "r") as fpi:
  subdirs = fpi.readlines()
for s in subdirs:
  line = s.strip()
  if len(line) < 1:
    continue
  print "Process", line
  items = line.split("_")
  print items, hop_pos
  hop_val = items[hop_pos]
  
  print hop_val

  k_nums = get_data(os.path.join(line, k_fname))
  kw_nums = get_data(os.path.join(line, kw_fname))
  dfk[hop_val] = k_nums
  dfkw[hop_val] = kw_nums
  
output_data(dfk, out_prefix+"_k.csv")
output_data(dfkw, out_prefix+"_kw.csv")

