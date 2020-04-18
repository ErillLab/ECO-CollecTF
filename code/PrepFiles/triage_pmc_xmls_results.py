import os
import sys
import glob

indir = sys.argv[1]
outdir = sys.argv[2]

if not os.path.exists(outdir):
  os.mkdir(outdir)
f1_outdir = os.path.join(outdir, "format_1R")
if not os.path.exists(f1_outdir):
  os.mkdir(f1_outdir)
unk_outdir = os.path.join(outdir, "unknownR")
if not os.path.exists(unk_outdir):
  os.mkdir(unk_outdir)
  
fpo = open("file_trackerR.txt", "w")
 
file_to_glob = os.path.join(indir, "p*.xml")
print file_to_glob
file_array = glob.glob(file_to_glob)
for f in file_array:
  base_name = os.path.basename(f)
  print base_name
  new_fname = ""
  with open(f, "r") as infile:
    contents = infile.read()

    f1apos = contents.find('<title>Results</title>')
    f1bpos = contents.find('<title>RESULTS AND DISCUSSION</title>')
    f1cpos = contents.find('<title>RESULTS</title>')
    f1dpos = contents.find('<title>Results and Discussion</title>')
    f1epos = contents.find('<title>Results/Discussion</title>')
    f1fpos = contents.find('<title>Results and discussion</title>')
    f1gpos = contents.find('<title>3. Results and Discussion</title>')
    f1hpos = contents.find('<title>Results and Discussion:</title>')
        
    if f1apos > -1 or f1bpos > -1 or f1cpos > -1 or f1dpos > -1 or f1epos > -1 or f1fpos > -1 or f1gpos > -1 or f1hpos > -1:
      format_type = "Format1"
      new_fname = os.path.join(f1_outdir, base_name)
    else:
      not_pos = contents.find("does not allow downloading")
      if not_pos > -1:
        format_type = "NotFull"
      else:
        new_fname = os.path.join(unk_outdir, base_name)
        format_type = "Unknown"
    
    fpo.write("%s\t%s\n" % (base_name, format_type))
    
  if len(new_fname) > 0:
    with open(new_fname, "w") as outfile:
      outfile.write("%s\n" % contents)
      
fpo.close()