##
# @file
#  
# This class implements the view to show a specific museum with ID  
# It has two views; view default or view all. A button toggles the two.
#  
#  
#  More details.
#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
from flask.views import View
from flask  import Blueprint
from . import main as main_blueprint
from flask import render_template, redirect, url_for, abort, flash, request, make_response
from . import apputils
from . import listman
from . import tree
from . import PTreeNode
from . import models
from . import definitions
from . import model_to_view
from . import Configuration
from . import showmuseumtypes

from PTreeNode import PTreeNode as PTreeNode


from flask import current_app as app
import pprint
import collections
import copy

from altair import Chart, Color, Scale
import pandas as pd
import traceback
import sys
import pickle
import time
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


class NakedId():
    from . import model_to_view
    modeltoview=model_to_view.Model_To_View()

## Purpose:Local getview for this view
# Arguments:
# 
# @prop  type
# @value value

    def getView(self,prop,value):
        dataname=definitions.DEFNAME+prop
        if (prop in definitions.DATATYPEDICT):
            return self.modeltoview.getView(prop,value)
	elif(dataname in definitions.DATATYPEDICT):
            datatype=definitions.DATATYPEDICT[dataname]
            return self.modeltoview.getViewForType(datatype,value)
        return value

    
## Purpose:Implements the FLASK view
# Returns a dictionary to show in the table
# Arguments:
# 
# @nid Project id to view
# @mid ?? not used

    def nakedidView(self,nid,mid):

	
        if (request.method == 'GET'):
	    
	    start_time = time.time()

	    try:
 		properties=apputils.getMuseumPropertiesForId(mid)
 	    except Exception, e:
 		print str(e)
 		return render_template('message.html', title="Internal application error",message="The application has experienced an error at views.py at line: 196   \n <br/><p><pre>"+str(e)+"</pre></p>")
	
	    pkeys=properties["head"]["vars"]
            pdict={}
            count=0
            for pk in pkeys:
                pdict[pk]=count
                count=count+1
        
        
            fdict={}
            allprops=[]
            for res in properties["results"]["bindings"]:
                for f in res:
		    if (not f in fdict):
			fdict[f]=[]
		    found=False
		    for di in fdict[f]:
			if (di == res[f]["value"]):
			    found=True
			    break
		    if (not  found):
			fdict[f].append(res[f]["value"])
                    if (f.startswith(definitions.DEFNAME)):
                        tup =(f[len(definitions.DEFNAME):].replace('_',' '),self.getView(f,res[f]["value"]))
                    elif (f.startswith(definitions.RANGENAME)):
                        tup =(f[len(definitions.RANGENAME):].replace('_',' '),self.getView(f,res[f]["value"]))
                    else:
                        tup =(f.replace('_',' '),self.getView(f,res[f]["value"]))
                    allprops.append(tup)
        
	    unique_props=set(allprops)
                    
        
            alltups=[[] for col in range(len(definitions.DEFAULT_VIEW_ALL_COLUMNS))]
            count=0
            for fi in definitions.DEFAULT_VIEW_ALL_COLUMNS:
                tups=[]
                field=str(fi)
                if ( field in fdict.keys()):
		    for di in fdict[field]:
			if (field.startswith(definitions.DEFNAME)):
			    tup =(field.replace('_',' '),self.getView(field.replace(definitions.DEFNAME,""),di))
			else:
			    tup =(field.replace('_',' '),self.getView(field,di))
			    
			tups.append(tup)
                alltups[count]=tups
                count=count+1
        
            
            museumname="Unknown"
        
            for res in properties["results"]["bindings"]:
                    if (definitions.NAME_OF_MUSEUM in res):
                        museumname=res[definitions.NAME_OF_MUSEUM]["value"]
                        break
                    
        
	    print("--- %s seconds ---" % (time.time() - start_time))
            return render_template('nakedid.html',
                                   docid=mid,
                                   alltups=alltups,
                                   allprops=sorted(unique_props),
                                   museumname=museumname,
                                   title="Details about a museum")
        
