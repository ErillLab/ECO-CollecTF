import os
import sys
import glob

in_dir = sys.argv[1]
out_dir = sys.argv[2]
subdir_array = sys.argv[3:]

if not os.path.exists(out_dir):
  os.mkdir(out_dir)
  
for sub in subdir_array:
  in_dir_sub = os.path.join(in_dir, sub)
  out_dir_sub = os.path.join(out_dir, sub)
  sys_cmd = "python map_brat_to_tags_dir.py "+ in_dir_sub + " "+ out_dir_sub 
  print sys_cmd
  os.system(sys_cmd)
  