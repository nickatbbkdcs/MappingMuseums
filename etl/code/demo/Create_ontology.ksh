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
iconv -f ascii -t utf8 -c ${FNAME} > xxx ; mv -v xxx ${FNAME}
ls -l ${FNAME}
#
python ${XBIN}/makeGMLNodesFromSheet.py ${MLNAMES} ${FNAME} ${GNAME} ${GNODESNAME} > sheet.graphml ; 
cat P1.graphml sheet.graphml P2.graphml  > demoontology.graphml
#ls -l demoontology.graphml
