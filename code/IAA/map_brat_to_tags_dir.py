import os
import sys
import glob

in_dir = sys.argv[1]
out_dir = sys.argv[2]

if not os.path.exists(out_dir):
  os.mkdir(out_dir)
  
file_to_glob = os.path.join(in_dir, "*.ann")
file_array = glob.glob(file_to_glob)
#print file_array
for f in file_array:
  base_name = os.path.basename(f)
  base_root = os.path.splitext(f)[0]
  in_fname = os.path.join(in_dir, base_root+".txt")
  sys_cmd = "python map_brat_to_tags.py "+ f + " " + in_fname + " "+ out_dir 
  print sys_cmd
  os.system(sys_cmd)
  