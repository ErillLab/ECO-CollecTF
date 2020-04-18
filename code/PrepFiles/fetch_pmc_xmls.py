import socket
import urllib2
import base64
import sys
import os
import time

timeout=30
socket.setdefaulttimeout(timeout)

header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)'}

replacer = "ZZZZZZZ"
url_root = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id="+replacer+"&rettype=xml"

def perform_request(the_url):
  the_str = ""
  try:
    ureq = urllib2.Request(the_url, headers=header)
    uresponse = urllib2.urlopen(ureq)
    the_str = uresponse.read()
  except:
    print "Error: ", sys.exc_info()[1]
  finally:
    return the_str

fname = sys.argv[1]
new_dir = sys.argv[2]

if not os.path.exists(new_dir):
  os.mkdir(new_dir)
  
with open(fname, "r") as myfile:
  inlines = myfile.readlines()
  
for l in inlines:
  id_line = l.strip()
  if len(id_line) < 1:
    continue
  print id_line
  (pmid, pmc) = id_line.split(",")
  
  new_file = os.path.join(new_dir, "pubmed_"+pmid+".xml")
  if os.path.exists(new_file):
    continue
  fetch_url = url_root.replace(replacer, pmc)
  print fetch_url
  abstract_xml = perform_request(fetch_url)
  if len(abstract_xml) > 1:
    with open(new_file, "w") as fpo:
      fpo.write(abstract_xml)
      fpo.write("\n")
  
  time.sleep(15)