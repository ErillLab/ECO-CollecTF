import os
import sys
import glob
import argparse

parser = argparse.ArgumentParser(description="parse xml file")
parser.add_argument('indir', help="Input dir with the files")
parser.add_argument('outdir', help="Output dir")
parser.add_argument('-m', '--ml', nargs='?', help="m=html, t=txt", default="-t")
args = parser.parse_args()

indir = args.indir
outdir = args.outdir
html = False
print args.ml
if args.ml == "m":
  html = True
  
if not os.path.exists(outdir):
  os.mkdir(outdir)
  
file_to_glob = os.path.join(indir, "p*.xml")
file_array = glob.glob(file_to_glob)
#print file_array
for f in file_array:
  sys_cmd = "python parse_pmc_xml_copyright.py "+f+" "+outdir
  print sys_cmd
  os.system(sys_cmd)
  