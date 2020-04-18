import os
import sys
import glob
import re
import copy
from nltk.corpus import stopwords
import OboICCalcP

class ExactMatchOntWordsWins:
  
  def remove_stops(self, the_words):
    ret_words = []
    for w in the_words:
      if w not in self.def_stops:
        ret_words.append(w)
    return ret_words
    
  def add_back_initial_letter(self, orig_name, new_name):
    # New name is a list of words at this point
    #print "add back:", orig_name, new_name
    ret_name = new_name
    first_part = orig_name.split(" ")[0].strip()
    if len(first_part)==1 and len(new_name) > 0:
      #print "first_part", first_part
      first_clean = new_name[0]
      if not first_part == first_clean:
        # Insert keeps returning a NoneType when try to put first part at beginning
        # so...
        new_name_str = first_part +" "+ " ".join(new_name)
        ret_name = new_name_str.split(" ")
        #print "Added", first_part,"back, now have:",     ret_name,"***************************************"
    #print "RETURNING:", ret_name
    return ret_name
  
  def get_ont_info(self, ic_data, no_annot, ont_root, annot_fake, ont_id_list, top_words):
    data = []
    for ont_id in ont_id_list:
      if ont_id == no_annot or ont_id==ont_root or ont_id==annot_fake:
        continue
      the_node = ic_data.get_node(ont_id)
      #print ic_data.ont_type, ont_id, the_node.prok
      # Do get all the GO entries because we need to get just MF or BP
      # And, sometimes prok entries have non-prok children but prok grandchildren
      # So get them all, and sort them out later
      #if ic_data.ont_type == "GO" and not the_node.prok:
      #  continue
      #print "Keep:", ont_id, the_node.prok
      #print "check ont:", ont_id, the_node.name, the_node.synonym
      # SO has _ in the names, it also has a lot of single letters that are stop words
      the_name = the_node.name
      if len(the_name) == 1:
        # Don't want single letter ontology names
        continue
      cleaned_up = self.remove_stops(the_name.replace("evidence", "").replace("_"," ").strip().  lower().split(" "))
      if ic_data.ont_type == "SO":
        cleaned_up = self.add_back_initial_letter(the_name, cleaned_up)
      #print "Adding name:", cleaned_up
      if len(top_words):
        cleaned_up_str = " ".join(cleaned_up) # have to add back the space for test
        #print "cleaned:", cleaned_up_str
        if cleaned_up_str in top_words:
          print "Remove name top word:", cleaned_up_str, ont_id, the_name
          continue
      info = [cleaned_up]
      if len(the_node.synonym) > 0:
        raw_syns = the_node.synonym.split("~~")
        # Need to remove the "" and EXACT
        for rs in raw_syns:
          matches = re.findall(r'\"(.+?)\"',rs)
          # There is a GO entry, GO:0070026 that has "NO binding" as a syn
          # When the "no" is removed, all that is left is binding. 
          # Put no back (won't match, but OK).
          orig_syn = matches[0].replace("evidence", "").replace("_"," ").strip().lower()
          if len(orig_syn)==1:
            continue
          if len(top_words):
            #print "OS:", orig_syn
            if orig_syn in top_words:
              print "Remove os top word:", orig_syn
              continue
          syn = self.remove_stops(orig_syn.split(" "))
          if ont_id == "GO:0070026":
            syn.insert(0, "no")
          if ic_data.ont_type == "SO":
            if len(syn) < 1:
              continue
            if syn[0] == "insdc":
              # Some weird thing, skip
              continue
            syn = self.add_back_initial_letter(orig_syn, syn)
            if ont_id == "SO:0000161":
              syn.append("a")
          if len(syn) > 0 and not syn in info:
            # Once _ is replaced by a space, SO can have duplicates
            #print "Syn:", syn
            info.append(syn)
      data.append((ont_id, info))
    return data

  def prune_ont_list(self, cur_tuples, new_root):
    print "Prune", new_root[:2]
    # Want only a subtree, so pull out that part
    top_node = self.ic_data.get_node(new_root)
    desc_node_ids = self.ic_data.get_descendants(top_node)
    #print "num desc features:", len(desc_node_ids)
    new_ids = [new_root]
    for id in desc_node_ids:
      if self.o_type == "GO":
        # We only want prok items
        the_node = self.ic_data.get_node(id)
        if id not in new_ids and the_node.prok:
          new_ids.append(id)
      else:
        if id not in new_ids:
          new_ids.append(id)
    # Now update the tuples list
    temp_ont_tuples = []
    for ot in cur_tuples:
      o_id = ot[0]
      if o_id in new_ids:
        temp_ont_tuples.append(ot)
        #print "Keeping", ot[0]
        #for s in ot[1]:
          #print "  ", s
    return temp_ont_tuples
  
  def score_words(self, s_set, ont_words):
    win_len = len(ont_words)
    #mcnt = 0
    #for w in ont_words:
    #  if w in s_set:
    #    mcnt += 1
    mcnt = len(s_set.intersection(ont_words))
    return float(mcnt)/win_len

  def get_top_words(self, top_words_fname):
    tws = []
    if top_words_fname is not None:
      with open(top_words_fname, "r") as fpi:
        for l in fpi:
          line = l.strip()
          if len(line) > 0:
            tws.append(line)
    return tws
  
    
  def __init__(self, ont_fname, top_words_fname=None, extra_ont=""):
    self.debug = 0
    self.winsize = 5
    self.min_match = 0.0
    self.def_stops = set(stopwords.words('english'))
    #print def_stops
    # Reuse code to read in ontology
    if "eco" in ont_fname:
      self.o_type = "ECO"
    elif "go" in ont_fname:
      self.o_type = "GO"
    elif "so" in ont_fname:
      self.o_type = "SO"
  
    self.top_words = self.get_top_words(top_words_fname)
    print "Top words:", self.top_words
    
    self.ic_data = OboICCalcP.OboICCalcP()
    self.ic_data.set_ont_type(self.o_type)
    self.ic_data.build_ont_tree(ont_fname, self.o_type)
    self.label_no_match = self.ic_data.get_no_match_label()
    self.label_ont_root = self.ic_data.get_ont_root_label()
    self.label_fake_root = self.ic_data.get_annot_root_label()
    print "self.label_fake_root", self.label_fake_root
    
    self.term_id_list = self.ic_data.get_id_list()
    print "Initial term len:", len(self.term_id_list)
    
    self.ont_tuples = self.get_ont_info(self.ic_data, self.label_no_match, self.label_ont_root, self.label_fake_root, self.term_id_list, self.top_words)
    print "Work with", len(self.ont_tuples),"terms in", self.o_type
    
    if self.o_type == "GO":
      if extra_ont == "BP":
        # just get the BioProc ones that are prok
        print "GO: get the BP prok entries"
        self.ont_tuples = self.prune_ont_list(self.ont_tuples, "GO:0008150")
    
      else:
        # get the Molecular Function ones that are prok
        print "GO: get the MF entries"
        self.ont_tuples = self.prune_ont_list(self.ont_tuples, "GO:0003674")
      print "Updated GO, work with", len(self.ont_tuples)
      
    elif self.o_type == "SO":
      #for tl in self.ont_tuples:
        #for wl in tl[1]:
          #print " ".join(wl)
        
      self.ont_tuples = self.prune_ont_list(self.ont_tuples, "SO:0000110")
         
    print "Updated ont, work with", len(self.ont_tuples)  
 
 
  def process_line(self, line, pmid, scnt):
    out_info = (0, self.label_no_match)
    s_output = False
    line = line.strip().lower()
    if line[-1] == '.':
      line = line[:-1]
    if len(line) > 0:
      #print "S:", line
      stokens = self.remove_stops(line.split(" "))
      stlen = len(stokens)
      setwords = set(stokens)
      line_max_score = 0
      line_max_ont_id = self.label_no_match
      line_max_win_set = ""
      line_max_ont_entry = ""
      for ont_tuple in self.ont_tuples:
        #print ont_tuple[0], ont_tuple[1]
        ont_id = ont_tuple[0]
        for ont_entry in ont_tuple[1]: # name and any synonys
          first_word = ont_entry[0]
          if first_word in setwords:
            # Well, something is in the sentence do all the work
            ont_set = set(ont_entry)
            winsize = len(ont_set)
            if winsize >= stlen:
              # Work on whole S
              #print "WHOLE S", ont_set, line
              score = self.score_words(setwords, ont_set)
            else:
              #print "WINDOW!", ont_id, "ont words:", ont_set
              pw = 0
              max_score = 0
              max_win_set = None
              while (pw+winsize)-1<stlen:
                win_set = set(stokens[pw:pw+winsize])
                #print ont_id, "  checking win:", win_set
                score = self.score_words(win_set, ont_set)
                #print "    ", score
                if score > max_score:
                  max_score = score
                  max_win_set = stokens[pw:pw+winsize]
                if score > line_max_score:
                  line_max_score = score
                  line_max_ont_id = ont_id
                  line_max_win_set = max_win_set
                  line_max_ont_entry = ont_entry
                pw+=1
              score = max_score
            if score >= self.min_match:
              if not s_output and self.debug:
                print "\nS:", pmid+"_"+str(scnt), line
                s_output = True
              if self.debug:
                print score, ont_id, "ont:", ont_entry, "win:", max_win_set
      # Output the max for this whole S, which could be 0
      if line_max_score < self.min_match:
        line_max_score = 0
        line_max_ont_id = self.label_no_match
        line_max_win_set = ""
        line_max_ont_entry = ""
      out_info = (line_max_score, line_max_ont_id, line_max_ont_entry, line_max_win_set)
    return out_info
    