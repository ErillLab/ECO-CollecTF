# Create the data_as_tags output as if converted from brat
import os
import sys
import random
import glob
import shutil
import numpy as np
import OboICCalc

def determine_num_hops(sigma):
  #draw = np.random.normal(0,sigma)
  print "p=", sigma
  draw = np.random.geometric(sigma, 1) # not really sigma, but p
  # need to subtract 1 since never get a 0
  draw = draw-1
  num_hops = np.floor(np.abs(draw))
  return num_hops
  
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

def choose_term(ic_data, b_param, start_term):
  # Note: when using ECOs used, sometimes curators put in a new or wrong ECO id
  # not in the 2018 list
  if b_param <= 0.0000001:
    print "Don't hop, use", start_term
    return start_term # just use the term
  bval = determine_num_hops(b_param)
  # Note: for ECO can't get more than 10 or 11 hops away from a starting point.
  try:
    # Note: will stop when reach the end of ECO, so can't hop, say, 20 hops.
    choices = ic_data.get_nodes_n_hops_away(start_term, bval)
  except:
    # This is a bogus ECO, I always substituted with ECO 0 in the real data
    choices=[]

  if len(choices) > 0:
    choice = random.randint(0,len(choices)-1)
    chosen = choices[choice]
  else:
    chosen = ic_data.get_ont_root_label()
  #print "hop:",bval,"from",start_term,"- chose:",chosen,"CHOICES:", choices
  print "hop:",bval,"from",start_term,"- chose:",chosen
  return chosen
  
def create_annot(term, acount):
  return '<term sem="'+term+'" id="T'+str(acount)+' "ECOConfidence="High" AssertionStrength="High" Category="BioProc" NextSentence="No" NegativeStatement="No">annotation</term id="T'+str(acount)+'">'
  
def generate_annot_docs(f, tags_docs_dir, datas_dir, fnr, fpr, b_val_to_use, annotators, ic_data, which):
  base_name = os.path.basename(f)
  base_root = os.path.splitext(base_name)[0]
  fp_count = 0
  fn_count = 0
  scnt = 0
  num_noannot_scnt = 0
  num_annot_scnt = 0  
  for annot in annotators:
    annot_count = 0 # for the "T" count in brat
    annot_docs_dir = os.path.join(tags_docs_dir, annot)

    if not os.path.exists(annot_docs_dir):
      os.mkdir(annot_docs_dir)
    annot_data_dir = os.path.join(datas_dir, annot)
    if not os.path.exists(annot_data_dir):
      os.mkdir(annot_data_dir)
      
    # copy the input name to the data dir
    to_file = os.path.join(annot_data_dir, base_name)
    shutil.copyfile(f, to_file)
    
    out_data_fname = os.path.join(annot_docs_dir, base_root+"_ef.txt")
    print "for annot", annot, "Output to:", out_data_fname
    with open(f, "r") as fpi:
      fpd = open(out_data_fname,"w")
      for l in fpi:
        line = l.strip();
        items = line.split("\t")
        print items
        if len(items) < 2:
          # No annotation here in Gold standard
          # If blank lines or the Results line, just write out
          if len(line) < 1 or (items[0]=="Results"):
            #print "Just output line"
            fpd.write("%s\n" % line)
          else:
            # We have a sentence but no Gold annotation. See if a FP?
            scnt += 1
            num_noannot_scnt += 1
            sent = line
            if fpr <= 0.000001:
              fpr_annot = 1
            else:
              fpr_annot = np.random.choice(np.arange(len(fpr)), p=fpr)
            #print "FPR?", fpr_annot,fpr
            if fpr_annot == 0:
              # Yes do wrong annotation. Get a term
              if which=='numpy':
                topic_pos = np.random.choice(np.arange(num_terms),p=ic_freqs)
              else:
                #np.random.randint(num_terms)
                topic_pos = random.randint(0,num_terms-1)
              etag = term_id_list[topic_pos]
              aterm = choose_term(ic_data, b_val_to_use, etag) # false positive, just pick something
              print "S# NO GS annot", scnt, etag, "Wrong FP", fpr_annot, aterm
              annot_count += 1
              out_str = sent+" "+create_annot(aterm,annot_count)
              fpd.write("%s\n" % out_str)
              fp_count += 1
            else:
              print "S# NO GS annot", scnt, "Correct NO annot"
              fpd.write("%s\n" % sent)
        else:
          # This sentence has an annotation
          etag = items[0]
          sent = items[1]
          print "Tag:", etag, "S:", sent
          scnt += 1
          num_annot_scnt +=1
          if len(etag) > 8:
            # An annotated S -- is there a false negative?
            if fnr <=0.000001:
              fnr_annot=1
            else:
              fnr_annot = np.random.choice(np.arange(len(fnr)), p=fnr)
            if fnr_annot == 0:
              print "S# GS annot", scnt, "Wrong FN_annot -- ", fnr_annot
              fpd.write("%s\n" % sent)
              fn_count += 1
            else:
              # Make AnnotA always be GS
              if annot == "AnnotA":
                hop_val_to_work_with = 0
              else:
                hop_val_to_work_with = b_val_to_use # beta
              aterm = choose_term(ic_data, hop_val_to_work_with, etag)
              print etag, "S# GS annot", scnt, "Correct TP output chose", aterm
              annot_count += 1
              out_str = sent+" "+create_annot(aterm,annot_count)
              fpd.write("%s\n" % out_str)
          else:
            print "ERROR -- no tag but should be one there"
            sys.exit(0)
      fpd.close()

  print "For pair for this doc FN:", fn_count, num_annot_scnt, float(fn_count)/float(num_annot_scnt)
  print "For pair for this doc FP:", fp_count, num_noannot_scnt, float(fp_count)/float(num_noannot_scnt)    
  return(fn_count, num_annot_scnt, fp_count, num_noannot_scnt, scnt)
  
pfile = sys.argv[1] # parameters file
fname = sys.argv[2] # obo file
tfile = sys.argv[3] # file with list of terms to use
root_dir = sys.argv[4] # root dir with GS output
which = sys.argv[5] # numpy or random

annotators = ["AnnotA","AnnotB"]

term_id_list = read_id_file(tfile)
num_terms = len(term_id_list)
print "num term ids:", num_terms

ic_data = OboICCalc.OboICCalc()
ic_data.build_ont_tree(fname, "ECO")
ont_root = "ECO:0000000"
ic_freqs = []
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
for i in ic_vals:
  ic_freqs.append(i/ic_sum)
  
gs_dir = os.path.join(root_dir, "gold_standard")
gs_docs_dir = os.path.join(gs_dir, "data")
file_to_glob = os.path.join(gs_docs_dir, "docs__0*")
gs_docs_subdirs = glob.glob(file_to_glob)
print "GS subdirs:", gs_docs_subdirs

out_root_dir = os.path.join(root_dir, "synthetic")
if not os.path.exists(out_root_dir):
  os.mkdir(out_root_dir)

# For some of the downstream processing, assumes a data dir
data_dir = os.path.join(out_root_dir, "data")
if not os.path.exists(data_dir):
  os.mkdir(data_dir)
data_as_tags_dir = os.path.join(out_root_dir, "data_as_tags")
if not os.path.exists(data_as_tags_dir):
  os.mkdir(data_as_tags_dir)
raw_stats_dir = os.path.join(out_root_dir, "raw_stats_split")
if not os.path.exists(raw_stats_dir):
  os.mkdir(raw_stats_dir)
  
params = read_params(pfile)
betas = params["beta"]
gamma1 = params["gamma1"]
gamma2 = params["gamma2"]
g1=gamma1[0]
g2=gamma2[0]

# root/annots/<docs_alpha-gamma1-gamma2-beta>/data/annotation?/AnnotA

for gs_subdir_path in gs_docs_subdirs:
  # Input for the gold standard
  gs_subdir = os.path.basename(gs_subdir_path)
  print "GS subdir:", gs_subdir
  gs_in_dir = os.path.join(gs_docs_dir, gs_subdir)
  file_to_glob = os.path.join(gs_in_dir, "results*.txt")
  file_array = glob.glob(file_to_glob)
  
  for g1 in gamma1:
    for g2 in gamma2:
      fp_total = 0
      fn_total = 0
      total_s = 0
      total_noannot_s = 0
      total_annot_s = 0
      
      fnr = [g1,1.0-g1]
      fpr = [g2,1.0-g2]
      print "FNR:", fnr
      print "FPR:", fpr
  
      for b in betas:
        # Subdirs to hold the annots
        annot_subdir = gs_subdir+"__"+str(g1)+"__"+str(g2)+"__"+str(b)
        print "Create subdir for annots:",
        tag_docs_dir = os.path.join(data_as_tags_dir, annot_subdir)
        print "tagged docs_dir dir:", tag_docs_dir
        if not os.path.exists(tag_docs_dir):
          os.mkdir(tag_docs_dir)
        rs_dir = os.path.join(raw_stats_dir, annot_subdir)
        if not os.path.exists(rs_dir):
          os.mkdir(rs_dir)
        datas_dir = os.path.join(data_dir, annot_subdir)
        if not os.path.exists(datas_dir):
          os.mkdir(datas_dir)
        # Process the input docs from the GS
        #b_sqrt = np.sqrt(b)
        #print "Beta (var):", b, "sqrt(b):",b_sqrt
        the_b_param = b # now this is a p val for geometric
        print "Using beta:", the_b_param
        for f in file_array:
          print "Annotate",f
          (fn, asn, fp, nasn, sn) = generate_annot_docs(f, tag_docs_dir, datas_dir, fnr, fpr, the_b_param, annotators, ic_data, which)
          fn_total += fn
          fp_total += fp
          total_s += sn
          total_annot_s += asn
          total_noannot_s += nasn
      print "G1", g1,"Overall FNR:", float(fn_total)/float(total_annot_s)
      print "G2", g2,"Overall FPR (G2):", float(fp_total)/float(total_noannot_s)
