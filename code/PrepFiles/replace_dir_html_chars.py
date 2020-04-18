import os
import sys
import glob

char_file = sys.argv[1]
indir = sys.argv[2]
outdir = sys.argv[3]

if not os.path.exists(outdir):
  os.mkdir(outdir)
  
file_to_glob = os.path.join(indir, "p*.xml")
file_array = glob.glob(file_to_glob)
#print file_array
for f in file_array:
  sys_cmd = "python replace_html_special_chars.py "+ char_file + " " + f + " " + outdir
  print sys_cmd
  os.system(sys_cmd)
  