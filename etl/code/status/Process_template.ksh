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
#cp -v ${DATANAME}.n3 ${DATANAME}.n3.bak
python ${XBIN}/processMuseums.py ${WDIR}/${FNAME} ${WDIR}/${TNAME} > ${DATANAME}.n3
#diff  ${DATANAME}.n3 ${DATANAME}.n3.bak
ls -lh ${WDIR}/${DATANAME}.n3 
cat ${WDIR}/${DATANAME}.n3|wc -l
cat ${DATANAME}.n3 | grep -v '""^^xsd' > ${WDIR}/xx
mv -v ${WDIR}/xx ${WDIR}/${DATANAME}.n3
