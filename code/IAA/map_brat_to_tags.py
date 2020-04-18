import os
import sys
import string

punctuation = set(string.punctuation)

brat_fname = sys.argv[1] # .ann file produced by brat
in_fname = sys.argv[2]
out_dir = sys.argv[3]

if not os.path.exists(out_dir):
  os.mkdir(out_dir)
  
indir = os.path.dirname(brat_fname)
who = os.path.basename(indir)
base_name = os.path.basename(brat_fname)
base_root = os.path.splitext(base_name)[0]
out_fname = os.path.join(out_dir, base_root+"_ef.txt")

instance_map = {}
char_pos_map = {}
pos = 0
lcnt = 0
with open(in_fname, 'r') as myfile:
  for l in myfile:
    for i in range(len(l)):
      char_pos_map[pos] = {"char":l[i]}
      pos += 1
    # Count the number of lines to add those extra end of line chars
    # Unix system counts end of line as 2 chars
    #   If do dos2unix first, don't need to add to pos
    #print "pos before", pos
    #pos += 1
    #print "    pos after", pos

print "Last pos:", pos    
with open(brat_fname, 'r') as myfile:
  for l in myfile:
    line = l.strip() 
    if len(line) > 1:
      items = line.split("\t")
      print "ITEMS:", items
      ann_instance = items[0]
      elem_info = items[1].split()
      instance_type = ann_instance[0]
      #semi_colon = items[1].find(";")
      if instance_type == "T":
        which_ont = elem_info[0]
        beg_pos = int(elem_info[1])
        end_pos = int(elem_info[-1]) # A multi-fragment annotation has a ; in it
        text = items[2]
        if ann_instance in instance_map:
          print "ERROR: repeated instance", items
          sys.exit(0)
        else:
          instance_map[ann_instance] = {"ont":which_ont,"start":beg_pos,"end":end_pos,"text":text, "ainst":ann_instance}
          
        print "lookup beg_pos:", beg_pos
        cur_beg = char_pos_map[beg_pos]
        if "instance" in cur_beg:
          cur_inst = cur_beg["instance"]
          cur_inst.append(ann_instance)
        else:
          cur_inst = [ann_instance]
        cur_beg["instance"] = cur_inst
        char_pos_map[beg_pos] = cur_beg
        cur_end = char_pos_map[end_pos]
        if "instance" in cur_end:
          cur_inst = cur_end["instance"]
          # want end to be in reverse order in case of multiples at same beg,end
          # they will be properly nested
          cur_inst.insert(0,ann_instance) 
        else:
          cur_inst = [ann_instance]
        cur_end["instance"] = cur_inst
        char_pos_map[end_pos] = cur_end 
      elif instance_type == "N":
        which_instance = elem_info[1]
        ont_id = ":".join(elem_info[2].split(":")[1:])
        if len(items) >= 3:
          ont_term = items[2]
        else:
          print "WARNING: no ont_term in line", line, base_root, who
          ont_term = ont_id
        if which_instance not in instance_map:
          print "ERROR: unknown instance", which_instance, items, base_root, who
          sys.exit(0)
        else:
          cur_item = instance_map[which_instance]
          cur_item["ont_id"] = ont_id
          cur_item["ont_term"] = ont_term
          instance_map[which_instance] = cur_item
      elif instance_type == "A":
        attrib_type = elem_info[0]
        which_instance = elem_info[1]
        attrib_val = elem_info[2]
        print "A: type: ", attrib_type, " which:", which_instance, " aval:", attrib_val
        if which_instance not in instance_map:
          print "ERROR: unknown instance", which_instance, items
          sys.exit(0)
        else:
          cur_item = instance_map[which_instance]
          cur_item[attrib_type] = attrib_val
          instance_map[which_instance] = cur_item
          print instance_map[which_instance]
      elif instance_type == "#":
        which_instance = elem_info[1]
        comment = items[2].replace('"', '\'').replace("\n", " ")
        print "NOTES:", base_root, which_instance, comment
        if which_instance not in instance_map:
          print "ERROR: unknown instance", which_instance, items
          sys.exit(0)
        else:
          cur_item = instance_map[which_instance]
          cur_item["notes"] = comment
          instance_map[which_instance] = cur_item
      else:
        print "Unknown instance:", ann_instance
        sys.exit(0)

#ref_keys = instance_map.keys() 
#ref_keys.sort() # doesn't sort in order T10 before T2
#for refs in ref_keys:
#  print refs, instance_map[refs]

print "Create:", out_fname
fpo = open(out_fname, "w")

out_str = ""
for p in range(pos):
  if p not in char_pos_map:
    continue
  #print p, char_pos_map[p]
  cur_char_info = char_pos_map[p]
  #out_str = ""
  if "instance" in cur_char_info:
    cur_inst = cur_char_info["instance"]
    print "instance:", cur_inst
    for curi in cur_inst:
      inst_info = instance_map[curi]
      print "   CURI", curi, inst_info
      which_ont = inst_info["ont"]
      if which_ont == "Assertion":
        print "WARNING: Assertion annotation", base_name, inst_info, who
        continue # Not doing Assertions at this time
      start = inst_info["start"]
      #print "inst info:", inst_info
      conf=""
      stren = ""
      cat = ""
      nexts = ""
      notes = ""
      negs = ""
      if "ECOConfidence" in inst_info:
        conf = " ECOConfidence=\""+inst_info["ECOConfidence"]+"\""
      else:
        if p==start:
          print "WARNING: no ECOConfidence in", base_name, inst_info, who
        conf = " ECOConfidence=\"None\""
      if "AssertionStrength" in inst_info:
        stren = " AssertionStrength=\""+inst_info["AssertionStrength"]+"\""
      else:
        if p==start:
          print "WARNING: no AssertionStrength in", base_name, inst_info, who
        stren = " AssertionStrength=\"None\""
      if "Category" in inst_info:
        cat = " Category=\""+inst_info["Category"]+"\""
      else:
        if p==start:
          print "WARNING: no Category in", base_name, inst_info, who
        cat = " Category=\"None\""
      if "NextSentence" in inst_info:
        nexts = " NextSentence=\""+inst_info["NextSentence"]+"\""
      else:
        nexts = " NextSentence=\"No\""
      if "NegativeStatement" in inst_info:
        negs = " NegativeStatement=\""+inst_info["NegativeStatement"]+"\""
      else:
        negs = " NegativeStatement=\"No\""        

      if "notes" in inst_info:
        notes = " notes=\""+inst_info["notes"]+ "\""
      if "ont_id" in inst_info:
        ont_id = inst_info["ont_id"]
        ecopos = ont_id.find("ECO:")
        print "ECPOS:", ecopos
        if ecopos < 0:
          ont = inst_info["ont"].upper()
          ont_id = ont+":"+ont_id          
        the_str= "<term sem=\""+ont_id+"\" id=\""+curi+"\""
      else:
        ont = inst_info["ont"]
        if p==start:
          print "WARNING: no ECOID in", base_name, inst_info, who
        the_str="<term sem=\""+ont+"\" normalized=\"False\" id=\""+curi+"\"" 
      if p==start:
        out_str += the_str+conf+stren+cat+nexts+negs+notes+">"

  out_str+= cur_char_info["char"]

  if "instance" in cur_char_info:
    cur_inst = cur_char_info["instance"]
    first_inst = True
    move_it = False
    move_char = ""
    for curi in cur_inst:
      inst_info = instance_map[curi]
      which_ont = inst_info["ont"]
      if which_ont == "Assertion":
        continue # Not doing Assertions at this time
      end = inst_info["end"]
      print "p:", p, "end:", end
      if p==end:
        last_char = out_str[-1]
        if first_inst and (last_char == " " or last_char == ',' or last_char == '.' or last_char == ';'):
          # having problems with double tags and > -- > is a punct char
          move_it = True
          move_char = last_char
          print "MOVE it:", move_char+"."
          out_str = out_str[:-1]
          first_inst = False
        out_str += "</term id=\"" +curi+"\">"
        #out_str+="</term>"
        #fpo.write("%s" % out_str)
      #print p,out_str
    if move_it:
      print "MOVED:", move_char+"."
      out_str += move_char
      
  #fpo.write("%s" % out_str)
#
# Go through and fix up any spaces and punct before </term> tags
new_out_str = ""
olen = len(out_str)
print "LEN out_str:", olen
move_chars = ""
move_it = False
in_beg_tag = False
for i in range(olen):
  if i+6<olen and out_str[i:i+6]=="</term":
    nlen = len(new_out_str)
    backup = 0
    for j in range(nlen-1, 0, -1):
      if new_out_str[j] == " " or new_out_str[j] == "," or new_out_str[j]=="." or new_out_str[j]==";":
        print "Backup:"
        backup+=1
      else:
        break
    if backup > 0:
      move_it = True
      move_chars = new_out_str[-backup:]
      new_out_str = new_out_str[:-backup]
      print "backuped:",new_out_str+"."

  elif i+5<olen and out_str[i:i+5]=="<term":
    in_beg_tag = True
  elif move_it and out_str[i] == ">":
    if i+7<olen and out_str[i+1:i+7]=="</term":
      # we have another ending tag, so don't move the chars
      nothing=1
    else:
      new_out_str += ">"+move_chars
      move_it = False
      continue
  elif in_beg_tag and out_str[i]==">":
    # I don't think brat keeps leading spaces
    if i+1 < olen:
      if out_str[i+1]=="<":
        nothing=1 # keep going
      elif out_str[i+1]==" ":
        print "FOUND a space at",i
      else:
        in_beg_tag = False
    else:
      in_beg_tag = False
  new_out_str+= out_str[i]

print "WRITE OUT"
fpo.write("%s" % new_out_str)
fpo.close()
  