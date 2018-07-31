#!/usr/bin/env python
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""

"""

from SPARQLWrapper import SPARQLWrapper, JSON
import operator

import sys
import csv
import time
import re
import cgi


SPARQLENDPOINT="http://193.61.44.11:8890/sparql"

DEFAULTGRAPH="http://bbk.ac.uk/MuseumMapProject/graph/v8"


LA_TRANSLATION_TABLE={}
REVERSE_LA_TRANSLATION_TABLE={}

SEPARATOR="$"
BASEDIR="./json/"
POSTCODE2_DISTR_DICT={}
POSTCODE2_COUNTY_DICT={}
POSTCODE2_COUNTRY_DICT={}
POSTCODE2_LA_DICT={}
POSTCODE2_REGION_DICT={}
COUNTY2_REGION_DICT={}
LA2_COUNTY_DICT={}
LA2_REGION_DICT={}
NAME_OF_MUSEUM		    = "Name_of_museum"
POSTCODE		    = "Postcode"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

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
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

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
	    #print 'key is in error:'+parts[header_dict['laua 11']].replace('"','')
	    keyerrors+=1

	if (len(parts[header_dict['gor 16']].replace('"','')) > 0):
	    if (parts[header_dict['gor 16']].replace('"','') in GOR_TRANSLATION_TABLE):
		gor=str(GOR_TRANSLATION_TABLE[parts[header_dict['gor 16']].replace('"','')])
		postcode2_region_dict[spc]=gor
	    else:
		postcode2_region_dict[spc]='UNKNOWN'
		unknown+=1
	else:
	    #print 'key is in error:'+parts[header_dict['gor 16']].replace('"','')
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


def readAdminData():
    pcfname=BASEDIR+'os_postcodes_io.csv'
    pcfname=BASEDIR+'postcodes.csv'
    pcfname=BASEDIR+'NSPL_AUG_2017_UK.csv'
    lafname=BASEDIR+'LocalAuthMap.csv'
    readONSPCRepo(pcfname,
			   lafname,
			   POSTCODE2_COUNTY_DICT,
			   POSTCODE2_COUNTRY_DICT,
			   POSTCODE2_LA_DICT,
			   POSTCODE2_REGION_DICT,
			   COUNTY2_REGION_DICT,
			   LA2_COUNTY_DICT,
			   LA2_REGION_DICT,
			   LA_TRANSLATION_TABLE,
			   REVERSE_LA_TRANSLATION_TABLE
                  )
    return True
        
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def getMarkerData():
    sparql = SPARQLWrapper(SPARQLENDPOINT)

    
    query="""
      prefix dcterms:         <http://purl.org/dc/terms/>  
    prefix owl:             <http://www.w3.org/2002/07/owl#> 
    prefix rdf:             <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    prefix rdfs:            <http://www.w3.org/2000/01/rdf-schema#>  
    prefix xml:             <http://www.w3.org/XML/1998/namespace> 
    prefix xsd:             <http://www.w3.org/2001/XMLSchema#>
    prefix prov:            <http://www.w3.org/ns/prov#>
    prefix time:            <http://www.w3.org/2006/time#>
    
    prefix bbkmm: <http://bbk.ac.uk/MuseumMapProject/def/> 
   
    SELECT DISTINCT  ?museum ?Latitude ?Longitude ?Name_of_museum ?Postcode  
    FROM <"""+DEFAULTGRAPH+""">
    WHERE { 
    ?museum  rdf:type bbkmm:Museum .
    ?museum  bbkmm:hasLatitude ?Latitude . 
    ?museum  bbkmm:hasLongitude ?Longitude . 
    OPTIONAL{ ?museum   bbkmm:hasName_of_museum ?Name_of_museum . } 
OPTIONAL{ ?museum   bbkmm:hasPostcode ?Postcode . } 

    } 
            
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def printtolist(key,listofmuseums,pads,incountry):

    LA_DECOR_TABLE={
	"England":"?????",
	"Channel Islands":" (Channel Islands)",
	"Isle of Man":" (Isle of Man)",
	"Northern Ireland":" (NI Loc Gov District)",
	"Scotland":" (Scottish Council Area)",
	"Wales":" (Welsh UA)"
    }
    LA_TRAIL_TABLE={
	"England":"",
	"Channel Islands":",,,,",
	"Isle of Man":",,,,",
	"Northern Ireland":",,,,,",
	"Scotland":",,,,,,",
	"Wales":",,,,,,,"
    }

    newkey=key.replace("/",",")
    nparts=newkey.split(",")
    for m in listofmuseums:
	(museum,name)=m
	mparts=museum.split("/")
	mpartslen=len(mparts)
	mkey=mparts[mpartslen-1]
	print "*?#?"+mkey+","+nparts[0]+":"+REVERSE_COUNTRY_TRANSLATION_TABLE[nparts[0]]+pads+","+nparts[2]+LA_DECOR_TABLE[nparts[0]]+":"+REVERSE_LA_TRANSLATION_TABLE[nparts[2]]+LA_TRAIL_TABLE[nparts[0]]
    return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def doCountry(incountry,inpseudo,pads,pade):
    treedict={}
    
    # Create england dict
    treedict[incountry]={}
    
    # Counties
    pseudo=inpseudo
    countiesdict={}
    countiesdict[pseudo]=[]
    
    
    # Put counties in regions
    for county in countiesdict:
        ladict={}
        for lakey, laval in LA2_COUNTY_DICT.iteritems():
            if (laval == county):
                ladict[lakey]=laval
    sla=sorted(ladict)
    for las in sla:
        print "?#?#? prova.py at line: 307 Dbg-out variable \las [",las,"]\n";
        countiesdict[pseudo].append(las)
        
    
    # Get all postcodes
    results=getMarkerData()
    
    rlen=len(results["results"]["bindings"])
    museumdict={}
    notinlacount=0
    
    for result in results["results"]["bindings"]:
        if ("museum" in result):
            museum=result["museum"]["value"]
            if (NAME_OF_MUSEUM in result):
                name=result[NAME_OF_MUSEUM]["value"]
                if (POSTCODE in result):
                    postcode=result[POSTCODE]["value"].replace(' ','')
                    
                    if (name and museum and postcode and postcode in POSTCODE2_LA_DICT):
                        thiscountry=POSTCODE2_COUNTRY_DICT[postcode].replace('"','')
                        if (thiscountry.strip() == incountry.strip()):
                            tup=(museum,name)
                            if (not thiscountry in museumdict):
                                museumdict[thiscountry]=[]
                            museumdict[thiscountry].append(tup)
    
                            if (postcode in POSTCODE2_LA_DICT):
                                thisla=POSTCODE2_LA_DICT[postcode]
                                key=thiscountry+"/"+pseudo+"/"+thisla
                                    
                                if (not key in museumdict):
                                    museumdict[key]=[]
                                museumdict[key].append(tup)
                            else:
                                print "NOT IN POSTCODE2_LA_DICT "+postcode
                            print postcode+" X_X_X "+thiscountry+"/"+pseudo+"/"+thisla
                            
                    else:
                        print "$$ NOT IN POSTCODE2_LA_DICT: "+postcode
                        if (postcode in POSTCODE2_DISTR_DICT):
                            print "But in region dict:"+POSTCODE2_DISTR_DICT[postcode]
                        if (postcode in POSTCODE2_COUNTY_DICT):
                            print "But in county  dict:"+POSTCODE2_COUNTY_DICT[postcode]
    
                        notinlacount+=1
    print incountry+": ("+str(len(museumdict[incountry]))+")"+str(museumdict[incountry])
    for la in sorted(countiesdict[county]):
        key=incountry+"/"+pseudo+"/"+la
        if (key in museumdict):
            print "    "+key+":->>("+str(len(museumdict[key]))+")"+str(museumdict[key])
        else:
            print "    No museums for this key:"+key
                
                    
    
    for la in sorted(countiesdict[county]):
        key=incountry+"/"+pseudo+"/"+la
        if (key in museumdict):
            printtolist(key,museumdict[key],pads,incountry)
        else:
            print "    No museums for this key:"+key
    
    
    return

##======================================================================================================
if __name__ == '__main__':
    """ Run Process from the command line. """


readAdminData()
doCountry("Wales","(pseudo) Wales","",",,")
doCountry("Scotland","(pseudo) Scotland",",",",")
doCountry("Northern Ireland","(pseudo) Northern Ireland",",,","")
doCountry("Channel Islands","(pseudo) Channel Islands","",",,")
doCountry('Isle of Man','(pseudo) Isle of Man',"",",,")







	    

