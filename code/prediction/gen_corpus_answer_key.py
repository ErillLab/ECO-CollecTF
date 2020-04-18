# This script generates an answer key based on the curator's annotations.
# It tracks if any curator made an annotation as well as if a majority did.
# The output is in a tab delimited format.
# python gen_corpus_answer_key.py \path\to\ECO_3 ECO_annotation3 3 eco_3_ans_key.txt T1 A2 D1

import os
import sys
import glob
import string


###########################################################
def check_bin_annots(the_annots):
  s_count = 0
  p_count = 0
  for item in the_annots:
    if "NextSentence" not in item or item["NextSentence"]=="No":
      s_count += 1
    elif item["NextSentence"]=="Yes":
      p_count += 1
  print "S_Count:", s_count, "P_Count:", p_count
  return (s_count>0, p_count>0)
  
def check_cat_annots(the_annots):
  sfs_count = sfp_count = 0
  bps_count = bpp_count = 0
  mfs_count = mfp_count = 0
  txs_count = txp_count = 0
  
  for item in the_annots:
    if "NextSentence" not in item or item["NextSentence"]=="No":
      single_annot = True
    elif item["NextSentence"]=="Yes":
      single_annot = False
      
    if "Category" in item:
      the_cat = item['Category']
      if the_cat == "SeqFeat":
        if single_annot:
          sfs_count += 1
        else:
          sfp_count += 1
      elif the_cat == "BioProc":
        if single_annot:
          bps_count += 1
        else:
          bpp_count += 1
      elif the_cat == "MolFn":
        if single_annot:
          mfs_count += 1
        else:
          mfp_count += 1
      elif the_cat == "Tax":
        if single_annot:
          txs_count += 1
        else:
          txp_count += 1      
  print "SFs_Count:", sfs_count, "BPs_Count:", bps_count, "MFs_Count:", mfs_count
  print "SFp_Count:", sfp_count, "BPp_Count:", bpp_count, "MFp_Count:", mfp_count
  print "Txs_Count:", txs_count, "Txp_Count:", txp_count
  return (sfs_count>0, sfp_count>0, bps_count>0, bpp_count>0, mfs_count>0, mfp_count>0, txs_count>0, txp_count>0)
  
def get_next_sentence(spos, slines):
  plain_ns = ""
  if i < len(slines)-1: 
    plain_ns = slines[i+1].strip()
    if len(plain_ns) < 1:
      j=i+2
      while j < len(slines):
        plain_ns = slines[j].strip()
        j += 1
        if len(plain_ns) > 1:
          break
  return plain_ns
  
def grab_term_tag(pos, sstr):
  #print "grab term:", pos, len(sstr), sstr
  ret_pos = len(sstr)
  chars = ""
  for i in range(pos, len(sstr)):
    chars += sstr[i]
    #print i, sstr[i]
    if sstr[i] == '>':
      ret_pos = i
      break
  if ret_pos == len(sstr):
    print "Error -- no end of term tag", len(sstr)
    print sstr
    sys.exit(0)
  items = chars.split()
  #print "ITEMS:", items
  data = {}
  for item in items:
    #print "item:", item
    if not item.find("=")>-1:
      continue
    item = item.replace("\"", "")
    item = item.replace(">", "")
    parts = item.split("=")
    #print parts
    data[parts[0]] = parts[1]
  #print "Data to return:", data
  return (ret_pos, data)
      
def grab_attrib(sstr):
  items = sstr.split("=")
  return items[1][1:-1]
  
def handle_sentence(s):
  i=0
  ni=0
  run_ni = 0
  new_line = ""
  tags = {}
  slen = len(s)
  annots = {}
  #print "INCOMING:", s
  while i < slen:
    #print "i:", i, "char:", s[i]
    if i+5<slen and s[i:i+5]=="<term":
      beg_pos = run_ni
      (i, info) = grab_term_tag(i,s)
      sstr = info["sem"]
      idstr = info["id"]
      i+= 1
      if idstr in tags:
        print "Error: repeated id in tag", idstr
        sys.exit(0)
      tags[idstr] = {"start":beg_pos, "sem":sstr}
      tags[idstr]["text_ni"] = ni
      #print "BEGIN:", tags[idstr]
      annots[idstr] = info
      annots[idstr]["start"] = beg_pos
      #print "      ", annots[idstr]
    elif i+6<slen and s[i:i+6]=="</term":
      end_pos = run_ni
      (i, info) = grab_term_tag(i, s)
      idstr = info["id"]
      i+= 1
      if idstr not in tags:
        print "Error: missing beginning id tag", idstr
        sys.exit(0)
      tags[idstr]["end"] = end_pos
      tags[idstr]["text"] = new_line[tags[idstr]["text_ni"]:ni]
      #print "END:", tags[idstr]
      annots[idstr]["end"] = end_pos
      annots[idstr]["text"] = tags[idstr]["text"]
      #print "    ", annots[idstr]
    else:
      new_line += s[i]
      i+=1
      ni+=1
      run_ni+=1
  #if len(tags):
  #  for tag in tags:
  #    item = tags[tag]
  #    print "tags found:",tag, item, new_line[item["start"]:item["end"]]+"."
        
  return annots
  

def gather_annots(count, s):
  annots = []
  if count > 0:
    s_annots = handle_sentence(s)
    #print "s_annots:", s_annots
    for s_a in s_annots:
      a = s_annots[s_a] # remove the brat tag id's
      # check for complete ECO id
      ecoid = a["sem"]
      #if len(ecoid) >= 11:
      annots.append(a)
  return annots
  
def determine_bin_answer_old(is_as, is_ap, is_bs, is_bp, is_cs, is_cp, is_ds, is_dp):
  any_single = is_as or is_bs or is_cs
  any_pair = is_ap or is_bp or is_cp
  maj_single = (is_as and is_bs) or (is_as and is_cs) or (is_bs and is_cs)
  maj_pair = (is_ap and is_bp) or (is_ap and is_cp) or (is_bp and is_cp)
  print "Any Single?", any_single, "Any pair:", any_pair
  print "Maj single?", maj_single, "Maj pair:", maj_pair
  return (any_single, any_pair, maj_single, maj_pair)
def determine_bin_answer(is_as, is_ap, is_bs, is_bp, is_cs, is_cp, is_ds, is_dp):
  any_single = (int(is_as) + int(is_bs) + int(is_cs) + int(is_ds) > 0)
  any_pair = (int(is_ap) + int(is_bp) + int(is_cp) + int(is_dp) > 0)
  maj_single = (int(is_as)+ int(is_bs) + int(is_cs) + int(is_ds) > (num_annotators/2.0))
  maj_pair = (int(is_ap)+ int(is_bp) + int(is_cp) + int(is_dp) > (num_annotators/2.0))
  print "Any Single?", any_single, "Any pair:", any_pair
  print "Maj single?", maj_single, "Maj pair:", maj_pair
  return (any_single, any_pair, maj_single, maj_pair)
#(any_sfs, any_sfp, maj_sfs, maj_sfp) = determine_cat_answer(sf_as, sf_ap, sf_bs, sf_bp, sf_cs, sf_cp)
def determine_cat_answer_old(cat_as, cat_ap, cat_bs, cat_bp, cat_cs, cat_cp, cat_ds, cat_dp):
  # One category at a time
  any_cat_single = cat_as or cat_bs or cat_cs
  any_cat_pair = cat_ap or cat_bp or cat_cp
  maj_cat_single = (cat_as and cat_bs) or (cat_as and cat_cs) or (cat_bs and cat_cs)
  maj_cat_pair = (cat_ap and cat_bp) or (cat_ap and cat_cp) or (cat_bp and cat_cp)
  print "Cat Any Single?", any_cat_single, "Any pair:", any_cat_pair
  print "Cat Maj single?", maj_cat_single, "Maj pair:", maj_cat_pair
  return (any_cat_single, any_cat_pair, maj_cat_single, maj_cat_pair)  
def determine_cat_answer(cat_as, cat_ap, cat_bs, cat_bp, cat_cs, cat_cp, cat_ds, cat_dp):
  # One category at a time
  any_cat_single = (int(cat_as) + int(cat_bs) + int(cat_cs) + int(cat_ds) > 0)
  any_cat_pair = (int(cat_ap) + int(cat_bp) + int(cat_cp) + int(cat_dp) > 0)
  maj_cat_single = (int(cat_as) + int(cat_bs) + int(cat_cs) + int(cat_ds) > (num_annotators/2.0))
  maj_cat_pair = (int(cat_ap) + int(cat_bp) + int(cat_cp) + int(cat_dp) > (num_annotators/2.0))
  print "Cat Any Single?", any_cat_single, "Any pair:", any_cat_pair
  print "Cat Maj single?", maj_cat_single, "Maj pair:", maj_cat_pair
  return (any_cat_single, any_cat_pair, maj_cat_single, maj_cat_pair)  
###########################################################
  
root_dir = sys.argv[1] 
sub_dir = sys.argv[2]
num_annotators = int(sys.argv[3]) # # annotators per doc
out_fname = sys.argv[4]
annotator_arr = sys.argv[5:]  # All annotators, Leader first

tags_dir = os.path.join(root_dir, "data_as_tags")
tags_dir = os.path.join(tags_dir, sub_dir)

annotA_dir = os.path.join(tags_dir, annotator_arr[0])
adocs = {}
rdocs = {}
file_to_glob = os.path.join(annotA_dir, "r*.txt")
print file_to_glob
file_array = glob.glob(file_to_glob)

for af in file_array:
  #print "af:", af
  base_name = os.path.basename(af)
  adocs[base_name] = [af]
  
# Docs for the other annotators
for annr in annotator_arr[1:]:
  #print "Annotator:", annr
  annr_dir = os.path.join(tags_dir, annr)
  file_to_glob = os.path.join(annr_dir, "r*.txt")
  annr_array = glob.glob(file_to_glob)
  for ar in annr_array:
    base_name = os.path.basename(ar)
    base_root = os.path.splitext(base_name)[0]
    if base_name not in adocs:
      #print "Warning: annotator", annr, "has",base_name, "not in first annotator",annotator_arr[1]
      pass
    else:
      adocs[base_name].append(ar)
      #print "adding", ar
      #raw_fname = os.path.join(raw_dir, base_root+"_raw_stats_split.txt")
   
fpo = open(out_fname, "w")
    # PMID_S AnyS AnyP MajS MajP AnySfS AnySfP MajSfS MajSfP  AnyBPS AnyBPP MajBPS MajBPP  AnyMFS AnyMFP MajMFS MajMFP
out_str="PMID_S\tAnyS\tAnyP\tMajS\tMajP\tAnySfS\tAnySfP\tMajSfS\tMajSfP\tAnyBPS\tAnyBPP\tMajBPS\tMajBPP\tAnyMFS\tAnyMFP\tMajMFS\tMajMFP\tAnyTxS\tAnyTxP\tMajTxS\tMajTxP"
fpo.write("%s\n" % out_str)
for doc in adocs:
  scnt = 0
  pmid = doc.split("_")[1]
  
  # We know there are 3 or 4 annotators per doc 
  the_files = adocs[doc]
  print doc #,the_files[0],the_files[1],the_files[2]

  fpa = open(the_files[0],"r")
  fpb = open(the_files[1],"r")
  fpc = open(the_files[2],"r")
  linesa = fpa.readlines()
  linesb = fpb.readlines()
  linesc = fpc.readlines()
  if num_annotators >= 4:
    fpd = open(the_files[3],"r")
    linesd = fpd.readlines()
  fpa.close()
  fpb.close()
  fpc.close()
  if num_annotators >= 4:
    fpd.close()
    
  if not (len(linesa) == len(linesb)):
    print "ERROR: differing number of lines for a and b for doc", doc
    sys.exit(0)
  if not (len(linesb) == len(linesc)):
    print "ERROR: differing number of lines for b and c for doc", doc
    sys.exit(0)
  if (num_annotators>=4) and not (len(linesc) == len(linesd)):
    print "ERROR: differing number of lines for c and d for doc", doc
    sys.exit(0)
    
  #print "Len:", len(linesa)
  for i in range(len(linesa)):
    if i==0: # Skip results header line
      continue
      
    linea = linesa[i].strip()
    lineb = linesb[i].strip()
    linec = linesc[i].strip()
    if num_annotators >= 4:
      lined = linesd[i].strip()
      
    if len(linea) < 1:
      continue
    scnt += 1
    print "\n", pmid, scnt
    print linea
    print lineb
    print linec
    if num_annotators >= 4:
      print lined
      
    counta = linea.count("<term")
    countb = lineb.count("<term")
    countc = linec.count("<term")
    if num_annotators >= 4:
      countd = lined.count("<term")
    a_annots = gather_annots(counta, linea)
    b_annots = gather_annots(countb, lineb)
    c_annots = gather_annots(countc, linec)
    if num_annotators >= 4:
      d_annots = gather_annots(countd, lined)
    print "\nA:", a_annots
    print "\nB:", b_annots
    print "\nC:", c_annots
    if num_annotators >= 4:
      print "\nD:", d_annots
    (is_as, is_ap) = check_bin_annots(a_annots)
    (is_bs, is_bp) = check_bin_annots(b_annots)  
    (is_cs, is_cp) = check_bin_annots(c_annots)
    if num_annotators >= 4:   
      (is_ds, is_dp) = check_bin_annots(d_annots)
    else:
      is_ds = False
      is_dp = False
    (any_s, any_p, maj_s, maj_p) = determine_bin_answer(is_as, is_ap, is_bs, is_bp, is_cs, is_cp, is_ds, is_dp)
    
    print "A:"
    (sf_as, sf_ap, bp_as, bp_ap, mf_as, mf_ap, tx_as, tx_ap) = check_cat_annots(a_annots)
    print "B:"
    (sf_bs, sf_bp, bp_bs, bp_bp, mf_bs, mf_bp, tx_bs, tx_bp) = check_cat_annots(b_annots)
    print "C:"
    (sf_cs, sf_cp, bp_cs, bp_cp, mf_cs, mf_cp, tx_cs, tx_cp) = check_cat_annots(c_annots)
    if num_annotators >= 4:
      print "D:"
      (sf_ds, sf_dp, bp_ds, bp_dp, mf_ds, mf_dp, tx_ds, tx_dp) = check_cat_annots(d_annots)
    else:
      sf_ds = sf_dp = bp_ds = bp_dp = mf_ds = mf_dp = tx_ds = tx_dp = False
    print "SF:"
    (any_sfs, any_sfp, maj_sfs, maj_sfp) = determine_cat_answer(sf_as, sf_ap, sf_bs, sf_bp, sf_cs, sf_cp, sf_ds, sf_dp)
    print "BP:"
    (any_bps, any_bpp, maj_bps, maj_bpp) = determine_cat_answer(bp_as, bp_ap, bp_bs, bp_bp, bp_cs, bp_cp, bp_ds, bp_dp)
    print "MF:"
    (any_mfs, any_mfp, maj_mfs, maj_mfp) = determine_cat_answer(mf_as, mf_ap, mf_bs, mf_bp, mf_cs, mf_cp, mf_ds, mf_dp)
    print "Tax:"
    (any_txs, any_txp, maj_txs, maj_txp) = determine_cat_answer(tx_as, tx_ap, tx_bs, tx_bp, tx_cs, tx_cp, tx_ds, tx_dp)
    
    # PMID_S AnyS AnyP MajS MajP AnySfS AnySfP MajSfS MajSfP  AnyBPS AnyBPP MajBPS MajBPP  AnyMFS AnyMFP MajMFS MajMFP AnyTxS AnyTxP MajTxS MajTxP
    out_str = pmid+"_"+str(scnt)+"\t"+str(int(any_s))+"\t"+str(int(any_p))+"\t"+str(int(maj_s))+"\t"+str(int(maj_p))+"\t"+str(int(any_sfs))+"\t"+str(int(any_sfp))+"\t"+str(int(maj_sfs))+"\t"+str(int(maj_sfp))+"\t"+str(int(any_bps))+"\t"+str(int(any_bpp))+"\t"+str(int(maj_bps))+"\t"+str(int(maj_bpp))+"\t"+str(int(any_mfs))+"\t"+str(int(any_mfp))+"\t"+str(int(maj_mfs))+"\t"+str(int(maj_mfp))+"\t"+str(int(any_txs))+"\t"+str(int(any_txp))+"\t"+str(int(maj_txs))+"\t"+str(int(maj_txp))
    fpo.write("%s\n" % out_str)
fpo.close()    