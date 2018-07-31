#!/usr/bin/ksh
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - # 
####SCRIPT NAME :
####SHORT  DESC :   
#    
### SYNOPSIS 
#    
#    
#    
#    
### DESCRIPTION 
#    
#    
#    
#    
### RETURNS 
#    
#    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - # 
#$$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - # 
set -ex # set trace
. ../etl.def
. ./suite.env
${WDIR}/Create_ontology.ksh
#The diretory name should be given as input to readontology to facilitate a predicates and datatypelist distinction
${WDIR}/Create_processing_template.ksh
${WDIR}/Process_template.ksh
${WDIR}/N3_to_RDF.ksh
#${WDIR}/Load_triples_to_DB.ksh
