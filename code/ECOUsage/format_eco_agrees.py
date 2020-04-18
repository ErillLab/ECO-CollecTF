import os
import sys
import operator
import OboInfo

def get_key(items):
  return items[0]+"_"+items[1]+"_"+items[3]+"_"+items[2]
def create_val_entry(pmid, items):
  return {"pmid":pmid,"text_passage":items[6]}
def create_conf_entry(pmid, items):
  value = create_val_entry(pmid, items)
  #print "conf val:", value
  return [value]
def create_ann_entry(pmid, items, confval):
  value = create_conf_entry(pmid, items)
  #print "ann entry:", value
  return {conf_val:value}
def create_full_entry(pmid, items, anns, confval):
  value = create_ann_entry(pmid, items, confval)
  return {anns:value}

def output_eids(passages, ic_data, fpo):
  # Sort by ECO ID first
  e_sorted = passages.keys()
  e_sorted.sort()
  for eid in e_sorted:
    node = ic_data.get_node(eid)
    #print node.name
    eid_entry = passages[eid]
    # Now we sort by num anns, which is a string, descending
    a_sorted = eid_entry.keys()
    a_sorted.sort(reverse=True)
    for an in a_sorted:
      ann_entry = eid_entry[an]
      # Now sort by the conf val, again a string
      c_sorted = ann_entry.keys()
      c_sorted.sort(reverse=True)
      for cf in c_sorted:
        c_array = ann_entry[cf]
        # At this point, the items aren't sorted
        for cval in c_array:
          pmid = cval["pmid"]
          text = cval["text_passage"].replace('"','')
          out_str = eid+","+node.name+","+an+","+cf+","+pmid+',"'+text+'"'
          #print out_str
          fpo.write("%s\n" % out_str)       
fname = sys.argv[1]
obo_fname = sys.argv[2]
out_fname = sys.argv[3]

ic_data = OboInfo.OboInfo()
ic_data.set_ont_type("ECO")
ic_data.build_ont_tree(obo_fname, "ECO")

tags = []
counts = {}
with open(fname, "r") as fpi:
  the_lines = fpi.readlines()
  
# get everything and see if we have pairs or not
for l in the_lines:
  line = l.strip()
  if len(line) < 1:
    continue
  items = line.split("\t")
  key = get_key(items)
  tags.append(key)
  
# Now re-process and don't keep a single if it has a pair
passages = {}

for l in the_lines:
  line = l.strip()
  if len(line) < 1:
    continue
  items = line.split("\t")
  eid = items[0]
  num_anns = items[4]
  conf_val = items[5]
  key = get_key(items)
  print key
  if key.find("No") > -1:
    ykey = key.replace("No", "Yes")
    if ykey in tags:
      print ykey, "in tags, skip"
      continue
  pmid = items[3].split("_")[1]
  
  if eid not in counts:
    counts[eid] = 1
  else:
    cur_val = counts[eid]+1
    counts[eid] = cur_val

  print eid, num_anns, conf_val, pmid
  
  if eid not in passages:
    passages[eid] = create_full_entry(pmid, items, num_anns, conf_val)
    #print "New eid:", passages[eid]
  else:
    cur_entry = passages[eid]
    #print "Need to add to current:", cur_entry
    if num_anns not in cur_entry:
      cur_entry[num_anns] = create_ann_entry(pmid, items, conf_val)
      #print num_anns,"not in entry, new", cur_entry[num_anns]
    else:
      cur_ann_entry = cur_entry[num_anns]
      #print "Need to add to ann", cur_ann_entry
      if conf_val not in cur_ann_entry:
        cur_ann_entry[conf_val] = create_conf_entry(pmid, items)
        #print "New conf", conf_val, cur_ann_entry[conf_val]
      else:
        cur_ann_entry[conf_val].append(create_val_entry(pmid, items))
        #print "ADD conf:", conf_val,cur_ann_entry[conf_val]
      #cur_entry[num_anns] = cur_ann_entry #?  
    #passages[eid] = cur_entry # do I need this?       
  #print "EID entry now:", passages[eid]    
    
    
e_sorted = counts.keys()
e_sorted.sort()
print "EIDs alphabetical"
for eid in e_sorted:
  print eid, counts[eid]
  
print "EIDs by count"
sorted_counts = sorted(counts.iteritems(), key=operator.itemgetter(1), reverse=True)
for eid in sorted_counts:
  print eid[0], eid[1]

fpo = open(out_fname, "w")
out_str="ECO Term,Name,Num Annotators,Confidence,PMID,Text Passage"
fpo.write("%s\n" % out_str)
output_eids(passages, ic_data, fpo)
fpo.close() 