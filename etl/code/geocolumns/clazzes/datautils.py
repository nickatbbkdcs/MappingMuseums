#!/usr/bin/env python

version = "1.7"
version_info = (1,7,0,"rc-1")
__revision__ = "$Rev: 66 $"

"""
Documentation
===============

Process infile .  Basic usage as a module:

process parameters infile

#  $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3

"""

# - - - - - - - - - - - - - - -    

def stripType(name):
    # Also remove type info
    lparen=name.find("(")
    if (lparen > -1):
	return name[0:lparen-1]
    else:
	return name
    
