import os
import sys
import string

def get_id(text):
  id_str = "id=\""
  id_str_len = len(id_str)
  ibpos = text.find(id_str)
  iepos = text.find('"', ibpos+id_str_len+1)
  id_val = text[ibpos:iepos+1]
  return id_val
  
def process_tag_text(text):
  print "process tag text:", text
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
  if bpos > -1:
    return {"skip_eco":True}
    
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
  print "ECO:", eco_id+".", eco_conf_val+"."
  print "  Category:", category_val+".", "AS:", assertion_val+"."
  print "  Next?", next_s_val+".", "Neg?", neg_s_val+"."
  return {"skip_eco":False, "eco":eco_id, "econf":eco_conf_val, "astr":assertion_val, "cat":category_val, "next":next_s_val, "neg":neg_s_val}
  
def remove_begin_tags(text):
  cleaned = ""
  in_tag = False
  tlen = len(text)
  #print "TLEN:", tlen
  for i in range(tlen):
    #print i, text[i], in_tag
    if not in_tag:
      #print "not in_tag"
      if text[i] == "<" and i+5<tlen and text[i:i+5]=="<term":
        in_tag = True
        #print "  in tag now"
      else:
        cleaned += text[i]
        #print "added to cleaned"
    else:
      #print "in tag"
      if text[i] == ">":
        in_tag = False
  return cleaned  
def remove_end_tags(text):
  cleaned = ""
  in_tag = False
  tlen = len(text)
  #print "TLEN:", tlen
  for i in range(tlen):
    #print i, text[i], in_tag
    if not in_tag:
      #print "not in_tag"
      if text[i] == "<" and i+6<tlen and text[i:i+6]=="</term":
        in_tag = True
        #print "  in tag now"
      else:
        cleaned += text[i]
        #print "added to cleaned"
    else:
      #print "in tag"
      if text[i] == ">":
        in_tag = False
  return cleaned
    
def process_tags(tag_list, tagged_text):
  # Need to remove the </term stuff
  # Could be a problem if not nested
  # tags need to be popped
  eco_info = {}
  num_tags_in_s = len(tag_list)
  for i in range(num_tags_in_s-1, -1, -1):
    tag_text = tag_list[i]
    id_str = get_id(tag_text)
    #print "Tag:", i, tag_text, id_str
    eco_data = process_tag_text(tag_text)
    eco_data["tagged"] = "SKIPPED"
    eco_info[id_str] = eco_data
  return eco_info
  
def format_tag(tag_map):
  sep = ";:;"
  str = tag_map["eco"]+sep+tag_map["econf"]+sep+tag_map["cat"]+sep+tag_map["astr"]+sep+tag_map["tagged"]+sep+tag_map["next"]+sep+tag_map["neg"]
  return str
  
  
in_fname = sys.argv[1] # _s_ef.txt file -- tagged version
out_dir = sys.argv[2] # place to write stats per annotator

if not os.path.exists(out_dir):
  os.mkdir(out_dir)

base_name = os.path.basename(in_fname)
base_root = os.path.splitext(base_name)[0]
out_fname = os.path.join(out_dir, base_root+"_raw_stats_split.txt")

fpo = open(out_fname, 'w') # tagged info

with open(in_fname, 'r') as myfile:
  lcnt = 0
  num_S = 0
  num_annots = 0
  num_negs = 0
  num_pairs = 0
  sent_pair = False # for annotated S, set in the current S and tested for the Next one
  a_paired_s = False # for non-annotated S and to carry along for the non-paired S output
  for l in myfile:
    # Skip the first line which has "Results", etc

    if lcnt > 0:
      line = l.strip() 
      if len(line) > 1:
        s_tags = []
        num_S += 1
        num_term_tags = line.count("<term")
        print "Line#:",lcnt+1,"num term tags:", num_term_tags
        
        sent = remove_begin_tags(line)
        sent = remove_end_tags(sent)
           
        # Gather info 
        etpos = 0
        spos = 0
        for i in range(num_term_tags):
          bpos = line.find("<term", spos)
          nspos = line.find("NextSentence", bpos+10)
          epos = line.find(">", nspos)
          tag_text = line[bpos:epos]
          id_str = get_id(tag_text)
          print "TAG:", tag_text
          print "ID STR:", id_str
          s_tags.append(tag_text)
          etpos = epos
          spos = epos
        #print "last pos:", etpos
        #print s_tags
        #print "REST:", line[etpos+1:]
        
        if len(s_tags) > 0:
          tag_data = process_tags(s_tags, line[etpos+1:])
          for t in tag_data:
            tdata = tag_data[t]
            print "TDATA:", tdata
            if tdata["skip_eco"]:
              print "Skipping", tdata
              continue
            num_annots += 1

            annot_num = t[4:-1]
            #print "t:",t
            formatted_tag = format_tag(tdata)
            ostr = "TAGGED\t"+str(num_S)+"\t"+annot_num+"\t"+ formatted_tag
            fpo.write("%s\n" % ostr)

            if tdata["next"] == "Yes":
              num_pairs += 1
              pair_num_S = num_S+1
              ostr = "TAGGED\t"+str(pair_num_S)+"\t"+annot_num+"\t"+ formatted_tag       
              fpo.write("%s\n" % ostr)
              
    lcnt += 1
  ostr = "SUMMARY\tNumDocS:"+str(num_S)+"\tNumAnnot:"+str(num_annots)+"\tNumPair:"+str(num_pairs)+"\tNumNeg:"+str(num_negs)  
  fpo.write("%s\n" % ostr)
fpo.close()
