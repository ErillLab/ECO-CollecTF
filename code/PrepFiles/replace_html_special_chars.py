import os
import sys

map_fname = sys.argv[1]
in_fname = sys.argv[2]
out_dir = sys.argv[3]

char_map = {}
len_char_map = {}

with open(map_fname, 'r') as myfile:
  for l in myfile:
    line = l.strip() 
    if len(line) > 1:
      items = line.split("\t")
      sp_chars = items[0]
      sp_chars_len = len(sp_chars)
      map_to = items[1]
      char_map[sp_chars] = map_to
the_entities = char_map.keys()
        
base_name = os.path.basename(in_fname)
out_fname = os.path.join(out_dir, base_name)
fpo = open(out_fname, "w")
with open(in_fname, 'r') as myfile:
  for l in myfile:
    #print "line:", l
    new_l = l
    for ent in the_entities:
      if new_l.find(ent) > -1:
        new_l = new_l.replace(ent, char_map[ent])

    fpo.write("%s" % new_l)
      
fpo.close()