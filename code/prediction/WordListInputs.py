import os
import sys
import glob
import datetime

class WordListInputs:

  def read_in_column(self, fname, col, sep):
    in_data = []
    with open(fname, "r") as fpi:
      for l in fpi:
        line = l.strip()
        if len(line) < 1:
          continue
        items = line.split(sep)
        if len(items) > col:
          in_data.append(items[col])
    return in_data
    
  def break_sentence(self, line):
    # Split on spaces
    slist = line.split(" ")
    sset = set(slist)
    return (slist, sset)
  
  def s_contains_p(self, wlist, text_line, text_set):
    found_one = False
    val = None
    for item in wlist:
      #print "item:", item
      # if the item has spaces, just search the text line
      if item.find(" ") > -1:
        if text_line.find(item) > -1:
          found_one = True
          val = item
          break
      else:
        if item in text_set:
          found_one = True
          val = item
          break
    return (found_one, val)
  
  def generate_to_phrases(self, to_items_in):
    tphrases = ['in order to']
    if len(to_items_in):
      to_items = to_items_in
      print "Use to items verbs from file"
    else:
      to_items = ['investigate', 'determine', 'do this', 'identify', 'detect', 'measure', 'visualize', 'confirm', 
       'test', 'ensure', 'validate', 'precisely determine', 'describe', 'statistically describe', 'depict', 'select', 'suggest',
       'pinpoint', 'further validate', 'predict', 'screen', 'map', 'examine', 'verify', 'focus', 'gain', 'demonstrate',
       'assess', 'compare', 'study', 'evaluate', 'understand', 'obtain', 'delineate', 'discount', 'to further assess', 'indicate', 'control', 'prove', 'analyse', 'perform']
    
    for ti in to_items:
      phrase = "to "+ ti
      tphrases.append(phrase)
    ed_items = ['hypothesized', 'predicted', 'tested', 'measured', "attempted to", 'tested', 'examined', 'performed', 'evaluated', 'conducted']
    for ei in ed_items:
      tphrases.append(ei)

    return set(tphrases)
  
  def generate_simple_assertions(self):
    return ['suggest', 'suggests', 'suggested', 'suggesting', 
          'indicate', 'indicates', 'indicated', 'indicating',
          'confirm', 'confirms', 'confirmed', 'confirming']

  def binding_words(self):
    return ['directly binds', 'was able to bind', 'was unable to bind', 'was shown to bind', 'was capable of binding', 'could not bind', 'was capable of binding']
  def generate_more_assertions(self):
    # Not sure about found and shows -- they are used for assertions and
    # for observations
    asserts = self.generate_simple_assertions()
    more = ['demonstrated', 'demonstrates', 'demonstrating',
            'determined',
            'revealed', 'reveals', 'revealing',
            'were able to identify',
            'identified',
            'implied', 'implying', 'implicated',
            'validated', 'validating',
            'detected',
            'were considered as', 'was considered as', 'were considered the',
            'explanation for', 'provided evidence for',
            'negative EMSA result', 'positive EMSA result',
            'consequently', 'on the basis of', 'it is concluded',
            'is thought to', 'was thought that', 'should play',
            'was reported', 'has been reported', 'was therefore deemed'
            ]
    asserts.extend(more)
    asserts.extend(self.binding_words())
    return asserts    
           
  def generate_wrap_phrases(self, nouns_list, verbs_list):
    # This is a little different from the to_phrases
    # Here add any new stuff to the lists already here
    tphrases = ['thus', 'therefore', 'altogether', 'in summary', 'together', 'taken in total', 'this analysis', 'results showed'
    ]
    firstp = ['the', 'this', 'these', 'our']
    firstp2 = ['this', 'these', 'they', 'they also further']
    secondp = ['data', 'findings', 'result', 'results', 'above data', 'results above', 'overall results']
    for n in nouns_list:
      if n not in secondp:
        secondp.append(n)
      if not n[-1] == 's':
        nn = n+"s"
        if nn not in secondp:
          secondp.append(nn)
    #print "wrap up secondp:", secondp
    adverbs = ['also', 'further', 'strongly', 'also strongly', 'clearly', 'additionally']
    verbs = ['suggests', 'supports', 'suggest', 'support',
           'indicated', 'suggested', 'suggested','supported',
           'indicate', 'shows', 'reflects', 'supported',
           'imply', 'implies', 'implied', 'showed', 'show',
           'agrees', 'indicates', 'reveal', 'provide evidence',
           'establish', 'showed', 'demonstrates',
           'demonstrate', 'demonstrated', 'confirm', 'confirmed', 'confirms'
           ]
    # verbs need special attention since datamuse doesn't provide variants
    for v in verbs_list:
      vlist = [v]
      if v[-1] == 'e':
        vlist.append(v+"s")
        vlist.append(v+"d")
      elif v[-1] == 'y':
        vlist.append(v[:-1]+"ies")
        vlist.append(v[:-1]+"ied")
      else:
        vlist.append(v+"s")
        vlist.append(v+"es") # sometimes right, sometimes wrong
        vlist.append(v+"ed")
      for w in vlist:
        if w not in verbs:
          verbs.append(w)
    #print "wrap up verbs:", verbs
    # Loop and get combos. Some will not be grammatical, but OK
    # since we likely won't see them
    for f in firstp:
      for s in secondp:
        for v in verbs:   
          tphrases.append(f+" "+s+" "+v)
          for a in adverbs:
            tphrases.append(f+" "+s+" "+a+" "+v)
    for f in firstp2:
      for v in verbs:
        tphrases.append(f+" "+v)
        for a in adverbs:
          tphrases.append(f+" "+a+" "+v)
    return set(tphrases)
  
  def __init__(self):
    self.debug = 1
  
    self.to_words_in_fname = "to_phrase_verbs_input.txt"
    self.wrapup_nouns_in_fname = "wrapup_nouns_input.txt"
    self.wrapup_verbs_in_fname = "wrapup_verbs_input.txt"
    
    if self.to_words_in_fname is not None:
      to_words_list = self.read_in_column(self.to_words_in_fname, 0, "\t")
    else:
      to_words_list = []
    if self.wrapup_nouns_in_fname is not None:
      wrapup_nouns_list = self.read_in_column(self.wrapup_nouns_in_fname, 0, "\t")
    else:
      wrapup_nouns_list = []
    if self.wrapup_verbs_in_fname is not None:
      wrapup_verbs_list = self.read_in_column(self.wrapup_verbs_in_fname, 0, "\t")
    else:
      wrapup_verbs_list = []      
    self.simple_asserts = self.generate_simple_assertions()
    self.more_asserts = self.generate_more_assertions()
    self.to_phrases = self.generate_to_phrases(to_words_list)
    self.wraps = self.generate_wrap_phrases(wrapup_nouns_list, wrapup_verbs_list)
    self.binding = self.binding_words()

    #print self.simple_asserts
    #print self.more_asserts
    #print self.to_phrases
    #print self.wraps

  def yes_or_no(self, the_words, text_line, text_set, which, pmid, snum):
    (got_one, value) = self.s_contains_p(the_words, text_line, text_set)
    if got_one:
      if self.debug:
        print which, value, pmid, snum
      return "1"
    else:
      return "0"

  def process_line(self, line, pmid, snum):
    sline = line.lower()
    (slist, sset) = self.break_sentence(sline)
    if self.debug:
      print pmid, snum
      print sline
      print sset

    out_items = []

    out_items.append(self.yes_or_no(self.simple_asserts, sline, sset, "SA", pmid, snum))

    out_items.append(self.yes_or_no(self.more_asserts, sline, sset, "MA", pmid, snum))

    out_items.append(self.yes_or_no(self.to_phrases, sline, sset, "TO", pmid, snum))
    
    out_items.append(self.yes_or_no(self.wraps, sline, sset, "WR", pmid, snum))

    out_items.append(self.yes_or_no(self.binding, sline, sset, "BI", pmid, snum))
    
    return out_items
