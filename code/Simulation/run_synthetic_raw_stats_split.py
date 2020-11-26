import os
import sys
import glob
import time

top_dir = sys.argv[1]

iaa_code_dir = "../IAA"
annot_str = "AnnotA AnnotB"

cur_dir = os.getcwd()
  
synth_dir = os.path.join(top_dir,"synthetic")
data_as_tags_dir = os.path.join(synth_dir, "data_as_tags")
raw_stats_top_dir = os.path.join(synth_dir, "raw_stats_split")

file_to_glob = os.path.join(data_as_tags_dir, "docs_*")
print "GLOB:", file_to_glob
run_dirs = glob.glob(file_to_glob)
for r in run_dirs:
  base_name = os.path.basename(r)
  print base_name
  raw_stats_dir = os.path.join(raw_stats_top_dir, base_name)
  print "Stats dir:", raw_stats_dir
  if not os.path.exists(raw_stats_dir):
    os.mkdir(raw_stats_dir)
  log_rs_dir = os.path.join(raw_stats_dir, "logs")
  if not os.path.exists(log_rs_dir):
    os.mkdir(log_rs_dir)
  log_file = os.path.join(log_rs_dir,"rss_log.txt")

  os.chdir(iaa_code_dir)
  sys_cmd = "python raw_split_dir_tree.py "+r+" "+raw_stats_dir+" "+annot_str+" > "+log_file
  print sys_cmd
  os.system(sys_cmd)
  os.chdir(cur_dir)
  time.sleep(2)