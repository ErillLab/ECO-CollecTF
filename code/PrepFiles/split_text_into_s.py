import os
import sys
import re
import nltk.data
import nltk.tokenize

# note r.l is for someone's name that caused a sentence break
extra_abbrevs = ['fig', 'figs', 'bv', 'sp', 'i.e', 'al', 'e.g', 'min', 'spp', 'subsp', 'pv', 'approx', 'no', 'arcA+V', 'r.l']
tok = nltk.data.load("english.pickle")
tok._params.abbrev_types.update(extra_abbrevs)

in_fname = sys.argv[1]
out_fname = sys.argv[2]

pat1 = re.compile(".*?(\.\d{1,3}\s)\s*[A|Z]+.*") # Only works if 2 spaces between .## and Uppercase letter. Hmmm

fpo = open(out_fname, "w")
with open(in_fname, 'r') as myfile:
  for l in myfile:
    line = l.strip()
    if len(line) < 1:
      fpo.write("\n")
    else:
      # This doesn't seem to work in the abbrevs list
      if line.find("arcA+V.") > -1:
        line = line.replace("arcA+V.", "arcA + V.")
      if line.find("PAO1. zur") > -1:
        line = line.replace("PAO1. zur", "PAO1.zur") # mistake in the original XML
      if line.find("P2Y. enterocolitica"):
        line = line.replace("P2Y. enterocolitica", "P2 Y. enterocolitica")
      temp_sent_list = tok.tokenize(line)

      # preprocess S for some special cases
      sent_list = []
      for s in temp_sent_list:
        x = pat1.match(s)
        if x:
          print x.groups()
          gtext = x.groups(1)[0]
          gpos = s.find(gtext)
          if gpos > -1:
            sent_list.append(s[:gpos+len(gtext)].strip())
            sent_list.append(s[gpos+len(gtext):].strip())
          else:
            sent_list.append(s)
        else:
          sent_list.append(s)        
      s = 0
      slen = len(sent_list)
      while s < slen: # Can't do for loop due to fixing a split S case
        # special cases that need to be split
        sent = sent_list[s]
        #print s, sent
        # This series don't split and should
        spos = sent.find("1 h. T")
        epos = 4
        if spos < 0:
          spos = sent.find("60 min. A")
          epos = 7
        if spos < 0:
          spos = sent.find("site R. A")
          epos = 7
        if spos < 0:
          spos = sent.find("site R. T")
          epos = 7 
        if spos < 0:
          spos = sent.find("26695. p")
          epos = 6
        if spos < 0:
          spos = sent.find("acetyl-P. A")
          epos = 9
        if spos < 0:
          spos = sent.find("36 h. I")
          epos = 5
        if spos > -1:
          sent = sent[:spos+epos]+"\n"+sent[spos+epos+1:]
        else:
          # This example is for 63C. but I don't want to make that an abbrev
          # join two together
          if sent.find("63C.") > -1 and s+1<slen:
            #print "matched 63C. and s+1<slen at s=",s
            s+=1
            sent2 = sent_list[s]
            lookfor = "difficile"
            if sent2[0:len(lookfor)]==lookfor:
              sent += " "+sent2
        #print "OUTPUT:", sent
        s+=1
        fpo.write("%s\n" % sent)
fpo.close()