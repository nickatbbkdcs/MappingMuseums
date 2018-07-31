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


class bbkmm_Scottish_Council_Area(object):
    
    _contained=1
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
	    column=int(bbkmm_Scottish_Council_Area._contained)
	    if (len(rowmodel[column]) > 0):
		link='${classURI("%s",%s,%s)}'		
		parts=rowmodel[column].strip().split(":")
		statementtemplate=link % ("bbkmm:Country","n3",datautils.stripType(parts[0]))
		return statementtemplate
	return ""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    def bbkmm_contains(self,clazzname,nodename,propertyname,clazzdata,rangetype,
		       symboltable,rowmodel,matrixmodel):
	return ""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
