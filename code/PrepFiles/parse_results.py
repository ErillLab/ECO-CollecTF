import os
import sys
import argparse
import re

from xml.etree.ElementTree import parse;
import xml.etree.ElementTree

# since nested, need to gather all the text down the tree
def process_xml(from_node, depth, para_text, fpo):
  #print "process_xml at level:", depth, from_node.tag
  if from_node.tag=="fig" or from_node.tag=="table-wrap":
    return ""
    
  #print "  Curr paragraph text:", para_text
  if from_node.text:
    #print "from_node text:", from_node.text.encode('utf-8')
    text = from_node.text.encode('utf-8')
    if len(text.strip()) > 0:
      para_text += text #from_node.text.encode('utf-8')
    #else:
    #  print "from_node text all blanks"
    
  for item in from_node:
    text = process_xml(item, depth+1, "", fpo)
    if len(text.strip()) > 0:
      para_text += text
      
  if from_node.tail:
    #print "from_node tail at level:", depth, from_node.tag, from_node.tail.encode('utf-8')
    text = from_node.tail.encode('utf-8')
    if len(text.strip()) > 0:
      para_text += text #from_node.tail.encode('utf-8')
    #else:
    #  print "from_node tail all blanks"
      
  if from_node.tag=="p" or from_node.tag=="title" or (depth > 0 and from_node.tag=="sec"):
    #print "PARAGRAPH:", para_text
    if from_node.tag=="title":
      if html:
        para_text = "<b>"+para_text+"</b>"
      #else:
      #  para_text += "\n"
    if len(para_text):
      #fpo.write("%s\n" % para_text.replace("\n\n", "\n"))
      if html:
        para_text += "<p>\n"
      else:
        para_text += "\n\n"

    #para_text = ""
     
  return para_text  
  
def check_children(the_elem):
  in_results = False
  for cnode in the_elem:
    if cnode.text:
      title = cnode.text.encode('utf-8')
      ltitle = title.lower()
      #print "ltitle:", ltitle
      if len(ltitle) < 75:
        r1pos = ltitle.find("results")
        r2pos = ltitle.find("results and discussion")
        r3pos = ltitle.find("results/discussion")

        #print "pos:", r1pos, r2pos, r3pos
        if r1pos > -1 or r2pos > -1 or r3pos > -1 :
          in_results = True
          break
  return in_results
  
  
parser = argparse.ArgumentParser(description="parse xml file")
parser.add_argument('fname', help="Full path to file")
parser.add_argument('outdir', help="Output dir")
parser.add_argument('-m', '--ml', nargs='?', help="m=html, t=txt", default="-t")
args = parser.parse_args()

fname = args.fname
outdir = args.outdir
html = False

if args.ml == "m":
  html = True
  
if not os.path.exists(outdir):
  os.mkdir(outdir)

doc_outdir = os.path.join(outdir, "results")
if not os.path.exists(doc_outdir):
  os.mkdir(doc_outdir)
  
base_name = os.path.basename(fname)
base_root = os.path.splitext(base_name)[0]
pmid = base_root.split("_")[1]

ofile = "results_"+pmid
if html:
  ofile += ".html"
else:
  ofile += ".txt"
print "Ofile:", ofile


results_fname = os.path.join(doc_outdir, ofile)
fpo = open(results_fname, "w")

tree = parse(fname)
in_results = False
for node in tree.getiterator():
  for elem in node.findall('body/sec'):
    #print elem
    if in_results:
      in_results = False
      break

#    try:
    stype = elem.get('sec-type')
    if stype:
      #print "stype:", stype
      #if stype == "methods" or stype == "materials|methods" or stype == "materials and methods":
      #  in_results = True #methods_s = process_method_xml(elem)
      #else:
      #print "check children:"
      in_results = check_children(elem)
      #print "stype in_results?", in_results, elem.tag

    else:
      #print "check children, no stype"
      in_results = check_children(elem)

    if in_results:    
      top_level_text = process_xml(elem, 0, "", fpo)
      #print "TOP LEVEL TEXT:", top_level_text
      if html:
        fpo.write("<html><head><title>"+pmid+"</title></head><body><p>\n")
    
      # Don't do the split trick to remove multiple spaces here because it also removes newlines
      text_out = top_level_text.replace("&#xA0;", " ")
      
      fpo.write("%s\n" % re.sub(' +',' ',text_out))
      if html:
        fpo.write("</body></html>")
      
fpo.close()

