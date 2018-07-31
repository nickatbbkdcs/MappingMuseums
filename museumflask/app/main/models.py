##
# @file
#  
# This module initialises the ONS dictionaries,all configuration lists, 
# and builds the datatype dictionary through database introspection. 
# * All predicates are found 
# * All datatypes are found
# * Search select menus initialised
# * Search show and query configuration
# * Columns to show in nakedview
# * Create cache for all lists
# * Read JSON geo files
# In dev mode all expensive operations are replaced with loading pickled objects.
# The option is set in the config file app/searchapplication.cfg
#
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from . import definitions
from . import apputils
from . import listman
from PTreeNode import PTreeNode as PTreeNode
from Configuration import Configuration as Configuration
import pprint
import json
from flask import current_app as app
import pickle

apis=[]

MODELS_INITITALISED=False


#-  -  -  -  -  -  -  

## Purpose:Pickles dictionaries
# Arguments:
# @o disct
# @name name

def pickleObject(o,name):
    print "Pickling dict: "+name
    with open(definitions.BASEDIR+name+'.pickle','wb') as f:
	pickle.dump(o, f, pickle.HIGHEST_PROTOCOL)
    f.close()
    print "done"
    return

#-  -  -  -  -  -  -  

## Purpose:Loads pickled dictionaries
# Arguments:
#  @name name
def loadObject(name):
    print "Loading dict: "+name
    with open(definitions.BASEDIR+name+'.pickle','rb') as f:
	o=pickle.load( f )
    f.close()
    print "done"
    return o 

#-  -  -  -  -  -  -  


## Purpose:Does all initialisations. Triggered on first request
def do_initdefinitions():

    global MODELS_INITITALISED
    assert(MODELS_INITITALISED == False)
    pp = pprint.PrettyPrinter(indent=4)

    # The following 3 methods have a side effect that the lists are entered into LISTS as well
    if (app.config['DEV_MODE'] == 'F'):
	definitions.LISTITEMS  = apputils.getmuseumpredicates()
	pickleObject(definitions.LISTITEMS,"LISTITEMS")
    else:
	definitions.LISTITEMS=loadObject("LISTITEMS")
	
    print 'LISTITEMS ++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    pp.pprint(definitions.LISTITEMS)
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'

    if (app.config['DEV_MODE'] == 'F'):
	definitions.ATTRITYPES = apputils.getpredicatestypes()
    else:
	definitions.ATTRITYPES=loadObject("ATTRITYPES")
	
	
    print 'ATTRITYPES ++++++++++++++++++++++++++++++++++++++++++++++++++++++'

    pp.pprint(definitions.ATTRITYPES)
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'

    if (app.config['DEV_MODE'] == 'F'):
	# Deal with all datatypes
	datatypelist=[]
	for plist in definitions.DATATYPESLISTNAME:
	    datatypelist=datatypelist+listman.getListCollection(plist)

	for plist in definitions.PREDICATELISTNAME:
	    definitions.PREDICATELIST=definitions.PREDICATELIST+listman.getListCollection(plist)


	for dtype in datatypelist:
	    parts=dtype.split('#')
	    colname=parts[0].replace(definitions.PREFIX_WITHCOLON+definitions.HASNAME,'')
	    colname=colname.replace(definitions.HASNAME,'')
	    typename=parts[1].replace(definitions.PREFIX_WITHCOLON,'')
	    definitions.DATATYPEDICT[colname]=typename
	    if (typename == definitions.DEFINED_HIERTYPE):
		# Create the list of all values
		apputils.createListOfAllValues(colname,typename,definitions.ATTRITYPES)

	
	definitions.ATTRITYPES = apputils.discoverDatatypes(definitions.ATTRITYPES)
	definitions.DATAGROUPS = apputils.getdatagroups(definitions.ATTRITYPES)

	# Deal with datatypes that are synthetic. I.e. not coming from the ETL process
	# They are defined in the datatypes directory
	definitions.DATATYPEDICT=apputils.discoverDatatypes(definitions.DATATYPEDICT)
				   


	# Pickle can only happen after all initialisations are done
	pickleObject(definitions.DATATYPEDICT,"DATATYPEDICT")
	pickleObject(definitions.PREDICATELIST,"PREDICATELIST")
	pickleObject(definitions.DATAGROUPS,"DATAGROUPS")
	pickleObject(definitions.ATTRITYPES,"ATTRITYPES")
    else:
	definitions.DATATYPEDICT=loadObject("DATATYPEDICT")
	definitions.PREDICATELIST=loadObject("PREDICATELIST")
	definitions.DATAGROUPS=loadObject("DATAGROUPS")
	#remove
	definitions.DATAGROUPS = apputils.getdatagroups(definitions.ATTRITYPES)
	
    print 'DATADICT ++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    pp.pprint(definitions.DATATYPEDICT)
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'

    print 'DATAGROUPS ++++++++++++++++++++++++++++++++++++++++++++++++++++++'
    pp.pprint(definitions.DATAGROUPS)
    print '++++++++++++++++++++++++++++++++++++++++++++++++++++++'


    # READ CONFIGURATIONS AND CREATE LISTS

    
    # SHOW
    #This does not work. Bug in database. Returns things in the wrong order in getList. Works everywhere else.
    # So we do the only thing we can...
    definitions.DEFAULT_SEARCH_SHOW_COLUMNS=apputils.readList(definitions.BASEDIR+'DEFAULT_SEARCH_SHOW_COLUMNS.txt')


    # FILTER
    # Add configuration for default columns for filter in search
    defaultlistname=str(definitions.DEFAULT_SEARCH_FILTER_COLUMNS_NAME+definitions.LISTNAME)
    definitions.DEFAULT_SEARCH_FILTER_COLUMNS=listman.getList(defaultlistname)
    if (app.config['DEV_MODE'] == 'F'  or len(definitions.DEFAULT_SEARCH_FILTER_COLUMNS) < 1):
	definitions.DEFAULT_SEARCH_FILTER_COLUMNS=apputils.readList(definitions.BASEDIR+'DEFAULT_SEARCH_FILTER_COLUMNS.txt')
	listman.updateList(defaultlistname,definitions.DEFAULT_SEARCH_FILTER_COLUMNS)
	definitions.DEFAULT_SEARCH_FILTER_COLUMNS=listman.getList(defaultlistname)

    definitions.LISTS[definitions.DEFAULT_SEARCH_FILTER_COLUMNS_NAME]=defaultlistname

    # SEEALL
    # Add configuration for columns to show in nakedid view
    defaultlistname=str(definitions.DEFAULT_VIEW_ALL_COLUMNS_NAME+definitions.LISTNAME)
    definitions.DEFAULT_VIEW_ALL_COLUMNS=listman.getList(defaultlistname)
    if (app.config['DEV_MODE'] == 'F'  or len(definitions.DEFAULT_VIEW_ALL_COLUMNS) < 1):
	definitions.DEFAULT_VIEW_ALL_COLUMNS=apputils.readList(definitions.BASEDIR+'DEFAULT_VIEW_ALL_COLUMNS.txt')
	listman.insertList(defaultlistname,definitions.DEFAULT_VIEW_ALL_COLUMNS)

    definitions.LISTS[definitions.DEFAULT_VIEW_ALL_COLUMNS_NAME]=defaultlistname

    # Done defaults, now cache all and create any missing reset lists
    if (app.config['DEV_MODE'] == 'F'):
	definitions.LISTS_VALUES=apputils.createListCache(definitions.LISTS) #temp    
	apputils.createResetLists(definitions.LISTS) #temp
	apputils.readAdminData()#temp    
    

    for key, val in definitions.JSONDATA_FILES.iteritems():
	with open(definitions.BASEDIR+val) as f:
	    print "?#?#? models.py at line: 96 Dbg-out variable \val [",val,"]\n";
	    j_str = f.readlines()
	    f.close()
	    definitions.JSONDATA[key]= j_str


    definitions.DATASETVERSION=app.config['DEFAULTGRAPH']
    MODELS_INITITALISED=True

    return

def initmodels():
    print "Models initialising"
    initdefinitions(False)

def initdefinitions(force):
    # Module initialisation
    global MODELS_INITITALISED
    # Force is used after configuration change
    if (force):
	do_initdefinitions()
    elif (not MODELS_INITITALISED):
	do_initdefinitions()
    return



