import os
import sys
import glob
import time

def process_scores_file(fname, type):
  data = {}
  print "Process scores file:", fname, "as type:", type
  with open(fname, "r") as fpi:
    for l in fpi:
      line = l.strip()
      if len(line) < 1:
        continue
      items = line.split("/")
      params = []
      for it in items:
        if it[0:4] == "docs":
          params = it.split("__")[1:]
          break
      if len(params) < 1:
        print "ERROR: couldn't get params from",line
        sys.exit(0)
      pkey = "__".join(params)
      if (type=="sent_iaa_k") or (type=="sent_iaa_f1"):
        # Split by , and get last value
        val = line.split(",")[-1]
      elif (type == "kw_stats") or (type == "flat_stats") or (type=="kw_stats_identity"):
        # Split by space
        val = line.split(" ")[-1]
      else:
        val = line.split(" ")[-4]
      #print "key:", pkey, "val:", val
      # At this level, we don't have duplicates in the file
      data[pkey] = float(val)
  return data

def fold_in_scores(compiled, scores, pos, replicates):
  for sckey in scores:
    if sckey in compiled:
      #print "Seen", sckey,"before, so add at", pos
      cur_val = compiled[sckey]
      cur_val[pos] = scores[sckey]
    else:
      #print "New", sckey
      repls = [0 for i in range(replicates)]
      repls[pos] = scores[sckey]
      compiled[sckey] = repls

      
top_dir = sys.argv[1] # Enter full path here

cur_dir = os.getcwd()
print "cur_dir:", cur_dir

prefix = "docs_outdir"
pair_file = os.path.join(cur_dir,"annot_pairs.txt")

steps = [1,2,3]
#steps = [2,3]

# If change these, see also run_synthetic_stats.py
# This allows kw stats to be run with different values for No-No matches.
# We use No-No pairing of IC=1, that is "_no1".
nos_suffixes = ["_no1"]
non_suffixes = [""] # to keep code same for all stat types

file_to_glob = os.path.join(top_dir, prefix+"*")

dir_array = glob.glob(file_to_glob)
if 1 in steps:
  for d in dir_array:
    # For each annotator, for each data_as_tags file, do the 
    # raw_stats_split file and save log to logs\rss_log.txt
    # Note: there is a separate raw_stats_split dir for each separate docs param run
    sys_cmd = "python run_synthetic_raw_stats_split.py "+d
    print sys_cmd
    os.system(sys_cmd)

if 2 in steps:
  for d in dir_array:
    # This uses the raw_stats_split files created in step 1
    # It runs each of the stats techniques (K, F, flat, multi=KW)
    # It creates various outputs in the stats dir UNDER raw_stats_split (under each
    # docs_outdir under each parameter set).
    # Kappa logs go under the data_as_tags\doc para set\logs
    # Other logs go under the raw_stat_split\doc parameter set\logs
    sys_cmd = "python run_synthetic_stats.py "+d+" "+pair_file
    print sys_cmd
    os.system(sys_cmd)
  
if not 3 in steps:
  print "Not running step 3"
  sys.exit(0)
  
# grep files also indicate the type
grep_files = ["sent_iaa_k", "sent_iaa_f1", "kw_stats", "f1ic_stats", "flat_stats", "f1flat_stats"]
grep_files = ['sent_iaa_k', "kw_stats"]#, "kw_stats_identity"]
# grep for gives what line in the output file to search for
# Note: COMPLETE works for IAA, use ANY2 for actual data
grep_for = ["COMPLETE", "COMPLETE", "KwIAA", "F1 micro", "K for", "F1 micro"]
grep_for = ['COMPLETE', "KwIAA"]#, "KwIAA"]


replicates = len(dir_array)
os.chdir(top_dir)

# This step takes all the IAA stat scores for EACH annotator PAIR, 
# buried down under each docs_output dir
# under each raw_stats_split/docs-params-dir/stats dir (uses find to get them)
# and writes all the pertinent lines to a scores_ file. There is one of these under
# each of the docs_outdirs. For simulation, there is only 1 such pair, so 1 line in
# the scores_ files. (The scores are the avg for THAT DOC SET.)
# THEN, it pools all the separate stats into a structure, compiled.
# This contains the scores for each doc set for the doc params.
# This is done for each of the stats types.
# THEN, it takes the compiled scores for that type and gets the avg, min, max.
# This last info is output to the summary_ file in the top most directory.
for i in range(len(grep_files)):
  compiled = {}
  if grep_files[i]=="kw_stats":
    loop_suffixes = nos_suffixes
  else:
    loop_suffixes = non_suffixes
  for suffix in loop_suffixes:
    for d in range(replicates):   
      os.chdir(prefix+str(d)) # for some reason didn't like chdir to d
      print "chdir to", prefix+str(d)
      
      file_root = grep_files[i]+suffix
      out_file = "scores_"+file_root+".txt"
      sys_cmd = "find . -name "+file_root+"\\*.txt -exec grep -H \""+grep_for[i]+"\" {} ';' > "+ out_file
   
      print sys_cmd
      os.system(sys_cmd)
      time.sleep(1)
      
      scores = process_scores_file(out_file, grep_files[i])
      fold_in_scores(compiled, scores, d, replicates)
      print "AFTER FOLD, compiled:", compiled
      os.chdir("..")
      
    print "chdir up a level to do summary for all replicates of type",grep_files[i]
    print file_root
    s_sorted = compiled.keys()
    s_sorted.sort()
    sum_ofname = os.path.join(top_dir, "summary_"+file_root+".txt")
    fpo = open(sum_ofname,"w")
    for skey in s_sorted:
      params = skey.split("__")
      pvalues = compiled[skey]
      mean = sum(pvalues)/len(pvalues)
      pvals_str = ",".join(map(str, pvalues))
      #print params,pvalues,min(pvalues),max(pvalues),mean
      out_str = ",".join(params)+","+pvals_str+","+str(min(pvalues))+","+str(max(pvalues))+","+str(mean)
      fpo.write("%s\n" % out_str)
    fpo.close()
    #print "--------------------------------------"
    
  
os.chdir(cur_dir)

  