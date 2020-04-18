import os
import sys
import glob
import datetime

import WordListInputs
import PgSfSp
import ExactMatchOntWordsWins

def get_pmid(fname):
  base_root = os.path.splitext(os.path.basename(fname))[0]
  fitems = base_root.split("_")
  pmid = fitems[1]
  return pmid

def replace_line(sline, word_list, with_word, rem_hyphen=False):
  for w in word_list:
    # Only do single words
    items = w.split(" ")
    if len(items) > 1:
      continue
    sline = sline.replace(w, with_word)
  if rem_hyphen:
      sline = sline.replace(with_word+"-", with_word+" ")
  return sline
  
dir_path = sys.argv[1]
out_fname = sys.argv[2]

print "Prep word lists"
word_list_class = WordListInputs.WordListInputs()
print "Prep PG SF SP"
pg_sf_sp_class = PgSfSp.PgSfSp()
pg_words = pg_sf_sp_class.pgs
#print "PG words:", pg_words

eco_fname = "eco_v2018-09-14.obo"
so_fname = "so.obo"
go_fname = "go.obo"

print "Prep", eco_fname
eco_class = ExactMatchOntWordsWins.ExactMatchOntWordsWins(eco_fname)
print "Prep", so_fname
so_class = ExactMatchOntWordsWins.ExactMatchOntWordsWins(so_fname, "ECO_1_2_top_words.txt")
print "Prep BP", go_fname
bp_class = ExactMatchOntWordsWins.ExactMatchOntWordsWins(go_fname, None, "BP")
print "Prep MF", go_fname
mf_class = ExactMatchOntWordsWins.ExactMatchOntWordsWins(go_fname, None, "MF")


file_to_glob = os.path.join(dir_path, "*_s.txt")
print "file to glob:", file_to_glob
file_array = glob.glob(file_to_glob)

fpo = open(out_fname, "w")
out_str = "PMID_S\tSimpleAssert\tMoreAssert\tToPhrase\tWrapUp\tBI\tPG\tSF\tSP\tTaxI\tTaxE\tECOScore\tECOID\tECOWords\tECOTextWords\tSOScore\tSOID\tSOWords\tSOTextWords\tGOBPScore\tGOBPID\tGOBPWords\tGOBPTextWords\tGOMFScore\tGOMFID\tGOMFWords\tGOMFTextWords\tSentence"
fpo.write("%s\n" % out_str)
for f in file_array:
  print "----", f
  with open(f, "r") as fpi:
    pmid = get_pmid(f)
    lcnt = 0
    scnt = 0
    for l in fpi:
      s_output = False
      lcnt += 1
      if lcnt == 1:
        continue
      line = l.strip()
      if len(line) < 1:
        continue
      if line[-1] == '.':
        line = line[:-1]
      if len(line) < 1:
        continue
      scnt += 1
      print "=========================================="
      print pmid, scnt, line
      out_vals = [pmid+"_"+str(scnt)]
      
      # Do this before lowercasing or other mods
      nline = replace_line(line, pg_words, "protein", True) # remove hyphens here
      print "nline:", nline
      nline2 = replace_line(line, pg_words, "gene", True) # remove hyphens here
      print "nline:", nline2
      
      print "Word lists"
      wl_info = word_list_class.process_line(line, pmid, scnt)
      print wl_info
      for wval in wl_info:
        out_vals.append(str(wval))
      print "pg sf sp"
      pgsfsp_info = pg_sf_sp_class.process_line(line, pmid, scnt)
      print pgsfsp_info
      for pval in pgsfsp_info:
        out_vals.append(str(pval))
      print "ECO"
      eco_info = eco_class.process_line(line, pmid, scnt)
      print eco_info
      # score, id, ont text, text match win
      for oval in eco_info:
        out_vals.append(str(oval))
      print "SO"
      so_info = so_class.process_line(line, pmid, scnt)
      print so_info
      for oval in so_info:
        out_vals.append(str(oval))

      print "GO BP"
      bp_info = bp_class.process_line(line, pmid, scnt)
      print "BP:", bp_info
      bp_info_2 = bp_class.process_line(nline, pmid, scnt)
      print "BP2:", bp_info_2, nline
      # info is a tuple with the score first
      if bp_info_2[0] > bp_info[0]:
        print "Using BP2"
        bp_info = bp_info_2
      bp_info_3 = bp_class.process_line(nline2, pmid, scnt)
      print "BP3:", bp_info_3, nline2
      # info is a tuple with the score first
      if bp_info_3[0] > bp_info[0]:
        print "Using BP3"
        bp_info = bp_info_3
      for oval in bp_info:
        out_vals.append(str(oval))
        
      print "GO MF"
      mf_info = mf_class.process_line(line, pmid, scnt)
      print "MF:", mf_info
      mf_info_2 = mf_class.process_line(nline, pmid, scnt)
      print "MF2:", mf_info_2, nline
      # info is a tuple with the score first
      mf_info_3 = mf_class.process_line(nline2, pmid, scnt)
      print "MF3:", mf_info_3, nline2
      # info is a tuple with the score first
      if mf_info_3[0] > mf_info[0]:
        print "Using MF3"
        mf_info = mf_info_3
      if mf_info_2[0] > mf_info[0]:
        print "Using MF2"
        mf_info = mf_info_2
      for oval in mf_info:
        out_vals.append(str(oval))
      #out_str = pmid+"_"+str(scnt)+"\t"+str(line_max_score)+"\t"+line_max_ont_id+"\t"+line
      # PMID_S SimpleAssert MoreAssert ToPhrase WrapUp BI P/G SF SP TaxI TaxE ECOScore ECOID ECOWords ECOTextWords
      # SOScore SOID SOWords SOTextWords GOBPScore GOBPID GOBPWords GOBPTextWords
      # GOMFScore GOMFID GOMFWords GOMFTextWords Sentence
      out_str = "\t".join(out_vals)+"\t"+line
      fpo.write("%s\n" % out_str)
      
    #sys.exit(0)        
fpo.close()          