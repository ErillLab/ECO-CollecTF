import os
import sys
import glob
import time

def run_grep(look_for, log_file, stats_file):
  sys_cmd = 'grep "'+look_for+'" '+log_file+" > "+stats_file+" 2> greperr.txt"
  os.system(sys_cmd)
  
top_dir = sys.argv[1]
pair_file = sys.argv[2]

cur_dir = os.getcwd()
iaa_code_dir = "../IAA"

steps = [1, 2]
#steps = [2]

nos = ["ECO:9999999"]
nos_suffixes = ["_no1"]

synth_dir = os.path.join(top_dir,"synthetic")
data_as_tags_dir = os.path.join(synth_dir, "data_as_tags")
raw_stats_dir = os.path.join(synth_dir, "raw_stats_split")
print "Running with dir", data_as_tags_dir
print "raw dir is", raw_stats_dir

if 1 in steps:
  labels_file = "yes_no_labels.txt"
  file_to_glob = os.path.join(data_as_tags_dir, "docs_*")
  print "GLOB:", file_to_glob
  run_dirs = glob.glob(file_to_glob)
  for r in run_dirs:
    (rtemp, alpha,gamma1,gamma2,beta) = r.split("__")
    #print "Process dir:", "a:",alpha,"g1:",gamma1,"g2:",gamma2,"b:",beta
    dstats_dir = os.path.join(r, "stats")
    #print "Stats dir:", dstats_dir
    if not os.path.exists(dstats_dir):
      os.mkdir(dstats_dir)
    logs_dir = os.path.join(r,"logs")
    if not os.path.exists(logs_dir):
      os.mkdir(logs_dir)
    log_file = os.path.join(logs_dir, "kappa_log.txt")
    os.chdir(iaa_code_dir)
    sys_cmd = "python run_cohen_k_iaa.py "+r+" "+pair_file+" "+labels_file+" "+dstats_dir+" > "+log_file
    print sys_cmd
    os.system(sys_cmd)
    os.chdir(cur_dir)
    time.sleep(1)
    
if 2 in steps:  
  file_to_glob = os.path.join(raw_stats_dir, "docs_*")
  print "GLOB:", file_to_glob
  run_dirs = glob.glob(file_to_glob)
  for r in run_dirs:
    base_name = os.path.basename(r)
    print "base:", base_name
    rstats_dir = os.path.join(r, "stats")
    print "Stats dir:", rstats_dir
    if not os.path.exists(rstats_dir):
      os.mkdir(rstats_dir)
    logs_dir = os.path.join(r, "logs")
    if not os.path.exists(logs_dir):
      os.mkdir(logs_dir)
    # Do the IC forms
    # Multiple Nos for kw ONLY
    labels_file = "../eco_v2018-09-14.obo"
    for n in range(len(nos)):
      log_file = os.path.join(logs_dir, "kw_log"+nos_suffixes[n]+".txt")
      os.chdir(iaa_code_dir)
      sys_cmd = "python run_multi_label_kwic_iaa.py "+synth_dir+" "+pair_file+" "+labels_file+" "+base_name+" "+nos[n]+" > "+log_file
      print sys_cmd
      os.system(sys_cmd)
      stats_file = os.path.join(rstats_dir,"kw_stats"+nos_suffixes[n]+".txt")
      os.chdir(cur_dir)
      time.sleep(1)
      run_grep("KwIAA", log_file, stats_file)   
      time.sleep(1)

