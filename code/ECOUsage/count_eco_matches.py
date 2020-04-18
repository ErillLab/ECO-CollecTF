import os
import sys
import glob
import copy
import math
import OboInfo
import CountInfo

def read_in_non_split_tags(fname, eco_root_id):
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
          next_val = annot_items[asInfo.next_pos]
          #print snum, "ECO:", eco_id, "conf:", econf, "pair", next_val
          if snum not in the_data:
            the_data[snum] = [{"eco_id":eco_id,"econf":econf,"matched":False,"pair":next_val}]
          else:
            the_data[snum].append({"eco_id":eco_id,"econf":econf,"matched":False,"pair":next_val})
  return the_data 
  
def get_raw_fname(fname):
  raw_fname = fname.replace("data", "raw_stats")
  raw_fname = raw_fname.replace("_s.txt", "_s_ef_raw_stats.txt")
  return raw_fname
  
def output_list(the_list, out_dir, which, count):
  out_fname = os.path.join(out_dir, "eco_agreements_"+which+".txt")
  with open(out_fname, "w") as fpo:
    for item in the_list:
      eid = item["eco_id"]
      snum = item["snum"]
      next_val = item["pair"]
      doc = item["doc"]
      sent = item["S"]
      conf = str(item["conf"])
      out_str = eid+"\t"+snum+"\t"+next_val+"\t"+doc+"\t"+count+"\t"+conf+"\t"+sent
      fpo.write("%s\n" % out_str)

def conf_val(str):
  if str=="High":
    return 3
  elif str=="Medium":
    return 2
  elif str=="Low":
    return 1
  else:
    return 0
 
def get_conf(conf_list, key):
  val = 0
  for (k,v) in conf_list:
    print k,v
    if k==key:
      val = v
  #print "return",val,"for key"
  return val
  
root_dir = sys.argv[1] 
sub_dir = sys.argv[2]
ont_fname = sys.argv[3]
out_dir = sys.argv[4]
annotator_arr = sys.argv[5:]  # All annotators, leader first

asInfo = CountInfo.CountInfo()
ic_data = OboInfo.OboInfo()
ic_data.set_ont_type("ECO")
ic_data.build_ont_tree(ont_fname, "ECO")
label_no_match = ic_data.get_no_match_label()
label_eco_root = ic_data.get_ont_root_label()
term_id_list = ic_data.get_id_list()

data_dir = os.path.join(root_dir, "data")
data_dir = os.path.join(data_dir, sub_dir)
rss_dir = os.path.join(root_dir, "raw_stats_split")
rss_dir = os.path.join(rss_dir, sub_dir)

# Preliminary
rs_dir = os.path.join(root_dir, "raw_stats")
if not os.path.exists(rs_dir):
  os.mkdir(rs_dir)
rs_dir = os.path.join(rs_dir, sub_dir)
if not os.path.exists(rs_dir):
  os.mkdir(rs_dir)
dt_dir = os.path.join(root_dir, "data_as_tags")
dt_dir = os.path.join(dt_dir, sub_dir)
annot_str = " ".join(annotator_arr) 
sys_cmd = "python raw_info_dir_tree.py "+dt_dir+" "+rs_dir+" "+annot_str+" > prelim_log.txt"
print sys_cmd
ret_val = os.system(sys_cmd)

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
      

unan_count = 3
maj_count = 2

S_unanimous = []
S_majority = []
total_S_unan = 0
total_S_maj = 0

#temp=["results_24146802_s.txt"]
for doc in adocs:
  scnt = 0
  # We know there are 3 annotators per doc so, shortcutting here
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
  if not (len(linesa) == len(linesb)):
    print "ERROR: differing number of lines for a and b for doc", doc
    sys.exit(0)
  if not (len(linesb) == len(linesc)):
    print "ERROR: differing number of lines for b and c for doc", doc
    sys.exit(0)

  
  raw_fnamea = get_raw_fname(the_files[0])
  raw_fnameb = get_raw_fname(the_files[1])
  raw_fnamec = get_raw_fname(the_files[2])
  A_tags = read_in_non_split_tags(raw_fnamea, label_eco_root)
  B_tags = read_in_non_split_tags(raw_fnameb, label_eco_root)
  C_tags = read_in_non_split_tags(raw_fnamec, label_eco_root)
  
  for i in range(len(linesa)):
    if i==0:
      continue

    linea = linesa[i].strip()
    lineb = linesb[i].strip()
    linec = linesc[i].strip()
    if len(linea) < 1:
      continue

    scnt += 1

    snum = str(scnt)
    print "checking S#", snum
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
    print "A has:", A_list
    print "B has:", B_list
    print "C has:", C_list
    
    this_s_ecos = []
    lists = {"A":A_list, "B":B_list, "C":C_list}
    eids = {}
    eids_next = {}
    eids_confs = {}
    for the_annot in lists:
      the_list = lists[the_annot]
      for item in the_list:
        eid = item["eco_id"]
        next_val = item["pair"]
        conf = conf_val(item["econf"])
        if the_annot not in eids:
          eids[the_annot] = [eid]
        else:
          eids[the_annot].append(eid)
        val = eid+"_"+next_val
        if the_annot not in eids_next:
          eids_next[the_annot] = [val]
        else:
          eids_next[the_annot].append(val)
        if the_annot not in eids_confs:
          eids_confs[the_annot] = [(val,conf)]
        else:
          eids_confs[the_annot].append((val,conf))
        if eid not in this_s_ecos:
          this_s_ecos.append(eid)
    print "Unique ecos this S:", this_s_ecos
    print "EIDs:", eids_next
    print "CONFS:", eids_confs
    for eid in this_s_ecos:
      count_pyes = 0
      count_pno = 0
      yes_conf = 0
      no_conf = 0
      eid_pyes = eid+"_"+"Yes"
      eid_pno = eid+"_"+"No"
      for the_annot in eids:
        the_list = eids_next[the_annot]
        if eid_pyes in the_list:
          count_pyes += 1
          yes_conf += get_conf(eids_confs[the_annot], eid_pyes)
        if eid_pno in the_list:
          count_pno += 1
          no_conf += get_conf(eids_confs[the_annot], eid_pno)
      print eid, count_pyes, count_pno
      if no_conf > 0:
        no_conf = float(no_conf)/float(count_pno)
        print "  no conf:", no_conf
      if yes_conf > 0:
        yes_conf = float(yes_conf)/float(count_pyes)
        print "  yes conf:", yes_conf
      if count_pno >= unan_count:
        S_unanimous.append({"eco_id":eid, "snum":snum, "doc":doc, "pair":"No", "S":linea, "conf":no_conf})
        total_S_unan += 1
      elif count_pno >= maj_count:
        S_majority.append({"eco_id":eid, "snum":snum, "doc":doc, "pair":"No", "S":linea, "conf":no_conf})
        total_S_maj += 1
        

      if count_pyes >= unan_count:
        S_unanimous.append({"eco_id":eid, "snum":snum, "doc":doc, "pair":"Yes", "conf":yes_conf,"S":linea+" "+linesa[i+1].strip()})
        total_S_unan += 1
      elif count_pyes >= maj_count:
        S_majority.append({"eco_id":eid, "snum":snum, "doc":doc, "pair":"Yes", "conf":yes_conf,"S":linea+" "+linesa[i+1].strip()})
        total_S_maj += 1
      
print "Total unanimous:", total_S_unan, len(S_unanimous)
print "Total majority:", total_S_maj, len(S_majority)

output_list(S_unanimous, out_dir, "unanimous", "3")

output_list(S_majority, out_dir, "majority", "2")
