import os
import sys
import glob

in_dir = sys.argv[1]
out_dir = sys.argv[2]
 
if not os.path.exists(out_dir):
  os.mkdir(out_dir)
  
file_to_glob = os.path.join(in_dir, "*_s_ef.txt")
print file_to_glob
file_array = glob.glob(file_to_glob)
#print file_array
for f in file_array:
  sys_cmd = "python raw_annot_split.py "+ f + " " + out_dir 

  print sys_cmd
  os.system(sys_cmd)
  