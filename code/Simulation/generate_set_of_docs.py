# After this script runs, we have the GS docs.
# This script calls generate_iaa_docs.dat so
# we have annotations for A and B in data and the data_as_tags files completed.
# An empty raw_stats_split dir is also made.
import sys
import os
import time

top_dir = sys.argv[1]
param_file = sys.argv[2] 
eco_branches_file = sys.argv[3] # Term list for drawing ECO terms
which = "random"

num_reps = 100
num_docs = 10
obo_file = "..\eco_v2018-09-14.obo"

term_file = eco_branches_file
  
cur_dir = os.getcwd()

if not os.path.exists(top_dir):
  os.mkdir(top_dir)
log_file = os.path.join(top_dir, "generate_docs_log.txt")  
sys_cmd = "echo GenerateLog > "+log_file
os.system(sys_cmd)

for i in range(num_reps):
  os.chdir(top_dir)
  new_subdir = "docs_outdir"+str(i)
  if not os.path.exists(new_subdir):
    os.mkdir(new_subdir)
  full_dir = os.path.join(top_dir, new_subdir)
  os.chdir(cur_dir)
  sys_cmd = "python generate_iaa_docs.py "+param_file+" "+obo_file+" "+term_file+" "+full_dir+" "+str(num_docs) + " " + which +" >> "+log_file
  print sys_cmd
  os.system(sys_cmd)
  time.sleep(1)
  
  sys_cmd = "python generate_iaa_annots.py "+param_file+" "+obo_file+" "+term_file+" "+full_dir+" "+which+" >> "+log_file
  print sys_cmd
  os.system(sys_cmd)
  
  