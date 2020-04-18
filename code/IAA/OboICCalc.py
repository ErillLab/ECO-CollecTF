import sys
import os
import copy
import math
import OntTerm
import numpy as np
np.seterr(all='raise')

class OboICCalc:
  # Errors in ECO -- we need to ignore these terms
  remove_ids = ["ECO:0000203", "ECO:0000217", "ECO:0001828", "ECO:0005611", "ECO:0005612", "ECO:0005613"]
  eco_root_id = "ECO:0000000"
  annot_root_id = "ECO:9999998"
  rest_ow_id = "ECO:9999999"
  rz_root_id = "RZ:EAssertionRoot"
  rz_annot_root_id = "RZ:9999998"
  rz_rest_ow_id = "RZ:9999999"
  
  # Fields we care about
  fields = ["is_a", "id", "name", "def", "synonym", "namespace", "subset", "is_obsolete"]
  # Fields we know we don't care about. The reason for this list is to make sure we are 
  # accounting for all fields in an entry. At some point, the ontology may add a new field,
  # and if we re-run this parse with the new file, this field will be output because
  # it is neither a field we want nor a field to ignore.
  ignore = ["consider", "xref", "disjoint_from", "intersection_of", "relationship", \
          "creation_date", "created_by", "comment", "alt_id", "replaced_by", "is_transitive", \
          "transitive_over", "holds_over_chain", "inverse_of", "property_value", "expand_assertion_to", \
          "is_class_level", "is_metadata_tag", "union_of"]

  def __init__(self):
    self.in_order = [] # Record the ONT IDs as we see them in .obo
    self.ont_terms = {} # The data structure containing the hierarchy. Key is ONT ID.
              # The value is the ont_term class, with children in a list and parents in a list.
    # Because the ont terms can be in any order, save P-C info until P is processed
    self.children = {}
    self.ont_type = "ECO"
    self.the_ont_root_id = OboICCalc.eco_root_id # ECO:0000000
    self.the_ont_annot_root_id = OboICCalc.annot_root_id # ECO:9999998
    self.the_ont_rest_ow_id = OboICCalc.rest_ow_id # ECO:9999999
    

  def set_ont_type(self, otype):
    self.ont_type = otype
    print "setting ontology to", otype
    if otype=="RZ":
      self.the_ont_root_id = OboICCalc.rz_root_id # RZ:0000005
      self.the_ont_annot_root_id = OboICCalc.rz_annot_root_id # RZ:9999998
      self.the_ont_rest_ow_id = OboICCalc.rz_rest_ow_id # RZ:0000000
    elif otype=="GO":
      self.the_ont_root_id = "GO:0000001"
      self.the_ont_annot_root_id = "GO:9999998"
      self.the_ont_rest_ow_id = "GO:9999999"
    elif otype=="SO":
      self.the_ont_root_id = "SO:0000001"
      self.the_ont_annot_root_id = "SO:9999998"
      self.the_ont_rest_ow_id = "SO:9999999"
    self.annot_root_id = self.the_ont_annot_root_id
    print self.the_ont_root_id
    
  def get_id_list(self):
    return self.in_order
    
  def get_ont_tree(self):
    return self.ont_terms
    
  def get_no_match_label(self):
    return self.the_ont_rest_ow_id #OboICCalc.rest_ow_id
    
  def get_ont_root_label(self):
    return self.the_ont_root_id #OboICCalc.eco_root_id
    
  def get_ont_root_pos(self):
    return self.in_order.index(self.the_ont_root_id) #(OboICCalc.eco_root_id)
    
  def get_annot_root_label(self):
    return self.annot_root_id
    
  def get_node(self, term):
    if term in self.ont_terms:
      return self.ont_terms[term]
    else:
      return None
    
    
  def get_siblings(self, node):
    sibs = []
    for p in node.parents:
      for c in self.ont_terms[p].children:
        #print node.id,"sib",c,"from parent",p
        if not c in sibs and not c==node.id:
          sibs.append(c)
    return sibs
    
  # Routine that gets all descendants of a node
  def get_descendants(self, node):
    # Descend iteratively
    #print "Node:", node.name
    descs = []
    nodes_to_visit = copy.copy(node.children)
    vlen = len(nodes_to_visit)
    #print "  Vlen:", vlen
    while vlen > 0:
      curnode = nodes_to_visit.pop(0)
      if (not curnode in descs):
        descs.append(curnode)
        #print "appending curnode:", curnode.name
        if len(self.ont_terms[curnode].children) > 0:
          nodes_to_visit.extend(self.ont_terms[curnode].children)
      vlen = len(nodes_to_visit)
    return descs

  def get_children(self, node):
    return node.children
    
  # Routine that gets all ancestors of a node
  def get_ancestors(self, node):
   # ascend iteratively
    #print "Ascend Node:", node.id
    ancs = []
    nodes_to_visit = copy.copy(node.parents)
    vlen = len(nodes_to_visit)
    #print "  Vlen:", vlen
    while vlen > 0:
      curnode = nodes_to_visit.pop(0)
      #print "checking node:", curnode
      if (not curnode in ancs):
        ancs.append(curnode)
        if len(self.ont_terms[curnode].parents) > 0:
          nodes_to_visit.extend(self.ont_terms[curnode].parents)
      vlen = len(nodes_to_visit)
    return ancs
  
  def am_i_a_leaf(self, node_id):
    curnode = self.ont_terms[node_id]
    if len(curnode.children) > 0:
      return False
    else:
      return True

  def am_i_a_one_up_node_any(self, node_id):
    # If any child is itself a leaf node, then yes
    res = False
    for c in self.ont_terms[node_id].children:
      if self.am_i_a_leaf(c):
        res = True
        break
    return res
      
  def am_i_a_one_up_node(self, node_id):
    # If each of the children is a leaf node, then yes
    if len(self.ont_terms[node_id].children) > 0:
      res = True
      for c in self.ont_terms[node_id].children:
        if not self.am_i_a_leaf(c):
          res = False
          break
    else:
      res = False
    return res
    
  # Routine to find best IC parent
  def find_best_parent_ic(self, term1, term2):
    res = 0.0
    #print "\nFind best for", term1, term2
    if term1 == term2:
      # return the IC of the term itself
      #print "both terms same"
      res = self.ont_terms[term1].IC
    else:
      if (term1 not in self.ont_terms) or (term2 not in self.ont_terms):
        print "WARNING: a term not in ontology:", term1, term2
        res = self.ont_terms[self.the_ont_root_id].IC
      else:
        #print "different terms"
        ont_term1 = self.ont_terms[term1]
        ont_term2 = self.ont_terms[term2]
        IC1 = ont_term1.IC
        IC2 = ont_term2.IC
        ancestors1 = self.get_ancestors(ont_term1)
        ancestors2 = self.get_ancestors(ont_term2)
        #print "IC calc A1:", ancestors1
        #print "IC calc A2:", ancestors2
        # First check if one of the terms is an ancestor of the other
        if term1 in ancestors2:
          #print term1,"is in ancestors2:", ancestors2
          res = IC1
        elif term2 in ancestors1:
          #print term2,"is in ancestors1:", ancestors1
          res = IC2
        else:
          #print "terms are not in each others ancestors"
          set1 = set(ancestors1)
          set2 = set(ancestors2)
          common = set.intersection(set1, set2)
          #print "Common:", common
          # See what the best IC is
          best_IC = -1.0
          best_id = ""
          for c_id in common:
            c_IC = self.ont_terms[c_id].IC
            #print "  ",c_id, c_IC
            if c_IC > best_IC:
              best_IC = c_IC
              best_id = c_id
          #print "best term:", best_id, best_IC
          res = best_IC
    return res
  
  
  # The code that handles the parsing and building the node tree.
  def build_ont_tree(self, fname, obo_type):
    print "obo_type:", obo_type
    print "self.the_ont_root_id:", self.the_ont_root_id
    # First create the new root and the "ROW" node
    the_term = OntTerm.OntTerm()
    the_term.synonym=''
    the_term.definition=''
    the_term.parents = []
    the_term.children = []
    the_term.prok = False
    the_term.id = self.the_ont_annot_root_id # Fake root
    the_term.name = "annotation root"
    self.in_order.append(the_term.id)

    row_term = OntTerm.OntTerm()
    row_term.synonym=''
    row_term.definition=''
    row_term.parents = []
    row_term.children = []
    row_term.prok = False
    row_term.id = self.the_ont_rest_ow_id
    row_term.name = "rest of world"
    self.in_order.append(row_term.id)

    the_term.children.append(self.the_ont_root_id) #(OboICCalc.eco_root_id)
    the_term.children.append(row_term.id)

    print "Building... fake root:", the_term.id, the_term.name, the_term.children
    print "ROW node:", row_term.id, row_term.name
    
    row_term.parents.append(the_term.id)

    self.ont_terms[the_term.id] = the_term
    self.ont_terms[row_term.id] = row_term

    # Read in the obo file and construct the rest of the tree
    num_skipped = 0
    save_term = False
    print "FNAME:", fname
    with open(fname, "r") as infile:
      in_term = False
      in_typedef = False

      for l in infile:
        line = l.strip()
        if len(line) < 1:
          continue
        if line.find("[Term]") > -1:
          # We are now in some .obo text that defines an entry.
          #print "In a term", line
          # Did we just process an entry to save?
          if save_term:
            # Code to update the data structure containing the hierarchy
            #print "Obsolete?", the_term.is_obs
            if not (the_term.is_obs or the_term.namespace=="cellular_component"):
              #print "  Save this", the_term.id
              if the_term.id in self.ont_terms:
                print "ERROR: repeated ontology id:", the_term.id
                sys.exit(0)

              # Since this is a legit entry, update parents to have this entry as a child.
              # We may or may not have seen the parent entry yet in go.obo.
              # If we have not, put the information in the children dictionary for later recovery.
              for p in the_term.parents:
                if not p in self.ont_terms:
                  # We haven't seen this entry yet, so save info temporarily
                  #print "     TheParents: (Temp save parent", p, " --> C:", the_term.id, ")"
                  if not p in self.children:
                    self.children[p] = [the_term.id]
                  else:
                    self.children[p].append(the_term.id)
                else:
                  # We have already processed this parent entry's obo, add the child.
                  #print "     TheParents: Update", p, "to have child", the_term.id 
                  self.ont_terms[p].children.append(the_term.id)

              # Does this entry have some children already saved?
              #print "    Children?"
              if the_term.id in self.children:
                for c in self.children[the_term.id]:
                  the_term.children.append(c)
                  #print "      Child:", c
          
              # Save the entry    
              self.ont_terms[the_term.id] = the_term
              #print "ONT TERMS:", self.ont_terms

              # And keep track of which ONT IDs we processed
              self.in_order.append(the_term.id)
            else:
              num_skipped+=1 # Either obsolete or a cellular compartment
      
          # Get ready to process this ONT entry      
          save_term = False
          the_term = OntTerm.OntTerm()
          the_term.synonym=''
          the_term.definition=''
          the_term.parents = []
          the_term.children = []
          the_term.prok = False
          def_count = 0
          in_term = True # This tells us to process upcoming lines for this entry
          in_typedef = False
          #print "Term!"
          # We'll pick up its info when we process the upcoming lines in .obo.
          continue
      
        elif line.find("[Typedef]") > -1:
          # We're not doing anything with this
          in_typedef = True
          in_term = False
          continue
      
        if in_term:
          # We're building up the ONT entry. 
          #items = line.split(": ") # don't do this.
          cpos = line.find(": ")
          if cpos < -1:
            print "ERROR: line"
            sys.exit(0)
      
          field_name = line[:cpos]
      
          if field_name in OboICCalc.fields:
            # Handle fields we care about
            val = line[cpos+1:].strip()
            if field_name == "id":
              if val not in OboICCalc.remove_ids:
                the_term.id = val
                #print "ONT ID:", val
                if val.find(obo_type) > -1:
                  save_term = True # We've seen the ID, so we'll want to save this (probably)
                  the_term.namespace = "eco"
                #else:
                  #print "  id not a", obo_type
            elif field_name == "name":
              the_term.name = val
              if val.find("manual assertion") > -1 or val.find("automatic assertion") > -1:
                save_term = False
            elif field_name == "def":
              if len(the_term.definition) < 1:
                the_term.definition = val
              else:
                the_term.definition = the_term.definition + "~~ "+val
            elif field_name == "synonym":
              # Only want EXACT
              epos = line.find("EXACT")
              if epos < 0:
                continue
              if len(the_term.synonym) < 1:
                the_term.synonym = val
              else:
                the_term.synonym = the_term.synonym + "~~ " + val # concatenate synonym fields
            elif field_name == "is_obsolete":
              #print "Obs?", field_name, val
              the_term.is_obs = val
            elif field_name == "namespace":
              the_term.namespace = val
            elif field_name == "subset":
              #print "Value: ", val
              if val == "gosubset_prok":
                the_term.prok = True
                #print field_name, val
            elif field_name == "is_a":
              parent_ont_id_str = val.split("!")[0]
              bpos = parent_ont_id_str.find("{")
              if bpos > -1:
                parent_ont_id_str = parent_ont_id_str[:bpos]
              parent_ont_id = parent_ont_id_str.strip()
              if parent_ont_id.find(obo_type) > -1:
                if not parent_ont_id in the_term.parents: # test just in case a duplicate
                  the_term.parents.append(parent_ont_id)
                  #print "IS_A", parent_ont_id
          
          elif field_name in OboICCalc.ignore:
            i=1 # ignore
          else:
            print "CHECK FIELD: ", field_name
        
        elif in_typedef: # Not using, skip
          #print "TD:", line
          i=1

    print "Num entries skipped:", num_skipped
    print "Total num terms kept in hierarchy:", len(self.in_order)

    # Add annot root node as parent of ECO's root (or other ontology root)
    the_ont = self.ont_terms[self.the_ont_root_id]
    the_ont.parents.append(self.the_ont_annot_root_id)
    #the_ont = self.ont_terms[OboICCalc.eco_root_id]
    #the_ont.parents.append(OboICCalc.annot_root_id)

      
    num_nodes = len(self.in_order) 
    IC_denom = math.log((1.0/float(num_nodes)), 2) # log2(1/total_nodes)
    
    for ont_id in self.in_order:
      #print "\nProcess", ont_id
      the_ont = self.ont_terms[ont_id]
      #print "  Name:", the_ont.name
      #if len(the_ont.parents)<1:  
        #print "    No parents"
      #print "  Parents:", the_ont.parents
      #print "  Children:", the_ont.children
      all_desc = self.get_descendants(the_ont)
      num_d = len(all_desc)
      #print "  Num descendants:", num_d
      the_ont.num_desc = num_d
      val = float(num_d + 1)/float(num_nodes)
      IC_numer = math.log(val, 2)
      the_ont.IC = IC_numer / IC_denom
      if the_ont.id == self.the_ont_annot_root_id: #OboICCalc.annot_root_id or the_ont.id==OboICCalc.rz_annot_root_id:
        the_ont.IC = 0.0 # for some reason getting -0.0

      #if ont_id == "ECO:0000000":
        #for oid in in_order:
          #if oid not in all_desc:
            #print "ECO:0000000 not ancestor of:", oid
        #sys.exit(0)
        
    print "Total num terms kept in hierarchy:", len(self.in_order)
    print "self.the_ont_annot_root_id:", self.the_ont_annot_root_id
    
  def updateNoNodeIC(self, use_id_ic):
    the_ont_ic = self.ont_terms[use_id_ic].IC
    self.ont_terms[self.get_no_match_label()].IC = the_ont_ic
    
  def updateNoNodeICVal(self, use_ic_val):
    self.ont_terms[self.get_no_match_label()].IC = use_ic_val
    
  def getICForNode(self, the_id):
    if the_id in self.ont_terms:
      return self.ont_terms[the_id].IC
    else:
      return None
      
  def calculate_Ae(self, A_id_use_info, B_id_use_info, num_samples):
    # Create the prob distribs based on usage
    num_ids = len(self.in_order)
    Aj = np.zeros(shape=(num_ids))
    A_total = 0
    for t in A_id_use_info:
      i = self.in_order.index(t)
      Aj[i] += A_id_use_info[t]
      if Aj[i] > 0:
        print "A: ",t,i,Aj[i]
      A_total += A_id_use_info[t]
    print "A total:", A_total
    Aj = Aj / float(A_total) 
    
    Bj = np.zeros(shape=(num_ids))
    B_total = 0
    for t in B_id_use_info:
      i = self.in_order.index(t)
      Bj[i] += B_id_use_info[t]
      if Bj[i] > 0:
        print "B: ",t,i,Bj[i]
      B_total += B_id_use_info[t]
    print "B total:", B_total
    Bj = Bj / float(B_total)
    
    total_ic = 0.0
    total_non_no_pairs = 0
    total_no_no_pairs = 0
    total_one_no_pairs = 0
    for i in range(num_samples):
      A_term_pos = np.random.choice(np.arange(num_ids), p=Aj)
      B_term_pos = np.random.choice(np.arange(num_ids), p=Bj)
      A_term = self.in_order[A_term_pos]
      B_term = self.in_order[B_term_pos]
      the_ic = self.find_best_parent_ic(A_term, B_term)
      #if i < 100:
      #  print "Pair for Ae calc: i:", i, A_term, B_term, the_ic
      if not (A_term==self.the_ont_rest_ow_id or B_term==self.the_ont_rest_ow_id):
        total_non_no_pairs += 1
      elif (A_term==self.the_ont_rest_ow_id and B_term==self.the_ont_rest_ow_id):
        total_no_no_pairs += 1
      elif (A_term==self.the_ont_rest_ow_id or B_term==self.the_ont_rest_ow_id):
        total_one_no_pairs += 1
      total_ic += the_ic
    total_ic = total_ic / float(num_samples)
    perc = float(total_non_no_pairs)/float(num_samples)
    print "Ae: ", total_ic 
    print "# non-no-used pairs:", total_non_no_pairs, "% non-no-used:",perc
    perc = float(total_no_no_pairs)/float(num_samples)
    print "# no-no-used pairs:", total_no_no_pairs, "% no-no-used:",perc
    perc = float(total_one_no_pairs)/float(num_samples)
    print "# something-no-used pairs:", total_one_no_pairs, "% one-no-used:",perc
    return total_ic # This avg is the Ae
    
  def calculate_Ae_v2(self, the_arr, N, num_samples):
    As = the_arr.sum(axis=1)
    print "row sum:",As[0:20]
    the_arr = the_arr/float(N)
    Aj = the_arr.sum(axis=1)
    Bj = the_arr.sum(axis=0)
    for i in range(20):
      print "V2 Ae Aj:", Aj[i], self.in_order[i]
      print "V2 Ae Bj:", Bj[i], self.in_order[i]
    num_ids = len(Aj)
    total_ic = 0.0
    total_non_no_pairs = 0
    total_no_no_pairs = 0
    total_one_no_pairs = 0
    for i in range(num_samples):
      A_term_pos = np.random.choice(np.arange(num_ids), p=Aj)
      B_term_pos = np.random.choice(np.arange(num_ids), p=Bj)
      A_term = self.in_order[A_term_pos]
      B_term = self.in_order[B_term_pos]
      the_ic = self.find_best_parent_ic(A_term, B_term)
      #if i < 100:
      #  print "V2 Pair for Ae calc: i:", i, A_term, B_term, the_ic
      if not (A_term==self.the_ont_rest_ow_id or B_term==self.the_ont_rest_ow_id):
        total_non_no_pairs += 1
      elif (A_term==self.the_ont_rest_ow_id and B_term==self.the_ont_rest_ow_id):
        total_no_no_pairs += 1
      elif (A_term==self.the_ont_rest_ow_id or B_term==self.the_ont_rest_ow_id):
        total_one_no_pairs += 1
      total_ic += the_ic
    total_ic = total_ic / float(num_samples)
    perc = float(total_non_no_pairs)/float(num_samples)
    print "V2 Ae: ", total_ic 
    print "V2# non-no-used pairs:", total_non_no_pairs, "% non-no-used:",perc
    perc = float(total_no_no_pairs)/float(num_samples)
    print "V2# no-no-used pairs:", total_no_no_pairs, "% no-no-used:",perc
    perc = float(total_one_no_pairs)/float(num_samples)
    print "V2# something-no-used pairs:", total_one_no_pairs, "% one-no-used:",perc
    return total_ic # This avg is the Ae
    
  def extra_node(self, t):
    if t==self.annot_root_id or t==self.rest_ow_id:
      return True
    else:
      return False
      
  def get_nodes_n_hops_away(self, term, want_num_hops):
    if want_num_hops < 1:
      return [term]

    keep = []
    seen = [term]
    #print "TERM", term, want_num_hops
    check_list = copy.copy(self.ont_terms[term].parents)
    check_list.extend(self.ont_terms[term].children)
    if want_num_hops == 1:
      #print "RETURNING:",check_list
      return check_list
    
    #print "Term has these parents and children:"
    #print check_list
    #print "\n"
    i = 2
    while True:
      new_list = []
      #print "HOP:", i
      for t in check_list:
        #print "Checking t", t
        if t not in seen and not self.extra_node(t):
          #print "  not seen"
          seen.append(t)
          parent_list = self.ont_terms[t].parents
          child_list = self.ont_terms[t].children
          for p in parent_list:
            #print "  has p:", p
            if p not in seen and p not in new_list and p not in check_list and not self.extra_node(p):
              #print "    added to new list"
              new_list.append(p)

          for c in child_list:
            #print "  has c:", c
            if c not in seen and c not in new_list and c not in check_list and not self.extra_node(c):
              #print "    added to new list"
              new_list.append(c)

          
      if i==want_num_hops:
        #print "Done num hops"
        keep = new_list
        break
      if len(new_list) < 1:
        #print "Done, no new nodes"
        keep = new_list
        break
      i+=1
      check_list = copy.copy(new_list)
    return keep

  
  def test_some_nodes(self):
    id=OboICCalc.annot_root_id
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id=OboICCalc.eco_root_id
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id="ECO:0000001"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id="ECO:0000006"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id="ECO:0000008"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id="ECO:0000009"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id="ECO:0000010"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "ECO:0005605"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "ECO:0005554"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "ECO:0005555"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "ECO:0000096"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = OboICCalc.rest_ow_id
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC

    term1 = "ECO:0000008"
    term2 = "ECO:0000008"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic

    term1 = "ECO:0000008"
    term2 = "ECO:0000009"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic

    term1 = "ECO:0000008"
    term2 = "ECO:0000010"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic

    term1 = "ECO:0000003"
    term2 = "ECO:0000010"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic

    term1 = "ECO:0005554"
    term2 = "ECO:0005555"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic

    term1 = "ECO:0000201"
    term2 = "ECO:0005555"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic

    term1 = "ECO:0000008"
    term2 = "ECO:0000096"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic
    
    term1 = "ECO:0000008"
    term2 = "ECO:0005554"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic
    
    term1 = "ECO:0000008"
    term2 = "ECO:0005555"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic
    
    term1 = "ECO:0000096"
    term2 = "ECO:0005554"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic
    
    term1 = "ECO:0000096"
    term2 = "ECO:0005555"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic
    
    term1 = "ECO:0000008"
    term2 = OboICCalc.rest_ow_id
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic

  def test_some_rz_nodes(self):
    id=self.the_ont_annot_root_id
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id=self.the_ont_root_id
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = self.the_ont_rest_ow_id
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "RZ:E0"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "RZ:EA"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "RZ:EP"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "RZ:E1"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "RZ:E2"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    id = "RZ:E3"
    print id, self.ont_terms[id].num_desc, self.ont_terms[id].IC
    
    term1 = "RZ:E2"
    term2 = "RZ:E3"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic

    term1 = "RZ:E1"
    term2 = "RZ:E3"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic
    
    term1 = "RZ:E1"
    term2 = "RZ:E0"
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic
    
    term1 = "RZ:E1"
    term2 = self.the_ont_rest_ow_id
    best_parent_ic = self.find_best_parent_ic(term1, term2)
    print term1, term2, best_parent_ic