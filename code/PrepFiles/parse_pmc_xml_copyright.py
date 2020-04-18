import os
import sys

from xml.etree.ElementTree import parse;
import xml.etree.ElementTree

def rem_tags(stext):
  # Not the best but the XML is stupid with all its italics and other tags in the title
  ntext = ""
  in_tag = False
  for p in range(len(stext)):
    char = stext[p]
    if char=="<":
      in_tag = True
    if not in_tag:
      ntext += char
    if char=='>':
      in_tag = False
  return ntext
  
  
fname = sys.argv[1]
outdir = sys.argv[2]

if not os.path.exists(outdir):
  os.mkdir(outdir)

  
base_name = os.path.basename(fname)
base_root = os.path.splitext(base_name)[0]
pmid = base_root.split("_")[1]
out_fname = os.path.join(outdir, pmid+".copyright")

doc_authors = []
journal_title = ""
publisher_name = ""
pub_year = ""
volume = ""
issue = ""
temp_year = ""
copyright_statement = ""
copyright_year = ""
copyright_holder =""
article_title = ""

tree = parse(fname)
in_methods = False
for node in tree.getiterator():
  for elem in node.findall('front/article-meta/contrib-group/contrib'):
    ctype = elem.get('contrib-type')
    if ctype == 'author':
      surname = ""
      for sn in elem.findall('name/surname'):
        if sn.text:
          surname += " "+sn.text.encode('utf-8')
      gvnames = ""
      for gn in elem.findall('name/given-names'):
        if gn.text:
          gvnames += " "+gn.text.encode('utf-8')
      
      doc_authors.append(surname.strip()+','+gvnames.strip())
  for elem in node.findall('pub-date/year'):
    ctype = elem.get('pub-type')
    if ctype == 'collection':
      pub_year = elem.text
    temp_year = elem.text
  for elem in node.findall('journal-title'):
    journal_title = elem.text.encode('utf-8')
    
  for elem in node.findall('volume'):
    volume = elem.text.encode('utf-8')
  for elem in node.findall('issue'):
    issue = elem.text.encode('utf-8')
    
  try:
    for elem in node.findall('copyright-statement'):
      # some are empty
      copyright_statement = elem.text.encode('utf-8')
  except:
    pass
  for elem in node.findall('copyright-year'):
    copyright_year = elem.text.encode('utf-8')
  for elem in node.findall('copyright-holder'):
    copyright_holder = elem.text.encode('utf-8')
    
if len(pub_year) < 1:
  pub_year = temp_year

vol_issue = volume
if len(issue) > 1:
  vol_issue += "("+issue+")"
if len(vol_issue) > 1:
  vol_issue+= '. '
  
# Easier to get article title like this rather than dig through the nested children
with open(fname, 'r') as fpi:
  content = fpi.read()
abeg = content.find('<article-title>')
alen = len('<article-title>')
aend = content.find('</article-title>')
article_title = rem_tags(content[abeg+alen:aend])
# Note many articles have a copyright year and holder but no statement.
if len(copyright_statement) < 1:
  copyright_statement = "Copyright"
if len(doc_authors) < 1 or len(journal_title)<1 or len(article_title) < 1:
  print "ERROR", pmid
  print "Authors:", doc_authors
  print "title:", article_title
  print "journal:", journal_title
  print "vol:", volume
  print "issue:", issue
  print "(C):", copyright_statement

else:
  with open(out_fname, "w") as fpo:
    fpo.write("PubMed ID: %s\n" % pmid)
    url = "https://pubmed.ncbi.nlm.nih.gov/"+pmid
    fpo.write("%s\n\n" % url)
  
    out_str = ", ".join(doc_authors)+", "+ article_title+". "+journal_title+". "+ vol_issue+ pub_year
    fpo.write("%s\n\n" % out_str)
    if "Copyright" not in copyright_statement:
      copyright_statement = "Copyright "+copyright_statement
    fpo.write("%s\n" % copyright_statement)
    if len(copyright_year) > 1:
      fpo.write("Year: %s\n" % copyright_year)
    if len(copyright_holder) > 1:
      copyright_holder = "Copyright holder: "+copyright_holder
      fpo.write("%s\n" % copyright_holder)
