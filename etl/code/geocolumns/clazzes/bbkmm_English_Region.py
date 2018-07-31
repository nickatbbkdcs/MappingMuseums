#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""
Documentation
===============

#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3

matrixmodel[symboltable['count']] = rowmodel


"""

from . import datautils

class bbkmm_English_Region(object):

    _contained=1

    _listofcontains= [6,8,7,9]
    _listofclazzes=[ 
		"bbkmm:English_County",
		"bbkmm:English_CA",
		"bbkmm:English_UA",
		"bbkmm:English_District_or_Borough"
	]
    _listofnodes=["n7","n11","n10","n9"]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def __init__(self):
        return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def bbkmm_hasTypedName(self,clazzname,nodename,propertyname,clazzdata,rangetype,
		      symboltable,rowmodel,matrixmodel):
        column=int(clazzdata)
	if (len(rowmodel[column]) > 0):
	    parts=rowmodel[column].strip().split(":")
	    return parts[0]+'"'+"^^"+rangetype.replace('"','')
	else:
	    return ""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def bbkmm_hasName(self,clazzname,nodename,propertyname,clazzdata,rangetype,
		      symboltable,rowmodel,matrixmodel):
        column=int(clazzdata)
	if (len(rowmodel[column]) > 0):
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
	if (len(rowmodel[column]) > 0):
	    parts=rowmodel[column].strip().split(":")
	    return '"'+parts[1]+"^^"+rangetype.replace('"','')
	else:
	    return ""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def bbkmm_containedBy(self,clazzname,nodename,propertyname,clazzdata,rangetype,
			  symboltable,rowmodel,matrixmodel):
        
        column=int(clazzdata)
	if (len(rowmodel[column]) > 0):
	    if (len(rowmodel[bbkmm_English_Region._contained]) > 0):
		link='${classURI("%s",%s,%s)}'
		parts=rowmodel[bbkmm_English_Region._contained].strip().split(":")
		statementtemplate=link % ("bbkmm:Country","n3",datautils.stripType(parts[0]))
		return statementtemplate
	return ""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


    def bbkmm_contains(self,clazzname,nodename,propertyname,clazzdata,rangetype,
		       symboltable,rowmodel,matrixmodel):


        column=int(clazzdata)
	if (len(rowmodel[column].strip()) > 0):
		link='${classURI("%s",%s,%s)}'
		statements=[]
		for i, cols in enumerate(bbkmm_English_Region._listofcontains):
		    if (len(rowmodel[cols].strip()) > 0):
			parts=rowmodel[cols].strip().split(":")
			statementtemplate=link % (bbkmm_English_Region._listofclazzes[i],
						  bbkmm_English_Region._listofnodes[i],datautils.stripType(parts[0]))
			statements.append(statementtemplate)

		#statementtemplate=link % ("bbkmm:English_Region","n8","London")
		#statements.append(statementtemplate)
		return statements
	return ""


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
