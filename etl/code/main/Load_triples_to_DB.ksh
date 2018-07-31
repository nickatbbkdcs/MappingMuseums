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
VLOADDIR=${STAGING_ARENA}/RDF/V${VERSION}
ISQL=/home/nlarsson/sw/virtuoso_install/bin/isql
$ISQL 1111 dba dba exec="delete  from db.dba.load_list ;"
$ISQL 1111 dba dba exec="ld_dir ('${VLOADDIR}', '*', 'http://bbk.ac.uk/MuseumMapProject/graph/v${VERSION}');\
rdf_loader_run ();"
