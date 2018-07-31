#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""
Documentation
===============

Process infile .  Basic usage as a module:

process parameters infile


python add_geonames_to_mainsheet.py ../main/MM_FINAL_18_JAN_2018.csv ./geocodes.csv > zz.csv ; soffice zz.csv


#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3


"""

#-------------------------------------------------------------------------------------    
# Set up the logging
#-------------------------------------------------------------------------------------    
import re, sys, os, random, codecs
from logging import getLogger, StreamHandler, Formatter, \
                    DEBUG, INFO, WARN, ERROR, CRITICAL

from bs4 import BeautifulSoup
import pprint
import copy
#import MMUtils
import importlib
import inspect


EXECUTABLE_NAME_FOR_USAGE='ProcessMuseums'
SEPARATOR="$"



#-------------------------------------------------------------------------------------    
# G L O B A L S 
#-------------------------------------------------------------------------------------    
HEADERDICT={}
GEO_HEADERDICT={}
PROJECT_ID='project_id'
NODES=[
    "DUMMY",
    "n3",#Country
    "n4",#Welsh
    "n5",#Scottish
    "n6",# NI
    "n8", # Region
    "n7", # County
    "n10",# UA
    "n11",# CA
    "n9"  # Borough
    ]
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


if __name__ == '__main__':
    """ Run Process from the command line. """


pp = pprint.PrettyPrinter(indent=4)

def getAdminAreaFromHeader(header,no):
    for key,val in header.items():
	if (val == no):
	    return key
    return None

def getGeoDatatype(gdata,no):
    return gdata[no].replace('"','').strip()


def notype(name):
    lparen=name.find("(")
    if (lparen > -1):
	newname=name[0:lparen]
    else:
	newname=name
    return newname.strip()



def processRow(header,gheader,gshortheader,gdatatype,datamodel,gdatamodel,datamatrix,gdatamatrix):
    pid=header[PROJECT_ID]
    gpid=gheader[PROJECT_ID]
    
    mid=datamodel[pid].replace('"','')
    found=False
    pc=0
#     print "?#?#? add_geonames_to_mainsheet.py at line: 68 Dbg-out variable \dlen [",dlen,"]\n";
#     while (dlen > 1):
# 	if (len(datamodel[dlen]) == 0):
# 	    datamodel[dlen]=""
# 	    print "?#?#? add_geonames_to_mainsheet.py at line: 72 Dbg-out variable \datamodel [",datamodel[dlen],"]\n";
# 	    dlen=dlen-1
# 	    print "?#?#? add_geonames_to_mainsheet.py at line: 74 Dbg-out variable \dlen [",dlen,"]\n";
	    
# 	else:
# 	    break
    
    
    line=('$'.join(datamodel).strip())
    ll=len(line)-1
    if(line[ll] == "$"):
	line=line+'""$'
    else:
	line=line+'$'
	
    sys.stdout.write(line)


    while (not found):
	#print "Comparing "+gdatamatrix[pc][gpid] +":"+mid
	geomid=gdatamatrix[pc][gpid].replace('"','')
	if (geomid == mid ):
	    out=[]
	    for ii, item in enumerate(gdatamatrix[pc][1:]):
		if (len(item)>1):
		  #  print "?#?#? add_geonames_to_mainsheet.py at line: 78 Dbg-out variable \item [",item,"]\n";
		    parts=item.split(":")

		    colname=getGeoDatatype(gdatatype,ii+1)
		    if (colname.find("xsd:") > -1):
			out.append('"#{refURI('+""+getGeoDatatype(gshortheader,ii+1)+","+NODES[ii+1]+",'"+notype(parts[0][1:])+"')}"+'"')
		    else:
			out.append('"#{refURI('+""+getGeoDatatype(gdatatype,ii+1)+","+NODES[ii+1]+",'"+notype(parts[0][1:])+"')}"+'"')
		    #out.append('"'+parts[1])
		else:
		    #out.append('')
		    out.append('')
		    
	    gl='$'.join(out).strip()

	    #print "?#?#? add_geonames_to_mainsheet.py at line: 77 Dbg-out variable \gl [",gl,"]\n";
            #print "LEMN:"+str(len(out))
	    sys.stdout.write(gl)
	    print
	    found=True
	else:
	    pc=pc+1
	if (not pc < len(gdatamatrix)):
	    found=True
	    for i in (range (1,19)):
		sys.stdout.write('$')
	    print
	    #print "**** COULT NOT FIND:"+mid
	    
    return
    
#-----------------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------------


fname=str(sys.argv[1])
#print "#?#?#? processMuseums.py at line: 690 Dbg-out variable \fname [",fname,"]\n";

# READY THE MAINSHEET
### Read fname
with open(fname) as f:
    content = f.readlines()
f.close()

header=content[0].split(SEPARATOR)
hcount=0
for h in header:
    HEADERDICT[h.replace('"','').replace(' ','_').lower().strip().replace('\n', '').replace('\r', '')]=hcount
    hcount=hcount+1

shortheader=content[1].split(SEPARATOR)
datatype=content[2].split(SEPARATOR)
visibility=content[3].split(SEPARATOR)
columnnumbers=content[4].split(SEPARATOR)


datastart=5
j=datastart
datamatrix=[]
matrixcount=0
contentlen=len(content)
contentlen=contentlen-datastart

for j in range (0,contentlen):
    datamatrix.append([])
    
j=datastart

while j < len(content):
    datamatrix[matrixcount]=content[j].split(SEPARATOR)
    matrixcount += 1
    j += 1

#print "------------------------------------------------------------------------------------"
#printRowModel(datamatrix)
#print "------------------------------------------------------------------------------------"

# Ready the GEO sheet -----------------------------------------------

gname=str(sys.argv[2])
### Read fname
with open(gname) as f:
    geo_content = f.readlines()
f.close()

geo_header=geo_content[0].split(SEPARATOR)
geo_hcount=0
for h in geo_header:
    GEO_HEADERDICT[h.replace('"','').replace(' ','_').lower().strip().replace('\n', '').replace('\r', '')]=geo_hcount
    geo_hcount=geo_hcount+1

geo_shortheader=geo_content[1].split(SEPARATOR)
geo_datatype=geo_content[2].split(SEPARATOR)
geo_visibility=geo_content[3].split(SEPARATOR)
geo_columnnumbers=geo_content[4].split(SEPARATOR)


datastart=5
j=datastart
geo_datamatrix=[]
geo_matrixcount=0
geo_contentlen=len(geo_content)
geo_contentlen=geo_contentlen-datastart

for j in range (0,geo_contentlen):
    geo_datamatrix.append([])
    
j=datastart

while j < len(geo_content):
    geo_datamatrix[geo_matrixcount]=geo_content[j].split(SEPARATOR)
    geo_matrixcount += 1
    j += 1

# Merge headers

for j in range(0,3):
    ll=len(content[j])-1
    line=content[j][0:ll].strip()
    if(line[0:ll] == "$"):
	line=line+'""$'
    else:
	line=line+'$'

    sys.stdout.write(line)
	
    out=[]
    hdr=geo_content[j].split(SEPARATOR)
  
    for i in (range(1,len(hdr))):
	#print ("GEO"+hdr[i])
	if (hdr[i].find("xsd:") > -1):
	    out.append('"uri:'+geo_shortheader[i].replace('"','').strip()+'"')
	else:
	    out.append(hdr[i].replace("bbkmm:","uri:").strip())
	    
#	if (hdr[i].find("xsd:") > -1):
#	    out.append(hdr[i].strip())
#	else:
#	    out.append(hdr[i].strip()+'_E"')
	    

    #print "?#?#? add_geonames_to_mainsheet.py at line: 186 Dbg-out variable \out [",out,"]\n";
      
    gl='$'.join(out)
    gl=gl.replace('"_E"','_E"')
    print(gl)

max=len(GEO_HEADERDICT)
#print "?#?#? add_geonames_to_mainsheet.py at line: 282 Dbg-out variable \max [",max,"]\n";
max=max+len(HEADERDICT)-1
#print "?#?#? add_geonames_to_mainsheet.py at line: 284 Dbg-out variable \max [",max,"]\n";
#print "?#?#? add_geonames_to_mainsheet.py at line: 190 Dbg-out variable \max [",max,"]\n";
for j in range(0,max):
    sys.stdout.write("Visible$")
print
for j in range(0,max):
    sys.stdout.write(str(j)+"$")
print


# Merge files

j=datastart
while j < len(content):
    #print "# Doing line["+str(j)+"]:"+content[j]
    row=j-datastart
    datamodel=datamatrix[row]
    geo_datamodel=geo_datamatrix[row]
    processRow(HEADERDICT,GEO_HEADERDICT,geo_shortheader,geo_datatype,datamodel,geo_datamodel,datamatrix,geo_datamatrix)
    j += 1









