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
${WDIR}/create_geocodes.ksh
${WDIR}/Create_ontology.ksh
#The diretory name should be given as input to readontology to facilitate a predicates and datatypelist distinction
${WDIR}/Create_processing_template.ksh
${WDIR}/Process_template.ksh
${WDIR}/N3_to_RDF.ksh
${WDIR}/Load_triples_to_DB.ksh
#Add geonames to sheet this cannot be repeated so should only be part of a full run
#and orchestrated to run before the main run
python ${WDIR}/add_geonames_to_mainsheet.py ${WDIR}/../main/${FNAME} ${WDIR}/${INFILE} > ${WDIR}/zz.csv 
mv -v ${WDIR}/zz.csv  ${WDIR}/../main/${FNAME_GEONAMES}
