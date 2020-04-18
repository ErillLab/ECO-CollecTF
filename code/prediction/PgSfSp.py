import os
import sys

# PG, SF, SP, TaxIndicator, TaxEvid 
class PgSfSp:
  def obtain_term_list(self, fname, colnum, sep, skip_first=True, do_lower=False):
    # The file has information in a tabular format
    # sep is the separator
    terms = []
    lcnt = 0
    with open(fname, "r") as fpi:
      for l in fpi:
        lcnt += 1
        if skip_first and lcnt==1:
          continue
        line = l.strip()
        if len(line) < 1:
          continue
        if do_lower:
          line = line.lower()
        items = line.split(sep)
        if len(items) > colnum:
          term = items[colnum].strip()
          if len(term) > 0:
            if not term in terms:
              terms.append(term)
    return terms

  def s_contains_p(self, wlist, text_line, text_set, do_lower=False):
    found_one = False
    val = None
    if do_lower:
      text_line = text_line.lower()
    for item in wlist:
      #print "item:", item
      # if the item has spaces, just search the text line
      if item.find(" ") > -1:
        if text_line.find(item) > -1:
          found_one = True
          val = item
          break
      else:
        if do_lower:
          for ts in text_set:
            if ts.lower() == item:
              found_one = True
              val = item
              break
        else:
          if item in text_set:
            found_one = True
            val = item
            break
    return (found_one, val)

  def __init__(self):    
    self.debug = 0

    self.pg_fname1 = "pg_sf_sp_wordlists.csv"
    self.pg_col = 1
    self.pg_sep = ","

    # Inefficient to reprocess same file, but it's a small file
    self.sf_fname1 = "pg_sf_sp_wordlists.csv"
    self.sf_col = 2
    self.sf_sep = ","

    self.sp_fname1 = "pg_sf_sp_wordlists.csv"
    self.sp_col = 3
    self.sp_sep = ","

    self.pgs = self.obtain_term_list(self.pg_fname1, self.pg_col, self.pg_sep)
    self.pgs.sort(lambda x,y: cmp(len(x.split(" ")), len(y.split(" "))), reverse=True)
    #print self.pgs

    self.sfs = self.obtain_term_list(self.sf_fname1, self.sf_col, self.sf_sep)
    self.sfs.sort(lambda x,y: cmp(len(x.split(" ")), len(y.split(" "))), reverse=True)
    #print self.sfs

    self.sps = self.obtain_term_list(self.sp_fname1, self.sp_col, self.sp_sep)
    self.sps.sort(lambda x,y: cmp(len(x.split(" ")), len(y.split(" "))), reverse=True)
    print self.sps

    self.inds_fname1 = "tax_phylogeny_words.txt"
    self.inds_col = 0
    self.inds_sep = "\t"
    
    self.evids_fname1 = "tax_phylogeny_words.txt"
    self.evids_col = 1
    self.evids_sep = "\t"
    
    self.indicators = self.obtain_term_list(self.inds_fname1, self.inds_col, self.inds_sep, False, True)
    self.indicators.sort(lambda x,y: cmp(len(x.split(" ")), len(y.split(" "))), reverse=True)
    print self.indicators
    
    self.evids = self.obtain_term_list(self.evids_fname1, self.evids_col, self.evids_sep, False, True)
    self.evids.sort(lambda x,y: cmp(len(x.split(" ")), len(y.split(" "))), reverse=True)
    print self.evids
    
    
  def break_sentence(self, line):
    # Split on spaces
    slist = line.split(" ")
    sset = set(slist)
    return (slist, sset)
   
  def process_line(self, sline, pmid, snum):
    (slist, sset) = self.break_sentence(sline)
    if self.debug:
      print pmid, snum
      print sline
      print sset
    out_items = []
    (got_one, value) = self.s_contains_p(self.pgs, sline, sset)
    if got_one:
      out_items.append("1")
      if self.debug:
        print "PG:", value, pmid, snum
    else:
      out_items.append("0")
    (got_one, value) = self.s_contains_p(self.sfs, sline, sset)
    if got_one:
      out_items.append("1")
      if self.debug:
        print "SF:", value, pmid, snum
    else:
      out_items.append("0")
    (got_one, value) = self.s_contains_p(self.sps, sline, sset)
    if got_one:
      out_items.append("1")
      if self.debug:
        print "SP:", value, pmid, snum
    else:
      out_items.append("0")
      
    (got_one, value) = self.s_contains_p(self.indicators, sline, sset, True)
    if got_one:
      out_items.append("1")
      if self.debug:
        print "TaxI:", value, pmid, snum
    else:
      out_items.append("0")
    (got_one, value) = self.s_contains_p(self.evids, sline, sset, True)
    if got_one:
      out_items.append("1")
      if self.debug:
        print "TaxE:", value, pmid, snum
    else:
      out_items.append("0")
      
    return out_items
    