import os
import sys
import random
import numpy as np
import OboICCalc

def read_params(pfname):
  params = {}
  with open(pfname, "r") as fpi:
    for l in fpi:
      line = l.strip()
      if len(line) < 1:
        continue
      items = line.split("\t")
      key = items[0].strip()
      vals = items[1].split(",")
      values = []
      for v in vals:
        values.append(float(v.strip()))
      params[key] = values
  return params

def read_id_file(ifname):
  terms = []
  with open(ifname, "r") as fpi:
    for l in fpi:
      line = l.strip()
      if len(line) < 1:
        continue
      terms.append(line)
  return terms

  
pfile = sys.argv[1] # parameters file
fname = sys.argv[2] # obo file
tfile = sys.argv[3] # file with list of terms to use
root_dir = sys.argv[4] # root dir for GS output
num_docs = int(sys.argv[5]) # number of docs to create
which = sys.argv[6] # numpy or random

params = read_params(pfile)
perc_annot_S = params["alpha"]
print params

term_id_list = read_id_file(tfile)
num_terms = len(term_id_list)
print "num term ids:", num_terms, which

# Get the IC's for the terms
ic_data = OboICCalc.OboICCalc()
ic_data.build_ont_tree(fname, "ECO")
ic_vals = []
ic_sum = 0.0
for t in term_id_list:
  icv = ic_data.getICForNode(t)
  if icv is None:
    icv = 0 # don't use this one
  print t,icv
  ic_vals.append(icv)
  ic_sum += icv
  
num_icvs = len(ic_vals)
if not num_terms == num_icvs:
  print "ERROR: Diff # terms",num_terms," v. ic vals",num_icvs
  sys.exit(0)

ic_freqs = []
for i in ic_vals:
  ic_freqs.append(i/ic_sum)
print "IC len:", num_icvs, "IC_sum:", ic_sum  
print ic_vals[:20]
print ic_freqs[:20]

label_no_match = ic_data.get_no_match_label()
label_eco_root = ic_data.get_ont_root_label()

num_S = 150
asInfo_sep = ";:;"
other_string = asInfo_sep+"None"+asInfo_sep+"None"+asInfo_sep+"None"+asInfo_sep+"SKIPPED"+asInfo_sep+"None"+asInfo_sep+"None"

if not os.path.exists(root_dir):
  os.mkdir(root_dir)
top_path = os.path.join(root_dir, "gold_standard")
if not os.path.exists(top_path):
  os.mkdir(top_path)
  
data_path = os.path.join(top_path, "data")
if not os.path.exists(data_path):
  os.mkdir(data_path)


for p in perc_annot_S:
  yes_no = [p]
  yes_no.append(1.0-p)
  doc_dir = os.path.join(data_path, "docs__"+str(p))
  total_num_S = 0
  total_num_annots = 0
  print "Doc dir:", doc_dir, yes_no
  if not os.path.exists(doc_dir):
    os.mkdir(doc_dir)

  for d in range(num_docs):
    doc_fname = os.path.join(doc_dir, "results_"+str(d+1)+"_s.txt")
    with open(doc_fname, "w") as fpo:
      fpo.write("Results\n\n");
      for s in range(num_S):
        total_num_S += 1
        s_has_topic = np.random.choice(np.arange(len(yes_no)), p=yes_no)
        snum = s+1
        sent = "\t"+"Sentence number "+ str(snum)
        if s_has_topic==0: # yes
          total_num_annots += 1
          if which == "numpy":
            topic_pos = np.random.choice(np.arange(num_terms),p=ic_freqs)
          else:
            topic_pos = random.randint(0,num_terms-1)
          topic = term_id_list[topic_pos]
          print topic, snum, topic_pos
          sent = topic+"\t"+"Sentence number "+ str(snum)
        fpo.write("%s\n" % sent)

  print "Percent:", p, "Num S:", total_num_S, "Num annots:", total_num_annots, "%:", float(total_num_annots)/float(total_num_S)
  