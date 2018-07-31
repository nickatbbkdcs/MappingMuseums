#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""
Documentation
===============

Process infile .  Basic usage as a module:

process parameters infile

# Nick Larsson (NickTex)

License: GPL 2 (http://www.gnu.org/copyleft/gpl.html) or BSD

"""

#-------------------------------------------------------------------------------------    
# Set up the logging
#-------------------------------------------------------------------------------------    
import re, sys, os, random, codecs
from logging import getLogger, StreamHandler, Formatter, \
                    DEBUG, INFO, WARN, ERROR, CRITICAL

from bs4 import BeautifulSoup
import pprint
import pandas as pd

MESSAGE_THRESHOLD = CRITICAL
EXECUTABLE_NAME_FOR_USAGE='MyApplicationProva'
SEPARATOR="$"
# Configure debug message logger (the hard way - to support python 2.3)
logger = getLogger(EXECUTABLE_NAME_FOR_USAGE)
logger.setLevel(DEBUG) # This is restricted by handlers later
console_hndlr = StreamHandler()
formatter = Formatter('%(name)s-%(levelname)s: "%(message)s"')
console_hndlr.setFormatter(formatter)
console_hndlr.setLevel(MESSAGE_THRESHOLD)
logger.addHandler(console_hndlr)


def message(level, text):
    ''' A wrapper method for logging debug messages. '''
    logger.log(level, text)



PREFIX='prefix'
DOMAINCLASS='domainclass'
SUBCLASS='subclasses'
COMMENT='comment'
LABEL='label'
URI='uri'

if __name__ == '__main__':
    """ Run Process from the command line. """




#-----------------------------------------------------------------------------------

def processStats(missingdata,errordata,listdata,header,datatype,row,rowno,invalidlist,doprint):
    
    i=0
    data=row.split(SEPARATOR)
    #print len(data)
    #print "?#?#? DQLprocess.py at line: 72 Dbg-out variable \data [",data,"]\n";
    for item in data:
        #print item
        actualdata=item.strip()
	if (i >= len(datatype)):
	    return
        checktype=datatype[i].lower().replace('"',"")
        if (len(actualdata)>0):
            if (checktype == "xsd:string"):
                noop=1
            elif (checktype == "xsd:positiveinteger" or checktype == "xsd:integer"):
                try:
                    int(actualdata)
                except ValueError:
                    is_valid_number = False
                    errordata[i]=errordata[i]+1
                    if (doprint):
                        print "NOT A VALID (I1)"+checktype+" ["+actualdata+"] Sheet["+str(rowno)+":"+str(i)+"]"
                    invalidlist.append(str(rowno)+":"+str(i))
            elif (checktype == "xsd:decimal"):
                try:
                    float(actualdata)
                except ValueError:
                    is_valid_number = False
                    errordata[i]=errordata[i]+1
                    if (doprint):
                        print "NOT A VALID (I1)"+checktype+" ["+actualdata+"] Sheet["+str(rowno)+":"+str(i)+"]"
                    invalidlist.append(str(rowno)+":"+str(i))
            elif (checktype.lower().find("range:positiveinteger") > -1 ):
                strippeddata=actualdata.strip().replace('"',"")
                if (actualdata.find(";") > -1):
                    if (len(strippeddata) == 1):
                        errordata[i]=errordata[i]+1
                        if (doprint):
                            print "NOT A VALID (I2) "+checktype+" ["+strippeddata+"] Sheet["+str(rowno)+":"+str(i)+"]"
                        invalidlist.append(str(rowno)+":"+str(i))
                    else:
                        parts=strippeddata.split(";")
                        startr=parts[0]
                        stopr=parts[1]
                        if (len(startr) > 0):
                            try:
                                int(startr)
                            except ValueError:
                                is_valid_number = False
                                errordata[i]=errordata[i]+1
                                if (doprint):
                                    print "NOT A VALID (I3)"+checktype+" ["+startr+"] Sheet["+str(rowno)+":"+str(i)+"]"
                                invalidlist.append(str(rowno)+":"+str(i))
                    
                        if (len(stopr) > 0):
                            try:
                                int(stopr)
                            except ValueError:
                                is_valid_number = False
                                errordata[i]=errordata[i]+1
                                if (doprint):
                                    print "NOT A VALID (I4)"+checktype+" ["+stopr+"] Sheet["+str(rowno)+":"+str(i)+"]"
                                invalidlist.append(str(rowno)+":"+str(i))
                elif (len(strippeddata) > 0):
                    try:
                        int(strippeddata)
                    except ValueError:
                        is_valid_number = False
                        errordata[i]=errordata[i]+1
                        if (doprint):
                            print "NOT A VALID (I5)"+checktype+" ["+strippeddata+"] Sheet["+str(rowno)+":"+str(i)+"]"
                        invalidlist.append(str(rowno)+":"+str(i))
                    
                else:
                    missingdata[i]=missingdata[i]+1
		
                    
            elif (checktype.find("hier:") > -1 ):
                strippeddata=actualdata.strip().replace('"','')
                if (listdata[i] == None):
                    listdata[i]=strippeddata
                else:
                    listdata[i]=listdata[i]+"#"+strippeddata
                if (len(strippeddata) > 0 and strippeddata[0] != "/"):
                    errordata[i]=errordata[i]+1
                    if (doprint):
                        print "NOT A VALID (1) "+checktype+" ["+strippeddata+"] Sheet["+str(rowno)+":"+str(i)+"]"
                    invalidlist.append(str(rowno)+":"+str(i))
                if (strippeddata.find("http") > -1):
                    errordata[i]=errordata[i]+1
                    if (doprint):
                        print "NOT A VALID (2) "+checktype+" ["+strippeddata+"] Sheet["+str(rowno)+":"+str(i)+"]"
                    invalidlist.append(str(rowno)+":"+str(i))
                if (len(strippeddata) == 0 ):
		    print "?#?#? DQLprocess.py at line: 162 Dbg-out variable \strippeddata [",strippeddata,"]\n";
                    missingdata[i]=missingdata[i]+1
            elif (checktype.find("bbkmm:") > -1 ):
                if (listdata[i] == None):
                    listdata[i]=actualdata
                else:
                    listdata[i]=listdata[i]+"#"+actualdata
		if (len(listdata[i]) < 1):
		    print "?#?#? DQLprocess.py at line: 169 Dbg-out variable \listdata [",listdata[i],"]\n";
                    missingdata[i]=missingdata[i]+1
		
        else:
	    missingdata[i]=missingdata[i]+1
#             if (checktype == "xsd:string"):
#                 missingdata[i]=missingdata[i]+1
#             elif (checktype == "xsd:positiveinteger" or checktype == "xsd:integer"):
#                 missingdata[i]=missingdata[i]+1

        i += 1
    return

#-----------------------------------------------------------------------------------

def printStats(missingdata,errordata,listdata,header,datatype,rows):
    #print "?#?#? DQLprocess.py at line: 166 Dbg-out variable \datatype [",datatype,"]\n";
    #print "?#?#? DQLprocess.py at line: 166 Dbg-out variable \header [",header,"]\n";
    #print "?#?#? DQLprocess.py at line: 166 Dbg-out variable \listdata [",listdata,"]\n";
    #print "?#?#? DQLprocess.py at line: 166 Dbg-out variable \errordata [",errordata,"]\n";
    #print "?#?#? DQLprocess.py at line: 166 Dbg-out variable \missingdata [",missingdata,"]\n";
    
    i=0
    for item in header:
        dtype=datatype[i]
        actualdata=item.strip()
        checktype=datatype[i].lower().replace('"',"")
        if (checktype == "xsd:string"):
            print("*****Column:{},Datatype:[{}] Missing: {} out of {}".format(header[i],checktype,missingdata[i],rows))
            print str(i)+"------------------------------------------------------------------------------------"
        elif (checktype == "xsd:positiveinteger" or checktype == "xsd:integer" or checktype == "xsd:decimal" or checktype.startswith("range:")):
            pad=""
            j=0
            while j < (len(header[i])+len(checktype)+int(25)):
                pad=pad+"."
                j += 1
            print("*****Column:{},Datatype:[{}] Error   values  : {} out of {}".format(header[i],checktype,errordata[i],rows))
            print("{}Missing values  : {} out of {}".format(pad,missingdata[i],rows))
            print str(i)+"------------------------------------------------------------------------------------"
        elif (checktype.find("bbkmm:")> -1 or checktype.find("hier:")> -1):
            print("#####Column:{},Datatype:[{}] Value range : ".format(header[i],checktype))
            valarr=listdata[i].split("#")
            j=0
            valarr=sorted(set(valarr))
            while j < len(valarr):
                print valarr[j]
                j += 1
            print("{}Missing values  : {} out of {}".format(pad,missingdata[i],rows))
            print str(i)+"------------------------------------------------------------------------------------"
        i += 1
    return

#-----------------------------------------------------------------------------------
def listDQL(fname):
### Read
    with open(fname) as f:
        content = f.readlines()
        f.close()
    header=content[0].split(SEPARATOR)
    shortheader=content[1].split(SEPARATOR)
    datatype=content[2].split(SEPARATOR)
    visibility=content[3].split(SEPARATOR)
    columnnumbers=content[4].split(SEPARATOR)
    cmax=len(columnnumbers)
    
    ERRORDATA= [0 for col in range(cmax)]
    MISSINGDATA= [0 for col in range(cmax)]
    LISTDATA= ["" for col in range(cmax)]
    
    
    i = 5
    invalidlist=[]
    doprint=True
    while i < len(content):
        #print "?#?#? DQLprocess.py at line: 220 Dbg-out variable \i [",i,"]\n";
        processStats(MISSINGDATA,ERRORDATA,LISTDATA,header,datatype,content[i],i,invalidlist,doprint)
        i += 1
        
    printStats(MISSINGDATA,ERRORDATA,LISTDATA,header,datatype,len(content))
    tot=0
    for e in ERRORDATA:
        tot=tot+e
        
    print "total errors:"+str(tot)

    return  tot

#-----------------------------------------------------------------------------------

def DQLClean(fname):
### Read
    with open(fname) as f:
        content = f.readlines()
        f.close()
    header=content[0].split(SEPARATOR)
    shortheader=content[1].split(SEPARATOR)
    datatype=content[2].split(SEPARATOR)
    visibility=content[3].split(SEPARATOR)
    columnnumbers=content[4].split(SEPARATOR)
    
    ERRORDATA= [0 for col in range(len(columnnumbers))]
    MISSINGDATA= [0 for col in range(len(columnnumbers))]
    LISTDATA= ["" for col in range(len(columnnumbers))]
    
    
    i = 5
    invalidlist=[]
    doprint=False
    while i < len(content):
        processStats(MISSINGDATA,ERRORDATA,LISTDATA,header,datatype,content[i],i,invalidlist,doprint)
        i += 1
#    print invalidlist
    for item in invalidlist:
        co=item.split(':')
        row=int(co[0])
        col=int(co[1])
        values=content[row].split(SEPARATOR)
#       print "before-------------------------------------------"
#       print values
#       print "error is "+values[col]
        #print content[row]
        values[col]=''
        content[row]='$'.join(values)
#       print "after-------------------------------------------"
#       print '$'.join(values)

    i = 0
    while i < len(content):
        sys.stdout.write(content[i])
        i += 1

    sys.stdout.flush()
    return    
#-----------------------------------------------------------------------------------
    

    

### Write
#f = open('outfile'+screenid+'_'+screenversion+'_'+str(filenumber)+'.n3','w')
#f.write( 'rdfs:domain '+dorisclass+' .'+'\n')
#f.close()

fname='/home/nlarsson/bbk/etl/code/main/MM_final_28_Jan_2018.csv'
fname='/home/nlarsson/bbk/etl/code/main/mm_input_maindatasheet_09_May_2018_FIXED.csv'
fname='/home/nlarsson/bbk/etl/code/main/mm_input_maindatasheet_26_June_2018.csv'

#DQLClean(fname)
tot=listDQL(fname)
exit(tot)
