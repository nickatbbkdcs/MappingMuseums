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

class bbkmm_Country(object):
    
    _root="<http://bbk.ac.uk/MuseumMapProject/def/AdminArea/id/n1/AdminArea>"
    _countries={"England":5,
                "Wales":2,
                "Scotland":3,
                "Northern Ireland":4
                }
    _contains={"England":"bbkmm:English_Region",
                "Wales":"bbkmm:Welsh_UA",
                "Scotland":"bbkmm:Scottish_Council_Area",
                "Northern Ireland":"bbkmm:NI_Loc_Gov_District"
                }
    _nodes={"England":"n8",
            "Wales":"n4",
            "Scotland":"n5",
            "Northern Ireland":"n6"
                }
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
            return parts[0]+'"'+"^^"+rangetype.replace('"','')
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

        return bbkmm_Country._root

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def bbkmm_contains(self,clazzname,nodename,propertyname,clazzdata,rangetype,
                       symboltable,rowmodel,matrixmodel):
        column=int(clazzdata)
        parts=rowmodel[column].strip().split(":")
        key=parts[0].replace('"','')
        if (key in bbkmm_Country._countries):
            if (len(rowmodel[bbkmm_Country._countries[key]]) > 0):
                link='${classURI("%s",%s,%s)}'
                parts=rowmodel[bbkmm_Country._countries[key]].strip().split(":")
                statementtemplate=link % (bbkmm_Country._contains[key],bbkmm_Country._nodes[key],parts[0])
                return statementtemplate

        return ""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
