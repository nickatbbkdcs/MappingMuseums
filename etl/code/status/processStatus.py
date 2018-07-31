#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""
Documentation
===============

Process infile .  Basic usage as a module:

process parameters infile

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

class Extension:

    def __init__(self, configs = {}):
        self.config = configs

    def getConfig(self, key):
        if self.config.has_key(key):
            return self.config[key][0]
        else:
            return ""

    def getConfigInfo(self):
        return [(key, self.config[key][1]) for key in self.config.keys()]

    def setConfig(self, key, value):
        self.config[key][0] = value


#-------------------------------------------------------------------------------------    
# G L O B A L S 
#-------------------------------------------------------------------------------------    
SOMECONSTANT_NAME='SOME'

# Unicode Reference Table:
# 0590-05FF - Hebrew
# 0600-06FF - Arabic
# 0700-074F - Syriac
# 0750-077F - Arabic Supplement
# 0780-07BF - Thaana
# 07C0-07FF - Nko

BOMS = { 'utf-8': (codecs.BOM_UTF8, ),
         'utf-16': (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE),
         #'utf-32': (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)
         }

def removeBOM(text, encoding):
    convert = isinstance(text, unicode)
    for bom in BOMS[encoding]:
        bom = convert and bom.decode(encoding) or bom
        if text.startswith(bom):
            return text.lstrip(bom)
    return text


dict={}
dict['hasId']='id2'
dict['isReferringTo']='id2'
tags=[]
tags.append('tag1')
tags.append('tag2')
tags.append('tag3')
dict['containsTags']=tags

#print dict
#uri='<http://'+baseuri+'/KnowledgeUnit/id/'+docid+'-'+id+'>'
PREFIX='prefix'
DOMAINCLASS='domainclass'
SUBCLASS='subclasses'
COMMENT='comment'
LABEL='label'
URI='uri'



UNQUOTEVALUES=True
sequenceorder=0
#-----------------------------------------------------------------------------------

def processLine(header,
		line,
		datamodel,
		symboltable):
    fm=1
    newline=""
    linecopy=copy.deepcopy(line)
    while (fm > 0):
        fm=linecopy.find("${")
        if (fm > -1):
            defstart=fm+2
            ll=len(linecopy)
            var=""
            while (defstart < ll and linecopy[defstart] !=  "}"):
                var=var+linecopy[defstart]
                defstart+=1
            estring=evaluatemacro(var,datamodel,symboltable)
            defstart+=1
            newline=newline+linecopy[0:fm]+estring
            linecopy=linecopy[defstart:ll]
    newline=newline+linecopy
    return newline

#-----------------------------------------------------------------------------------

def evaluatemacro(var,datamodel,symboltable):

    
    is_valid_number=True
    try:
        int(var)
    except ValueError:
        is_valid_number = False
    assign=var.find("=")
    if (is_valid_number == True):
        # return row[number]
        noop=1
	if (UNQUOTEVALUES):
		unquotedvalue=datamodel[int(var)].replace('"','')
		return unquotedvalue 
	else:
		return datamodel[int(var)]
    else:
        #just eval
	if(assign > 0):
		syms=var.split("=")
		var=syms[1]
		leftside=syms[0]
        lparen=var.find("(")
	if (lparen > -1):
		rparen=var.find(")")
		param=var[lparen+1:rparen]
		funcname=var[0:lparen]
	        returnval=globals()[funcname](param)
		if(assign > 0):
			symboltable[leftside]=returnval
		return returnval
	else:
		if (var in symboltable):
			return symboltable[var]
		else:
			returnval=globals()[var]()
			if(assign > 0):
				symboltable[leftside]=returnval
				
		return returnval
		
    return ""

#-----------------------------------------------------------------------------------

def processTemplate(header,template,datamodel,SYMBOLTABLE):
	i = 1
	while i < len(template):
		newline=processLine(header,
				    template[i],
				    datamodel,
				    SYMBOLTABLE)
		print newline
		i += 1

#-----------------------------------------------------------------------------------

def sourcetype():
	return "MuseumType"
def museumaddressURI(uri):
	suri="<http://bbk.a.c.uk/MuseumMapProject/data/Address/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE["sequenceorder"])+">"
	return suri
def srcuri():
	return "MuseumType"
def sourceURI(uri):
	suri="<http://bbk.a.c.uk/MuseumMapProject/data/TemporalAddressProvenance/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE["sequenceorder"])+">"
	return suri

def siteURI(uri):
	suri="<http://bbk.a.c.uk/MuseumMapProject/data/Site/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE["sequenceorder"])+">"
	return suri
def siteURIandInc(uri):
	suri="<http://bbk.a.c.uk/MuseumMapProject/data/Site/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE["sequenceorder"])+">"
	SYMBOLTABLE["sequenceorder"]=SYMBOLTABLE["sequenceorder"]+1
	return suri
def temporaladdressURI(uri):
	suri="<http://bbk.a.c.uk/MuseumMapProject/data/TemporalAddress/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE["sequenceorder"])+">"
	return suri
def hasbeginning(beg):
	return "\""+datamodel[int(beg)]+"\"^^xsd:Date"
def hasend(end):
	return "\""+datamodel[int(end)]+"\"^^xsd:Date"
def museumURI(mus):
	return "MuseumType:"+mus

def getTemporalSequenceOrder():
	retval=SYMBOLTABLE["sequenceorder"]
	return str(retval)

def temporalSequenceOrder():
	retval=SYMBOLTABLE["sequenceorder"]
	SYMBOLTABLE["sequenceorder"]=SYMBOLTABLE["sequenceorder"]+1
	return str(retval)

#-----------------------------------------------------------------------------------
def preAmble():
    
    print '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .'
    print '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .'
    print '@prefix foaf: <http://xmlns.com/foaf/0.1/> .'
    print '@prefix org:             <http://www.w3.org/ns/org#> .'
    print '@prefix time: <http://www.w3.org/2006/time#> . '
    print "@prefix prov:            <http://www.w3.org/ns/prov#>          . "
    print "@prefix vcard:           <http://www.w3.org/2006/vcard/ns#>    . "
    print "@prefix xsd:             <http://www.w3.org/2001/XMLSchema#> . "
    print "@prefix owl:             <http://www.w3.org/2002/07/owl#> . "
    print "@prefix rdf:             <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . "
    print "@prefix xml:             <http://www.w3.org/XML/1998/namespace> . "
    print "@prefix dcterms:         <http://purl.org/dc/terms/> . "
    print "@prefix bbkmm:  	    <http://bbk.a.c.uk/MuseumMapProject/def/> . "
    print "@base                    <http://bbk.a.c.uk/MuseumMapProject/def/> . "
    
    print ''
    print 'bbkmm:Museum a           rdfs:Class,owl:Class ;'
    print 'rdfs:subClassOf  org:Organisation .'
    print ''
    print 'bbkmm:TemporarySite a rdfs:Class,owl:Class ;'
    print 'rdfs:subClassOf org:Site;'
    print 'rdfs:subClassOf time:TemporalEntity .'
    print ''
    print 'org:SiteAddress  rdf:type  owl:DatatypeProperty ;'
    print 'rdfs:label "org:siteAddress"@en ;'
    print 'rdfs:comment "org:siteAddress"@en ;'
    print 'rdfs:domain bbkmm:TemporarySite;'
    print 'rdfs:range vcard:Address  .'
    print ''
    print 'time:hasBeginning  rdf:type owl:DatatypeProperty ;'
    print 'rdfs:label "time:hasBeginning"@en ;'
    print 'rdfs:comment "time:hasBeginning"@en ;'
    print 'rdfs:domain bbkmm:TemporarySite;'
    print 'rdfs:range xsd:date  .'
    print ''
    print 'time:hasEnd      rdf:type  owl:DatatypeProperty ;'
    print 'rdfs:label "time:hasEnd"@en ;'
    print 'rdfs:comment "time:hasEnd"@en ;'
    print 'rdfs:domain bbkmm:TemporarySite;'
    print 'rdfs:range xsd:date  .'
    print ''
    print 'bbkmm:hasSequenceOrder  rdf:type  owl:DatatypeProperty ;'
    print 'rdfs:label "bbkmm:hasSequenceOrder"@en ;'
    print 'rdfs:comment "bbkmm:hasSequenceOrder"@en ;'
    print 'rdfs:domain bbkmm:TemporarySite;'
    print 'rdfs:range xsd:positiveInteger .'
    print ''
    print 'prov:hadPrimarySource  rdf:type owl:DatatypeProperty ;'
    print 'rdfs:label "prov:hadPrimarySource"@en ;'
    print 'rdfs:comment "prov:hadPrimarySource"@en ;'
    print 'rdfs:domain bbkmm:TemporarySite;'
    print 'rdfs:range prov:Entity  .'
    return

#-----------------------------------------------------------------------------------



### Write
#f = open('outfile'+screenid+'_'+screenversion+'_'+str(filenumber)+'.n3','w')
#f.write( 'rdfs:domain '+dorisclass+' .'+'\n')
#f.close()
sequenceorder=0
fname='/home/nlarsson/bbk/python/aux/status/Status_Change_28_07_17.csv'
### Read
with open(fname) as f:
	content = f.readlines()
f.close()
headerline=content[0]
datamodel=content[3].split(SEPARATOR)
header=headerline.split(SEPARATOR)

SYMBOLTABLE={}

i = 1
j = 3
columnptr=14
baseptr=3
shift=11
idheader=content[1].split(SEPARATOR)
typeheader=content[2].split(SEPARATOR)
visheader=content[3].split(SEPARATOR)
countheader=content[4].split(SEPARATOR)
last=16
for i in [0,1,3,4,5,6,7,18]:
   sys.stdout.write(header[i]+"$") 
print ""
for i in [0,1,2,3,4,5,6,7]:
   sys.stdout.write(idheader[i]+"$") 
print ""
for i in [0,1,3,4,5,6,7,18]:
   sys.stdout.write(typeheader[i]+"$") 
print ""

while j < len(content):
    datamodel=content[j].split(SEPARATOR)
    #print "?#?#? processAddress.py at line: 327 Dbg-out variable \datamodel [",datamodel,"]\n";
    
    #sys.stdout.write('Line:'+str(j))
    repeatcolumns=""
    for i in range(0,2):
	repeatcolumns=repeatcolumns+datamodel[i]+"$"
    sys.stdout.write(repeatcolumns)

    col=baseptr
    while (col < len(datamodel )):
	for k in range(1,6):
	    #print k,":",col,idheader[col], datamodel[col]
	    sys.stdout.write(datamodel[col]+"$")
	    col=col+1
	    if (col >= len(datamodel)):
	    	break

	#print ""
	#print datamodel[18]
	sys.stdout.write(datamodel[18])
	# Check if more dates
	if (col+1 >= len(datamodel)):
	    break
	dates=datamodel[col]+datamodel[col+1]
	#print "?#?#? processAddress.py at line: 345 Dbg-out variable \col [",col,"]\n";
	#print "?#?#? processAddress.py at line: 345 Dbg-out variable \dates [",dates,"]\n";
	if (len(dates.strip()) < 4):
	    break
	else:
	    sys.stdout.write( repeatcolumns)
	    
	#				print "moving "+datamodel[columnptr+col]+"["+str(columnptr+col)+"] to "+datamodel[baseptr+col] 
	
    j += 1

	







