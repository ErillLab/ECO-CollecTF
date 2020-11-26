# Before running this script, need to run IAA scripts.
# This calculates alpha. 
import os
import sys
import glob
import copy
import math
import json

import OboICCalc
import AstatsInfo

def update_pn_counts(count, num_annotators):
  ltn = lfp = lfn = ltp = 0
  if num_annotators == 3:
    if count==0:
      ltn = 1
      print "adding TN"
    elif count==1:
      lfp = 1
      print "adding FP"
    elif count==2:
      lfn = 1
      print "adding FN"
    else:
      ltp = 1
      print "adding TP"
  else:
    if count == 0:
      ltn = 1
      print "Adding TN"
    elif count == 1:
      lfp = 1
      print "Adding FP"
    elif count == 3:
      lfn = 1
      print "Adding FN"
    elif count == 4:
      ltp = 1
      print "Adding TP"
    elif count == 2:
      print "SKIP -- a count tie"
      # Need to skip count==2 in this case
  return (ltn, lfp, lfn, ltp)
  
def calc_num_annots(nat, nbt, nct, ndt):
  num_a = 0
  num_b = 0
  num_c = 0
  num_d = 0
  if nat > 0:
    num_a = 1
  if nbt > 0:
    num_b = 1
  if nct > 0:
    num_c = 1
  if ndt > 0:
    num_d = 1
  #print "num_a:", num_a, "b:", num_b, "c:", num_c, "d:", num_d
  total = num_a+num_b+num_c+num_d
  return total
  
def count_annots(l1, l2, l3, l4):
  num_a_tags = l1.count("<term")
  num_b_tags = l2.count("<term")
  num_c_tags = l3.count("<term")
  num_d_tags = l4.count("<term")
  return calc_num_annots(num_a_tags, num_b_tags, num_c_tags, num_d_tags)
  
def count_split_annots(l1, l2, l3, l4):
  num_a_tags = len(l1)
  num_b_tags = len(l2)
  num_c_tags = len(l3)
  num_d_tags = len(l4)
  return calc_num_annots(num_a_tags, num_b_tags, num_c_tags, num_d_tags)
  
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
  
def num_hops_between(term1, term2):
  maxw = 20
  num_hops = maxw
  found = False
  for want in range(maxw+1):
    node_list = ic_data.get_nodes_n_hops_away(term1, want)
    if len(node_list) < 1:
      found = False
      num_hops = want
      break
    #print term1, "HOP:", want, "len:",len(node_list)
    #print node_list
    if term2 in node_list:
      found = True
      num_hops = want
      break
  return num_hops
  
def compare_lists(listA, listB, hop_arr_len):
    hop_c = [0 for i in range(hop_arr_len)]
    list1 = copy.deepcopy(listA)
    list2 = copy.deepcopy(listB)
    print "1:", list1
    print "2:", list2
    matched_pairs = []
    num_matched_annots = 0
    total_ic = 0.0
    num_total_hops = 0
    total_sq_hops = 0
    total_half_sq_hops = 0
    # Need to go through both lists and do all exact matches first
    # Note could have A: E1106, E96; B: E96, E:1810 and
    # if the exacts are not done first you get
    # E1106 - E96
    # E96 - E1810
    #print "Check exact first"
    for i in range(len(list1)):
      a = list1[i]
      a_id = a["eco_id"]
      for j in range(len(list2)):
        b = list2[j]
        if b["matched"]:
          # already paired this one, skip
          continue
        b_id = b["eco_id"]
        #print "Exact Compare", a_id, b_id
        if b_id==a_id:
          matched = True
          a["matched"] = True
          b["matched"] = True
          list1[i] = a
          list2[j] = b
          matched_pairs.append((a_id, b_id))
          # reminder these are exact matches
          break
          
    # Now do non-exact matches
    #print "check IN exact next"
    for i in range(len(list1)):
      a = list1[i]
      a_id = a["eco_id"]
      if a["matched"]:
        continue
      else:
        best_ic = -1.0
        best_b_id = ""
        best_b = None
        best_b_pos = -1
        # Want to find the best pairing
        for j in range(len(list2)):
          b = list2[j]
          if b["matched"]:
            # already paired this one, skip
            continue
          b_id = b["eco_id"]
          #print "In-exact Compare", a_id, b_id
          ic_val = ic_data.find_best_parent_ic(a_id, b_id)
          if ic_val > best_ic:
            best_ic = ic_val
            best_b_id = b_id
            best_b = b
            best_b_pos = j
      if best_ic > -1.0:
        # we founds something to pair this with
        matched_pairs.append((a_id, best_b_id))
        matched = True
        a["matched"] = True
        best_b["matched"] = True
        list1[i] = a
        list2[best_b_pos] = best_b
      
    print "Matched pairs:", matched_pairs
    for (an_a, an_b) in matched_pairs:
      print "Pair:", an_a, an_b
      if an_a in term_id_list:
        #a_pos = label_idx[an_a]
        the_id = an_a
      else:
        print "WARNING: A",an_a,"not in ECO"
        #a_pos = ic_data.get_ont_root_pos() #0 # make it be to the top one
        the_id = label_eco_root
      if an_b in term_id_list:
        #b_pos = label_idx[an_b]
        other_id = an_b
      else:
        print "WARNING: B",an_b,"not in ECO"
        #b_pos = ic_data.get_ont_root_pos() #0 # make it be to the top one
        other_id = label_eco_root 

      ic_val = ic_data.find_best_parent_ic(the_id, other_id)
      num_hops = num_hops_between(the_id, other_id)
      hop_c[num_hops] += 1
      sq_hops = num_hops*num_hops
      half_hops = float(num_hops)/2.0
      sq_half_hops = half_hops*half_hops
      print an_a,an_b,"  ic=", ic_val, "hops=", num_hops,"sq hops=",sq_hops
      if num_hops >=3:
        print "LGHOPS:", num_hops, the_id, other_id
      total_ic += ic_val
      num_matched_annots +=1
      num_total_hops += num_hops
      total_sq_hops += sq_hops
      total_half_sq_hops += sq_half_hops
      
    return (num_matched_annots, total_ic, num_total_hops, total_sq_hops, total_half_sq_hops, hop_c)
 
############################################################ 
param_file = sys.argv[1]

# get the ECO info set up
asInfo = AstatsInfo.AstatsInfo()
ic_data = OboICCalc.OboICCalc()
ic_data.set_ont_type("ECO")
ic_data.build_ont_tree("../eco_v2018-09-14.obo", "ECO")
label_no_match = ic_data.get_no_match_label()
label_eco_root = ic_data.get_ont_root_label()
term_id_list = ic_data.get_id_list()

# Counting stuff
total_unique_s = 0
total_overall_s = 0
total_annot_s = 0
total_num_annots = 0

total_split_annot_s = 0
total_num_ties = 0 
total_num_split_ties = 0

#####################################################
def process_annotator_group(root_dir, sub_dir, num_annotators_per_doc, annotator_arr):
  print "process group:", root_dir, sub_dir, annotator_arr
  global total_unique_s
  global total_overall_s
  global total_annot_s
  global total_num_annots
  global total_split_annot_s
  global total_num_ties
  global total_num_split_ties

  
  if num_annotators_per_doc > 3:
    do_d = True
  else:
    do_d = False
  data_dir = os.path.join(root_dir, "data_as_tags")
  data_dir = os.path.join(data_dir, sub_dir)
  rss_dir = os.path.join(root_dir, "raw_stats_split")
  rss_dir = os.path.join(rss_dir, sub_dir)

  annotA_dir = os.path.join(data_dir, annotator_arr[0])
  adocs = {}
  rdocs = {}
  file_to_glob = os.path.join(annotA_dir, "r*.txt")
  file_array = glob.glob(file_to_glob)

  for af in file_array:
    print "af:", af
    base_name = os.path.basename(af)
    adocs[base_name] = [af]

  for annr in annotator_arr[1:]:
    print "Annotator:", annr
    annr_dir = os.path.join(data_dir, annr)
    file_to_glob = os.path.join(annr_dir, "r*.txt")
    annr_array = glob.glob(file_to_glob)
    raw_dir = os.path.join(rss_dir, annr)
    for ar in annr_array:
      base_name = os.path.basename(ar)
      base_root = os.path.splitext(base_name)[0]
      if base_name not in adocs:
        print "ERROR: haven't seen", base_name, "for", annr
      else:
        adocs[base_name].append(ar)
        print "adding", ar
        #raw_fname = os.path.join(raw_dir, base_root+"_raw_stats_split.txt")
      

  for doc in adocs:
    scnt = 0
    # We know there are 3 annotators per doc so, shortcutting here. Oops later had 4 annotators
    the_files = adocs[doc]
    print doc,the_files[0],the_files[1],the_files[2]
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
      fpd = open(the_files[3], "r")
      linesd = fpd.readlines()
      fpd.close
      
    if not (len(linesa) == len(linesb)):
      print "ERROR: differing number of lines for a and b for doc", doc
      sys.exit(0)
    if not (len(linesb) == len(linesc)):
      print "ERROR: differing number of lines for b and c for doc", doc
      sys.exit(0)
    if do_d and (not len(linesa) == len(linesd)):
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
    else:
      D_tags = []
      
    for i in range(len(linesa)):
      if i==0:
        continue
      
      # Count the annotations NOT split, just if they are there are not
      linea = linesa[i].strip()
      lineb = linesb[i].strip()
      linec = linesc[i].strip()
      if len(linea) < 1:
        continue
      total_unique_s += 1
      scnt += 1
      #print "\n",linea
      #print lineb
      #print linec
      if do_d:
        lined = linesd[i].strip()
        #print lined
        total_overall_s += 4
      else:
        total_overall_s += 3
        lined = ""
      # count just gives 1/0 for whether the line (ie S) has any annot
      count = count_annots(linea, lineb, linec, lined)
      #print "S regular:", scnt, "count:", count
      if do_d and count == 2:
        total_num_ties += 1
        
      total_annot_s += count
      #print "Total S that have been annotated so far:", total_annot_s
      

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
      #print "A has:", A_list
      #print "B has:", B_list
      #print "C has:", C_list
      D_list = []
      if do_d:
        if snum in D_tags:
          D_list = D_tags[snum]
        #print "D has:", D_list

      # Now count the annots with the split pairs
      count = count_split_annots(A_list, B_list, C_list, D_list)
      #print "S split:", scnt, "count:", count
      if do_d and count == 2:
        total_num_split_ties += 1
        
      total_split_annot_s += count
      #print "Total Split-S that have been annotated so far:", total_split_annot_s
      
      
      
# read in param file
with open(param_file, "r") as jfp:
  params = json.load(jfp)

for param in params:
  process_annotator_group(param["root_dir"], param["sub_dir"], param["num_annotators_per_doc"], param["annotators"])
  

print "Total S:", total_overall_s, "Total split annot s", total_split_annot_s
alpha = float(total_split_annot_s)/float(total_overall_s)

print "Split Alpha:", alpha


