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
ls -l ${FNAME_GEONAMES}
#   
python ${XBIN}/makeGMLNodesFromSheet.py ${MLNAMES} ${FNAME_GEONAMES} ${GNAME} ${GNODESNAME} > madesheet.graphml ; 
cat museumontologyP1.graphml madesheet.graphml museumontologyP2.graphml  > museumontology.graphml
ls -l museumontology.graphml
${XBIN}/fixgraphmlfile.ksh `pwd`/museumontology.graphml
iconv -f ascii -t utf8 -c ${FNAME_GEONAMES} > xxx ; mv -v xxx ${FNAME_GEONAMES}
ls -l ${FNAME_GEONAMES}
