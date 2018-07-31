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
# $$Author$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - # 
set -ex # set trace
rdf2rdf ${WDIR}/${DATANAME}.n3 ${WDIR}/${DATANAME}.rdf
ls -lh ${WDIR}/${DATANAME}.rdf 
cat ${WDIR}/${DATANAME}.rdf|wc -l
mkdir -p ${STAGING_ARENA}/RDF/V${VERSION}||true
mv -v ${WDIR}/${DATANAME}.rdf ${STAGING_ARENA}/RDF/V${VERSION}/${DATANAME}.rdf

