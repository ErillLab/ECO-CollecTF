import os
import sys
import glob
import numpy as np
import math
import AstatsInfo
import OboICCalc

np.seterr(all='raise')
flat_type = "flat"
ic_type = "ic"

  
def build_id_mapping(term_list):
  icnt = 0
  item_idx = {}
  idx_item = {}
  for the_info in term_list:
    # Don't need to check for remove ids 
    # since that was handled when the obo file was processed.
    # Also the no match label has been added already.
    if not the_info in item_idx:
      item_idx[the_info] = icnt
      idx_item[icnt] = the_info
      icnt += 1
  return (item_idx, idx_item)

def build_use_map(term_list):
  items = {}
  for the_info in term_list:
    if not the_info in items:
      items[the_info] = 0
  return items

def update_use_counts(annot_list, use_map, eco_root_id):
  for snum in annot_list:
      tag_list = annot_list[snum]
      for tag in tag_list:
        the_id = tag["eco_id"]
        print "The id:", the_id

        if not the_id in use_map:
          # There may be an eco id typo/error, use the ECO root
          the_id = eco_root_id
          print " error, now use", the_id
        cur_cnt = use_map[the_id]+1
        use_map[the_id] = cur_cnt   
        print the_id, use_map[the_id]
        
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
          econf = annot_items[asInfo.econf_pos]
          print snum, "ECO:", eco_id, "conf:", econf
          if snum not in the_data:
            the_data[snum] = [{"eco_id":eco_id,"econf":econf,"matched":False}]
          else:
            the_data[snum].append({"eco_id":eco_id,"econf":econf,"matched":False})
  return the_data
 
def a_exact_in_b(a_id, B_list):
  res = -1
  for j in range(len(B_list)):
    b = B_list[i]
    if b["matched"]:
      continue
    b_id = b["eco_id"]
    if b_id == a_id:
      res = j
      break
  return res
 
def increment_use(id_use_info, the_term):
  if the_term in id_use_info:
    cur_cnt = id_use_info[the_term] + 1
    id_use_info[the_term] = cur_cnt

 
def output_iaa(which, the_arr, wgt_arr, N, idx_label, wmax, itype):
  the_arr = the_arr/float(N) # freq
  
  #print the_arr
  rows = the_arr.sum(axis=1) # marginals
  cols = the_arr.sum(axis=0)
  
  Ao = the_arr.trace()
  Ae = 0.0
  for i in range(len(rows)):
    Ae += rows[i]*cols[i]
  print which,"Ao=", Ao, "Ae=",Ae, "K=",(Ao-Ae)/(1.0-Ae)
    
  # Po' = mult count * ic then div by wmax
  Po_arr = (the_arr * wgt_arr)
  Po = Po_arr.sum() #/ wmax in final formula wmax is just in denom
  print "Po = ", Po
  
  # Pe' we need to deal with the marginals, so do the sum
  Pe = 0.0
  for i in range(len(rows)):
    for j in range(len(cols)):
      Pe += rows[i]*cols[j]*wgt_arr[i,j]
  print "Pe = ", Pe

  K = (Po - Pe)/(wmax - Pe)  
  print which, "KwIAA:", K
  if itype == flat_type:
    qo = 1.0 - Po
    qe = 1.0 - Pe
    K = 1.0 - (qo/qe)
    print which, "Qo:", qo, "Qe:", qe, "K:", K
  return K

# Checked the counts, they are right
def output_count_array(the_arr, wgt_arr, idx_label, num_labels, N):
  for i in range(num_labels):
    for j in range(num_labels):
      if the_arr[i,j] > 0:
        print idx_label[i],",",idx_label[j],":", the_arr[i,j],"freq:",the_arr[i,j]/float(N),"ic:",wgt_arr[i,j]
        
fname = sys.argv[1] # obo file
sroot_dir = sys.argv[2] # Dir above the annotator dirs with the S with the data. Used to count S
split_dir = sys.argv[3] # Same as above except the dir is the raw_stats_split
iaa_type = sys.argv[4] # flat or ic 
no_ic_id = sys.argv[5] #  ECO:9999999
annotator_arr = sys.argv[6:]  # Only 2 annotators at a time

print "ARGS:", sys.argv

all_ones = False

ic_data = OboICCalc.OboICCalc()
the_obo_type = "ECO"
ic_data.set_ont_type(the_obo_type)
ic_data.build_ont_tree(fname, the_obo_type)


label_no_match = ic_data.get_no_match_label()
label_eco_root = ic_data.get_ont_root_label()

term_id_list = ic_data.get_id_list()

# Get the labels from the first column of the file
(label_idx, idx_label) = build_id_mapping(term_id_list)
labels = label_idx.keys()
num_labels = len(labels)

print "Num labels:", num_labels

annotators = "-".join(annotator_arr)
print annotator_arr

#if use_ont_root_ic_for_no:
#  ic_data.updateNoNodeIC(label_eco_root)
#  print "New No IC:", ic_data.getICForNode(label_no_match)
# use IC from ECO:0000000 for NO
if no_ic_id.find("AVG") > -1:
  icval = float(no_ic_id.split(":")[1])
  ic_data.updateNoNodeICVal(icval)
else:
  ic_data.updateNoNodeIC(no_ic_id)
print "Use No IC:", ic_data.getICForNode(label_no_match)
 
A_id_use_info = build_use_map(term_id_list)
B_id_use_info = build_use_map(term_id_list)

asInfo = AstatsInfo.AstatsInfo()

count_arr = np.zeros(shape=(num_labels, num_labels))
if all_ones:
  sweight_arr = np.ones(shape=(num_labels, num_labels))
else:
  sweight_arr = np.zeros(shape=(num_labels, num_labels))

Adoc_dir = os.path.join(sroot_dir, annotator_arr[0])
Bdoc_dir = os.path.join(sroot_dir, annotator_arr[1])
A_dir = os.path.join(split_dir, annotator_arr[0])
B_dir = os.path.join(split_dir, annotator_arr[1])

# Get the docs' sentence files. Only need the S
file_to_glob = os.path.join(Adoc_dir, "*_s.txt")
#print file_to_glob

file_array = glob.glob(file_to_glob)
total_scnt = 0
num_no_no_annots = 0
total_no_other_annots = 0
total_num_annots = 0
total_matched_annots = 0
E0_cnt = 0
for af in file_array:
  print "File:", af
  base_name = os.path.basename(af)
  base_root = os.path.splitext(base_name)[0]
  bf = os.path.join(Bdoc_dir, base_name)
  if not os.path.exists(bf):
    #print "Skipping", base_name, "since not in B dir"
    continue
  
  # Both annotators have annotated this doc.
  # Get the split annotations for each
  af_split = os.path.join(A_dir, base_root+"_ef_raw_stats_split.txt")
  bf_split = os.path.join(B_dir, base_root+"_ef_raw_stats_split.txt")
  A_tags = read_in_split_tags(af_split, label_eco_root)
  B_tags = read_in_split_tags(bf_split, label_eco_root)

  # For IC Ae need to first accumulate each annotator's use of the term ids
  print "Update A's ECO usage"
  #print "A tags:", A_tags
  update_use_counts(A_tags, A_id_use_info, label_eco_root)
  print "Update B's ECO usage"
  #print "B Tags:", B_tags
  update_use_counts(B_tags, B_id_use_info, label_eco_root)
  
  
  with open(af, "r") as fpi:
    doc_lines = fpi.readlines()
  
  scnt = 0
  no_match_pos = label_idx[label_no_match]
  for i in range(len(doc_lines)):
    # Skip first line since this is the section "Results"
    if i==0:
      continue
    doc_line = doc_lines[i].strip()
    if len(doc_line) < 1:
      continue
    
    scnt += 1
    total_scnt += 1
    #print "Process line#", i, "scnt:", scnt, doc_line
    snum = str(scnt)
    
    if snum in A_tags:
      A_list = A_tags[snum]
    else:
      A_list = []
    if snum in B_tags:
      B_list = B_tags[snum]
    else:
      B_list = []
      
    print "A has:", A_list
    print "B has:", B_list
    if len(A_list) == 0 and len(B_list) == 0:
      count_arr[no_match_pos,no_match_pos] += 1.0
      if iaa_type == flat_type:
        sweight_arr[no_match_pos,no_match_pos] = 1.0
      else:
        sweight_arr[no_match_pos,no_match_pos] = ic_data.getICForNode(label_no_match)
      total_num_annots += 1
      print "No-No annot match on", label_no_match
      num_no_no_annots += 1
      #print "total anns:", total_num_annots, "num no-no:", num_no_no_annots
      increment_use(A_id_use_info, label_no_match)
      increment_use(B_id_use_info, label_no_match)
      continue
      
    matched_pairs = []
    # Need to go through both lists and do all exact matches first
    # Note could have A: E1106, E96; B: E96, E:1810 and
    # if the exacts are not done first you get
    # E1106 - E96
    # E96 - E1810
    for i in range(len(A_list)):
      a = A_list[i]
      a_id = a["eco_id"]
      for j in range(len(B_list)):
        b = B_list[j]
        if b["matched"]:
          # already paired this one, skip
          continue
        b_id = b["eco_id"]
        #print "Compare", a_id, b_id
        if b_id==a_id:
          matched = True
          a["matched"] = True
          b["matched"] = True
          A_list[i] = a
          B_list[j] = b
          matched_pairs.append((a_id, b_id))
          # reminder these are exact matches
          break
          
    # Now do non-exact matches
    for i in range(len(A_list)):
      a = A_list[i]
      a_id = a["eco_id"]
      if a["matched"]:
        continue
      else:
        best_ic = -1.0
        best_b_id = ""
        best_b = None
        best_b_pos = -1
        for j in range(len(B_list)):
          b = B_list[j]
          if b["matched"]:
            # already paired this one, skip
            continue
          b_id = b["eco_id"]
          print "Compare", a_id, b_id
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
        A_list[i] = a
        B_list[best_b_pos] = best_b
      
    #print "A_list:", A_list
    #print "B_list:", B_list
    print "Matched pairs:", matched_pairs

    for (an_a, an_b) in matched_pairs:
      print "Pair:", an_a, an_b
      if an_a in label_idx:
        a_pos = label_idx[an_a]
        the_id = an_a
      else:
        print "WARNING: A",an_a,"not in ECO"
        a_pos = ic_data.get_ont_root_pos() #0 # make it be to the top one
        the_id = label_eco_root
      if an_b in label_idx:
        b_pos = label_idx[an_b]
        other_id = an_b
      else:
        print "WARNING: B",an_b,"not in ECO"
        b_pos = ic_data.get_ont_root_pos() #0 # make it be to the top one
        other_id = label_eco_root 
      if iaa_type == flat_type:
        count_arr[a_pos,b_pos] += 1.0
        if a_pos==b_pos:
          sweight_arr[a_pos,b_pos] = 1.0
      else:
        ic_val = ic_data.find_best_parent_ic(the_id, other_id)
        count_arr[a_pos,b_pos] += 1
        sweight_arr[a_pos,b_pos] = ic_val # just put the value in the matrix
        print "   pair ic_val:", ic_val
        if a_pos==1 and b_pos==1:
          print "  updating 1,1 to:", count_arr[1,1]
      total_num_annots += 1
      #print "total:", total_num_annots
      total_matched_annots += 1
      #print "total matched:", total_matched_annots
      if the_id=="RZ:E0" and other_id=="RZ:E0":
        E0_cnt+= 1
        print "E0 matched count so far:", E0_cnt, count_arr[1,1]
        
    # Do the unmatched ones now
    for a in A_list:
      the_id = a["eco_id"]
      if the_id in label_idx: # we do have some non-obo ECO ids
        a_pos = label_idx[the_id]
      else:
        print "WARNING: A",the_id,"not in ECO"
        a_pos = ic_data.get_ont_root_pos() #0 # make it be to the top one
        the_id = label_eco_root
      if not a["matched"]:
        b_pos = no_match_pos
        other_id = label_no_match
        print "Update A->None:",the_id,"at:",a_pos,",",label_no_match,"at:",b_pos
        increment_use(B_id_use_info, label_no_match)
        total_no_other_annots += 1
        if iaa_type == flat_type:
          count_arr[a_pos,b_pos] += 1.0
          # don't update weights here
        else:
          ic_val = ic_data.find_best_parent_ic(the_id, other_id)
          count_arr[a_pos,b_pos] += 1
          sweight_arr[a_pos,b_pos] = ic_val # just save the value
          print "   A->None ic_val:", ic_val
          if a_pos==1 and b_pos==1:
            print "  updating 1,1 to:", count_arr[1,1]
        total_num_annots += 1
    for b in B_list:
      the_id = b["eco_id"]
      if the_id in label_idx:
        b_pos = label_idx[the_id]
      else:
        print "WARNING: B",the_id,"not in ECO"
        b_pos = ic_data.get_ont_root_pos() #0
        the_id = label_eco_root
      if not b["matched"]:
        other_id = label_no_match
        print "Update None->B:",label_no_match,"at:",no_match_pos,",",the_id,"at:",b_pos
        increment_use(A_id_use_info, label_no_match)
        total_no_other_annots += 1
        a_pos = no_match_pos
        if iaa_type == flat_type:
          count_arr[no_match_pos, b_pos] += 1.0
          # don't update weights here
        else:
          ic_val = ic_data.find_best_parent_ic(the_id, other_id)
          print "   None->B ic_val:", ic_val
          count_arr[no_match_pos,b_pos] += 1
          sweight_arr[no_match_pos,b_pos] = ic_val
          if a_pos==1 and b_pos==1:
            print "  updating 1,1 to:", count_arr[1,1]
        total_num_annots+= 1
    #print "total_num_annots so fars:", total_num_annots            
    
Nsum = count_arr.sum() # still a count matrix here
print "N as arr sum:", Nsum
# By outputing the count array 
# verified the array is being updated correctly 
output_count_array(count_arr, sweight_arr, idx_label, num_labels, total_num_annots)
# For IC IAA, need to do a sampling to calc the Ae
# Based strictly on counting the random pairs, 
#   the % of No-No pairs is less with Ae ~ 0.60999 compared to the observed 408/594=0.688
#   also % of NON-no pairings (ex: ECO8-ECO9) is also less with Ae ~ 0.043 versus 54/594 = 0.091
# It makes sense that the chance pairings would have fewer meaningful pairs
#print "compute IC_Ae next"
#IC_Ae = ic_data.calculate_Ae(A_id_use_info, B_id_use_info, 1000000)
#print "IC_Ae:", IC_Ae
#print "Get ready for IC_Ae V2"
#IC_Ae2 = ic_data.calculate_Ae_v2(count_arr, total_num_annots, 1000000)
#print "IC_Ae2:", IC_Ae2

iaa_val = output_iaa("ECO_"+annotators, count_arr, sweight_arr, total_num_annots, idx_label, 1.0, iaa_type)
print "total_num_annots:", total_num_annots, "num matched:", total_matched_annots, "num No-No:", num_no_no_annots, "num No with ECO:", total_no_other_annots
#print "E0-E0",E0_cnt
print "Final Kw", iaa_val