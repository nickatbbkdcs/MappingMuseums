#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

##
# @file
# The program reads a graphml file which contains the ontology and creates a macro
# template which contains classes,predicates and individuals. Combining this template
# with the data sheet produces N3 RDF in the next step.
# Arguments:
# argument1 : ontology.graphml
# argument2 : domain label = this label is used to partition the generated model in case
#             many sheets are being processed.
#
# The program uses beautiful soup to parse the graphML file.
# The program makes 2 passes over the same ontology file. The first pass collects information
# on subclasses etc and the second pass generates the code.
#
# General outline:
#   
#   PASS1: Process all nodes and edges and collect information in  dictionaries and maps.
#   PASS2: Process all nodes to generate content classes
#          Process all edges to generate predicates
#          Process all edges to generate individuals
#          Generate list declarations for datatypes and predicates
#
#   The datatypes and predicates are used in the web application to build menus and
#   decide on what capabilities should be attributed to a data item.
#
#   The basenode id is as before n0 ZERO, the museum class.
#
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3

import re, sys, os, random, codecs

from bs4 import BeautifulSoup
import copy




#-------------------------------------------------------------------------------------    
# G L O B A L S 
#-------------------------------------------------------------------------------------    


PREFIX='bbkmm'
PREFIX_WITHCOLON='bbkmm:'
DOMAINCLASS='domainclass'
SUBCLASS='subclasses'
COMMENT='comment'
LABEL='label'
URI='uri'
SUBCLASSNAMESEPARATOR='-'

BASENODEID="n0"
BASENODENAME="Museum"



if __name__ == '__main__':
    """ Run Process from the command line. """

### Maps for storing data about classes and properties
INHERITANCEMAP={}
CLASSTOPROPERTYMAP={}
SUBCLASSDATADICT={}
CLASSDATADICT={}
CLASSNODENUMBERDICT={}
CLAZZES=[]
LISTCLAZZES={}
PREDICATES={}
DATATYPEDICT={}

NAMEDINSTANCE="hasNamedInstance"
URI="uri"
NODES=None
EDGES=None

## Definitions for our abstract types
IS="Is"
DEF="def"
HAS="has"
DEFRANGE="defRange"
DEFCLASS="defClass"
HIER_TYPE="HierType"
LIST_TYPE="ListType"
RANGE_TYPE="RangeType"
EMITTING  = True

#-----------------------------------------------------------------------------------
## Purpose: Emits the declaration or supresses it depending on state of EMITTING
# Arguments:
#  @emitstring
def emitDeclaration(emitstring):
    if (EMITTING == True):
	print emitstring
	    

#-----------------------------------------------------------------------------------
## Purpose: Removes unwanted characters from string
# Arguments:
#  @name is a string needing cleanup
def cleanName(name):
    name=name.replace(" ","_").replace("/","_and_")
    return ''.join([i for i in name if (i.isalpha() or i == "_")])

#-----------------------------------------------------------------------------------
## Purpose: Adds a name to the datatype dict
# Arguments:
#  @name name to add 
#  @datatype datatyep to add
def addToDataTypeDict(name,datatype):
    dt=datatype.replace(PREFIX_WITHCOLON,"")
    if (dt.startswith(DEFRANGE)):
	DATATYPEDICT[name]=RANGE_TYPE
    elif (dt.startswith(DEFCLASS)):
	DATATYPEDICT[name]=HIER_TYPE
    elif (name.startswith(DEF)):
	DATATYPEDICT[name]=LIST_TYPE
    else:
	DATATYPEDICT[name]=datatype
    return
#-----------------------------------------------------------------------------------
## Purpose: Generates the datatype list at end of processing.
# Arguments:
#  @label name of list label
def generateDataTypeList(label):
    #d:myList d:contents ("one" "two" "three" "four" "five") 

    decl=""
    for x in DATATYPEDICT.keys():
        v=DATATYPEDICT[x]
	decl=decl+" "+'"'+x+'#'+v+'"'

    alldecl=PREFIX_WITHCOLON+"DataTypeList_"+label+" "+PREFIX_WITHCOLON+"contents ("+decl+") ."    
    return alldecl
#-----------------------------------------------------------------------------------

## Purpose:Adds an instance to the dictionary for the list.
# Arguments:
#  @clazz name of class
#  @instancevalue name of instance
def addToListForDeclaration(clazz,instancevalue):
    if (clazz in LISTCLAZZES):
        v=LISTCLAZZES[clazz]
    else:
        v=[]
    v.append(instancevalue.replace('"',''))
    LISTCLAZZES[clazz]=v
    return

#-----------------------------------------------------------------------------------
## Purpose: Declares a list with its content as name label
# Arguments:
#  @label name of list
def generateListDeclarations(label):
    #d:myList d:contents ("one" "two" "three" "four" "five") 

    alldecl=""
    for x in LISTCLAZZES.keys():
        v=LISTCLAZZES[x]
        decl=""
        for item in v:
            if (len(decl)== 0):
                decl=decl+'"'+item+'"'
            else:
                decl=decl+" "+'"'+item+'"'
        alldecl=alldecl+"\n"+x+"List "+PREFIX_WITHCOLON+"contents ("+decl+") ."    

        # Generate the instance accessor
        colon=x.find(":")+1
        coreclass=x[colon:]
        declareProperty(x,x[0:colon]+HAS+coreclass,"xsd:string")

##  predicatelist
    decl=""
    alldecl=alldecl+"\n"
    for item in PREDICATES.keys():
        if (item.find(NAMEDINSTANCE) < 0 and item.find(PREFIX_WITHCOLON) > -1  ):
            item.replace(PREFIX_WITHCOLON,"")
            if (len(decl)== 0):
                decl=decl+'"'+item+'"'
            else:
                decl=decl+" "+'"'+item+'"'
	elif (item.startswith(DEFRANGE)):
                decl=decl+" "+'"'+PREFIX_WITHCOLON+item+'"'
	    
    alldecl=alldecl+"\n"+PREFIX_WITHCOLON+"PredicateList_"+label+" "+PREFIX_WITHCOLON+"contents ("+decl+") ."    

    return alldecl


#-----------------------------------------------------------------------------------
## Purpose:Constructs the inheritance map
# Arguments:
#  @base base class
#  @derived class
def addSubClass(base,derived):
    global INHERITANCEMAP
    if (not derived in INHERITANCEMAP):
        INHERITANCEMAP[derived]=base
    return
#-----------------------------------------------------------------------------------
## Purpose:Gets a subclass from the map if it is a derived class
# Arguments:
#  @classmap
#  @derivedin
def getSubClass(classmap,derivedin):
    derived=copy.copy(derivedin)
    if (derived in classmap):
        while (derived in classmap):
            derived=classmap[derived]
        return derived
    else:
        return derived
        
#-----------------------------------------------------------------------------------
## Purpose:Gets a subclass for a property if it is implemented by the derived class
# Arguments:
#  @classmap  map of classes
#  @derivedin derived class
#  @property  property to look for.
#
def getSubClassForProperty(classmap,derivedin,property):
    global CLASSTOPROPERTYMAP
    
    derived=copy.copy(derivedin)
    if (derived in classmap):
        while (derived in classmap):
	    if (derived in CLASSTOPROPERTYMAP):
		propertiestups=CLASSTOPROPERTYMAP[derived]
		for tups in propertiestups:
		    (propertyname,rangetype)=tups
		    if (property == propertyname):
			return derived
            derived=classmap[derived]
        return derived
    else:
        return derived
#-----------------------------------------------------------------------------------
## Purpose:Return a parent class to clazz
# Arguments:
#  @classmap map of classes
#  @clazz class to look for
def getParentClass(classmap,clazz):
    for key, val in classmap.iteritems():
	if (val == clazz):
	    return key
    return clazz
#-----------------------------------------------------------------------------------
## Purpose: Get root class for clazz
# Arguments:
#  @classmap map of classes
#  @clazz class to look for
def getRootClass(classmap,clazz):
    clazzcopy=copy.copy(clazz)
    found=False
    while (not found):
	for key, val in classmap.iteritems():
	    if (key == clazzcopy):
		clazzcopy=val
		found=True
		break
	if (found):
	    found=False
	else:
	    found=True
    return clazzcopy
        
#-----------------------------------------------------------------------------------
## Purpose:Return a list of parameters decoded from the input string
# Arguments:
#  @params input string
#  @separator=','
def getparams(params,separator=','):
    plist=[]
    paramcp=copy.deepcopy(params)
    comma=paramcp.find(separator)
    if (comma < 0):
        plist.append(params)
    else:
        while (comma > -1):
            aparam=paramcp[:comma]
            plist.append(aparam)
            paramcp=paramcp[comma+1:]
            comma=paramcp.find(separator)
        plist.append(paramcp)
        
    
    return plist


#-----------------------------------------------------------------------------------
## Purpose: Is the name an abstract class? E.g. defClass
# Arguments:
#  @propertyname
def iscomplextype(propertyname):
    colon=propertyname.find(":")
    if (colon > -1):
	rest=propertyname[colon:]
	rest=rest.replace(HAS,DEFCLASS)
	complextype=propertyname[0:colon]+rest
	if (complextype in CLASSDATADICT):
	    return True
	else:
	    return False
    return False

#-----------------------------------------------------------------------------------
## Purpose: Declares a dataproperty with domain and range
# Arguments:
#  @domain domain
#  @propertyname name of property
#  @rangetype    range of property
def declareProperty(domain,propertyname,rangetype):
    global CLASSTOPROPERTYMAP

    ## Check if this has a defclass as well, in which case we supress the generation
												
    if (not iscomplextype(propertyname)):
	print ""
	emitDeclaration(" "+propertyname+" rdf:type owl:DatatypeProperty ;")
	emitDeclaration("                rdfs:label \""+propertyname+"\"@en ;")
	emitDeclaration("                rdfs:comment \""+propertyname+"\"@en ;")
	if (rangetype.find('"') >= 0):
	    # We have a string and dont output it
	    emitDeclaration("                rdfs:domain "+domain+" .")
	else:
	    # Normal rangetype
	    emitDeclaration("                rdfs:domain "+domain+" ;")
	    emitDeclaration("                rdfs:range "+rangetype+" .")

	PREDICATES[propertyname]="DUMMY"
	addToDataTypeDict(propertyname,rangetype)
	if (not domain in CLASSTOPROPERTYMAP):
	    CLASSTOPROPERTYMAP[domain]=[]
	    tup=(propertyname,rangetype)
	    CLASSTOPROPERTYMAP[domain].append(tup)
	else:
	    found=False
	    tuplist=CLASSTOPROPERTYMAP[domain]
	    for t in tuplist:
		tp,tr=(t)
		if (tp == propertyname):
		    found=True
		    break
	    if (not found):
		tup=(propertyname,rangetype)
		CLASSTOPROPERTYMAP[domain].append(tup)

    return


#-----------------------------------------------------------------------------------
## Purpose: Declare the propertyname as an objectproperty
# Arguments:
#  @domain domain
#  @propertyname name of property
#  @rangetype range of property
#
def declareObjectProperty(domain,propertyname,rangetype):
    global CLASSTOPROPERTYMAP
    
    print ""
    # This corrects for the property name being wrong for defclasses.
    if (rangetype.find(DEFCLASS)>0):
	# We change the has to def
	propertyname=propertyname.replace(HAS,DEF)

    if (propertyname.find(":") > -1):
        emitDeclaration(" "+propertyname+" rdf:type owl:ObjecttypeProperty ;")
    else:
        emitDeclaration(" "+PREFIX_WITHCOLON+propertyname+" rdf:type owl:ObjecttypeProperty ;")
    
    emitDeclaration("                rdfs:label \""+propertyname+"\"@en ;")
    emitDeclaration("                rdfs:comment \""+propertyname+"\"@en ;")
    emitDeclaration("                rdfs:domain "+domain+" ;")
    emitDeclaration("                rdfs:range "+rangetype+" .")

    if (propertyname.find(DEFRANGE) >= 0):
	addToDataTypeDict(propertyname,propertyname)
    else:
	addToDataTypeDict(propertyname,rangetype)
    PREDICATES[propertyname]="DUMMY"
    if (not domain in CLASSTOPROPERTYMAP):
	CLASSTOPROPERTYMAP[domain]=[]
	tup=(propertyname,rangetype)
	CLASSTOPROPERTYMAP[domain].append(tup)
    else:
	found=False
	tuplist=CLASSTOPROPERTYMAP[domain]
	for t in tuplist:
	    tp,tr=(t)
	    if (tp == propertyname):
		found=True
		break
	if (not found):
	    tup=(propertyname,rangetype)
	    CLASSTOPROPERTYMAP[domain].append(tup)
	
    return


#-----------------------------------------------------------------------------------
## Purpose: Declare a subclass with special concern for hier classes and derived classes
# Arguments:
#  @clazz the new class
#  @subclazz the ancestor class
#  @srcdatacontent Column number in sheet
#  @datacontent Data supplied in graphML file.
def declareSubclass(clazz,subclazz,srcdatacontent,datacontent):
    if (len(srcdatacontent.strip()) > 0 and len(datacontent.strip()) > 0):
	#We have a hier class, check for slashes to be sure
	if (srcdatacontent.find("/") > -1 and datacontent.find("/") > -1):
	    emitDeclaration(PREFIX_WITHCOLON+srcdatacontent[1:].replace("/",SUBCLASSNAMESEPARATOR)+" rdfs:subClassOf "+PREFIX_WITHCOLON+datacontent[1:].replace("/",SUBCLASSNAMESEPARATOR)+" .")
	    return
    elif (len(srcdatacontent.strip()) > 0):
	# We have a conditional class dependent on any content in the column number (srcdatacontent)
	emitDeclaration('${ExistsSubClass("'+clazz+'","rdfs:subClassOf", "'+subclazz+'",'+srcdatacontent+')}')
	return

    print ""

    emitDeclaration(clazz+" rdfs:subClassOf "+subclazz+" .")
    print ""
    declareObjectProperty(clazz,""+PREFIX_WITHCOLON+"isSubClassInstanceOf",subclazz)
    print ""
    return

#-----------------------------------------------------------------------------------
## Purpose:Decide if we need a sequenced (temporal) uri or unsequenced.
# Arguments:
#  @clazzname
def getClassURI(clazzname):
    if (isTemporal(clazzname)):
	return "temporalClassURI"
    else:
	return "classURI"


#-----------------------------------------------------------------------------------
## Purpose:Is clazzname a temporal class or derived from one?
# Arguments:
#  @clazzname
def isTemporal(clazzname):
    global INHERITANCEMAP
    global CLASSTOPROPERTYMAP

    ## Case 1: Name
    if (clazzname.lower().find('temporal') > -1):
	return True

    #Case 2 : Subclassof
    subclazz=getSubClass(INHERITANCEMAP,clazzname)
    if (subclazz.lower().find('temporal') > -1):
	return True
    
    #Case 3 : Class is referred by a property going from a temporal
    for key,val in CLASSTOPROPERTYMAP.items():
	for item in val:
	    (propertyname,rangetype)=item
	    if (rangetype == clazzname):
		if (key.lower().find('temporal') > -1):
		    return True
    return False
    

#-----------------------------------------------------------------------------------
## Purpose: Declare the subclass relationship between two classes.
#           clazz is subclassinstance of subclazz
# Arguments:
#  @clazz ancestor class
#  @src clazz id
#  @subclazz new class
#  @subsrc subclass id
#  @property name of property to describe relationship
#  @srcdatacontent any content of the graphML data field

def declareInstanceLinkage(clazz,src,subclazz,subsrc,property,srcdatacontent):
    # Look for clazz in  inheritancemap keys
    # if found make vale new key and recurse
    # if last value has a defClass in it we skip.
    
    root=getRootClass(INHERITANCEMAP,clazz.strip())
    if (root.startswith(PREFIX_WITHCOLON+DEFCLASS)):
	# The classname needs to be full path and not just bbkmm:Other,so cannot use only clazzname here
	# Can we omit if both are the same? check 
	emitDeclaration('${DeclareDefLinkage('+
			PREFIX_WITHCOLON+srcdatacontent[1:].replace("/",SUBCLASSNAMESEPARATOR)+','+
			src.strip()+','+
			property+','+
			subclazz.strip()+','+
			subsrc.strip()+','+
			srcdatacontent+','+
			getClassURI(clazz.strip())+','+
			getClassURI(subclazz.strip())+
			')}')
    elif (len(srcdatacontent) > 0):
	emitDeclaration('${ExistsLinkage('+
			clazz.strip()+','+
			src.strip()+','+
			property+','+
			subclazz.strip()+','+
			subsrc.strip()+','+
			srcdatacontent+','+
			getClassURI(clazz.strip())+','+
			getClassURI(subclazz.strip())+
			')}')

    else:
	emitDeclaration('${DeclareDefLinkage('+
			clazz.strip()+','+
			src.strip()+','+
			property+','+
			subclazz.strip()+','+
			subsrc.strip()+','+
			srcdatacontent+','+
			getClassURI(clazz.strip())+','+
			getClassURI(subclazz.strip())+
			')}'
			)
    print ""
    return

#-----------------------------------------------------------------------------------
## Purpose: Generate class declaration from node
# Arguments:
#  @node node
def processNode(node):
    ntypenode=node.find("y:shape")
    datanodes=node.find("data",{"key":DESCRIPTIONNODENAME})
    datacontent=""
    if (datanodes != None):
        for subnode in datanodes:
            datacontent= subnode

    ntype=ntypenode["type"]
    if (ntype == "roundrectangle"):
        #we have a class decl
        clazzname = node.find("y:nodelabel").text.strip()
        if (clazzname.startswith(PREFIX)):
            print ""
            emitDeclaration(clazzname+" a    owl:Class, rdfs:Class;")
            emitDeclaration("rdfs:label           \""+clazzname+"Class\"@en ;")
            emitDeclaration("rdfs:comment         \""+clazzname+"Class\"@en .")
            CLAZZES.append(clazzname)
	    CLASSDATADICT[clazzname]=datacontent
	    CLASSNODENUMBERDICT[clazzname]=str(node['id'])
	elif (clazzname.startswith(DEFCLASS)):
            emitDeclaration("")
            emitDeclaration(PREFIX_WITHCOLON+clazzname+" a    owl:Class, rdfs:Class;")
            emitDeclaration("rdfs:label           \""+clazzname+"Class\"@en ;")
            emitDeclaration("rdfs:comment         \""+clazzname+"Class\"@en .")
            CLAZZES.append(clazzname)
	    CLASSDATADICT[clazzname]=datacontent
	    CLASSNODENUMBERDICT[clazzname]=str(node['id'])
        else:
            while getattr(node, 'edge', None):
                s = s.nextSibling
                print "S:"+s
    elif (ntype == "rectangle"):
        pnode= node.find("y:nodelabel")
        if (pnode != None):
            prefixes= pnode.text.strip()
            emitDeclaration(" @prefix "+prefixes)
            emitDeclaration("\n")
    return

#-----------------------------------------------------------------------------------
## Purpose: Process edge to generate predicates or subclassing
# Arguments:
#  @edge edge
#  @nodes list of nodes
def processEdge(edge,nodes):
    global INHERITANCEMAP

    edgename=edge.find("y:edgelabel").text.strip()
    src=edge["source"]
    target=edge["target"]

    for node in nodes:
        if (node['id'] == src):
            srcnode=node
            break
    for node in nodes:
        if (node['id'] == target):
            targetnode=node
            break

    srclabel=srcnode.find("y:nodelabel").text.strip()
    targetlabel=targetnode.find("y:nodelabel").text.strip()
    datanodes=targetnode.find("data",{"key":DESCRIPTIONNODENAME})
    datacontent=""
    if (datanodes != None):
        for subnode in datanodes:
            datacontent= subnode
	    
    srcdatanodes=srcnode.find("data",{"key":DESCRIPTIONNODENAME})
    srcdatacontent=""
    if (srcdatanodes != None):
        for subnode in srcdatanodes:
            srcdatacontent= subnode
	    
    
    colon	   = srclabel.find(":")+1
    clazz	   = srclabel
    targettypenode = targetnode.find("y:shape")
    targetntype	   = targettypenode["type"]
    srctypenode	   = srcnode.find("y:shape")
    srcntype	   = srctypenode["type"]
    
    if (srcntype == "roundrectangle" and targetntype == "roundrectangle" and edgename.find("rdfs:") < 0):
            declareObjectProperty(srclabel,edgename,targetlabel)
            if (edgename.find(":") >= 0):
		subclass=getSubClass(INHERITANCEMAP,srclabel)
		if (subclass != srclabel):
		    emitDeclaration('${'+getClassURI(getSubClassForProperty(INHERITANCEMAP,srclabel,edgename))+'("'+getSubClassForProperty(INHERITANCEMAP,srclabel,edgename)+'",'+src+')} '+edgename+' ${'+getClassURI(targetlabel)+'("'+targetlabel+'",'+target+')} .')
		else: 
		    # Check if we have an inherited property
		    parent=getParentClass(INHERITANCEMAP,srclabel)
		    if (parent == srclabel):
			emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,srclabel))+'("'+getSubClass(INHERITANCEMAP,srclabel)+'",'+src+')} '+edgename+' ${'+getClassURI(targetlabel)+'("'+targetlabel+'",'+target+')} .')
		    else:
			emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,srclabel))+'("'+getSubClass(INHERITANCEMAP,srclabel)+'",'+src+')} '+edgename+' ${'+getClassURI(targetlabel)+'("'+targetlabel+'",'+target+')} .')
			
            elif (targetlabel.find(DEFCLASS) < 0 ):
                emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,srclabel))+'("'+getSubClass(INHERITANCEMAP,srclabel)+'",'+src+')} '+PREFIX_WITHCOLON+edgename+' ${'+getClassURI(targetlabel)+'("'+targetlabel+'",'+target+')} .')
		# Excluding ranges and normal has object properties  but including def accessors
		if (edgename.find(DEFRANGE) < 0 and edgename.find(DEF) >= 0):
		    # We need to generate an instance of that object property as well
		    # of the correct labels
		    emitDeclaration('${'+getClassURI(targetlabel)+'("'+targetlabel+'",'+target+')}'+'  ${property("'+PREFIX_WITHCOLON+HAS+edgename.replace(DEF,"")+'","xsd:string",'+datacontent+')} .')
                
    elif (srcntype == "roundrectangle" and targetntype == "roundrectangle" and edgename.find("rdfs:") >= 0):
        # classX rdfs:subClassOf classY
        # Add classhier here
        if (edgename.lower() == "rdfs:subclassof"):
            addSubClass(targetlabel,srclabel)
	    declareSubclass(srclabel,targetlabel,srcdatacontent,datacontent)
	    ## Declare the hierarchy linkage between instances
	    declareInstanceLinkage(srclabel,src,targetlabel,target,PREFIX_WITHCOLON+"isSubClassInstanceOf",srcdatacontent)
	    # Find the base class
	    npath=getNodePath(srcnode['id'])
	    base=npath.split("/")[0]
	    # Create the accessor name
	    accessor=base.replace(DEFCLASS,DEF)
	    ddictkey=DEFRANGE+srclabel.replace(PREFIX_WITHCOLON,"")
	    if (base in CLASSDATADICT):
	        basecontent=CLASSDATADICT[base]
	        bc=basecontent.split(",")
	        if (base.find(DEFCLASS) >= 0 and base != targetlabel):
	            # Create the data statement as a post op and collect all the data needed in a dict
	            # with the same name as the defclass
	            if (not base in SUBCLASSDATADICT):
		        SUBCLASSDATADICT[base]=[]
		    SUBCLASSDATADICT[base].append(datacontent)
	            #now data statement into list specific to base
	            bc=basecontent.split(",")
		    if (len(srcdatacontent.strip()) > 0 ):
		      #We have a hier class, check for slashes to be sure
		      if (srcdatacontent.find("/") > -1 ):
			  # We need to overcome the same classname problem in the inheritancemap for hierarchies
			  # This needs to be fixed for real with full classnames in the map.
		          emitDeclaration('${altSubClass("'+PREFIX_WITHCOLON+BASENODENAME+'",'+
					  str(BASENODEID)+
					  ',"'+accessor+
					  '","'+PREFIX_WITHCOLON+srcdatacontent[1:].replace("/",SUBCLASSNAMESEPARATOR)+
					  '","'+srcdatacontent+'","'+bc[0]+'")}')
		      else:
		          emitDeclaration('${altSubClass("'+PREFIX_WITHCOLON+BASENODENAME+'",'+str(BASENODEID)+',"'+accessor+'","'+srclabel+'","'+srcdatacontent+'","'+bc[0]+'")}')
		    else:
		        emitDeclaration('${altSubClass("'+PREFIX_WITHCOLON+BASENODENAME+'",'+str(BASENODEID)+',"'+accessor+'","'+srclabel+'","'+srcdatacontent+'","'+bc[0]+'")}')
		elif (base.find(DEFCLASS) >= 0 ):
		    # We are looking at baseclass and need to output altclass template
		    emitDeclaration('${altSubClass("'+PREFIX_WITHCOLON+BASENODENAME+'",'+str(BASENODEID)+',"'+accessor+'","'+PREFIX_WITHCOLON+srcdatacontent[1:].replace("/",SUBCLASSNAMESEPARATOR)+'","'+srcdatacontent+'","'+bc[0]+'")}')
		elif (not ddictkey in DATATYPEDICT):
		    # Not a defclass, just plain inheritance. We need to create the properties
		    # Each property will need to be explicitly defined as they are column driven
		    if (base in CLASSTOPROPERTYMAP):
			proptuples=CLASSTOPROPERTYMAP[base]
			for tup in proptuples:
			    pname,ptype=(tup)
			    emitDeclaration('${ExistsProperty('+getClassURI(srclabel.strip())+','+
					    '"'+srclabel+'",'+
					    src+','+
					    srcdatacontent+',"'+pname+
					    '","'+ptype+'")}')
		    

    elif (srclabel.startswith(PREFIX) and edgename.find("rdfs:")<0 and targetlabel.find(PREFIX+":")<0):
        if (edgename.find(":") > -1):
            emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,clazz))+'("'+getSubClass(INHERITANCEMAP,clazz)+'" ,'+src+')}'+" "+"${property(\""+edgename+"\",\""+targetlabel+"\","+datacontent+")} .")
        else:
            # This is where instances are declared. We collect the uri and the values for later declaration of a List of values
	    if (edgename.find(NAMEDINSTANCE) > -1):
		# Declare the hasnamedinstance
		params=datacontent.split(",")
		dtype=params[0]
		emitDeclaration('${classGlobalURI("'+getSubClass(INHERITANCEMAP,clazz)+'",'+edgename.replace(NAMEDINSTANCE,"")+')}  ${property("'+PREFIX_WITHCOLON+"hasName"+'",'+dtype+','+targetlabel+',"Visible")} .')
		# Add to lists so we get a list defined with all the values
		addToListForDeclaration(getSubClass(INHERITANCEMAP,clazz),targetlabel)

		# If this is a namedinstance we generate the ISNAMEDINSTANCE property
		isprop=getSubClass(INHERITANCEMAP,clazz).replace(HAS,"").replace(PREFIX_WITHCOLON,'')
		isprop=PREFIX_WITHCOLON+IS+isprop+"NamedInstance"
		emitDeclaration('${altNamedInstance("'+getSubClass(INHERITANCEMAP,clazz)+'",'+src+','+" a "+','+targetlabel+','+edgename.replace(NAMEDINSTANCE,"")+','+datacontent+')}' )
	    elif (not iscomplextype(PREFIX_WITHCOLON+edgename)):
		if (len(datacontent) > 0):
		    emitDeclaration('${'+getClassURI(getSubClassForProperty(INHERITANCEMAP,clazz,PREFIX_WITHCOLON+edgename))+'("'+getSubClassForProperty(INHERITANCEMAP,clazz,PREFIX_WITHCOLON+edgename)+'",'+src+')}  ${property("'+PREFIX_WITHCOLON+edgename+'","'+targetlabel.replace('"','')+'",'+datacontent+')} .')

    elif (targetntype == "ellipse"):
        datanodes=targetnode.find("data",{"key":DESCRIPTIONNODENAME})
        datacontent=""
        if (datanodes != None):
            for subnode in datanodes:
                datacontent= subnode.strip()
        pnode= targetnode.find("y:nodelabel")
        if (pnode != None):
            pvalue= pnode.text.strip()
	if (edgename.startswith(URI)):
	    edgename=edgename.replace(URI,PREFIX)
            emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,clazz))+'("'+getSubClass(INHERITANCEMAP,clazz)+'",'+src+')}'+" "+edgename+" ${DATACONTENT("+datacontent+')}  .')
        elif (datacontent.find("xsd:") < 0):
            emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,clazz))+'("'+getSubClass(INHERITANCEMAP,clazz)+'",'+src+')}'+" "+edgename+" "+'"'+pvalue+'" .')
        else:
            emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,clazz))+'("'+getSubClass(INHERITANCEMAP,clazz)+'",'+src+')}'+" "+edgename+" \""+pvalue+'"^^'+datacontent+' .')
            
    elif ( edgename.find("rdfs:")<0 ):
        if (targetlabel.find("xsd:")>=0):
            if (edgename.find(":") > -1):
                emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,clazz))+'("'+getSubClass(INHERITANCEMAP,clazz)+'",'+src+')}'+" "+"${property(\""+edgename+"\",\""+targetlabel+"\","+datacontent+")} .")
            else:
                emitDeclaration('${'+getClassURI(getSubClass(INHERITANCEMAP,clazz))+'("'+getSubClass(INHERITANCEMAP,clazz)+'",'+src+')}  ${property("'+PREFIX_WITHCOLON+edgename+'","'+targetlabel+'",'+datacontent+')} .')
                
    elif (  targetlabel.find(PREFIX_WITHCOLON)<0):
        if (edgename.find(":")> -1):
            print  srclabel+" "+edgename+" "+targetlabel+" ."
            # Add classhier here
            if (edgename.lower() == "rdfs:subclassof"):
                addSubClass(srclabel,targetlabel)
        else:
            emitDeclaration(srclabel+' '+PREFIX_WITHCOLON+edgename+' '+targetlabel+' .')
    else:
        emitDeclaration(srclabel+"  "+edgename+" "+targetlabel+" .")


    return


#-----------------------------------------------------------------------------------
## Purpose: Generate classes resulting from hierarchies 
# Arguments:
#  @edge edge
#  @nodes list of nodes
#
def processEdgeProperties(edge,nodes):
    edgename=edge.find("y:edgelabel").text.strip()

    src	   = edge["source"]
    target = edge["target"]
    
    for node in nodes:
        if (node['id'] == src):
            srcnode=node
            break
    for node in nodes:
        if (node['id'] == target):
            targetnode=node
            break

    srclabel	= srcnode.find("y:nodelabel").text.strip()
    targetlabel	= targetnode.find("y:nodelabel").text.strip()
    datanodes	= targetnode.find("data",{"key":DESCRIPTIONNODENAME})
    datacontent	= ""
    if (datanodes != None):
        for subnode in datanodes:
            datacontent= subnode

    
    colon=srclabel.find(":")+1
    clazz=srclabel
    
        
    
    targettypenode=targetnode.find("y:shape")
    targetntype=targettypenode["type"]
    

    if (srclabel.startswith(PREFIX) and edgename.find("rdfs:")<0 and targetlabel.find(PREFIX_WITHCOLON)<0):
        if (edgename.find(":") > -1):
            dummy=1
        elif (targetntype != "roundrectangle"):
            ### This is where the instance properties are handled
	    if (edgename.startswith(NAMEDINSTANCE)):
		noop=0
	    else:
		declareProperty(clazz,""+PREFIX_WITHCOLON+edgename,targetlabel)
	    
    elif (targetntype == "ellipse"):
        datanodes=targetnode.find("data",{"key":DESCRIPTIONNODENAME})
        datacontent=""
        if (datanodes != None):
            for subnode in datanodes:
                datacontent= subnode.strip()
        pnode= targetnode.find("y:nodelabel")
        if (pnode != None):
            pvalue= pnode.text.strip()
	    # Check for uri
	if (edgename.startswith(URI)):
	    # Declare the uri property
	    declareObjectProperty(clazz,""+edgename.replace(URI,PREFIX),targetlabel)
	    
            
    elif ( edgename.find("rdfs:")<0 ):
        if (targetlabel.find("xsd:")>=0):
            if (edgename.find(":") > -1):
                declareProperty(clazz,""+edgename,targetlabel)
            else:
                dummy=1
                
    elif (  targetlabel.find(PREFIX_WITHCOLON)<0):
        if (edgename.find(":")> -1):
            dummy=1
        else:
            dummy=1
    else:
        dummy=1


    return
    

#-----------------------------------------------------------------------------------
## Purpose:Finds the node with the description of the data in the GraphML file from the header.
# Arguments:
#  @gmlkeys
def getDescriptionNodeName(gmlkeys):
    for k in gmlkeys:
	if (k["attr.name"] == "description"):
	    return k["id"]
	
    return "ERROR: CANNOT FIND NODE WITH DESCRIPTION IN GRAPHML FILE"

#<key attr.name="description" attr.type="string" for="node" id="d6"/>

#-----------------------------------------------------------------------------------
## Purpose: Return node with id
# Arguments:
#  @id id to look for
#  @nodes list of nodes
def getNodeWithId(id,nodes):
    for node in nodes:
	if (node['id'] == id):
	    label=node.find("y:nodelabel").text.strip()
	    return label
    return None



#-----------------------------------------------------------------------------------
## Purpose: Return the edge that points to a specific node
# Arguments:
#  @node Node to look for
#  @edges list of edges
#  @nodes list of nodes
def getEdgewithTarget(node,edges,nodes):
    for edge in edges:
	if (edge['source'] == node):
	    return edge['target']
    return None

#-----------------------------------------------------------------------------------
## Purpose:Generate a path to the node via ancestor class
# Arguments:
#  @idl list of nodes
#  @nodes list of nodes
def getNodePathName(idl,nodes):
    np=""
    for p in idl:
	np=np+"/"+getNodeWithId(p,nodes)
    return np[1:]
#-----------------------------------------------------------------------------------
## Purpose: Generate list of nodes on path to id
# Arguments:
#  @id node to look for
#  @edges list ef edges
#  @nodes list of nodes
def getNodePathIds(id,edges,nodes):
    idl=[]
    idl.append(id)
    nno=getEdgewithTarget(id,edges,nodes)
    while(nno != None):
	idl.append(nno)
	nno=getEdgewithTarget(str(nno),edges,nodes)
    
    return idl


#-----------------------------------------------------------------------------------
## Purpose:Convert list of nodes to string path
#
# Arguments:
#  @id id to look for
def getNodePath(id):
    global NODES
    global EDGES
    ipath=getNodePathIds(id,EDGES,NODES)
    ppath=getNodePathName(ipath[::-1],NODES)
    
    return ppath

#-----------------------------------------------------------------------------------
# MAIN STARTING
#-----------------------------------------------------------------------------------

if (sys.argv[1]):
    fp = str(sys.argv[1])
else:
    fp = "museumontology.graphml"

if (sys.argv[2]):
    processinglabel=sys.argv[2]
else:
    processinglabel="mainsheet"
    

with open(fp) as file:
    soup = BeautifulSoup(file, "lxml")



NODES = soup.findAll("node")
EDGES = soup.findAll("edge")


gmlkeys = soup.findAll('key',{"attr.name":True})
DESCRIPTIONNODENAME=getDescriptionNodeName(gmlkeys)




### PASS 1. No declarations emitted
EMITTING  = False

for node in NODES:
    processNode(node)

for edge in EDGES:
    processEdgeProperties(edge,NODES)

for edge in EDGES:
    processEdge(edge,NODES)

### PASS 2. Emit declarations
EMITTING   =True

print "#################################################################"
print "#"
print "#$Content classes"
print "#"
print "#################################################################"
print ""

for node in NODES:
    processNode(node)

for edge in EDGES:
    processEdgeProperties(edge,NODES)




print "#################################################################"
print "#"
print "#$Individuals"
print "#"
print "#################################################################"
print ""
for edge in EDGES:
    processEdge(edge,NODES)

print generateListDeclarations(processinglabel)    
print
print generateDataTypeList(processinglabel)


