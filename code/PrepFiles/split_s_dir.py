import os
import sys
import glob

in_dir = sys.argv[1]
out_dir = sys.argv[2]

if not os.path.exists(out_dir):
  os.mkdir(out_dir)
  
file_to_glob = os.path.join(in_dir, "*.txt")
file_array = glob.glob(file_to_glob)
#print file_array
for f in file_array:
  base_name = os.path.basename(f)
  base_root = os.path.splitext(base_name)[0]
  out_fname = os.path.join(out_dir, base_root+"_s.txt")
  sys_cmd = "python split_text_into_s.py "+ f + " " + out_fname
  print sys_cmd
  os.system(sys_cmd)
  