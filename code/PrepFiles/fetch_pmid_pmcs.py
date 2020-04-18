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
#url_root = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id="+replacer+"&rettype=xml"
url_root = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=pmidToPMC&email=ehobbs2@umbc.edu&format=csv&ids="
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

def do_call(id_list, appendfile):
  print "DO Call"  

  istr = ",".join(id_list)
  fetch_url = url_root+istr
  #print fetch_url
  results = perform_request(fetch_url)
  if len(results) > 1:
    with open(appendfile, "a") as fpo:
      fpo.write(results)

        
fname = sys.argv[1]
appendfile = sys.argv[2]


with open(fname, "r") as myfile:
  inlines = myfile.readlines()
  
id_list = []
for l in inlines:
  id_line = l.strip()
  if len(id_line) < 1:
    continue
  #print id_line
  if len(id_list) < 200:
    id_list.append(id_line)
  else:
    do_call(id_list, appendfile)
    id_list = []
  
    time.sleep(15)
    
if len(id_list):
  do_call(id_list, appendfile)
  