##
# @file
# This module implements : 1. All the methods for accessing the ONS data for locations.
#                          2. All the definitions used in processing the ONS data.
#                          3. The query engine used in search.
#                           
#  
#  
#  
#  
#  
#  
#  
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import Form
from wtforms import StringField, SubmitField,RadioField,SelectField
from wtforms.validators import Required
from flask import request
from flask.views import View
from flask  import Blueprint

from jinja2 import TemplateNotFound


import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
import operator

import sys
import time
import re
import cgi
import copy
import importlib
import inspect
import os

from flask import current_app as app

from . import listman
from . import definitions
from app.main import datatypes


REVERSE_COUNTRY_TRANSLATION_TABLE={
    "England":"E92000001",
    "Channel Islands":"L93000001",
    "Isle of Man":"M83000003",
    "Northern Ireland":"N92000002",
    "Scotland":"S92000003",
    "Wales":"W92000004"
    }


COUNTRY_TRANSLATION_TABLE={
    "E92000001":"England",
    "L93000001":"Channel Islands",
    "M83000003":"Isle of Man",
    "N92000002":"Northern Ireland",
    "S92000003":"Scotland",
    "W92000004":"Wales"
    }

#cat NSPL_AUG_2017_UK.csv | awk -F, '{print $16}' | sort -u

COUNTY_TRANSLATION_TABLE={
    "E10000002"	: "Buckinghamshire",		
#    "E10000003"	: "Cambridgeshire",		
    "E10000006"	: "Cumbria",		
    "E10000007"	: "Derbyshire",		
    "E10000008"	: "Devon",		
    "E10000009"	: "Dorset",		
    "E10000011"	: "East Sussex",		
    "E10000012"	: "Essex",		
    "E10000013"	: "Gloucestershire",		
    "E10000014"	: "Hampshire",		
    "E10000015"	: "Hertfordshire",		
    "E10000016"	: "Kent",		
    "E10000017"	: "Lancashire",		
    "E10000018"	: "Leicestershire",		
    "E10000019"	: "Lincolnshire",		
    "E10000020"	: "Norfolk",		
    "E10000021"	: "Northamptonshire",		
    "E10000023"	: "North Yorkshire",		
    "E10000024"	: "Nottinghamshire",		
    "E10000025"	: "Oxfordshire",		
    "E10000027"	: "Somerset",		
    "E10000028"	: "Staffordshire",		
    "E10000029"	: "Suffolk",		
    "E10000030"	: "Surrey",		
    "E10000031"	: "Warwickshire",		
    "E10000032"	: "West Sussex",		
    "E10000034"	: "Worcestershire",		
    "E99999999"	: "(pseudo) England (UA/MD/LB",		
    "L99999999"	: "(pseudo) Channel Islands",		
    "M99999999"	: "(pseudo) Isle of Man",		
    "N99999999"	: "(pseudo) Northern Ireland",		
    "S99999999"	: "(pseudo) Scotland",		
    "W99999999"	: "(pseudo) Wales"		
    }

REVERSE_COUNTY_TRANSLATION_TABLE={
    "Buckinghamshire" :     "E10000002",		
    #    "E10000003"	: "Cambridgeshire",		
    "Cumbria" :     "E10000006",		
    "Derbyshire" :     "E10000007",		
    "Devon" :     "E10000008",		
    "Dorset" :     "E10000009",		
    "East Sussex" :     "E10000011",		
    "Essex" :     "E10000012",		
    "Gloucestershire" :     "E10000013",		
    "Hampshire" :     "E10000014",		
    "Hertfordshire" :     "E10000015",		
    "Kent" :     "E10000016",		
    "Lancashire" :     "E10000017",		
    "Leicestershire" :     "E10000018",		
    "Lincolnshire" :     "E10000019",		
    "Norfolk" :     "E10000020",		
    "Northamptonshire" :     "E10000021",		
    "North Yorkshire" :     "E10000023",		
    "Nottinghamshire" :     "E10000024",		
    "Oxfordshire" :     "E10000025",		
    "Somerset" :     "E10000027",		
    "Staffordshire" :     "E10000028",		
    "Suffolk" :     "E10000029",		
    "Surrey" :     "E10000030",		
    "Warwickshire" :     "E10000031",		
    "West Sussex" :     "E10000032",		
    "Worcestershire" :     "E10000034",		
    "(pseudo) England (UA/MD/LB" :     "E99999999",		
    "(pseudo) Channel Islands" :     "L99999999",		
    "(pseudo) Isle of Man" :     "M99999999",		
    "(pseudo) Northern Ireland" :     "N99999999",		
    "(pseudo) Scotland" :     "S99999999",
    "(pseudo) Wales" : "W99999999"	
    }


GOR_TRANSLATION_TABLE={
    "E12000001"	: "North East",
    "E12000002"	: "North West",
    "E12000003"	: "Yorkshire and The Humber",
    "E12000004"	: "East Midlands",
    "E12000005"	: "West Midlands",
    "E12000006"	: "East of England",
    "E12000007"	: "London",
    "E12000008"	: "South East",
    "E12000009"	: "South West",
    "W99999999"	: "(pseudo) Wales",
    "S99999999"	: "(pseudo) Scotland",
    "N99999999"	: "(pseudo) Northern Ireland",
    "L99999999"	: "(pseudo) Channel Islands",
    "M99999999"	: "(pseudo) Isle of Man"
    }

REVERSE_GOR_TRANSLATION_TABLE={
    "North East":"E12000001",
    "North West":"E12000002",
    "Yorkshire and The Humber":"E12000003",
    "East Midlands":"E12000004",
    "West Midlands":"E12000005",
    "East of England":"E12000006",
    "London":"E12000007",
    "South East":"E12000008",
    "South West":"E12000009",
    "(pseudo) Wales":"W99999999",
    "(pseudo) Scotland":"S99999999",
    "(pseudo) Northern Ireland":"N99999999",
    "(pseudo) Channel Islands":"L99999999",
    "(pseudo) Isle of Man":"M99999999"
    }


CA_CODE_TO_GOR_TABLE={
"E47000001":"E12000002",
"E47000002":"E12000003",
"E47000003":"E12000003",
"E47000004":"E12000002",
"E47000005":"E12000001",
"E47000006":"E12000001",
"E47000007":"E12000005",
"E47000008":"E12000006",
"E47000009":"E12000009"
}


# "LAD17CD,LAD17NM,CAUTH17CD,CAUTH17NM,FID"


CA_CODE_TO_NAME_TABLE={
"E47000001":"Greater Manchester",
"E47000002":"Sheffield City Region",
"E47000003":"West Yorkshire",
"E47000004":"Liverpool City Region",
"E47000005":"North East",
"E47000006":"Tees Valley",
"E47000007":"West Midlands",
"E47000008":"Cambridgeshire and Peterborough",
"E47000009":"West of England"
}

REVERSE_CA_CODE_TO_NAME_TABLE={
    "Greater Manchester" :     "E47000001",
    "Sheffield City Region" :     "E47000002",
    "West Yorkshire" :     "E47000003",
    "Liverpool City Region" :     "E47000004",
    "North East" :     "E47000005",
    "Tees Valley" :     "E47000006",
    "West Midlands" :     "E47000007",  
    "Cambridgeshire and Peterborough" :     "E47000008",
    "West of England":"E47000009"
}



LA_TO_CA_CODES_TABLE={
"E08000001":"E47000001",
"E08000002":"E47000001",
"E08000003":"E47000001",
"E08000004":"E47000001",
"E08000005":"E47000001",
"E08000006":"E47000001",
"E08000007":"E47000001",
"E08000008":"E47000001",
"E08000009":"E47000001",
"E08000010":"E47000001",
"E08000016":"E47000002",
"E08000017":"E47000002",
"E08000018":"E47000002",
"E08000019":"E47000002",
"E08000032":"E47000003",
"E08000033":"E47000003",
"E08000034":"E47000003",
"E08000035":"E47000003",
"E08000036":"E47000003",
"E06000006":"E47000004",
"E08000011":"E47000004",
"E08000012":"E47000004",
"E08000013":"E47000004",
"E08000014":"E47000004",
"E08000015":"E47000004",
"E06000047":"E47000005",
"E06000057":"E47000005",
"E08000021":"E47000005",
"E08000022":"E47000005",
"E08000023":"E47000005",
"E08000024":"E47000005",
"E08000037":"E47000005",
"E06000005":"E47000006",
"E06000001":"E47000006",
"E06000002":"E47000006",
"E06000003":"E47000006",
"E06000004":"E47000006",
"E08000025":"E47000007",
"E08000026":"E47000007",
"E08000027":"E47000007",
"E08000028":"E47000007",
"E08000029":"E47000007",
"E08000030":"E47000007",
"E08000031":"E47000007",
"E07000008":"E47000008",
"E07000009":"E47000008",
"E07000010":"E47000008",
"E07000011":"E47000008",
"E07000012":"E47000008",
"E06000031":"E47000008",
"E06000022":"E47000009",
"E06000023":"E47000009",
"E06000025":"E47000009"
}

LA_TO_CA_NAMES_TABLE={
"Bolton":"Greater Manchester",
"Bury":"Greater Manchester",
"Manchester":"Greater Manchester",
"Oldham":"Greater Manchester",
"Rochdale":"Greater Manchester",
"Salford":"Greater Manchester",
"Stockport":"Greater Manchester",
"Tameside":"Greater Manchester",
"Trafford":"Greater Manchester",
"Wigan":"Greater Manchester",
"Barnsley":"Sheffield City Region",
"Doncaster":"Sheffield City Region",
"Rotherham":"Sheffield City Region",
"Sheffield":"Sheffield City Region",
"Bradford":"West Yorkshire",
"Calderdale":"West Yorkshire",
"Kirklees":"West Yorkshire",
"Leeds":"West Yorkshire",
"Wakefield":"West Yorkshire",
"Halton":"Liverpool City Region",
"Knowsley":"Liverpool City Region",
"Liverpool":"Liverpool City Region",
"St. Helens":"Liverpool City Region",
"Sefton":"Liverpool City Region",
"Wirral":"Liverpool City Region",
"County Durham":"North East",
"Northumberland":"North East",
"Newcastle upon Tyne":"North East",
"North Tyneside":"North East",
"South Tyneside":"North East",
"Sunderland":"North East",
"Gateshead":"North East",
"Darlington":"Tees Valley",
"Hartlepool":"Tees Valley",
"Middlesbrough":"Tees Valley",
"Redcar and Cleveland":"Tees Valley",
"Stockton-on-Tees":"Tees Valley",
"Birmingham":"West Midlands",
"Coventry":"West Midlands",
"Dudley":"West Midlands",
"Sandwell":"West Midlands",
"Solihull":"West Midlands",
"Walsall":"West Midlands",
"Wolverhampton":"West Midlands",
"Cambridge":"Cambridgeshire and Peterborough",
"East Cambridgeshire":"Cambridgeshire and Peterborough",
"Fenland":"Cambridgeshire and Peterborough",
"Huntingdonshire":"Cambridgeshire and Peterborough",
"South Cambridgeshire":"Cambridgeshire and Peterborough",
"Peterborough":"Cambridgeshire and Peterborough",
"Bath and North East Somerset":"West of England",
"Bristol, City of":"West of England",
"South Gloucestershire":"West of England"
}


LA_TRANSLATION_TABLE={}
REVERSE_LA_TRANSLATION_TABLE={}

from . import model_to_view
modeltoview=model_to_view.Model_To_View()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
## Purpose:Small set of functions to change the appearance of names (strings)
def rotate(l, n):
    return l[n:] + l[:n]

import re

def snake2camel(name):
    return re.sub(r'(?:^|_)([a-z])', lambda x: x.group(1).upper(), name)
 
def snake2camelback(name):
    return re.sub(r'_([a-z])', lambda x: x.group(1).upper(), name)
 
def camel2snake(name):
    return name[0].lower() + re.sub(r'(?!^)[A-Z]', lambda x: '_' + x.group(0).lower(), name[1:])
 
def camelback2snake(name):
    return re.sub(r'[A-Z]', lambda x: '_' + x.group(0).lower(), name)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose: Reads the ONS csv data creates all dictionaries needed for processing
# Arguments:
# @fname                   name of ons file
# @lafname                 local authority definition file
# @postcode2_county_dict 
# @postcode2_country_dict 
# @postcode2_la_dict 
# @postcode2_region_dict 
# @county2_region_dict 
# @la2_county_dict 
# @la2_region_dict 
# @la_translation_dict 
# @reverse_la_translation_dict 

def readONSPCRepo(fname,
		  lafname,
		  postcode2_county_dict,
		  postcode2_country_dict,
		  postcode2_la_dict,
		  postcode2_region_dict,
		  county2_region_dict,
		  la2_county_dict,
		  la2_region_dict,
		  la_translation_dict,
		  reverse_la_translation_dict
		 
	       ):
    count=0
    with open(lafname) as f:
	content = f.readlines()
    f.close()


    for line in content:
	parts=line.split(',')
	la_translation_dict[parts[0].replace('"','')]=parts[1].replace('"','').replace('\n','').replace('\r','')
	reverse_la_translation_dict[parts[1].replace('"','').replace('\n','').replace('\r','')]=parts[0].replace('"','')
	#print parts[0]+'=='+parts[1]
	
#   pcd 0,pcd2 1,pcds 2,dointr 3,doterm 4,usertype 5,oseast1m 6,osnrth1m 7,osgrdind 8,oa11 9,cty 10,
#   laua 11,ward 12,hlthau 13,hro 14,ctry 15,gor 16,pcon 17,eer 18,teclec 19,ttwa 20,
#   pct 21,nuts 22,park 23,lsoa11 24,msoa11 25,wz11 26,ccg 27,bua11 28,buasd11 29,ru11ind 30,
#   oac11 31,lat 32,long 33,lep1 34,lep2 35,pfa 36 ,imd 37

    with open(fname) as f:
	content = f.readlines()
	header=content[0].split(',')
	lc=1
    f.close()


    header_dict={}
    hcount=0
    for h in header:
	header_dict[h.strip()]=hcount
	hcount=hcount+1

    keyerrors=0
    unknown=0
    print 'starting dict....'
    while (lc < len(content)):
	line=content[lc]
	line = line.strip()
	parts=line.split(',')
	pc=parts[header_dict['pcd 0']].replace('"','').replace(' ','')
	spc=str(pc)

	if (len(parts[header_dict['cty 10']].replace('"','')) >0):
	    if (parts[header_dict['cty 10']].replace('"','') in COUNTY_TRANSLATION_TABLE):
		county=str(COUNTY_TRANSLATION_TABLE[parts[header_dict['cty 10']].replace('"','')])
		postcode2_county_dict[spc]=county
	    else:
		postcode2_county_dict[spc]='UNKNOWN'
		unknown+=1
	else:
	    #print 'key is in error:'+ parts[header_dict['cty 10']].replace('"','')
	    keyerrors+=1
	    
	if (len(parts[header_dict['ctry 15']].replace('"','')) > 0):
	    if (parts[header_dict['ctry 15']].replace('"','') in COUNTRY_TRANSLATION_TABLE):
		postcode2_country_dict[spc]=str(COUNTRY_TRANSLATION_TABLE[parts[header_dict['ctry 15']].replace('"','')])
	    else:
		postcode2_country_dict[spc]='UNKNOWN'
		unknown+=1
	else:
	    #print 'key is in error:'+ parts[header_dict['ctry 15']].replace('"','')
	    keyerrors+=1

	if (len(parts[header_dict['laua 11']].replace('"','')) > 0):
	    if (parts[header_dict['laua 11']].replace('"','') in  la_translation_dict):
		la=str(la_translation_dict[parts[header_dict['laua 11']].replace('"','')])
		postcode2_la_dict[spc]=la
	    else:
		postcode2_la_dict[spc]='UNKNOWN'
		unknown+=1
	else:
	    keyerrors+=1

	if (len(parts[header_dict['gor 16']].replace('"','')) > 0):
	    if (parts[header_dict['gor 16']].replace('"','') in GOR_TRANSLATION_TABLE):
		gor=str(GOR_TRANSLATION_TABLE[parts[header_dict['gor 16']].replace('"','')])
		postcode2_region_dict[spc]=gor
	    else:
		postcode2_region_dict[spc]='UNKNOWN'
		unknown+=1
	else:
	    keyerrors+=1

	county2_region_dict[county]=gor
	la2_county_dict[la]=county
	la2_region_dict[la]=gor
	    
	    
	lc+=1
    f.close()
    print 'key errors were '+str(keyerrors)
    print 'unknown errors were '+str(keyerrors)
    return

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose: Reads district and county names.
# Arguments:
#  
# @fname name of file to read
def readNames(fname):
    adict={}
    lc=0
    with open(fname) as f:
	content = f.readlines()
	while (lc < len(content)):
	    line=content[lc]
	    parts=line.split(',')
	    adict[parts[0].strip()]=parts[1].strip()
            lc+=1
    f.close()
    adict['\\N']='UNKNOWN'
    adict['E99999999']='UNKNOWN'
    adict['L99999999']='UNKNOWN'
    adict['M99999999']='UNKNOWN'
    adict['S99999999']='UNKNOWN'
    adict['N99999999']='Northern Ireland,Belfast'
    adict['W99999999']='Cardiff Central,Wales'
    
    return adict

county_id_2_name_dict=readNames(definitions.BASEDIR+'county.csv')
distr_id_2_name_dict=readNames(definitions.BASEDIR+'distr.csv')

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Sets up reading of the ONS data
# Arguments:
#  
def readAdminData():
    pcfname=definitions.BASEDIR+'os_postcodes_io.csv'
    pcfname=definitions.BASEDIR+'postcodes.csv'
    pcfname=definitions.BASEDIR+'NSPL_AUG_2017_UK.csv'
    lafname=definitions.BASEDIR+'LocalAuthMap.csv'
    readONSPCRepo(pcfname,
		  lafname,
		  definitions.POSTCODE2_COUNTY_DICT,
		  definitions.POSTCODE2_COUNTRY_DICT,
		  definitions.POSTCODE2_LA_DICT,
		  definitions.POSTCODE2_REGION_DICT,
		  definitions.COUNTY2_REGION_DICT,
		  definitions.LA2_COUNTY_DICT,
		  definitions.LA2_REGION_DICT,
		  LA_TRANSLATION_TABLE,
		  REVERSE_LA_TRANSLATION_TABLE
		  )
    return True
	
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Reads a list of names from a file. Used for configuration
# Arguments:
#  
# @fname name of file to read
def readList(fname):
    alist=[]
    
    with open(fname) as f:
	content = f.readlines()
	for l in content:
	    alist.append(l.strip())
    f.close()
    return alist

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#

## Purpose:Creates an RDF list of values for properties in listnames.
# This is used to allow configurations to be reset after a change
# If a list named xxListReset does not exist create one from the name xxList 
# Called in models ini
# Arguments:
#  
# @listnames conveniece method to create lists for many properties
def createResetLists(listnames):
    for alist in listnames.keys():
        values=listman.getList(listnames[alist]+"Reset")
        if (app.config['DEV_MODE'] == 'F'  or len(values) < 1):
            values=listman.getList(listnames[alist])
            if (len(values) < 1):
                print "createResetLists *** ERROR : no list values for list "+listnames[alist]
                print "createResetLists *** ERROR : Bad things will happen "
            else:
                listman.insertList(listnames[alist]+"Reset",values)
                definitions.RESET_LISTS[listnames[alist]]=listnames[alist]+"Reset"
                definitions.RESET_LISTS_VALUES[listnames[alist]]=values
                
        else:
            definitions.RESET_LISTS_VALUES[listnames[alist]]=values
            definitions.RESET_LISTS[listnames[alist]]=listnames[alist]+"Reset"
            
    return 

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#
## Purpose:Generates a unique list of values for a property from the DB
# Arguments:
#  
# @colname
# @typename
def getValuesForType(colname,typename):
    basename=colname.replace(definitions.DEFNAME,"")
    try:
	results=getallMuseumsOfProperty(definitions.PREFIX_WITHCOLON+basename)
    except Exception, e:
	print str(e)
	return render_template('message.html', title="Internal application error",message="The application has experienced an error at views.py at line: 525   \n <br/><p><pre>"+str(e)+"</pre></p>")
       

    typemap={}
    typelist=[]

    for res in results["results"]["bindings"]:
	mtype=res[basename]["value"].encode('utf-8')
	if (typename == definitions.DEFINED_HIERTYPE):
	    mtype=mtype.replace(definitions.HTTPSTRING+definitions.RDFDEFURI,'')
	    parts=mtype.split(definitions.HIER_SUBCLASS_SEPARATOR)
	    path=""
	    for p in parts:
		path=path+str(p)
		if (not path in typemap):
		    typemap[str(path)]=True
		path=path+definitions.HIER_SUBCLASS_SEPARATOR
	else:
	    if (not mtype in typemap):
		typemap[str(mtype)]=True

    
    for key  in typemap.keys():
	typelist.append(key)

    typemap=None
    
    return typelist

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose: Generates a unique list of values for a column from a map and inserts it in db
# Arguments:
#  
# @colname    property
# @typename   type of property
# @attritypes the map from which the values are taken
def createListOfAllValues(colname,typename,attritypes):
    colcopy=colname.replace(definitions.DEFNAME,definitions.DEFNAME+"Class")
    propertytype=""
    for attributepair in attritypes:
        attribute=attributepair[0].strip()
        propertytype=attributepair[1].strip()
	if (propertytype== colcopy):
	    lname=propertytype+definitions.LISTNAME
	    values=listman.getList(lname)
	    if (len(values) < 1):
		values=getValuesForType(colname,typename)
		listman.insertList(lname,values)
		return 
	
    return 

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#

## Purpose:# Creates a cache for all lists accessibel by name key
#            Called in models ini
# Arguments:
#  
# @listnames list of names for the lists to cache
def createListCache(listnames):
    cache={}
    for alist in listnames.keys():
        values=listman.getList(listnames[alist])
	if (len(values) < 1):
	    print "createListCache *** ERROR : no list values for list "+listnames[alist]
	    print "createListCache *** ERROR : Bad things will happen "
	else:
            cache[alist]=values
    return cache

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Get content for a column for all museums
# Arguments:
#  
# @property column name
def getallMuseumsOfProperty(property): 
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])

    colquery=getQueryForCol(property.replace(definitions.PREFIX_WITHCOLON,"").replace(definitions.HASNAME,""),0,False)    
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 


    SELECT DISTINCT  ?museum ?textcontent ?"""+property.replace(definitions.PREFIX_WITHCOLON,"").replace(definitions.HASNAME,"")+"""
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    WHERE {
       ?museum rdf:type """+definitions.PREFIX_WITHCOLON+"""Museum .
       ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.NAME_OF_MUSEUM+""" ?textcontent .
       """+colquery+""" 
              }
    ORDER BY ASC(?property)
              
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Get all properties for a museum with id
# Arguments:
#  
# @shortid museum id
def getMuseumPropertiesForId(shortid):
    museumid=' "'+shortid+'"^^xsd:string .'
    querycols=""
    queryparams=""
    coldict={}

    i=0
    for tup in definitions.LISTITEMS:
	col,val=tup
	coldict[col]=val
    rcount=0
    for key, val in coldict.iteritems():
	if (key.find(definitions.DEFRANGE) > -1):
	    querycols=querycols+getQueryForCol(key.replace(definitions.DEFRANGE,""),rcount)
	else:
	    querycols=querycols+getQueryForCol(key,rcount)


	if (key.find(definitions.DEFRANGE) > -1):
	    queryparams=queryparams+"?"+key.replace(definitions.DEFRANGE,"")+" "
	else:
	    queryparams=queryparams+"?"+key.replace("def","")+" "
	rcount+=1

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
    SELECT DISTINCT  ?museum  """+str(queryparams)+""" 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    WHERE {
           ?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
            ?museum """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.PROJECT_ID+""" """+str(museumid)+"""
    """+str(querycols)+"""
    } """

    sparql.setQuery(query)
    sparql.setMethod("POSTDIRECTLY")
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
	

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Get  data for use with the Admin data property of ONS classifications for visualisation
# Arguments:
#  
# @patharray the menu path
# @startperiod start year
# @endperiod   end year
# @columns=None columns to retrieve
# @locationname="location" The location attribute to retrieve on

def getVizLocationData(patharray,startperiod,endperiod,columns=None,locationname="location"):
    
    pl=len(patharray)-1
    placename=patharray[pl].replace("_CA","").replace("_"," ")
    placename=placename.replace(" CA","")
    placenamewithquotes='"'+placename+'"'

    querycols=""
    queryparams=""
    if (columns != None):
	rcount=0
	for col in columns:
	    querycols=querycols+getQueryForCol(col,rcount)
	    queryparams=queryparams+"?"+col+" "
	    rcount+=1
	    
	
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    if (placename =="UK"):
	subquery="""
	?museum a bbkmm:Museum .
	?adm a bbkmm:Country   .
	?museum bbkmm:refersToCountry ?adm .
	?adm bbkmm:hasName ?"""+locationname+""" .
	"""
    else:
        ## Country level has no containment so we need to remove this bit if query is for country
	localcontainment="""?adm """+definitions.PREFIX_WITHCOLON+"""contains ?"""+locationname+""" ."""
	for key, val in COUNTRY_TRANSLATION_TABLE.iteritems():
	    if (placename == val):
		localcontainment=""
		break;
    
	subquery="""
	?museum a """+definitions.PREFIX_WITHCOLON+"""Museum .
	?adm """+definitions.PREFIX_WITHCOLON+"""hasName  """+placenamewithquotes+"""^^xsd:string .
	"""+localcontainment+"""
	?"""+locationname+""" a ?clazz .
	?"""+locationname+""" """+definitions.PREFIX_WITHCOLON+"""containedBy ?adm .
	BIND(concat(\""""+definitions.HTTPSTRING+definitions.RDFDEFURI+"""refersTo",strafter(STR(?clazz),"/def/")) AS ?pred) .
	?museum ?pred2 ?"""+locationname+""" .
	"""


    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
    SELECT DISTINCT  ?museum ?clazz ?"""+locationname+""" ?Year_opened ?Year_closed """+str(queryparams)+""" 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    FROM <"""+app.config['GEOADMINGRAPH']+""">
    WHERE
    {
    
    """+subquery+"""
    """+str(querycols)+"""

    OPTIONAL {
     ?museum    """+definitions.PREFIX_WITHCOLON+"""defRangeYear_opened ?duri_Year_opened_3 .
               ?duri_Year_opened_3  """+definitions.PREFIX_WITHCOLON+"""isSubClassInstanceOf  ?vr_Year_opened_3 .
               ?vr_Year_opened_3    """+definitions.PREFIX_WITHCOLON+"""hasLowerRange ?lr_Year_opened_3 .
               ?lr_Year_opened_3    """+definitions.PREFIX_WITHCOLON+"""hasLowerValue ?lv_Year_opened_3 .
               ?vr_Year_opened_3    """+definitions.PREFIX_WITHCOLON+"""hasUpperRange ?ur_Year_opened_3 .
               ?ur_Year_opened_3    """+definitions.PREFIX_WITHCOLON+"""hasUpperValue ?uv_Year_opened_3 .
          BIND (CONCAT(?lv_Year_opened_3,":",?uv_Year_opened_3)  as ?Year_opened)
             }


    OPTIONAL {
     ?museum    """+definitions.PREFIX_WITHCOLON+"""defRangeYear_closed ?duri_Year_closed_4 .
               ?duri_Year_closed_4 """+definitions.PREFIX_WITHCOLON+"""isSubClassInstanceOf  ?vr_Year_closed_4 .
               ?vr_Year_closed_4    """+definitions.PREFIX_WITHCOLON+"""hasLowerRange ?lr_Year_closed_4 .
               ?lr_Year_closed_4    """+definitions.PREFIX_WITHCOLON+"""hasLowerValue ?lv_Year_closed_4 .
               ?vr_Year_closed_4    """+definitions.PREFIX_WITHCOLON+"""hasUpperRange ?ur_Year_closed_4 .
               ?ur_Year_closed_4    """+definitions.PREFIX_WITHCOLON+"""hasUpperValue ?uv_Year_closed_4 .
          BIND (CONCAT(?lv_Year_closed_4,":",?uv_Year_closed_4)  as ?Year_closed)
             }



    } """

    sparql.setQuery(query)
    sparql.setMethod("POSTDIRECTLY")
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
	

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Retrieves data to be used with the browse page
# Arguments:
#  
# @columns columns to retrieve
# @filters=None 
# @vardict=None dictionary to be used when SPARQL variables duplicate each other

def getMarkerData(columns,filters=None,vardict=None): 

    vizgeoquery="""
    ?adm a ?clazz .
    ?adm bbkmm:hasName  '${GEOENTITY}'^^xsd:string .
    BIND(concat('http://bbk.ac.uk/MuseumMapProject/def/refersTo',strafter(STR(?clazz),'/def/')) AS ?pred) .
    ?museum ?pred2 ?adm .
    \n """

    vizadmgeoquery="""
    ?adm a ${GEOADMAREA} .
    ?adm bbkmm:hasTypedName  ?geoadmname .
    BIND(concat(strafter(STR(?adm),'/def/')) AS ?GeoAdmcol) .
    ?museum ?pred2 ?adm .
    \n """

    geoquery=""
    querycols=""
    queryparams=""
    filter=""
    if (filters==None):
	filters=[]

## Deal with the visualisation geo query
#  Once this works it should be turned into a ligthweight datatype class that
#  can be added dynamically and does not have all the search interfaces. Only need
#  to work with markerdata and getquery for col. Remnove params from markerdata

    if (definitions.GEOCOL in columns):
	for key, val in vardict.iteritems():
	    vizgeoquery=vizgeoquery.replace(key.strip(),val.strip())
	geoquery=vizgeoquery
	queryparams=queryparams+"?"+definitions.GEOCOL+" "
	columns.remove(definitions.GEOCOL)
	filters.append('FILTER(STR(?pred) = STR(?pred2))')
    elif (definitions.GEOADMCOL in columns):
	for key, val in vardict.iteritems():
	    vizadmgeoquery=vizadmgeoquery.replace(key.strip(),val.strip())
	geoquery=vizadmgeoquery
	queryparams=queryparams+"?"+definitions.GEOADMCOL+" ?geoadmname "
	columns.remove(definitions.GEOADMCOL)


    for f in filters:
	filter=filter+f+" . \n"
	
    rcount=1
    for col in columns:
        querycols=querycols+getQueryForCol(col,rcount)
        queryparams=queryparams+"?"+col+" "
	rcount+=1


    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

    SELECT DISTINCT  ?museum ?Latitude ?Longitude """+str(queryparams)+""" 
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    FROM <"""+app.config['GEOADMINGRAPH']+""">
    WHERE { 
    ?museum  rdf:type """+definitions.PREFIX_WITHCOLON+"""Museum .
    ?museum  """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.LATITUDE+""" ?Latitude . 
    ?museum  """+definitions.PREFIX_WITHCOLON+definitions.HASNAME+definitions.LONGITUDE+""" ?Longitude . 
    """+str(geoquery)+"""
    """+str(querycols)+"""
    """+str(filter)+"""
    } """

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Removes type info from name
# Arguments:
#  
# @shortid
def getMuseumPropertiesForIdWorking(shortid):
    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
    
SELECT DISTINCT  ?p ?o
FROM <"""+app.config['DEFAULTGRAPH']+""">
FROM <http://bbk.a.c.uk/MuseumMapOrdnance/graph/v1>
WHERE { 
        <http://bbk.ac.uk/MuseumMapProject/data/Museum/id/"""+shortid+"""> ?p ?o .

        
    }
     """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    
    properties = sparql.query().convert()
    return properties

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Is this clazz an abstract clazz?
# Obviously the hard coding needs to go. The names are available in the db.
# Arguments:
#  
# @clazz name
def isDataClass(clazz):
    if (clazz.find(":") < 0 and (clazz == "Visitor_Numbers_Data" or clazz == "Governance_Change" or clazz == "Admin_Area")):
	return True
    else:
	return False

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Loads a class inmplementation
# Arguments:
#  
# @clazz name
def getDataClassInstance(clazz):
    
    l=__name__.rfind(".")
    mname=__name__[:l]+"."+"datatypes."+clazz
    instance=None
    try:
	my_module = importlib.import_module(mname)
	try:
	    MyClass = getattr(my_module, clazz)
	    instance = MyClass()

	except AttributeError:
	    print "?#?#? apputils.py at line: 908 Dbg-out variable \clazz [",clazz,"]\n";
	    print "$$$$$$$$$ CLASS DOES NOT EXIST !"
	    
    except ImportError:
	print "?#?#? apputils.py at line: 903 Dbg-out variable \mname [",mname,"]\n";
	print "$$$$$$$$$ MODULE  DOES NOT EXIST !"
	 
	 
    return instance


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Look for data type implementations and create a cache
# This works both on the attritypes (LIST) and the datadict (DICT) so we need to check which it is
# Arguments:
#  
# @datadict cache
def discoverDatatypes(datadict):

    dname=os.path.dirname(inspect.getfile(sys.modules[__name__]))+"/"+"datatypes"
    dstruct=str(type(datadict))
    # Get a list of all files in directory
    for file in os.listdir(dname):
	if file.endswith(".py"):
	    fname=os.path.join(dname, file)
	    parts=fname.split("/")
	    plen=len(parts)
	    modname=parts[plen-1]
	    fdot=modname.find(".")
	    dataname=modname[:fdot]
	    if (not dataname.startswith("__")):
		# Compare with datatypes
		if (dstruct == "<type 'dict'>"):
		    if (not dataname in datadict):
			# If not in datadict check it loads
			instance=getDataClassInstance(dataname)
			if (instance == None):
			    print "$$$$$$ NOT LOADING DATATYPE "+dataname
			else:
			    datadict[dataname]=dataname
			    # Check its interface
		else:
		    # Attritypes
		    found=False
		    for item in datadict:
			name,ntype=(item)
			if (name == dataname):
			    found=True
			    break;
		    if (not found):
			instance=getDataClassInstance(dataname)
			if (instance == None):
			    print "$$$$$$ NOT LOADING DATATYPE "+dataname
			else:
			    datatypeforsearch=instance.getSearchType()
			    tup=(dataname,datatypeforsearch)
			    datadict.append(tup)
			    # Check its interface

    return datadict
    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Creates the select menu for the datatypes used in search
# loop over all types picking non xml datatype
# add List to typename (dataproperty)
# get list from database
# add all elements of list as group:typename to map
# Arguments:
#  
# @attributetypes the types to retrieve the values for
def getdatagroups(attributetypes):

    grouplist=[]
    acount=0
    for attributepair in attributetypes:
        #        print attributepair
        attribute=attributepair[0].strip()
        propertytype=attributepair[1].strip()
        if (not propertytype in definitions.XML_TYPES):
            sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    
	    query=definitions.RDF_PREFIX_PRELUDE+"""
            prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

            select DISTINCT * 
            FROM <"""+app.config['DEFAULTGRAPH']+""">
            where {
                    """+definitions.PREFIX_WITHCOLON+propertytype+definitions.LISTNAME+""" """+definitions.PREFIX_WITHCOLON+"""contents/rdf:rest*/rdf:first ?item
                  }
                  """
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            if (len(results["results"]["bindings"]) < 1):
		# Check for range type and replace with atomic type
		
		if (propertytype in definitions.DATATYPEDICT):
		    dvalue=definitions.DATATYPEDICT[propertytype]
		    if (dvalue == definitions.DEFINED_RANGETYPE):
			# Get type
			dtype=propertytype.replace(definitions.DEFRANGE,"")
			dvalue=definitions.DATATYPEDICT[dtype]
			attributetypes[acount]=(attribute,dvalue.replace(definitions.XML_TYPES_PREFIX,""))
		    else:
			if (isDataClass(definitions.DATATYPEDICT[attribute])):
			    instance=getDataClassInstance(definitions.DATATYPEDICT[attribute])
			    datatypeforsearch=instance.getSearchType()
			    attributetypes[acount]=(attribute,datatypeforsearch)

		elif (attribute in definitions.DATATYPEDICT):
		    # We have a class
		    if (isDataClass(definitions.DATATYPEDICT[attribute])):
			instance=getDataClassInstance(definitions.DATATYPEDICT[attribute])
			datatypeforsearch=instance.getSearchType()
			attributetypes[acount]=(attribute,datatypeforsearch)
		else:
		    option="<option value='1 Missing data here !'>1 Missing data here !</option>"
		    grouplist.append((propertytype,option))
		    option="<option value='2 Missing data here !'>2 Missing data here !</option>"
		    grouplist.append((propertytype,option))
            else:
                listname=propertytype+definitions.LISTNAME
                definitions.LISTS[propertytype]=listname
                
	    if (propertytype.find(definitions.DEFCLASS) > -1):
		dtype=propertytype.replace(definitions.DEFCLASS,definitions.DEFNAME).strip()
	    else:
		dtype=propertytype.strip()


	    # Now get all the values from the DB, create presentation items for search menu and create the
	    # menuitems.
	    itemlist=[]
            for result in results["results"]["bindings"]:
                item=result["item"]["value"].strip()
		itemlist.append(item)

	    sorteditems=sorted(list(set(itemlist)))
	    uniqvalues={}
            for item in sorteditems:
		presitem=item
		if (dtype in definitions.DATATYPEDICT):
		    dvalue=definitions.DATATYPEDICT[dtype] 
		    presitem=modeltoview.getViewForType(dvalue,item)
		    item=modeltoview.getTypeForViewForSearch(dvalue,presitem)
		else:
		    print "ERRIOROOR : DTYPE "+dtype+" NOT FOUND"

		uniqvalues[item]=presitem

	    sorteditems=None
	    skeys=sorted(uniqvalues.keys())
	    for key in skeys :
		option="<option value='"+key+"'>"+uniqvalues[key].replace("_"," ")+"</option>"
		grouplist.append((propertytype,option))

	    uniqvalues=None
	    results=None
	acount+=1
	
    return grouplist
                
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
  

## Purpose:Retrieves classes and predicates. Side effect that they go into
#          the definitions dict as well
# 
def getpredicatestypes(): 

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

SELECT DISTINCT ?property, ?range
FROM <"""+app.config['DEFAULTGRAPH']+""">
WHERE {
 values ?propertyType { owl:ObjectProperty }
  ?s      ?property ?o .
  ?s a """+definitions.PREFIX_WITHCOLON+"""Museum .
  ?property rdfs:range ?range
filter( strstarts( str(?property), str("""+definitions.PREFIX_WITHCOLON+""") ) )
}
 

         """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    var=results['head']['vars']
    varstr=var[0]
    count=0
    clazzes=[]

    for result in results["results"]["bindings"]:
	rtype=result["range"]["value"]
        if (rtype.find("http://www.w3.org/2001/XMLSchema#")> -1):
            rtype=rtype.replace("http://www.w3.org/2001/XMLSchema#","")
        elif (rtype.find("/")> -1):
              uricomponents=rtype.split('/')
              urilen=len(uricomponents)-1
              clazzname=uricomponents[urilen]
              rtype=clazzname
              hashtag=rtype.find('#')
              if ( hashtag > -1):
                  rtype=rtype[hashtag+1:]
              
	uri=result["property"]["value"]
	uricomponents=uri.split('/')
	clazzname=uricomponents[5]
	if (clazzname.find(definitions.DEFRANGE)> -1):
	    rtype=clazzname
	    clazzname=clazzname.replace(definitions.DEFRANGE,"")
	else:
	    clazzname=clazzname.replace(definitions.HASNAME,"")
	    clazzname=clazzname.replace(definitions.DEFNAME,"")

	if (not clazzname =="isSubClassInstanceOf"):
	    clazzes.append((clazzname,rtype))
	    definitions.PROPERTY_TYPES_DICT[clazzname]=rtype
	    
	count=count+1
    return clazzes

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Retrieves all predicats relating to a museum
# 
def getmuseumpredicates(): 

    predicatelistname="PredicateList"

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 

SELECT DISTINCT ?property
FROM <"""+app.config['DEFAULTGRAPH']+""">
WHERE {
 values ?propertyType { owl:ObjectProperty }
  ?s      ?property ?o .
  ?s a """+definitions.PREFIX_WITHCOLON+"""Museum 
filter( strstarts( str(?property), str("""+definitions.PREFIX_WITHCOLON+""") ) )
}
 

         """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    var=results['head']['vars']
    varstr=var[0]
    count=0
    clazzes=[]

    for result in results["results"]["bindings"]:
	uri=result[varstr]["value"]
	uricomponents=uri.split('/')
	clazzname=uricomponents[5]
        clazzname=clazzname.replace(definitions.HASNAME,"")

        ### !! NOTE we dont want this visible as it is only for system use
	if (not clazzname == "isSubClassInstanceOf"):
	    clazzes.append((clazzname,clazzname))
	count=count+1


    definitions.LISTS["Predicate"]=predicatelistname


    
    return clazzes


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Returns the column if defined in the datatyep map
# Arguments:
#  
# @incol col to look for
def getDefinedType(incol):
    if (not incol.startswith(definitions.DEFNAME)):
	defcol=definitions.DEFNAME+incol
	if (defcol in definitions.DATATYPEDICT):
	    col=defcol
	else:
	    defcol=definitions.DEFRANGE+incol
	    if (defcol in definitions.DATATYPEDICT):
		col=defcol
	    else:
		col=incol
    else:
	col=incol
    return col
    

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Is this column an abstract type?
# Arguments:
#  
# @incol  colomn
# @defcol its abstract type name

def isTypeAClazz(incol,defcol):
    
    if (incol == defcol and  definitions.DATATYPEDICT[defcol].find("xsd") < 0):
	return True
    else:
	return False
    

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Creates a query for a column
# Arguments:
#  
# @incol the column to search
# @rcount variable repeat count
# @optional=True Is the query optional?
# @museumuri='?museum ' name of museum class variable
# @matchstrings=[] query match string
# @conditions=[]   condition
# @matchcolumns=[] column name
# @coltoargdict={} macro name for column in case type is an implementation class

def getQueryForCol(incol,
		   rcount,optional=True,
		   museumuri='?museum ',
		   matchstrings=[],
		   conditions=[],
		   matchcolumns=[],
		   coltoargdict={}):


    rangequery="""
    OPTIONAL {
     ?museum    bbkmm:defRange${column_name} ?duri_${rcount} .
               ?duri_${rcount} bbkmm:isSubClassInstanceOf  ?vr_${rcount} .
               ?vr_${rcount}    bbkmm:hasLowerRange ?lr_${rcount} .
               ?lr_${rcount}    bbkmm:hasLowerValue ?lv_${rcount} .
               ?vr_${rcount}    bbkmm:hasUpperRange ?ur_${rcount} .
               ?ur_${rcount}    bbkmm:hasUpperValue ?uv_${rcount} .
          BIND (CONCAT(?lv_${rcount},":",?uv_${rcount})  as ?${column_name})
	     }
    \n """



#- - - - -
    col=getDefinedType(incol)
    query=""
    
											
    if (not col in definitions.DATATYPEDICT):
	print "$$$$$$$$$$$$$$$$$$ "+col+" col not found"
    elif (definitions.DATATYPEDICT[col] == definitions.DEFINED_RANGETYPE):
	query=rangequery.replace("${column_name}",incol).replace("${rcount}",str(incol)+"_"+str(rcount))
    elif(definitions.DATATYPEDICT[col] == definitions.DEFINED_LISTTYPE):
        # Get the object property and then its hasObject
        query=museumuri+definitions.PREFIX_WITHCOLON+col+' ?'+col+'uri . \n'
	colwithoutdef=col[3:]
        query=query+'?'+col+'uri '+definitions.PREFIX_WITHCOLON+definitions.HASNAME+colwithoutdef+' ?'+colwithoutdef+'  \n'
        if(optional):
            query="OPTIONAL{"+query+" . } \n"
        else:
            query=query+" .  \n"
    elif(definitions.DATATYPEDICT[col] == definitions.DEFINED_HIERTYPE):
        # Get the object property and then its hasObject
	colwithoutdef=col[3:]
        query=museumuri+definitions.PREFIX_WITHCOLON+col+' ?'+colwithoutdef+'  \n'
        if(optional):
            query="OPTIONAL{"+query+" . } \n"
        else:
            query=query+" .  \n"
    elif (definitions.DATATYPEDICT[col] in definitions.XML_TYPES_WITH_PREFIX):
        #  plain type
        if(optional):
            query="OPTIONAL{ "+museumuri+"  "+definitions.PREFIX_WITHCOLON+definitions.HASNAME+col+" ?"+col+" . } \n"
        else:
            query= museumuri+"  "+definitions.PREFIX_WITHCOLON+definitions.HASNAME+col+" ?"+col+" .  \n"

    elif (col in definitions.DATATYPEDICT and isDataClass(definitions.DATATYPEDICT[col])):
	instance=getDataClassInstance(definitions.DATATYPEDICT[col])
	if (incol in matchcolumns):
	    query=instance.getQuery(incol,
				    rcount,
				    matchstrings[coltoargdict[incol]],
				    conditions[coltoargdict[incol]],
				    matchcolumns[coltoargdict[incol]])
	else:
	    query=instance.getQuery(incol,
				    rcount,
				    None,
				    None,
				    None)
	    
	
    else:
	print "$$$$$$$$$$ ERROR UNKNOWN DATATYPE "+col+"$$$$$$$$$$"
	query=""
	    
    return query


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
## Purpose:Create virtuoso data type statement for column
# Arguments:
#  
# @col name
# @coltocountdict variable counts
# @lowerorupper="" name of SPARQL variable

def getCol(col,coltocountdict,lowerorupper=""):
    dtype=getDefinedType(col)
    if (dtype.startswith(definitions.DEFRANGE)):
	##Return lower index
	rcount=coltocountdict[col]
	if (len(lowerorupper)>0):
	    q='STRDT(?'+lowerorupper+'_${rcount},'+definitions.DATATYPEDICT[col]+')'
	else:
	    q='STRDT(?lv_${rcount},'+definitions.DATATYPEDICT[col]+')'
	    
        return q.replace("${rcount}",str(col)+"_"+str(rcount))
    else:
	return "?"+col
    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


## Purpose:Returns a filter clause for a column
# Arguments:
#  
# @matchcolumns   columns
# @conditions     conditions 
# @matchstrings   strings to match
# @coltocountdict variable count

def getFilterClause(matchcolumns,conditions,matchstrings,coltocountdict): 
    matchfilter=""
    filterdict={}

    for col,cond,match in zip(matchcolumns,conditions,matchstrings):

	if (col not in filterdict):
	   filterdict[col]=[]

        if (len(match) >0):
	    defcol=getDefinedType(col)
	    print definitions.DATATYPEDICT[defcol]
	    isd=isDataClass(definitions.DATATYPEDICT[defcol])
	    ist=isTypeAClazz(col,defcol)
	    
	    if (not defcol in definitions.DATATYPEDICT):
		print defcol+" col not found"

	    elif (cond == "match"):
		if (isTypeAClazz(col,defcol)):
		    if (isDataClass(definitions.DATATYPEDICT[defcol])):
			rcount=coltocountdict[col]
			instance=getDataClassInstance(definitions.DATATYPEDICT[defcol])
			filterdict[col].append(("||",instance.getMatchFilter(rcount,match,cond)))
		# Check if we have a hier
		elif (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_HIERTYPE):
		    defmatch=modeltoview.getTypeForView(definitions.DEFINED_HIERTYPE,match)		    
		    filterdict[col].append(("||",'(CONTAINS(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(defmatch)+'")))'))
		elif (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_LISTTYPE):
		    filterdict[col].append(("||",'(LCASE(str('+"?"+str(col)+')) = '+'LCASE("'+str(match)+'"))'))
		else:
		    filterdict[col].append(("||",'(CONTAINS(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(match)+'")))'))
		    
	    elif (cond == "notmatch"):
		if (isTypeAClazz(col,defcol)):
		    if (isDataClass(definitions.DATATYPEDICT[defcol])):
			rcount=coltocountdict[col]
			instance=getDataClassInstance(definitions.DATATYPEDICT[defcol])
			filterdict[col].append(("||",instance.getMatchFilter(rcount,match,cond)))
		elif (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_HIERTYPE):
		    defmatch=modeltoview.getTypeForView(definitions.DEFINED_HIERTYPE,match)		    
		    filterdict[col].append(("||",'(! CONTAINS(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(defmatch)+'")))'))
		elif (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_LISTTYPE):
		    filterdict[col].append(("||",'(LCASE(str('+"?"+str(col)+')) != '+'LCASE("'+str(match)+'"))'))
		else:
		    filterdict[col].append(("||",'(! CONTAINS(LCASE(str('+"?"+str(col)+')),'+'LCASE("'+str(match)+'")))'))
		    
	    elif (isTypeAClazz(col,defcol)):
		if (isTypeAClazz(col,defcol)):
		    if (isDataClass(definitions.DATATYPEDICT[defcol])):
			rcount=coltocountdict[col]
			instance=getDataClassInstance(definitions.DATATYPEDICT[defcol])
			## We dont have any dataclasses with nonnumeric comparisons (match/not)
			## To fix similar problems in the match/not perhaps the below solution can just be copied?
			fl=len(filterdict[col])
			if (fl == 0):
			    filterdict[col].append( (") . \n",instance.getCompareFilter(rcount,match,cond)))
			elif (fl == 1):
			    filterdict[col].append( (" ","FILTER("+instance.getCompareFilter(rcount,match,cond)))
			else:
			    filterdict[col].append( (" ","). \n FILTER("+instance.getCompareFilter(rcount,match,cond)))

##          Range lower value=lv uppervalue=uv
            elif (cond == "LTE"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' <= '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' <= '+match+')'))
            elif (cond == "LT"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' < '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' < '+match+')'))
            elif (cond == "GT"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' > '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' > '+match+')'))
            elif (cond == "GTE"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' >= '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' >= '+match+')'))
            elif (cond == "EQ"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' = '+match+')'))
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' = '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' = '+match+')'))
            elif (cond == "NEQ"):
		if (definitions.DATATYPEDICT[defcol] == definitions.DEFINED_RANGETYPE):
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' < '+match+')'))
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' > '+match+')'))
		else:
		    filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' != '+match+')'))
	    # Range
            elif (cond == "PLTE"):
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' <= '+match+')'))
            elif (cond == "PLT"):
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"lv")+' <= '+match+')'))
            elif (cond == "PGT"):
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' > '+match+')'))
            elif (cond == "PGTE"):
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' >= '+match+')'))
            elif (cond == "PEQ"):
		filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' <= '+match+')'))
		filterdict[col].append(("||",'('+match+' <= '+getCol(col,coltocountdict,"uv")+')'))
            elif (cond == "PNEQ"):
		filterdict[col].append(("&&",'('+getCol(col,coltocountdict,"lv")+' != '+match+')'))
		filterdict[col].append(("||",'('+getCol(col,coltocountdict,"uv")+' != '+match+')'))
	    # Date
            elif (cond == "DLTE"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' <= "'+match+'"^^xsd:date)'))
            elif (cond == "DLT"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' < "'+match+'"^^xsd:date)'))
            elif (cond == "DGT"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' > "'+match+'"^^xsd:date)'))
            elif (cond == "DGTE"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' >= "'+match+'"^^xsd:date)'))
            elif (cond == "DEQ"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' = "'+match+'"^^xsd:date)'))
            elif (cond == "DNEQ"):
                filterdict[col].append(("||",'('+getCol(col,coltocountdict)+' != "'+match+'"^^xsd:date)'))
        elif (cond == "True"):
            filterdict[col].append(("||",'(STR('+getCol(col,coltocountdict)+') =  STR(true) )'))
        elif (cond == "False"):
            filterdict[col].append(("||",'(STR('+getCol(col,coltocountdict)+') =  STR(false) )'))

    for key, val in filterdict.iteritems():
	if (len(val) == 1):
	    op,cond=val[0]
	    matchfilter=matchfilter+ "FILTER ("+cond+") . \n"
	else:
	    tempfilter=""
	    for f in val:
		op,cond=f
		tempfilter=tempfilter+cond+" "+op
	    tlen=len(tempfilter)-2
	    tempfilter=tempfilter[0:tlen]
	    matchfilter=matchfilter+ "FILTER ("+tempfilter+") . \n"
    filterdict=None
    return matchfilter

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Purpose:Create a query for a list of columns
# Arguments:
#  
# @columns      column names
# @matchcolumns match names
# @conditions   conditions
# @matchstrings strings to match
# @ordercolumn  which column to order on

def getSearchResults(columns,matchcolumns,conditions,matchstrings,ordercolumn): 
    querycols=""
    queryparams=""
    coltocountdict={}
    coltoargdict={}
    


    ## Make sure we have subject in columns. Adding it here means it becomes optional.
    ## This should be removed eventually so that it is always optional if specified.
    if (not definitions.NAME_OF_MUSEUM in columns):
	columns.insert(0,definitions.NAME_OF_MUSEUM)

    argcount=0
    for col in matchcolumns:
	coltoargdict[col]=argcount
	argcount+=1

    rcount=1
    for col in columns:
        querycols=querycols+getQueryForCol(col,rcount,matchstrings=matchstrings,
					   conditions=conditions,
					   matchcolumns=matchcolumns,
					   coltoargdict=coltoargdict)
        queryparams=queryparams+"?"+col+" "
	coltocountdict[col]=rcount
	rcount+=1

    matchfilter=getFilterClause(matchcolumns,conditions,matchstrings,coltocountdict)
    

### Mapdata additions, make sure not to duplicate properties
    map_querycols=""
    map_queryparams=""


    map_columns=[definitions.LATITUDE,definitions.LONGITUDE]
    for map_col in map_columns:
	if (not map_col in columns):
	    map_querycols=map_querycols+getQueryForCol(map_col,rcount,optional=False)
	    map_queryparams=map_queryparams+"?"+map_col+" "
	    coltocountdict[map_col]=rcount
	    rcount+=1
	    

    sparql = SPARQLWrapper(app.config['SPARQLENDPOINT'])
    query=definitions.RDF_PREFIX_PRELUDE+"""
    prefix """+definitions.PREFIX_WITHCOLON+""" <http://"""+definitions.RDFDEFURI+"""> 
   
    SELECT DISTINCT  ?museum """+str(queryparams)+"""  """+str(map_queryparams)+"""
    FROM <"""+app.config['DEFAULTGRAPH']+""">
    FROM <http://bbk.ac.uk/MuseumMapProject/graph/ukadmin>
    WHERE { 
    ?museum  rdf:type """+definitions.PREFIX_WITHCOLON+"""Museum .
    """+str(map_querycols)+"""
    """+str(querycols)+str(matchfilter)+"""
    } ORDER BY """+str(ordercolumn)

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    newresults=[]
    newres=[]
    for key in results["head"]["vars"]:
        newres.append(key)
    newresults.append(newres)

    for res in results["results"]["bindings"]:
        newres=[]
        for key in results["head"]["vars"]:
            if (key in res):
                newres.append(res[key]["value"])
            else:
                newres.append("")
        newresults.append(newres)
                
        
    return newresults



# Processes and methodologies can make good servants but are poor masters.
#    - Mark Dowd, John McDonald & Justin Schuh 
#      in "The Art of Software Security Assessment"
     
