#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""
Documentation
===============


#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3

"""

from . import datautils


class bbkmm_English_District_or_Borough(object):
    _listofcontainedby= [6,8]
    _listofclazzes=[ 
		"bbkmm:English_County",
		"bbkmm:English_CA"
	]
    _listofnodes=["n7","n11"]
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def __init__(self):
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def bbkmm_hasTypedName(self,clazzname,nodename,propertyname,clazzdata,rangetype,
		      symboltable,rowmodel,matrixmodel):
        column=int(clazzdata)
	if (len(rowmodel[column].strip()) > 0):
	    parts=rowmodel[column].strip().split(":")
	    return parts[0]+'"'+"^^"+rangetype.replace('"','')
	else:
	    return ""


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def bbkmm_hasName(self,clazzname,nodename,propertyname,clazzdata,rangetype,
		      symboltable,rowmodel,matrixmodel):
        column=int(clazzdata)
	#print "LEN"+str(len(rowmodel[column].strip()))
	#print "["+rowmodel[column].strip()+"]"
	if (len(rowmodel[column].strip()) > 0):
	    parts=rowmodel[column].strip().split(":")
	    lparen=parts[0].find("(")
	    lparen=lparen-1
	    return parts[0][0:lparen]+'"'+"^^"+rangetype.replace('"','')
	else:
	    return ""


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def bbkmm_hasONSid(self,clazzname,nodename,propertyname,clazzdata,rangetype,
		       symboltable,rowmodel,matrixmodel):
        column=int(clazzdata)
	if (len(rowmodel[column].strip()) > 0):
	    parts=rowmodel[column].strip().split(":")
	    return '"'+parts[1]+"^^"+rangetype.replace('"','')
	else:
	    return ""


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def bbkmm_containedBy(self,clazzname,nodename,propertyname,clazzdata,rangetype,
			  symboltable,rowmodel,matrixmodel):

        column=int(clazzdata)
	if (len(rowmodel[column].strip()) > 0):
		link='${classURI("%s",%s,%s)}'
		statements=[]
		for i, cols in enumerate(bbkmm_English_District_or_Borough._listofcontainedby):
		    if (len(rowmodel[cols].strip()) > 0):
			parts=rowmodel[cols].strip().split(":")
			statementtemplate=link % (bbkmm_English_District_or_Borough._listofclazzes[i],
						  bbkmm_English_District_or_Borough._listofnodes[i],datautils.stripType(parts[0]))
			statements.append(statementtemplate)

		parts=rowmodel[column].strip().split(":")
		if (parts[1].startswith("E090")):
		    parts=rowmodel[column].strip().split(":")
		    statementtemplate=link % ("bbkmm:English_Region","n8","London")
		    statements.append(statementtemplate)

		return statements
	return ""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def bbkmm_contains(self,clazzname,nodename,propertyname,clazzdata,rangetype,
		       symboltable,rowmodel,matrixmodel):
	return ""


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

