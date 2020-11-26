# Run the scripts in the IAA directory first.
# Use the V2 version, this is the most accurate for simulation.
# python run_annot_pairs_as_gs_v2.py params_from_data_config.txt v2 corpus_FNR_FPR.txt

import os
import sys
import time
import json 


param_file = sys.argv[1]
vers = sys.argv[2] # v1 or v2
ofname = sys.argv[3]

eco_fname = "../eco_v2018-09-14.obo"

if vers == "v2":
  the_script = "annotator_pairs_as_gs_v2.py"
else:
  the_script = "annotator_pairs_as_gs.py"
  
fpo = open(ofname, "w")
fpo.write("FNR FPR Run "+vers+"\n")
fpo.close()

# read in param file
with open(param_file, "r") as jfp:
  params = json.load(jfp)

for param in params:
  root_dir = param["root_dir"]
  sub_dir = param["sub_dir"]
  fpo = open(ofname, "a")
  fpo.write("%s\n\n" % sub_dir)
  fpo.close()
  annotator_arr = param["annotators"]
  # Since the first set needs to be handled specially since A1 and M1 are not paired, handle each set individually
  # Set up for groups of 1 being scored and 2 others.
  if "S1" in annotator_arr:
    print "ECO_1_2 annotators"
    annotator_list = ["T1 S1 A1 M1", "S1 T1 A1 M1", "A1 T1 S1", "M1 T1 S1"]
  elif "M2" in annotator_arr:
    print "ECO_4_5 annotators"
    if vers == "v1":
      print "  Group by 3s for v1"
      annotator_list = ["A1 A2 D1", "A1 A2 M2", "A1 D1 M2", "A2 A1 D1", "A2 A1 M2", "A2 D1 M2", "D1 A1 A2", "D1 A1 M2", "D1 A2 M2", "M2 A1 A2", "M2 A1 D1", "M2 A2 D1"]
    else:
      print "  Group by 4's for v2"
      annotator_list = ["A1 A2 D1 M2", "A2 A1 D1 M2", "D1 A1 A2 M2", "M2 A1 A2 D1"]
  else:
    print "ECO_3 annotators"
    annotator_list = ["T1 D1 A2", "D1 T1 A2", "A2 T1 D1"]
  for alist in annotator_list:
    sys_cmd = "python "+the_script+" "+root_dir+" "+sub_dir+" "+eco_fname+" "+alist+" >> "+ ofname
    print sys_cmd
    os.system(sys_cmd)
    time.sleep(2)
    

time.sleep(3)

gamma1_pos = 3
gamma2_pos = -1
tpr_pos = 3
tnr_pos = -1
gamma1_values = []
gamma2_values = []
truepr_values = []
truenr_values = []
with open(ofname, "r") as fpi:
  for l in fpi:
    line = l.strip()
    if line.find("Split Gamma1:") > -1:
      items = line.split()
      gamma1_values.append(float(items[gamma1_pos]))
      gamma2_values.append(float(items[gamma2_pos]))
    if line.find("Split TPR:") > -1:
      items = line.split()
      truepr_values.append(float(items[tpr_pos]))
      truenr_values.append(float(items[tnr_pos]))
time.sleep(3)


avg_fnr = sum(gamma1_values)/len(gamma1_values)
avg_fpr = sum(gamma2_values)/len(gamma2_values)

with open(ofname, "a") as fpo:
  fpo.write("----------------\n")
  fpo.write("FNR = FN/(FN+TP)\n")
  fpo.write("FPR = FP/(FP+TN)\n\n")
  out_str = "Avg FNR (G1): "+str(avg_fnr)+"; Avg FPR (G2): "+str(avg_fpr)
  fpo.write("%s\n" % out_str)

  

