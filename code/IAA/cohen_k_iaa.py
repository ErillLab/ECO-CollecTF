import os
import sys
import glob
import numpy as np
import math

np.seterr(all='raise')

def get_column(fname, col):
  icnt = 0
  item_idx = {}
  idx_item = {}
  with open(fname, "r") as infile:
    for l in infile:
      line = l.strip()
      if len(line) < 1:
        continue
      items = line.split("\t")
      the_info = items[0]
      if not the_info in item_idx:
        item_idx[the_info] = icnt
        idx_item[icnt] = the_info
        icnt += 1
  return (item_idx, idx_item)

def get_id(text):
  id_str = "id=\""
  id_str_len = len(id_str)
  ibpos = text.find(id_str)
  iepos = text.find('"', ibpos+id_str_len+1)
  id_val = text[ibpos:iepos+1]
  return id_val
  
def process_tag_text(text):
  #print "process tag text:", text
  eco_id_len = 11
  eco_conf_str = "ECOConfidence=\""
  eco_conf_len = len(eco_conf_str)
  assertion_str = "AssertionStrength=\""
  assertion_str_len = len(assertion_str)
  category_str = "Category=\""
  category_str_len = len(category_str)
  next_s_str = "NextSentence=\""
  next_s_str_len = len(next_s_str)
  neg_s_str = "NegativeStatement=\""
  neg_s_str_len = len(neg_s_str)
  
  # Check if not normalized
  bpos = text.find('normalized="False"')
  skip_the_eco = False
  if bpos > -1:
    skip_the_eco = True # not normalized
    
  # Get ECO id
  bpos = text.find("ECO:")
  epos = bpos+eco_id_len
  eco_id = text[bpos:epos]
  # Get ECO Confidences
  bpos = text.find(eco_conf_str)
  epos = text.find('"', bpos+eco_conf_len+1)
  eco_conf_val = text[bpos+eco_conf_len:epos]
  # Get Assertion strength         
  bpos = text.find(assertion_str)
  epos = text.find('"', bpos+assertion_str_len+1)
  assertion_val = text[bpos+assertion_str_len:epos]
  # Get category
  bpos = text.find(category_str)
  epos = text.find('"', bpos+category_str_len+1)
  category_val = text[bpos+category_str_len:epos]
  # Get if sentence pair
  bpos = text.find(next_s_str)
  epos = text.find('"', bpos+next_s_str_len)
  next_s_val = text[bpos+next_s_str_len:epos]
  # Get if Negative
  bpos = text.find(neg_s_str)
  epos = text.find('"', bpos+neg_s_str_len)
  neg_s_val = text[bpos+neg_s_str_len:epos]

  
  #print text
  #print "ECO:", eco_id+".", eco_conf_val+"."
  #print "  Category:", category_val+".", "AS:", assertion_val+"."
  #print "  Next?", next_s_val+".", "Neg?", neg_s_val+"."
  return {"skip_eco":False, "eco":eco_id, "econf":eco_conf_val, "astr":assertion_val, "cat":category_val, "next":next_s_val, "neg":neg_s_val}

def count_tag_pairs(seco_tags, want_pairs):
  # for this don't care about nesting etc. Just if pair or not
  tcount = 0
  for eco_data in seco_tags:
    #print "count_pairs Tag:", eco_data, "want pairs?", want_pairs
    if want_pairs:
      if eco_data["next"]=="Yes":
        tcount += 1
    elif eco_data["next"]=="No":
        tcount += 1
  #print "pairs returning:",tcount
  return tcount

def count_tag_higheco_highassertion(seco_tags):
  # for this don't care about nesting etc. Just if have any
  # high-high tag at all.
  tcount = 0
  for eco_data in seco_tags:
    #print "count_High-High:", eco_data
    if ("econf" not in eco_data) or ("astr" not in eco_data):
      continue
    if eco_data["econf"]=="High" and eco_data["astr"]=="High":
      tcount += 1
  #print "hh returning:",tcount
  return tcount
  
def get_all_tags(s_tags):
  eco_tags = []
  for st in s_tags:
    eco_tags.append(process_tag_text(st))
  return eco_tags

  
def gather_tag_info(num_term_tags, line):
  # Gather info 
  s_tags = []
  etpos = 0
  spos = 0
  for i in range(num_term_tags):
    bpos = line.find("<term", spos)
    nspos = line.find("NextSentence", bpos+10)
    epos = line.find(">", nspos)
    tag_text = line[bpos:epos]
    id_str = get_id(tag_text)
    #print "gather_tag_info TAG:", tag_text
    #print "ID STR:", id_str
    s_tags.append(tag_text)
    etpos = epos
    spos = epos
  return s_tags
  
def determine_label(count):
  if count > 0:
    label = "yes"
  else:
    label = "no"
  return label

  
def update_counts(A, B, arr, label_idx):
  y_pos = label_idx["yes"]
  n_pos = label_idx["no"]
  if A=="yes" and B=="yes":
    arr[y_pos,y_pos] += 1.0
  elif A=="yes" and B=="no":
    arr[y_pos,n_pos] += 1.0
  elif A=="no" and B=="yes":
    arr[n_pos, y_pos] += 1.0
  else:
    arr[n_pos, n_pos] += 1.0

def calc_cohen_kappa(the_arr):
  Ao = the_arr.trace()
  rows = the_arr.sum(axis=1)
  print "marginals on rows (A):", rows
  cols = the_arr.sum(axis=0)
  print "marginals on cols (B):", cols
  Ae = 0.0
  for i in range(len(rows)):
    Ae += rows[i]*cols[i]
  print "Ao:", Ao, "Ae:", Ae, (1.0-Ae)
  try:
    K = (Ao - Ae)/(1.0 - Ae)
  except:
    print "WARNING! Ae=1.0"
    K = (Ao - Ae)/(1.0 - .999999999)
  return K

def output_iaa(which, the_arr, N):
  the_arr = the_arr/float(N)
  print which
  print the_arr
  K = calc_cohen_kappa(the_arr)
  print "K for",which,":", K
  return K

def output_stats(which, x):
  print "X:",x
  minx = min(x)
  maxx = max(x)
  median = sorted(x)[len(x)//2]
  mean = sum(x)/len(x)
  if len(x) > 1:
    stdev = math.sqrt(sum([(val - mean)**2 for val in x])/(len(x) - 1))
  print which,": Min:",minx," ; Max:",maxx," ; Median: ",median
  print which,": Mean:", mean
  if len(x) > 1:
    print which,":    Stdev:", stdev
  
lfname = sys.argv[1] # file with the labels in 1st column
root_dir = sys.argv[2] # Dir above the annotator dirs with the S
stats_dir = sys.argv[3] # Dir where the stats output goes
annotator_arr = sys.argv[4:]  # Only 2 annotators at a time

subdir = os.path.basename(root_dir)

(label_idx, idx_label) = get_column(lfname, 0)
labels = label_idx.keys()
num_labels = len(labels)

print "Num labels:", num_labels
print annotator_arr
ann_str = "_".join(annotator_arr)

any1_label_arr = np.zeros(shape=(num_labels, num_labels))
any2_label_arr = np.zeros(shape=(num_labels, num_labels))
scomplete_label_arr = np.zeros(shape=(num_labels, num_labels))
hh_label_arr = np.zeros(shape=(num_labels, num_labels))

local_any1_arr = np.zeros(shape=(num_labels, num_labels))
local_any2_arr = np.zeros(shape=(num_labels, num_labels))
local_comp_arr = np.zeros(shape=(num_labels, num_labels))

A_dir = os.path.join(root_dir, annotator_arr[0])
B_dir = os.path.join(root_dir, annotator_arr[1])

file_to_glob = os.path.join(A_dir, "*_s_ef.txt")
file_array = glob.glob(file_to_glob)
total_scnt = 0
any1_list = []
any2_list = []
comp_list = []
for af in file_array:
  print "A File:", af
  base_name = os.path.basename(af)
  bf = os.path.join(B_dir, base_name)
  if not os.path.exists(bf):
    #print "Skipping", base_name, "since not in B dir"
    continue
    
  with open(af, "r") as afile:
    a_lines = afile.readlines()
  with open(bf, "r") as bfile:
    b_lines = bfile.readlines()
    
  if not (len(a_lines)==len(b_lines)):
    print "ERROR:",base_name,"has DIFFERENT number of lines"
    sys.exit(0)
    
  A_sentpair = False
  B_sentpair = False
  scnt = 0
  for i in range(len(a_lines)):
    # Skip first line since this is the section "Results"
    if i==0:
      continue
    aline = a_lines[i].strip()
    bline = b_lines[i].strip()
    #print "aline:", aline
    #print "bline:", bline
    if len(aline)==0 and (not (len(bline)==0)):
      #print "aline:", aline
      #print "bline:", bline
      print "ERROR:", base_name,". A's line is blank and B's is not"
      sys.exit(0)
    if len(bline)==0 and (not (len(aline)==0)):
      print "ERROR:", base_name,". B's line is blank and A's is not"
      sys.exit(0)
      
    if len(aline) < 1:
      continue
      
    # We have 2 S with something  
    # For this is it OK if A and B have diff #'s of tags
    #print "------------------------------------------------------------------"
    scnt += 1
    total_scnt += 1
    #print "Process line#", i, "scnt:", scnt
    
    num_a_tags = aline.count("<term")
    num_b_tags = bline.count("<term")
    
    # Get the tags
    as_tags = gather_tag_info(num_a_tags, aline)
    bs_tags = gather_tag_info(num_b_tags, bline)
    
    # if this S has ANY annotation on both, we are good
    # BUT it will not match the 2nd S of a pair to anything
    acount_any1 = len(as_tags)
    bcount_any1 = len(bs_tags)
    a_call = determine_label(acount_any1)
    b_call = determine_label(bcount_any1)
    
    update_counts(a_call, b_call, any1_label_arr, label_idx)
    update_counts(a_call, b_call, local_any1_arr, label_idx)
    #print "ANY1:"
    #print any1_label_arr
    
    # If the S has ANY annotations on both, we are good
    # AND if this is the 2nd of a pair and the other has any
    # annotation, we are also good 
    # So, for S-S regular matching use any1 counts above
    # If a previous S was a 1st S, update the any1 counts
    if A_sentpair:
      acount_any1 += 1
      A_sentpair = False # reset for current S
    if B_sentpair:
      bcount_any1 += 1
      B_sentpair = False # reset for current S
    a_call = determine_label(acount_any1)
    b_call = determine_label(bcount_any1)
    update_counts(a_call, b_call, any2_label_arr, label_idx)
    update_counts(a_call, b_call, local_any2_arr, label_idx)
    #print "ANY2:"
    #print any2_label_arr
    #print "ANY2 is THIS S a pair?"
    aecos_tags = get_all_tags(as_tags)
    becos_tags = get_all_tags(bs_tags)
    acount_any2 = count_tag_pairs(aecos_tags, True)
    bcount_any2 = count_tag_pairs(becos_tags, True)
    #print "  A:", acount_any2, "B:", bcount_any2
    if acount_any2 > 0:
      A_sentpair = True
    if bcount_any2 > 0:
      B_sentpair = True
    
    # See if A.B has any non-pair annotation
    # will see if they match with the Next S or not
    acount_complete = count_tag_pairs(aecos_tags, False)
    bcount_complete = count_tag_pairs(becos_tags, False)
    a_call = determine_label(acount_complete)
    b_call = determine_label(bcount_complete)
    update_counts(a_call, b_call, scomplete_label_arr, label_idx)
    update_counts(a_call, b_call, local_comp_arr, label_idx)
    #print "COMPLETE:"
    #print scomplete_label_arr

    # marked as a pair by both or as complete by both
    # Not concerned if one is both pair and complete and the other is only 1
    # This is the next most relaxed matching compared to any
    # NOTE this is really a multi-label situation:
    # complete, pair, no. Although can't do no and anything else,
    # can do complete and pair
    #acount_pair = count_tag_pairs(aecos_tags, True)
    #bcount_pair = count_tag_pairs(becos_tags, True)
       
    # And for high-high annotations
    # What to do if A has high but B has medium?
    # Right high=yes, everything else no
    acount_hh = count_tag_higheco_highassertion(aecos_tags)
    bcount_hh = count_tag_higheco_highassertion(becos_tags)
    a_call = determine_label(acount_hh)
    b_call = determine_label(bcount_hh)
    update_counts(a_call, b_call, hh_label_arr, label_idx)
    #print "HH any:"
    #print hh_label_arr
    
  #print "ANY2", scnt
  #print local_any2_arr
  a1K = output_iaa("ANY1 for "+base_name, local_any1_arr, scnt)
  a2K = output_iaa("ANY2 for "+base_name, local_any2_arr, scnt)
  aCK = output_iaa("COMPLETE for "+base_name, local_comp_arr, scnt)
  any1_list.append(a1K)
  any2_list.append(a2K)
  comp_list.append(aCK)
  local_any1_arr.fill(0.0)
  local_any2_arr.fill(0.0)
  local_comp_arr.fill(0.0)

print "============================================"
print "Total number of S:", total_scnt
#print "Any2", total_scnt
#print any2_label_arr

K1 = output_iaa("ANY1 at end", any1_label_arr, total_scnt)
K2 = output_iaa("ANY2 at end", any2_label_arr, total_scnt)
K3 = output_iaa("COMPLETE at end:",scomplete_label_arr, total_scnt)
HH = output_iaa("HH at end:", hh_label_arr, total_scnt)
foname = os.path.join(stats_dir, "sent_iaa_k_"+subdir+"_"+ann_str+".txt")
fpo = open(foname, "w")
fpo.write("ANY1,%f\n" %K1)
fpo.write("ANY2,%f\n" %K2)
fpo.write("COMPLETE,%f\n" %K3)
fpo.write("HH,%f\n" %HH)
fpo.close()
print "--------------------------------------------------"
output_stats("ANY1", any1_list)
output_stats("ANY2", any2_list)
output_stats("COMPLETE", comp_list)
