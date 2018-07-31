#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

##
# @file
#  This program takes a template file and the data sheet and fills the template
#  with values from the data sheet thereby generating the RDF statements required to
#  build the model. This is done by iterating over all rows in the datasheet and applying the
#  template for each row. This means that some statements will be generated multiple times
#  however the database (virtuoso) does not seem to mind processing the same information several times.
#  It does mean that the size of the data and thereby also the processing time increases. This is not a
#  problem with the scale of the museum data.
#  The processLine method receives the whole datamatrix as well as the current row. The implication is
#  that macros could be written to work columnwise as well as rowwise if necessary.
#  The evaluatemacro processing is recursive so some macros generate new macros gradually refining the output.
#  The updateChangesByLine method allows deferred processing until the whole line has been evaluated by adding
#  statements to the LINECHANGELIST.This is used for generating sequence orders for temporal classes.
#
# OPTIONS
#    parser = optparse.OptionParser(usage="%prog inputfilename.csv outputfilename.template [options]")
#
#    parser.add_option("-c", "--cleanurlnames", dest="cleanurlnames",
#                      help="Remove non letters and digits from last path of url -c yes means activates cleaning")
#    parser.add_option("-r", "--root", 
#		      dest="root",
#                      help="Name of the root class (graphml node=n1")
#
#    parser.add_option("-m", "--modulename", 
#		      dest="moduleprefix",
#                      help="path to directory with clazzes module")
#
#
# argv1:input data sheet as csv
# argv2:input macro file name
#
# Outline:
#  
#    Process options  
#    Read files
#    Generate header information
#    Create the datamatrix from the sheet.
#    Process each row in the datamatrix against the template
#      ProcessLine
#         Evaluatemacro
#      updateChangesByLine
#
#

#  
#  
#  
#  
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3

import re, sys, os, random, codecs

from bs4 import BeautifulSoup
import copy
import importlib
import inspect





#-------------------------------------------------------------------------------------    
# G L O B A L S 
#-------------------------------------------------------------------------------------    
EXECUTABLE_NAME_FOR_USAGE='ProcessMuseums'
SEPARATOR="$" # csv separator
URIBASE='<http://bbk.ac.uk/MuseumMapProject/def/{}/id/{}/{}>' #base URI template
TEMPORALURIBASE='<http://bbk.ac.uk/MuseumMapProject/def/{}/id/{}/{}/seq{}>' #base temporal template
UNQUOTEVALUES=True
sequenceorder=0 # sequenceorder for temporal classes
eventsequenceorder=0 # Not used
EVENTSEQUENCEORDERKEY="eventsequenceorder" #not used
SEQUENCEORDERKEY="sequenceorder"
TEMPORALMEASUREMENT_MUSEUMKEY="temporalmeasurementsequenceorder" # key to access sequenceorder for a specific museum
HEADERDICT={}
PROJECTID='project_id' #museum id
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#-------------------------------------------------------------------------------------    
# G L O B A L S 
#-------------------------------------------------------------------------------------    
PREFIX='bbkm:'
LINECHANGELIST=[] # Macros to be executed once macro processing of a line terminates.

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


if __name__ == '__main__':
    """ Run Process from the command line. """



#-----------------------------------------------------------------------------------
## Purpose:Removes type info from name
# Arguments:
#  @name
def stripType(name):
    # Also remove type info
    lparen=name.find("(")
    if (lparen > -1):
	return name[0:lparen-1]
    else:
	return name

#-----------------------------------------------------------------------------------
## Purpose: Add macro to execute after line processing terminates
# Arguments:
#  @macro macro
def addLineChangeMacro(macro):
    LINECHANGELIST.append(macro)
    return True


#-----------------------------------------------------------------------------------
## Purpose: Process one row in the template
# Arguments:
# @line  Line to process
# @datamodel Current row from sheet
# @datamatrix Complete sheet
# @symboltable Symbol table to store/read values from
#
def processLine(line,datamodel,datamatrix,symboltable):
    fm=1
    newline=""
    linecopy=copy.deepcopy(line)
    while (fm > -1):
        fm=linecopy.find("${")
        if (fm > -1):
            defstart=fm+2
            ll=len(linecopy)
            var=""
            while (defstart < ll and linecopy[defstart] !=  "}"):
                var=var+linecopy[defstart]
                defstart+=1
            estring=evaluatemacro(var,datamodel,datamatrix,symboltable)
            defstart+=1
            newline=newline+linecopy[0:fm]+estring
            linecopy=linecopy[defstart:ll]
    newline=newline+linecopy
    return newline

#-----------------------------------------------------------------------------------
## Purpose: Return position of the next separator in params string
# Arguments:
# @params string input
# @separator separator to use

def findNextSeparator(params,separator):
    
    paramslen=len(params)
    start=0
    quotes1='"'
    quotes2="'"
    found=False
    while (start < paramslen):
        if (params[start] == separator):
            comma=start
            found=True
            break;
        elif (params[start] == quotes1):
            start=start+1
            while (start < paramslen):
                if (params[start] == quotes1):
                    start=start+1
                    break
                else:
                    start=start+1
        elif (params[start] == quotes2):
            start=start+1
            while (start < paramslen):
                if (params[start] == quotes2):
                    start=start+1
                    break
                else:
                    start=start+1
        else:
            start=start+1

    if (found):
        return start
    else:
        return -1
    

#-----------------------------------------------------------------------------------
## Purpose: Return list of parameters from string
# Arguments:
# @params input string
# @separator=','

def getparams(params,separator=','):
    plist=[]
    paramcp=copy.deepcopy(params)
    comma=findNextSeparator(params,separator)
    
    if (comma < 0):
        plist.append(params)
    else:
        while (comma > -1):
            aparam=paramcp[:comma]
            plist.append(aparam)
            paramcp=paramcp[comma+1:]

            comma=findNextSeparator(paramcp,separator)
        plist.append(paramcp)
        
    
    return plist

#-----------------------------------------------------------------------------------
## Purpose: Evaluates a macro found on a line or returns the value in the sheet at col=var
# Arguments:
# @var name of macro or column number
# @datamodel input sheet row
# @datamatrix complete sheet
# @symboltable Symbol table to store/read values from



def evaluatemacro(var,datamodel,datamatrix,symboltable):
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
            # Find last right paren starting from the back to avoid dealing with quoted params
            varlen=len(var)-1
            while (varlen >= 0):
                if (var[varlen] == ")"):
                    break
                varlen=varlen-1
            if (varlen < 0):
                # Raise error
                print "ERROR *** No right paren found in this string:"+var
            rparen=varlen
            param=var[lparen+1:rparen]
            funcname=var[0:lparen]
	    localparams=getparams(param)
	    pc=0
	    for p in localparams:
		if (p.find("$$") >= 0):
		    p=p.replace("$$","")
		    p=p.replace("$","").replace("'","").replace('"','')
		    p=evaluatemacro(p,datamodel,datamatrix,symboltable)
		    localparams[pc]=p
		pc+=1
			
	    if (len(param) == 0):
		returnval=globals()[funcname]()
	    else:
		returnval=globals()[funcname](localparams)
		
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
## Purpose: Process all lines in template
# Arguments:
#  @header
#  @template
#  @datamodel
#  @datamatrix
#  @SYMBOLTABLE

def processTemplate(header,template,datamodel,datamatrix,SYMBOLTABLE):
    i = 1
    while i < len(template):
        newline=processLine(template[i],datamodel,datamatrix,SYMBOLTABLE)
        print newline
        i += 1

#-----------------------------------------------------------------------------------
## Purpose:Remove unwanted characters
# Arguments:
# @name string to filter
def cleanName(name):
    return ''.join([i for i in name if (i.isalpha()or i == '/')])

#-----------------------------------------------------------------------------------
## Purpose:Special cleaning aware of hierarchies
# Arguments:
#  @name String to clean
def cleanNameForAltSub(name):
    name=name.replace(" ","_")
    return ''.join([i for i in name if (i.isalpha()or i == '/' or i == '_')])

#-----------------------------------------------------------------------------------
## Purpose: Declare all namespaces
def preamble():
    print "#################################################################"
    print "#"
    print "#    References"
    print "#"
    print "#################################################################"
    print "@prefix org:             <http://www.w3.org/ns/org#>           . "
    print "@prefix time:            <http://www.w3.org/2006/time#>           . "
    print "@prefix prov:            <http://www.w3.org/ns/prov#>          . "
    print "@prefix vcard:           <http://www.w3.org/2006/vcard/ns#>    . "
    print "@prefix xsd:             <http://www.w3.org/2001/XMLSchema#> . "
    print "@prefix owl:             <http://www.w3.org/2002/07/owl#> . "
    print "@prefix rdf:             <http://www.w3.org/1999/02/22-rdf-syntax-ns#> . "
    print "@prefix xml:             <http://www.w3.org/XML/1998/namespace> . "
    print "@prefix xsd:             <http://www.w3.org/2001/XMLSchema#> . "
    print "@prefix rdfs:            <http://www.w3.org/2000/01/rdf-schema#> . "
    print "@prefix dcterms:         <http://purl.org/dc/terms/> . "
    print "@prefix bbkmm:  	    <http://bbk.ac.uk/MuseumMapProject/def/> . "
    print "@base                    <http://bbk.ac.uk/MuseumMapProject/def/> . "
    print ""
    print "#################################################################"
    print ""
    print "#Individuals"
    print ""
    print "#################################################################"
    print ""
    return

#-----------------------------------------------------------------------------------
## Purpose:Convert date from slash based to hyphen based
# Arguments:
#  @date date to convert
def convertdate(date):
    parts=date.split("/")
    newdate=str(parts[2])+"-"+str(parts[0])+"-"+str(parts[1])
    return newdate

if __name__ == '__main__':
    """ Run Process from the command line. """


#-----------------------------------------------------------------------------------
# Below are the implementations of macros used in the templates
#-----------------------------------------------------------------------------------
## Purpose:
# Arguments:
def sourcetype():
    return "MuseumType"
#-----------------------------------------------------------------------------------
## Purpose:Returns URI for museum
# Arguments:
#  @uri column number for project id
def museumaddressURI(uri):
    suri="<http://bbk.ac.uk/MuseumMapProject/def/Address/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE[SEQUENCEORDERKEY])+">"
    return suri
#-----------------------------------------------------------------------------------
## Purpose:
# Arguments:
def srcuri():
    return "MuseumType"
#-----------------------------------------------------------------------------------
## Purpose:Returns uri for temporal class
# Arguments:
#  @uri column number for proj id
def sourceURI(uri):
    suri="<http://bbk.ac.uk/MuseumMapProject/def/TemporalAddressProvenance/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE[SEQUENCEORDERKEY])+">"
    return suri
#-----------------------------------------------------------------------------------
## Purpose:Returns uri for temporal class
# Arguments:
#  @uri column number for proj id
def siteURI(uri):
    suri="<http://bbk.ac.uk/MuseumMapProject/def/Site/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE[SEQUENCEORDERKEY])+">"
    return suri
#-----------------------------------------------------------------------------------
## Purpose:
# Arguments:
#  @uri
def siteURIandInc(uri):
    suri="<http://bbk.ac.uk/MuseumMapProject/def/Site/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE[SEQUENCEORDERKEY])+">"
    SYMBOLTABLE[SEQUENCEORDERKEY]=SYMBOLTABLE[SEQUENCEORDERKEY]+1
    return suri
#-----------------------------------------------------------------------------------
## Purpose:Returns uri for temporal class
# Arguments:
#  @uri column number for proj id
def temporaladdressURI(uri):
    suri="<http://bbk.ac.uk/MuseumMapProject/def/TemporalAddress/id/"+datamodel[int(uri)].replace('"','')+"_"+str(SYMBOLTABLE[SEQUENCEORDERKEY])+">"
    return suri
#-----------------------------------------------------------------------------------
## Purpose:Returns begin range date for range types
# Arguments:
#  @beg column number
def hasbeginning(beg):
    return datamodel[int(beg)]+"^^xsd:Date"
#-----------------------------------------------------------------------------------
## Purpose:Returns begin range date for range types
# Arguments:
#  @end column number
def hasend(end):
    return datamodel[int(end)]+"^^xsd:Date"

#-----------------------------------------------------------------------------------
## Purpose:
# Arguments:
#  @mus
def museumURI(mus):
    return "MuseumType:"+mus


#-----------------------------------------------------------------------------------
## Purpose:Returns the current sequence number for the current class
def getTemporalSequenceOrder():
    retval=SYMBOLTABLE[SEQUENCEORDERKEY]
    return str(retval)


#-----------------------------------------------------------------------------------
## Purpose:Increments and returns the current sequence number for the current class 
def temporalSequenceOrder():
    retval=SYMBOLTABLE[SEQUENCEORDERKEY]
    SYMBOLTABLE[SEQUENCEORDERKEY]=SYMBOLTABLE[SEQUENCEORDERKEY]+1
    return str(retval)



#-----------------------------------------------------------------------------------
## Purpose:Get the key for the temporal sequence number

def getTemporalSequenceOrderKey():
    key=datamodel[HEADERDICT["project_id"]]+"/"+TEMPORALMEASUREMENT_MUSEUMKEY
    key=key.replace('"','')
    return key


#-----------------------------------------------------------------------------------
## Purpose: Increments the temporal sequence number after line processing completes.
# Arguments:

def temporalSequenceOrderInt():
    key=getTemporalSequenceOrderKey()

    if (key not in SYMBOLTABLE):
	SYMBOLTABLE[key]=1

    addLineChangeMacro('${executeTemporalSequenceOrderInt("'+key+'")}')

    retval=SYMBOLTABLE[key]
    return "xsd:integer("+str(retval)+")"


#-----------------------------------------------------------------------------------
## Purpose:Increment a specific key or create it
# Arguments:
#  @key
def executeTemporalSequenceOrderInt(key):
    global SYMBOLTABLE
    thiskey=key[0].replace('"','')
    
    if (thiskey not in SYMBOLTABLE):
	SYMBOLTABLE[thiskey]=1
    else:
	SYMBOLTABLE[thiskey]+=1
    return ""

#-----------------------------------------------------------------------------------
## Purpose:
# Arguments:

def addressChangeEventType():
    return '"bbkmm:AddressChangeEvent"'


#-----------------------------------------------------------------------------------
## Purpose:
# Arguments:
def statusChangeEventType():
    return '"bbkmm:StatusChangeEvent"'

#-----------------------------------------------------------------------------------
## Purpose:Returns the sequence order number as data statement
# Arguments:

def hasEventSequenceOrder():
    global SYMBOLTABLE
    retval=SYMBOLTABLE[EVENTSEQUENCEORDERKEY]
    SYMBOLTABLE[EVENTSEQUENCEORDERKEY]=SYMBOLTABLE[EVENTSEQUENCEORDERKEY]+1
    return "xsd:integer("+str(retval)+")"

#-----------------------------------------------------------------------------------
## Purpose:Get the instance representing the clazz. This instance can then be called
# Arguments:
#  @clazz name of class
def getDataClassInstance(clazz):
    dotp=__name__.rfind(".")
    thisname=__name__[:dotp]

    if (options['moduleprefix'] == None ):
	mname="clazzes."+clazz
    else:
	mname=options['moduleprefix']+".clazzes."+clazz

    instance=None
    try:
	my_module = importlib.import_module(mname)
	try:
	    MyClass = getattr(my_module, clazz)
	    instance = MyClass()

	except AttributeError:
	    print "$$$$$$$$$ CLASS DOES NOT EXIST !"
	    
    except ImportError:
	print "$$$$$$$$$ MODULE  DOES NOT EXIST !"
	 
	 
    return instance
    
    
#-----------------------------------------------------------------------------------
## Purpose:Return triple for s p o
# Arguments:
#  @param s p o as list
def ExistsSubClass(param):
    subject=param[0].replace('"','')
    predicate=param[1].replace('"','')
    object=param[2].replace('"','')
    column=param[3]
    if (len(column) > 0):
	icol=int(column)
	value=datamodel[icol].replace('"','').strip()
	lv=len(value)
	if (lv > 0):
	    return  " "+subject+" "+predicate+" "+object+" ."
	else:
	    return ""
    else:
	    return ""
	
#-----------------------------------------------------------------------------------
## Purpose: Return subclass linkage declaration between nodes
# Arguments:
#  @param parameters
def ExistsLinkage(param):
    global SYMBOLTABLE

    column=param[5]
    if (len(column) > 0):
	icol=int(column)
	value=datamodel[icol].replace('"','').strip()
	lv=len(value)
	if (lv > 0):
	    value=value.split(":")[0]
	    value=stripType(value)
	    fromnode=param[1]
	    tonode=param[4]
	    fromname=value.strip()
	    toname=value.strip()
	    if (fromnode == "n1"):
		fromname=param[3].replace("bbkmm:","")
	    if (tonode == "n1"):
		toname=param[3].replace("bbkmm:","")
		
	    link='${%s("%s",%s,%s)}  %s  ${%s("%s",%s,%s)}  . '
	    statementtemplate=link % (str(param[6]),str(param[0]),str(fromnode),str(fromname),str(param[2]),str(param[7]),str(param[3]),str(tonode),str(toname))
	    statement=processLine(statementtemplate,datamodel,datamatrix,SYMBOLTABLE)
	    return statement
	else:
	    return ""
    else:
	return ""
	

#-----------------------------------------------------------------------------------
## Purpose:
# Arguments:
#  @param
def DeclareDefLinkage(param):
    global SYMBOLTABLE

    link='${%s("%s",%s)}  %s  ${%s("%s",%s)}  . '
    statementtemplate=link % (str(param[6]),str(param[0]),str(param[1]),param[2],str(param[7]),str(param[3]),str(param[4]))
    statement=processLine(statementtemplate,datamodel,datamatrix,SYMBOLTABLE)
    return statement
	
#-----------------------------------------------------------------------------------
## Purpose: This takes care of the inherited properties from a non-def or temporal class.
# We need to have a module for each class (replace : with _)
# A function representing the property with the same name
# Taking an interface of data from here. This way it will be generic if complicated.
# Change all the Exists to lowercase, they are not classes.
#  @param parameters
def ExistsProperty(param):
    global SYMBOLTABLE

    clazzname=param[1]
    modulename=param[1].replace(":","_").replace('"','')
    nodename=param[2]
    clazzdata=param[3]
    propertyname=param[4].replace(":","_").replace('"','')
    rangetype=param[5]
    instance=getDataClassInstance(modulename)
    method_to_call = getattr(instance, propertyname)
    result = method_to_call(clazzname,
			    nodename,
			    propertyname,
			    clazzdata,
			    rangetype,
			    SYMBOLTABLE,
			    datamodel,
			    datamatrix
			    )
    if (str(type(result)) == "<type 'str'>"):
	if (len(result) > 0):
	    icol=int(clazzdata)
	    value=datamodel[icol].replace('"','')
	    parts=value.split(":")
	    pname=stripType(parts[0]).strip()
	    link='${%s("%s",%s,%s)} %s  %s  . '
	    statementtemplate=link % (str(param[0]),
				      str(param[1]),
				      str(param[2]),
				      str(pname),
				      param[4].replace('"',''),
				      result.strip())
	    statement=processLine(statementtemplate,datamodel,datamatrix,SYMBOLTABLE)
	    return statement
	else:
	    return ""
    else:
	statements=""
	for res in result:
	    if (len(res) > 0):
		icol=int(clazzdata)
		value=datamodel[icol].replace('"','')
		parts=value.split(":")
		pname=stripType(parts[0]).strip()
		link='${%s("%s",%s,%s)} %s  %s  . '
		statementtemplate=link % (str(param[0]),
					  str(param[1]),
					  str(param[2]),
					  str(pname),
					  param[4].replace('"',''),
					  res.strip())
		statement=processLine(statementtemplate,datamodel,datamatrix,SYMBOLTABLE)
		statements=statements+"\n"+statement

	return statements    

#-----------------------------------------------------------------------------------
## Purpose: Generate individuals for hier classes when the correct value for the class is present
# Arguments:
#  @param parameters
def altNamedInstance(param):

    clazz=param[0].replace('"','')
    nodeid=param[1]
    predicate=param[2].replace('"','')
    comparestring=param[3].replace('"','')
    edgename=param[4].replace('"','')
    dtype=param[5].replace('"','')
    col=int(param[6].replace('"',''))
    
									    
    value=datamodel[col].replace('"','')

    subject=classURI([clazz,nodeid])

    globalclass=classGlobalURI([clazz,edgename])

    if ( value == comparestring):
	return  " "+subject+" "+predicate+" "+clazz+"_"+edgename+" ."
    else:
	return ""
    return

#-----------------------------------------------------------------------------------
## Purpose: Generate subclass statement for hier classes when the correct value for the class is present
# Arguments:
#  @param parameters
def altSubClass(param):
    clazz=param[0].replace('"','')
    nodeid=param[1]
    predicate=param[2].replace('"','')
											
    subclass=param[3].replace('"','')
    comparestring=param[4].replace('"','')
    col=int(param[5].replace('"',''))
    value=cleanNameForAltSub(datamodel[col])
    subject=classURI([clazz,nodeid])

    if ( value == comparestring):
	return  subject+" "+predicate+" "+subclass+" ."
    else:
	return ""
    return

#-----------------------------------------------------------------------------------
## Purpose: Generate subclass uri and declare subclass if not done.
# Arguments:
#  @params
def classGlobalURI(params):
    GLOBALURIBASE='<http://bbk.ac.uk/MuseumMapProject/def/{}/{}>'
    clazzname=params[0].replace('"','')
    baseclazz=clazzname[clazzname.find(":")+1:]
    instance=params[1].replace(" ","_")
    retval=GLOBALURIBASE.format(baseclazz,instance)
    hits=0
    if (retval in SYMBOLTABLE):
        hits=int(SYMBOLTABLE[retval])
    else:
        SYMBOLTABLE[retval]=0
    if (hits == 0):
        print clazzname+"_"+instance+" rdfs:subClassOf  "+clazzname+" ."
        print retval+" a  "+clazzname+"_"+instance+" ."

    hits += 1
    SYMBOLTABLE[retval]=hits
        
    return str(retval)

#-----------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------
## Purpose:Return uri for temporal class and declare class if not done
# Arguments:
#  @params
def temporalClassURI(params):
    clazzname=params[0].replace('"','')
    baseclazz=clazzname[clazzname.find(":")+1:]
    nodeid=params[1]
    key=getTemporalSequenceOrderKey()
    if (key not in SYMBOLTABLE):
	SYMBOLTABLE[key]=0
    retval=TEMPORALURIBASE.format(baseclazz,nodeid,datamodel[HEADERDICT[PROJECTID]].replace('"',''),SYMBOLTABLE[key])
    
    hits=0
    if (retval in SYMBOLTABLE):
        hits=int(SYMBOLTABLE[retval])
    else:
        SYMBOLTABLE[retval]=0
    if (hits == 0):
        print retval+" a "+clazzname+" ."

    hits += 1
    SYMBOLTABLE[retval]=hits
        
    return str(retval)

#-----------------------------------------------------------------------------------
## Purpose:Return class uri and declare class if not done
# Arguments:
#  @params
def classURI(params):
    clazzname=params[0].replace('"','')
    baseclazz=clazzname[clazzname.find(":")+1:]
    nodeid=params[1]

    if (len(params) > 2):
	rowid=str(params[2]).replace('"','')
    elif (nodeid == "n1"):
	rowid=baseclazz.replace("bbkmm:","")
    else:
	rowid=datamodel[HEADERDICT[PROJECTID]].replace('"','')

    if (options['cleanurlnames'] == None or options['cleanurlnames'] == 'no'):
	retval=URIBASE.format(baseclazz.strip(),nodeid,datamodel[HEADERDICT[PROJECTID]].replace('"',''))
    else:
	retval=URIBASE.format(baseclazz.strip(),nodeid,cleanNameForAltSub(rowid))

    hits=0

    if (retval in SYMBOLTABLE):
        hits=int(SYMBOLTABLE[retval])
    else:
        SYMBOLTABLE[retval]=0
    if (hits == 0):
        print retval+" a "+clazzname+" ."

    hits += 1
    SYMBOLTABLE[retval]=hits
    return str(retval)

#-----------------------------------------------------------------------------------
## Purpose:Return refersto class uri 
# Arguments:
#  @params
def refURI(params):
    clazzname=params[0].replace('"','')
    baseclazz=clazzname[clazzname.find(":")+1:]
    nodeid=params[1]

    if (len(params) > 2):
	rowid=str(params[2]).replace('"','')
    elif (nodeid == "n1"):
	rowid=baseclazz.replace("bbkmm:","")
    else:
	rowid=datamodel[HEADERDICT[PROJECTID]].replace('"','')
	
    retval=URIBASE.format(baseclazz.strip(),nodeid,cleanNameForAltSub(rowid))

    return str(retval)

#-----------------------------------------------------------------------------------
## Purpose:Execute whatever statement is in a cell in the sheet
# Arguments:
# Pulls in cell value and executes it
#  @params cell number
def DATACONTENT(params):
    global SYMBOLTABLE

    cellptr=int(params[0])
    statementtemplate=datamodel[cellptr]
    # Remove outside double quotes
    statementtemplate=statementtemplate[1:len(statementtemplate)-2]
    if (len(statementtemplate) < 3):
	statementtemplate='""^^xsd:string'
    statementtemplate=statementtemplate.replace("#","$")
    statement=processLine(statementtemplate,datamodel,datamatrix,SYMBOLTABLE)
    return statement

#-----------------------------------------------------------------------------------
## Purpose: Declare the value of a property by name with a type and pointer to the column in the sheet
# Arguments:
#  @param
def property(param):
    prop=param[0].replace('"','')
    datatype=param[1].replace('"','')
    dlist=[]
    if (param[2].find("[") > -1):
        #We have a list
        pl=len(param[2])-1
        dlist=getparams(param[2][1:pl],';')

    dl=len(dlist)
    datalen=len(datamodel)
    value=""
    if (dl >0):
        for item in dlist:
            dl=dl-1
            itemasint=int(item)
            if (dl == 0):
                if (itemasint < datalen):
                    value=value+datamodel[itemasint]
            else:
                if (itemasint < datalen):
                    value=value+datamodel[itemasint]+","
    elif(len(param)== 3):
        # We have a string named property
        statement1=" {} \"{}\"^^{}".format(param[0].replace('"',''),param[1].replace('"',''),param[2].replace('"',''))
        return statement1
    else:
	hassemicolon=param[2].find(";")
	if (hassemicolon >= 0):
	    idata=param[2].split(";")
	    ipos=int(idata[1])
	    icol=int(idata[0])
	    idptr=int (icol)

	    if  (len (datamodel[icol].strip()) == 0):
		value=""
	    elif (idptr < datalen):
		cdata=datamodel[icol].split(";")
		value=cdata[ipos]
	    else:
		dptr=int (param[2])
		if (dptr < datalen):
		    value=datamodel[dptr]
	else:
	    # if we have a string use that, if we have an int it will be a ptr to the datamodel
	    ustring = unicode(param[2], 'utf-8')
	    if (ustring.isnumeric() and int(param[2]) > -1 and int(param[2]) < len(datamodel)):
		value=datamodel[int(param[2])]
	    else:
		value=param[2]
		if (value.startswith("xsd:")):
		    # We have a non-dataptr, such as a return value from a function
		    lparam=value.find("(")+1
		    rparam=value.find(")")
		    if (rparam < 0 or lparam < 0):
			print "Property: Expected parethesis value here:"+value
		    else:
			value=value[lparam:rparam]
			param[2]=value
			
    vis=param[3].replace('"','')
    value=value.replace('"','').strip()
    
    ### Note: ETL data quality should have been checked before we get to loading the data
    ### all data is now assumed to be correct and none of the phony values should ever occur
    if (datatype.lower() == "xsd:positiveinteger"):
        datatype="xsd:integer"
        try:
            int(value)
        except ValueError:
            value="000000"
            
    if (datatype.lower() == "xsd:date" and len(value) == 0):
        value="3000-01-01" 
    elif (datatype.lower() == "xsd:date" and len(value) < 4): 
        value="4000-01-01"
    elif (datatype.lower() == "xsd:date" and len(value) == 4): 
        value=str(value)+"-01-01"
    elif (datatype.lower() == "xsd:date" ): 
        value=convertdate(value)
        
    if (datatype.lower() == "xsd:boolean" and (value.lower() == "y" or value.lower() == "yes")):
        value="true"
    elif (datatype.lower() == "xsd:boolean" and (value.lower() == "n" or value.lower() != "no")):
        value="false"
    elif (datatype.lower() == "xsd:boolean" and len(value) == 0):
        value=""
    elif (datatype.lower() == "xsd:boolean" and (value.lower() != "false" or value.lower() != "true")):
        value=""
    
    statement1=" {} \"{}\"^^{}".format(prop,value,datatype)
    return statement1


#-----------------------------------------------------------------------------------
## Purpose: Execute macros after line processing  terminates
def updateChangesByLine():

    ## This function is made to execute for each line of input in case there are updates depending on the line change
    ## that are generated by the code.

    for item in LINECHANGELIST:
	macro=LINECHANGELIST.pop()
        processLine(macro,datamodel,datamatrix,SYMBOLTABLE)

    return True

#-----------------------------------------------------------------------------------
## Purpose:parse_options
def parse_options():

    try:
        optparse = __import__("optparse")
    except:
	print OPTPARSE_WARNING
	return None

    parser = optparse.OptionParser(usage="%prog inputfilename.csv outputfilename.template [options]")

    parser.add_option("-c", "--cleanurlnames", dest="cleanurlnames",
                      help="Remove non letters and digits from last path of url -c yes means activates cleaning")
    parser.add_option("-r", "--root", 
		      dest="root",
                      help="Name of the root class (graphml node=n1")

    parser.add_option("-m", "--modulename", 
		      dest="moduleprefix",
                      help="path to directory with clazzes module")

    (options, args) = parser.parse_args()

    if not len(args) == 2:
        parser.print_help()
        return None


    return {'root': options.root,
            'moduleprefix': options.moduleprefix,
            'cleanurlnames': options.cleanurlnames }
    
#-----------------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------------



options = parse_options()

sequenceorder=0
eventsequenceorder=0

fname=str(sys.argv[1])
tname=str(sys.argv[2])

### Read
with open(fname) as f:
    content = f.readlines()
f.close()
preamble()

header=content[0].split(SEPARATOR)
hcount=0
for h in header:
    HEADERDICT[h.replace('"','').replace(' ','_').lower().strip().replace('\n', '').replace('\r', '')]=hcount
    hcount=hcount+1

shortheader=content[1].split(SEPARATOR)
datatype=content[2].split(SEPARATOR)
visibility=content[3].split(SEPARATOR)
columnnumbers=content[4].split(SEPARATOR)

template=[]
foundindividuals=False

with open(tname) as f:
    firsttemplate = f.readlines()
f.close()

### Find #$Individuals to avoid repeating all the definitions
for line in firsttemplate:
    if (line.find("#$Individuals") > -1):
        foundindividuals=True
        template.append(line)
    elif (foundindividuals == True):
        template.append(line)
    else:
        print line
        
SYMBOLTABLE={}
SYMBOLTABLE[EVENTSEQUENCEORDERKEY]=eventsequenceorder

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

j=datastart
while j < len(content):
    row=j-datastart
    datamodel=datamatrix[row]
    SYMBOLTABLE["count"]=row
    processTemplate(header,template,datamodel,datamatrix,SYMBOLTABLE)
    updateChangesByLine()
    j += 1









