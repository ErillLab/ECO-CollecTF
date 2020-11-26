# Use python 2.7, and have numpy installed.
# This work was done using the Anaconda environment.
# This script compiles the brat information in an intermediate format that combines the brat annotation
# information -- the ECO term selected and the attributes -- into a more easily processed XML format.
# This format is an extension of the Genia format.
# Then the IAA scores are calculated.

# Note: output directories will be created in the same directory as the brat data directory.
# The outputs will be in the IAA directory, IAA_sent_iaa_k_avg.txt and IAA_multi_label_iaa_kwic_avg.txt
#
# python ECO-CollecTF_run_iaa_scripts.py \path\to\ECO_1_2 ECO_annotation_1_2 3 team_1_pairs.txt ..\eco_v2018-09-14.obo T1 S1 A1 M1
# python ECO-CollecTF_run_iaa_scripts.py \path\to\ECO_3 ECO_annotation3 3 team_2_pairs.txt ..\eco_v2018-09-14.obo T1 A2 D1
# python ECO-CollecTF_run_iaa_scripts.py \path\to\ECO_4_5 ECO_annotation_4_5 4 team_3_pairs.txt ..\eco_v2018-09-14.obo A1 A2 D1 M2

import os
import sys
import shutil
def execute_step(sys_cmd, msg):
  print msg, ":", sys_cmd
  ret_val = 0
  ret_val = os.system(sys_cmd)
  if ret_val != 0:
    print "ERROR running", sys_cmd
    sys.exit(0)
  
in_top_dir = sys.argv[1]
under_dir = sys.argv[2] # ECO_annotation_1_2 or ECO_annotation3 Note use of underscores in names
num_reviewers_per_doc = sys.argv[3]
pairs_file = sys.argv[4] # The annotator pairs teams
eco_obo_file = sys.argv[5]
annotators = sys.argv[6:]


ynlabels_file = "yes_no_labels.txt"
use_no_term_ic = "ECO:9999999" # Our code for no annotation being created.

# data from brat copied to data subdir already, data is where it lives on the brat server.
subdirs = ["data_as_tags", "IAA", "raw_stats_split", "logs"]
for sdir in subdirs:
  subdir = os.path.join(in_top_dir, sdir)
  if not os.path.exists(subdir):
    print subdir
    os.mkdir(subdir)
  underdir = os.path.join(subdir, under_dir)
  if not os.path.exists(subdir):
    os.mkdir(subdir)
iaa_dir = os.path.join(in_top_dir, "IAA") # Output

annot_str = " ".join(annotators) 

# Do steps 1 and 2 for computing K IAA. Also do steps 3 and 4 for the KwIC IAA.
steps_to_do = ["1", "2", "3", "4"]
#steps_to_do = ['5']
# Convert to the easier-to-deal-with format
in_step1 = os.path.join(in_top_dir, "data")
in_step1 = os.path.join(in_step1, under_dir)
out_step1 = os.path.join(in_top_dir, "data_as_tags")
out_step1 = os.path.join(out_step1, under_dir)
log_dir = os.path.join(in_top_dir, "logs")
log_step1 = os.path.join(log_dir, "map_brat_to_tags_log.txt")
if "1" in steps_to_do:
  sys_cmd = "python map_brat_to_tags_dir_tree.py "+in_step1+" "+out_step1+" "+annot_str+" > "+log_step1
  execute_step(sys_cmd, "Step 1")
  

# IAA - Cohen's K
in_step2 = out_step1
if "2" in steps_to_do:
  for w in ["k"]:
    log_step2 = os.path.join(log_dir, "sent_iaa_"+w+"_log.txt")
    sys_cmd = "python run_cohen_k_iaa.py "+in_step2+" "+pairs_file+" "+ynlabels_file+" "+iaa_dir+" > "+log_step2
    execute_step(sys_cmd, "Step 2")
    base_name = os.path.basename(log_step2)
    to_file = os.path.join(iaa_dir, base_name)
    shutil.copyfile(log_step2, to_file)
    avg_file = os.path.join(iaa_dir, "IAA_sent_iaa_"+w+"_avg.txt")
    sys_cmd = "python get_avg_iaas.py "+log_step2+' "K for ANY2 at end" > '+avg_file 
    execute_step(sys_cmd, "Step 2b k")
    
# Using a convenience format to line up the annotations for the multi-label comparisons
in_step3 = out_step1
out_step3 = os.path.join(in_top_dir, "raw_stats_split")
out_step3 = os.path.join(out_step3, under_dir)
log_step3 = os.path.join(log_dir, "raw_split_log.txt")
if "3" in steps_to_do:
  sys_cmd = "python raw_split_dir_tree.py "+in_step3+" "+out_step3+" "+annot_str+" > "+log_step3
  execute_step(sys_cmd, "Step 3")
  
# IAA multi-label - Cohen's Kw with IC (KwIC)
if "4" in steps_to_do:
  for w in ["kwic"]:
    log_step4 = os.path.join(log_dir, "multi_label_iaa_"+w+"_log.txt")
    labels_file = eco_obo_file
    sys_cmd = "python run_multi_label_kwic_iaa.py "+in_top_dir+" "+pairs_file+" "+labels_file+" "+under_dir+" "+use_no_term_ic+" > "+log_step4
    execute_step(sys_cmd, "Step 4")
    base_name = os.path.basename(log_step4)
    to_file = os.path.join(iaa_dir, base_name)
    shutil.copyfile(log_step4, to_file)
    avg_file = os.path.join(iaa_dir, "IAA_multi_label_iaa_"+w+"_avg.txt")
    sys_cmd = "python get_avg_iaas.py "+log_step4+' "Final Kw" > '+avg_file
    execute_step(sys_cmd, "Step 4 "+w)

# Extra processing convenience for ECOUsage
if '5' in steps_to_do:
  in_step2 = out_step1
  out_step2 = os.path.join(in_top_dir, "raw_stats")
  out_step2 = os.path.join(out_step2, under_dir)
  log_step2 = os.path.join(log_dir, "raw_annot_stats_log.txt")
  sys_cmd = "python raw_annot_stats_dir_tree.py "+in_step2+" "+out_step2+" "+annot_str+" > "+log_step2
  execute_step(sys_cmd, "Step 2")