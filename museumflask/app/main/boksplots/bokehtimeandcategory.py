from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.palettes import brewer
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.layouts import row
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.palettes import Spectral10
from bokeh.palettes import Category20_20
from bokeh import palettes
from random import shuffle
from numpy import pi 
import numpy as np 
import pandas as pd
import colorsys
from bokeh.layouts import layout 
from bokeh.models import ( 
  HoverTool, ColumnDataSource, Legend, LegendItem, GlyphRenderer,Circle
)
from bokeh.models import CustomJS

from bokeh.plotting import figure 
from bokeh.palettes import brewer 
import datetime
from bokeh.models import DatetimeTickFormatter
from bokeh.models.glyphs import Rect as rect
from collections import OrderedDict
from . import bokutils

import copy

from app.main import tree
from app.main import apputils
from app.main import definitions
from app.main import showmuseumtypes



TIME="Time"

class BokehTimeAndCategory():


## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 

# Called by opened up to give time
# Logic 2


    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @topic
# @results
# @firstyear
# @lastyear
# @topictype
# @inparameters

    def getOpenedUpToGivenTimePerTopic(topic,results,firstyear,lastyear,topictype,inparameters):
	parameters=bokutils.remove_options(inparameters)
	plen=len(parameters)
	if (topic == "location"):
	    subtarget=parameters[1]
	elif (plen > 1):
	    subtarget=topic+"-"+"-".join(parameters[1:(plen)])
	else:
	    subtarget=topic+"-"
	    
        alltopics={}
        musdict={}
        inyear="Year_opened"
        buckets=[]
        for i in range(firstyear,lastyear+1):
            buckets.append(float(0))
        print "len buckets="+str(len(buckets))
        obscount=0
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (topic  in res):
                if (inyear in res):
                    year=res[inyear]["value"]
		    obscount=obscount+1
		    if (topic == "location"):
			subs=bokutils.getSubFromLocation(res,topic,subtarget)
		    else:
			subs=bokutils.getSubFromtimeandcat(res,topic,topictype,subtarget)
			
		    for s in subs:
			alltopics[str(s)]=copy.deepcopy(buckets)
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (topic  in res):
		if (topic == "location"):
		    subs=bokutils.getSubFromLocation(res,topic,subtarget)
		else:
		    subs=bokutils.getSubFromtimeandcat(res,topic,topictype,subtarget)
	    else:
		subs=[]


            openyear=""
            if ("Year_opened" in res):
                openyear=res["Year_opened"]["value"]
            if (openyear == "" or len(subs) == 0):
                nop=0
            else:
		for s in subs:
		    musdict[uri]=(openyear,s)

	# Diff between logic 2 and 4: Openings should have 4
	lpar=parameters[0]
	if (lpar == "Year_opened"):
	    alltopics=BokehTimeAndCategory.logic4(musdict,alltopics,firstyear,lastyear)
	else:
	    alltopics=BokehTimeAndCategory.logic2(musdict,alltopics,firstyear,lastyear)
	return alltopics

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     


    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @topic
# @results
# @firstyear
# @lastyear
# @topictype
# @parameters

    def getOpenedDictionaryAllTopics(topic,results,firstyear,lastyear,topictype,parameters):
        alltopics={}
        musdict={}
        buckets=[]
        for i in range(firstyear,lastyear+1):
            buckets.append(float(0))
        
        for res in results["results"]["bindings"]:
	    if (definitions.YEAR_OPENED in res):
		subs=[definitions.YEAR_OPENED]
		for s in subs:
		    alltopics[str(s)]=copy.deepcopy(buckets)

        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (definitions.YEAR_OPENED  in res):
		subs=[definitions.YEAR_OPENED]
	    else:
		subs=[]

	    openyear=""
            if (definitions.YEAR_OPENED in res):
                openyear=res[definitions.YEAR_OPENED]["value"]
	    closeyear=""
	    if (definitions.YEAR_CLOSED in res):
                closeyear=res[definitions.YEAR_CLOSED]["value"]

            if (closeyear == "" or  openyear == "" or len(subs) == 0 ):
                nop=0
		print "FOUND A MISSING YEAR :"+str(closeyear)+":" +str(openyear) +":"+ str(len(subs))
            else:
		for s in subs:
		    musdict[uri]=(openyear,closeyear,s)

	alltopics=BokehTimeAndCategory.logic1(musdict,alltopics,firstyear,lastyear)
        return alltopics

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     
# Logic1

# Logic: Suppose the time selected is t; for each museum with an opening date (fo,to) and a closing date (fc,tc), we add to the count for time t as follows:
# If t < fo then 0
# If fo <= t <= to then t-fo+1 / to-fo+1
# If to < t < fc then 1
# If fc <= t <= tc then tc-t+1 / tc-fc+1 
# If t> tc then 0


    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @musdict
# @alltopics
# @firstyear
# @lastyear

    def logic1(musdict,alltopics,firstyear,lastyear):
        countobs=0
        for key, val in musdict.iteritems():
	    countobs=countobs+1
            openyear,closeyear,sub=val
            parts=openyear.split(":")
            fo=int(parts[0])
            to=int(parts[1])

            parts=closeyear.split(":")
            fc=int(parts[0])
            tc=int(parts[1])
	    # Changed
	    for t in range(firstyear,lastyear+1):
		if (t < fo or t > tc):
		    nop=0
		else:
		    idx=t-firstyear
		    if (t > to and t < fc):
			alltopics[str(sub)][idx]=alltopics[str(sub)][idx]+float(1)
		    else:
			if (t >= fo and t <= to):
			    frac=float(t - fo + 1)/float(to - fo + 1)
			    alltopics[str(sub)][idx]=alltopics[str(sub)][idx]+frac
			if (t >= fc and t <= tc):
			    frac=float(tc - t + 1)/float(tc - fc + 1)
			    alltopics[str(sub)][idx]=alltopics[str(sub)][idx]+frac



	
        for skey, sval in alltopics.iteritems():
	    vi=0
	    for v in sval:
		sval[vi]=int(v+float(0.5))
		vi=vi+1
	    
        timeseries=[]
        for i in range(firstyear,lastyear+1):
            timeseries.append(i)
        
        alltopics[TIME]=timeseries
    
        

	return alltopics
	
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     
# Logic2
# Logic: Suppose the time selected is t; for each museum with an opening date (fo,to) we add to the count for time t as follows:
# If t < fo then 0
# If fo <= t <= to then t-fo+1 / to-fo+1
# If to < t then 1

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @musdict
# @alltopics
# @firstyear
# @lastyear

    def logic2(musdict,alltopics,firstyear,lastyear):
        countobs=0
        for key, val in musdict.iteritems():
	    countobs=countobs+1
            openyear,sub=val
            parts=openyear.split(":")
            fo=int(parts[0])
            to=int(parts[1])

	    # changed
	    for t in range(firstyear,lastyear+1):
		idx=t-firstyear
		if (t < fo ):
		    nop=0
		elif (t >= fo and t <= to):
			frac=float(t-fo+1)/float(to-fo+1)
			alltopics[str(sub)][idx]=alltopics[str(sub)][idx]+frac
		elif(t > to):
		    alltopics[str(sub)][idx]=alltopics[str(sub)][idx]+float(1)


                        
        
        for skey, sval in alltopics.iteritems():
	    vi=0
	    for v in sval:
		sval[vi]=int(v+float(0.5))
		vi=vi+1

        timeseries=[]
        for i in range(firstyear,lastyear+1):
            timeseries.append(i)
        
        alltopics[TIME]=timeseries
	return alltopics

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     
# Logic4
# If t < fo then 0
# If fo <= t <= to then 1 / to-fo+1
# If to < t then 0


    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @musdict
# @alltopics
# @firstyear
# @lastyear

    def logic4(musdict,alltopics,firstyear,lastyear):
        countobs=0
        for key, val in musdict.iteritems():
	    countobs=countobs+1
            openyear,sub=val
            parts=openyear.split(":")
            fo=int(parts[0])
            to=int(parts[1])


	    # changed
	    for t in range(firstyear,lastyear+1):
		idx=t-firstyear
		if (t < fo  or to < t):
		    nop=0
		elif (t >= fo and t <= to):
			frac=float(1)/float(to-fo+1)
			alltopics[str(sub)][idx]=alltopics[str(sub)][idx]+frac
		elif(t > to):
		    alltopics[str(sub)][idx]=alltopics[str(sub)][idx]+float(1)


                        
        
        for skey, sval in alltopics.iteritems():
	    vi=0
	    for v in sval:
		sval[vi]=int(v+float(0.5))
		vi=vi+1

        timeseries=[]
        for i in range(firstyear,lastyear+1):
            timeseries.append(i)
        
        alltopics[TIME]=timeseries
	return alltopics

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     
# Logic5
# Logic: Suppose the time selected is t; for each museum with a closing date (fc,tc) we add to the count for time t as follows:
# If t < fc then 0
# If fc <= t <= tc then 1 / tc-fc+1
# If tc < t then 0

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @musdict
# @alltopics
# @firstyear
# @lastyear

    def logic5(musdict,alltopics,firstyear,lastyear):
        countobs=0
        for key, val in musdict.iteritems():
	    countobs=countobs+1
            closeyear,sub=val
            parts=closeyear.split(":")
            fc=int(parts[0])
            tc=int(parts[1])


	    for t in range(firstyear,lastyear+1):
		if (t < fc or tc < t):
		    nop=0
		else:
		    idx=t-firstyear
		    if (fc <= t and t <= tc):
			frac=float(1)/float(tc-fc+1)
			alltopics[str(sub)][idx]=alltopics[str(sub)][idx]+frac


        
                    
        for skey, sval in alltopics.iteritems():
	    vi=0
	    for v in sval:
		sval[vi]=int(v+float(0.5))
		vi=vi+1
        
        timeseries=[]
        for i in range(firstyear,lastyear+1):
            timeseries.append(i)
        
        alltopics[TIME]=timeseries
    
	return alltopics
    
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     
# Called by opened up to a given time, ALL

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @topic
# @results
# @firstyear
# @lastyear
# @topictype
# @parameters

    def getOpenedUpToGivenTimeAllTopics(topic,results,firstyear,lastyear,topictype,parameters):
        alltopics={}
        musdict={}
        inyear=definitions.YEAR_OPENED
        buckets=[]
        for i in range(firstyear,lastyear+1):
            buckets.append(float(0))
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
	    if (inyear in res):
		year=res[inyear]["value"]
		subs=[definitions.YEAR_OPENED]
		for s in subs:
		    alltopics[str(s)]=copy.deepcopy(buckets)
                
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            sub=""
            if (definitions.YEAR_OPENED  in res):
		subs=[definitions.YEAR_OPENED]
	    else:
		subs=[]
            openyear=""
            if (definitions.YEAR_OPENED in res):
                openyear=res[definitions.YEAR_OPENED]["value"]
            if (openyear == "" or len(subs) == 0):
                nop=0
            else:
		for s in subs:
		    musdict[uri]=(openyear,s)
                        
	alltopics=BokehTimeAndCategory.logic2(musdict,alltopics,firstyear,lastyear)
        return alltopics





## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     
## Called by open at a given time, logic 1
## Called by open over time , logic 1
    
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @topic
# @results
# @firstyear
# @lastyear
# @topictype
# @inparameters

    def getOpenedDictionaryPerTopic(topic,results,firstyear,lastyear,topictype,inparameters):
	parameters=bokutils.remove_options(inparameters)
	plen=len(parameters)
	if (topic == "location"):
	    subtarget=parameters[1]
	elif (plen > 1):
	    subtarget=topic+"-"+"-".join(parameters[1:(plen)])
	else:
	    subtarget=topic+"-"
	    
        alltopics={}
        musdict={}
        inyear=definitions.YEAR_OPENED
        buckets=[]
        for i in range(firstyear,lastyear+1):
            buckets.append(float(0))
        obscount=0
	
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (topic  in res):
                if (inyear in res):
                    year=res[inyear]["value"]
		    obscount=obscount+1
		    if (topic == ("location")):
			subs=bokutils.getSubFromLocation(res,topic,subtarget)
		    else:
			subs=bokutils.getSubFromtimeandcat(res,topic,topictype,subtarget)
			
		    for s in subs:
			alltopics[str(s)]=copy.deepcopy(buckets)
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (topic  in res):
		if (topic == "location"):
		    subs=bokutils.getSubFromLocation(res,topic,subtarget)
		else:
		    subs=bokutils.getSubFromtimeandcat(res,topic,topictype,subtarget)
	    else:
		subs=[]

	    openyear=""
            if (definitions.YEAR_OPENED in res):
                openyear=res[definitions.YEAR_OPENED]["value"]
	    closeyear=""
	    if (definitions.YEAR_CLOSED in res):
                closeyear=res[definitions.YEAR_CLOSED]["value"]

            if (closeyear == "" or  openyear == "" or len(subs) == 0 ):
                nop=0
		print "FOUND A MISSING YEAR :"+str(closeyear)+":" +str(openyear) +":"+ str(len(subs))
            else:
		for s in subs:
		    musdict[uri]=(openyear,closeyear,s)
                        
        
	alltopics=BokehTimeAndCategory.logic1(musdict,alltopics,firstyear,lastyear)
        return alltopics

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -     

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @topic
# @results
# @firstyear
# @lastyear
# @topictype
# @inparameters

    def getClosedDictionaryPerTopic(topic,results,firstyear,lastyear,topictype,inparameters):
	
	parameters=bokutils.remove_options(inparameters)
	plen=len(parameters)
	if (topic == "location"):
	    subtarget=parameters[1]
	elif (plen > 1):
	    subtarget=topic+"-"+"-".join(parameters[1:(plen)])
	else:
	    subtarget=topic+"-"

        alltopics={}
        musdict={}
        inyear=definitions.YEAR_CLOSED
        buckets=[]
        for i in range(firstyear,lastyear+1):
            buckets.append(float(0))
        obscount=0
        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (topic  in res):
                if (inyear in res):
                    year=res[inyear]["value"]
		    obscount=obscount+1
		    if (topic == "location"):
			subs=bokutils.getSubFromLocation(res,topic,subtarget)
		    else:
			subs=bokutils.getSubFromtimeandcat(res,topic,topictype,subtarget)
			
		    for s in subs:
			alltopics[str(s)]=copy.deepcopy(buckets)

        
        for res in results["results"]["bindings"]:
            uri=res["museum"]["value"]
            year=""
            if (topic  in res):
		if (topic == "location"):
		    subs=bokutils.getSubFromLocation(res,topic,subtarget)
		else:
		    subs=bokutils.getSubFromtimeandcat(res,topic,topictype,subtarget)
	    else:
		subs=[]

            closeyear=""
            if (definitions.YEAR_CLOSED in res):
                closeyear=res[definitions.YEAR_CLOSED]["value"]

            if (closeyear == "" or len(subs) == 0):
                nop=0
            else:
		for s in subs:
		    musdict[uri]=(closeyear,s)
                        
        
	alltopics=BokehTimeAndCategory.logic5(musdict,alltopics,firstyear,lastyear)
        return alltopics

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @results
# @topic
# @parameters
# @contextdict

    def showTopicPlot(results,topic,parameters,contextdict):   
        
        if (topic == definitions.SIZE or topic == definitions.DOMUS_SUBJECTCLASSIFICATION):
	    dtype="LISTTYPE"
	else:
	    dtype="HIERTYPE"
	    
	
	if (parameters[0] == definitions.YEAR_OPENED ):
            valuedict=BokehTimeAndCategory.getOpenedUpToGivenTimePerTopic(topic,results,bokutils.FIRST_YEAR,bokutils.LAST_YEAR,dtype,parameters)
	elif (parameters[0] == definitions.YEAR_CLOSED ):
            valuedict=BokehTimeAndCategory.getClosedDictionaryPerTopic(topic,results,bokutils.FIRST_YEAR,bokutils.LAST_YEAR,dtype,parameters)
	elif (parameters[0] == definitions.YEAR_EXISTS ):
            valuedict=BokehTimeAndCategory.getOpenedDictionaryPerTopic(topic,results,bokutils.FIRST_YEAR,bokutils.LAST_YEAR,dtype,parameters)

	colordict={}
	colors=bokutils.getColors(len(valuedict.keys()),False,False)
        cptr=0
        for k in valuedict.keys():
            colordict[k]=colors[cptr]
            cptr=cptr+1


	title=contextdict[bokutils.SERVER_PATH][len("/visualisations"):].replace("_"," ")
	newparameters=bokutils.remove_options(parameters)


	newparameters=None
        p=BokehTimeAndCategory.getTimePlot(valuedict,colordict,title,"Year","Count",parameters,contextdict)
        
        
        return p
    

    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @valuedict
# @colors
# @title
# @xtitle
# @ytitle

    def getTimePlot(valuedict,colors,title,xtitle,ytitle):
    
        x_time=[]
        
        for i, year in enumerate(valuedict["Time"]):
            dyear=datetime.datetime(int(year), 1, 1, 0, 0)
            x_time.append(dyear)
    
    
        p = figure(plot_height=bokutils.PLOT_HEIGHT,plot_width=bokutils.PLOT_WIDTH, x_axis_type='datetime',title=title, tools=[hover,"crosshair","box_zoom","reset","pan"])
        p.xaxis.formatter = DatetimeTickFormatter(years = ['%Y'])
    
        p.xaxis.axis_label = xtitle
        p.yaxis.axis_label = ytitle
        p.xaxis.major_label_orientation = 'vertical'
    
        #Fix this in case of topic plot
        #band_x = np.append(x_time, x_time[::-1])
        #band_y = np.append(valuedict["Year_closed"], valuedict["Year_opened"][::-1])
    
        
        # a line works fine with time objects
        kcount=0
        for key,val in valuedict.items():
            if (key != TIME):
                
                desc=[]
                for i in range(0,len(valuedict[TIME])):
                    desc.append(key)
                source = ColumnDataSource(data=dict(
                    x=x_time,
                    y=valuedict[key],
                    desc=desc))
                p.line(x_time, valuedict[key],color=colors[key],legend=key)
                p.circle('x', 'y', size=5, source=source,color=colors[key])
                kcount=kcount+1
                if (kcount > bokutils.MAX_CATEGORY_LINES):
                    break
                
        #p.patch(band_x, band_y, color='#7570B3', fill_alpha=0.2)
        p.legend.click_policy="hide"
        p.legend.orientation = "vertical"
        p.legend.location = "top_left"
        return p

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
##  BUG VALUE IS zeor otherwise it works.
##
    @staticmethod

## Purpose:Removes type info from name
# Arguments:
# 
# @valuedict
# @colors
# @title
# @xtitle
# @ytitle
# @parameters
# @contextdict

    def getTimePlot(valuedict,colors,title,xtitle,ytitle,parameters,contextdict):



#          tooltips=[
#                  ("Year", "@x{%Y}"),
#                  ("Value", "@y{int}"),
#                  ("Category", "@desc"),
#                  ],





        x_time=[]
        
        for i, year in enumerate(valuedict["Time"]):
            dyear=datetime.datetime(int(year), 1, 1, 0, 0)
            x_time.append(dyear)

    # Why are tooltip.style not working?
    # Is there a css way to force orderly popup position like float left sequential?
        callback_hover = CustomJS(code="""
        var tooltip = document.getElementById("static-tooltip");
          //console.log(tooltip);
	if (tooltip != null )
	{
	  tooltip.style.color = "blue";
	  tooltip.style.left = "0px";
	 }
	""")
        hover =HoverTool(
 	  tooltips="""
	  <div id="static-tooltip" style="background-color:lightblue">
 		   <span style="font-size: 16px;">Category: @desc</span>
 		   <span style="font-size: 14px;"><br>Year:@x{%Y}</span>
 		   <span style="font-size: 14px;"><br>Value:@y{int}</span>
 		   </div>
 		   """, callback=callback_hover,

        formatters={
                'x'      : 'datetime', # use 'datetime' formatter for 'date' field
                },
    
        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='mouse',
        point_policy="snap_to_data"
            
        )
    
    
        p = figure(plot_height=bokutils.PLOT_HEIGHT,plot_width=bokutils.PLOT_WIDTH, x_axis_type='datetime',title=title, tools=[hover,"crosshair","box_zoom","reset","pan"])
        p.xaxis.formatter = DatetimeTickFormatter(years = ['%Y'])
    
        p.xaxis.axis_label = xtitle
        p.yaxis.axis_label = ytitle
        p.xaxis.major_label_orientation = 'vertical'
    
        #Fix this in case of topic plot
        #band_x = np.append(x_time, x_time[::-1])
        #band_y = np.append(valuedict[definitions.YEAR_CLOSED], valuedict[definitions.YEAR_OPENED][::-1])
    
        
        # a line works fine with time objects
        kcount=0
	#legend = Legend(items=[LegendItem(label=dict(field="x"), renderers=[l])])
	litems=[]
	rendererdone=False
        #for key,val in valuedict.items():
        for key in sorted(valuedict.iterkeys()):
	    val=valuedict[key]
            if (key != TIME):
                desc=[]
                for i in range(0,len(valuedict[TIME])):
                    desc.append(key)
                source = ColumnDataSource(data=dict(
                    x=x_time,
                    y=valuedict[key],
                    desc=desc
		    ))
                circ=p.circle('x', 'y', size=5, source=source,color=colors[key])
		cp=circ.properties_with_refs()
		cpp=circ.properties(with_bases=True)
		cpc=circ.properties_containers()
		cpr=circ.properties_with_values(include_defaults=True)
 		grs = circ.select(dict(type=GlyphRenderer))
 		for glyph in grs:
 		    if isinstance(glyph.glyph, Circle):
 			circle_renderer = glyph
			c_pr=circle_renderer.properties_with_values(include_defaults=True)
			

# https://groups.google.com/a/continuum.io/forum/#!topic/bokeh/a3TblmxcNKU
#https://github.com/bokeh/bokeh/issues/1512
#https://github.com/bokeh/bokeh/issues/1189

                hover.renderers.append(circle_renderer)


                litems.append(LegendItem(label=bokutils.makeLegendKey(key), renderers=[circ]))
#                p.line(x_time, valuedict[key],color=colors[key],legend=bokutils.makeLegendKey(key))
                p.line(x_time, valuedict[key],color=colors[key])
                kcount=kcount+1
		ltup=(key,key)
                
        #p.patch(band_x, band_y, color='#7570B3', fill_alpha=0.2)
        #p.legend.click_policy="hide"
        #p.legend.orientation = "vertical"
        #p.legend.location = "top_left"

	#new_legend = p.legend[0]
	#p.legend[0].plot = None
	#p.add_layout(new_legend, 'right')

	p.add_layout(Legend(items=litems,
			    glyph_height=bokutils.LEGEND_GLYPH_HEIGHT,
			    glyph_width=bokutils.LEGEND_GLYPH_WIDTH,),
		     'right')



        return p

## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @me
# @parameters
# @contextdict

    def createPlot(self,me,parameters,contextdict):

	location=str(contextdict[bokutils.PLOT_LOCATION_KEY][0].replace("'",""))

	props=[definitions.NAME_OF_MUSEUM,
	       definitions.PROJECT_ID,
	       definitions.YEAR_OPENED,
	       definitions.YEAR_CLOSED,
	       me]
	markerdict={}
        if (location != bokutils.PLOT_LOCATION_UK):
	    markerdict['${GEOENTITY}']=location
	    props.append(definitions.GEOCOL)


 	try:
 	    results=apputils.getMarkerData(props,vardict=markerdict)
 	except Exception, e:
 	    print str(e)
 	    return render_template('message.html', title="Internal application error",message="The application has experienced an error at views.py at line: 525   \n <br/><p><pre>"+str(e)+"</pre></p>")
	


        
        
        
        p = BokehTimeAndCategory.showTopicPlot(results,me,parameters,contextdict)
               
        return p
        
## - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - -  - - - - 


## Purpose:Removes type info from name
# Arguments:
# 
# @me
# @parameters
# @contextdict

    def createLocationPlot(self,me,parameters,contextdict):
	results=apputils.getVizLocationData(parameters,bokutils.FIRST_YEAR,bokutils.LAST_YEAR)
        p = BokehTimeAndCategory.showTopicPlot(results,me,parameters,contextdict)
	
        return p
        
    
