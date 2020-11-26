# Here annotator A is being evaluated, with B and C as the gold standard.
# Only count annotations where B and C agree (both annotated, or both did not)
# This script determines FNR and FPR only.

import os
import sys
import glob
import copy
import math
import OboICCalc
import AstatsInfo

 
def read_in_split_tags(fname, eco_root_id):
  the_data = {}
  with open(fname, 'r') as myfile:
    for l in myfile:
      line = l.strip() 
      if len(line) > 1:
        items = line.split("\t")
        #print items
        if items[0] == "TAGGED":
          snum = items[asInfo.snum_pos]
          # Can have multiple snums in a doc
          data = items[asInfo.data_pos]
          annot_items = data.split(asInfo.sep)
          eco_id = annot_items[asInfo.eid_pos]
          if eco_root_id.find("RZ") > -1:
            eco_id = map_rz_tags(eco_id) 
          econf = annot_items[asInfo.econf_pos]
          #print snum, "ECO:", eco_id, "conf:", econf
          if snum not in the_data:
            the_data[snum] = [{"eco_id":eco_id,"econf":econf,"matched":False}]
          else:
            the_data[snum].append({"eco_id":eco_id,"econf":econf,"matched":False})
  return the_data 

def get_raw_fname(fname):
  raw_fname = fname.replace("data_as_tags", "raw_stats_split")
  raw_fname = raw_fname.replace("_ef", "_ef_raw_stats_split")
  return raw_fname
  
    
root_dir = sys.argv[1] 
sub_dir = sys.argv[2]
eco_file = sys.argv[3]
annotator_arr = sys.argv[4:]  # All annotators, leader first

print root_dir, sub_dir, eco_file, annotator_arr


if len(annotator_arr) > 3:
  if "M1" in annotator_arr:
    do_d = False
  else:
    do_d  = True
else:
  do_d = False
 
asInfo = AstatsInfo.AstatsInfo()
ic_data = OboICCalc.OboICCalc()
ic_data.set_ont_type("ECO")
ic_data.build_ont_tree(eco_file, "ECO")
label_no_match = ic_data.get_no_match_label()
label_eco_root = ic_data.get_ont_root_label()
term_id_list = ic_data.get_id_list()

data_dir = os.path.join(root_dir, "data_as_tags")
data_dir = os.path.join(data_dir, sub_dir)
rss_dir = os.path.join(root_dir, "raw_stats_split")
rss_dir = os.path.join(rss_dir, sub_dir)

print "Scoring annotator", annotator_arr[0]
annotA_dir = os.path.join(data_dir, annotator_arr[0])
adocs = {}
rdocs = {}
file_to_glob = os.path.join(annotA_dir, "r*.txt")
file_array = glob.glob(file_to_glob)

for af in file_array:
  #print "af:", af
  base_name = os.path.basename(af)
  adocs[base_name] = [af]
  
# Docs for the other annotators
for annr in annotator_arr[1:]:
  #print "Annotator:", annr
  annr_dir = os.path.join(data_dir, annr)
  file_to_glob = os.path.join(annr_dir, "r*.txt")
  annr_array = glob.glob(file_to_glob)
  raw_dir = os.path.join(rss_dir, annr)
  for ar in annr_array:
    base_name = os.path.basename(ar)
    base_root = os.path.splitext(base_name)[0]
    if base_name not in adocs:
      #print "Warning: annotator", annr, "has",base_name, "not in first annotator",annotator_arr[1]
      nothing=1
    else:
      adocs[base_name].append(ar)
      #print "adding", ar
      #raw_fname = os.path.join(raw_dir, base_root+"_raw_stats_split.txt")
      

total_s_skipped = 0
total_tn_annot_s = 0
total_tp_annot_s = 0
TNp = 0 # for counting pairs split (which puts annot in both lines)
FPp = 0
FNp = 0
TPp = 0

for doc in adocs:
  scnt = 0
  
  the_files = adocs[doc]
  #print doc,the_files[0],the_files[1],the_files[2]
  fpa = open(the_files[0],"r")
  fpb = open(the_files[1],"r")
  fpc = open(the_files[2],"r")
  linesa = fpa.readlines()
  linesb = fpb.readlines()
  linesc = fpc.readlines()
  fpa.close()
  fpb.close()
  fpc.close()
  if do_d:
    fpd = open(the_files[3],"r")
    linesd = fpd.readlines()
    fpd.close()
    
  if not (len(linesa) == len(linesb)):
    print "ERROR: differing number of lines for a and b for doc", doc
    sys.exit(0)
  if not (len(linesb) == len(linesc)):
    print "ERROR: differing number of lines for b and c for doc", doc
    sys.exit(0)
  if do_d and not (len(linesa)==len(linesd)):
    print "ERROR: differing number of lines for a and d for doc", doc
    sys.exit(0)
  
  raw_fnamea = get_raw_fname(the_files[0])
  raw_fnameb = get_raw_fname(the_files[1])
  raw_fnamec = get_raw_fname(the_files[2])
  A_tags = read_in_split_tags(raw_fnamea, label_eco_root)
  B_tags = read_in_split_tags(raw_fnameb, label_eco_root)
  C_tags = read_in_split_tags(raw_fnamec, label_eco_root)
  
  if do_d:
    raw_fnamed = get_raw_fname(the_files[3])
    D_tags = read_in_split_tags(raw_fnamed, label_eco_root)
    
  for i in range(len(linesa)):
    if i==0:
      continue
      
    # Use B and C as the GS -- where they agree it is a TP
    linea = linesa[i].strip()
    lineb = linesb[i].strip()
    linec = linesc[i].strip()
    if do_d:
      lined = linesd[i].strip()
    else:
      lined = ""
      
    if len(linea) < 1:
      continue
    scnt += 1
    #print "\n",linea
    #print lineb
    #print linec
    #print lined
    
    snum = str(scnt)
    #print "checking S#", snum
    if snum in A_tags:
      A_list = A_tags[snum]
    else:
      A_list = []
    if snum in B_tags:
      B_list = B_tags[snum]
    else:
      B_list = []
    if snum in C_tags:
      C_list = C_tags[snum]
    else:
      C_list = []
    D_list = []
    if do_d:
      if snum in D_tags:
        D_list = D_tags[snum]
        
    #print "A has:", A_list
    #print "B has:", B_list
    #print "C has:", C_list
    if do_d:
      #print "D has:", D_list
      pass 
    if not do_d:
      # If B and C have >= 1 annot each, it's a TP
      if len(B_list)>0 and len(C_list)>0:
        #print "3 annots", scnt, "GS annotated"
        total_tp_annot_s += 1
        if len(A_list) > 0:
          TPp += 1
          #print "Adding TPp"
        else:
          FNp += 1
          #print "adding FNp"
      elif len(B_list)==0 and len(C_list)==0:
        #print "3 annots", scnt, "GS NOT annot"
        total_tn_annot_s += 1
        if len(A_list) > 0:
          FPp += 1
          #print "adding FPp"
        else:
          TNp += 1
          #print "Adding TNp"
      else:
        #print "B and C disagree, skip"
        total_s_skipped += 1
    else:
      if len(B_list)>0 and len(C_list)>0 and len(D_list)>0:
        #print "4 annots", scnt, "GS annotated"
        total_tp_annot_s += 1
        if len(A_list) > 0:
          TPp += 1
          #print "Adding TPp"
        else:
          FNp += 1
          #print "adding FNp"      
      elif len(B_list)==0 and len(C_list)==0 and len(D_list)==0:
        #print "4 annots", scnt, "GS NOT annot"
        total_tn_annot_s += 1
        if len(A_list) > 0:
          FPp += 1
          #print "adding FPp"
        else:
          TNp += 1
          #print "Adding TNp"      
      else:
        # Disagree
        #print "They don't agree, skip"
        total_s_skipped += 1
        
    #print "So far, # true s:", total_tp_annot_s, "# neg s:", total_tn_annot_s, "# skipped:", total_s_skipped
    #print "So far TPp:", TPp, "FPp:", FPp, "TNp:", TNp, "FNp:", FNp
    
print "Total tp annot s:", total_tp_annot_s, "Total tn annot s:", total_tn_annot_s
print "Total s skipped:", total_s_skipped
print "TPp:", TPp, "FPp:", FPp, "TNp:", TNp, "FNp:", FNp
# Formula from https://en.wikipedia.org/wiki/Sensitivity_and_specificity
gamma1 = float(FNp)/float(FNp+TPp) # FNR = FN/(FN+TP)
gamma2 = float(FPp)/float(FPp+TNp) # FPR = FP/(FP+TN)
print annotator_arr[0], "Split Gamma1:", gamma1, "Gamma2:", gamma2

