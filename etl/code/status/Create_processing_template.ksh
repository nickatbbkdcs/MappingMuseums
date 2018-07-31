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
ls -l ${WDIR}/${GFILE}
#cp -v ${WDIR}/${TNAME} ${WDIR}/${TNAME}.bak
python ${XBIN}/readontology.py ${WDIR}/${GFILE} ${DATANAME} > ${WDIR}/${TNAME}
#diff ${WDIR}/${TNAME} ${WDIR}/${TNAME}.bak
ls -l ${WDIR}/${TNAME}
