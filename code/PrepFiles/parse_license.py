import os
import sys
import argparse
  
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

doc_outdir = os.path.join(outdir, "licenses")
if not os.path.exists(doc_outdir):
  os.mkdir(doc_outdir)
  
base_name = os.path.basename(fname)
base_root = os.path.splitext(base_name)[0]
pmid = base_root.split("_")[1]

ofile = "license_"+pmid
if html:
  ofile += ".html"
else:
  ofile += ".txt"
print "Ofile:", ofile


license_fname = os.path.join(doc_outdir, ofile)

our_text = """This is a derivative work of PMID.
The ECO-CollecTF dataset has pulled out the Results (or Results and Discussion) section 
and stored this section in a separate text file, TEXT_FILE,
with individual sentences on separate lines. 
The license of the original work applies to the TEXT_FILE.

In addition, ECO-CollecTF includes curator generated annotations for this section. 
These changes do not suggest the licensor endorses this usage. 
------
The original license has been extracted from the PUBMED_XML,
and is shown below for convenience. 
Refer to the original PUBMED_XML, supplied in the accompanying  
XML directory, for the license, copyright notice, authors, and title."""
our_text = our_text.replace("PMID", "PubMed PMID:"+pmid)
our_text = our_text.replace("PUBMED_XML", "PubMed/PMC XML file, pubmed_"+pmid+".xml")
our_text = our_text.replace("TEXT_FILE", "results_"+pmid+".txt")
with open(fname, 'r') as fpi:
  content = fpi.read()
  
lbeg = content.find("<license")
if lbeg < 0:
  lbeg = content.find("<p>Re-use of this article is permitted in accordance with")
  if lbeg < 0:
    lbeg = content.find("<copyright-statement>")
    if lbeg < 0:
      print "ERROR: no license found", fname
      sys.exit(0)
    else:
      lend_tag = "</copyright-statement>"
  else:
    lend_tag = "</p>"
else:
  lend_tag = "</license>"
  
lend = content.find(lend_tag, lbeg)
if lend > lbeg:
  ltext = content[lbeg:lend+len(lend_tag)]
  fpo = open(license_fname, "w")   
  fpo.write("%s\n" % our_text)
  fpo.write("------------------------------\n")
  fpo.write("License for PMID:"+pmid+"\n")
  fpo.write("%s\n" % ltext)
  fpo.close()

else:
  print "ERROR: No end of license found", fname, content[lbeg:lbeg+30], lend_tag


