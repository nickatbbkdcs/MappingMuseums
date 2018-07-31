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
python ${XBIN}/processMuseums.py  ${WDIR}/${INFILE} ${WDIR}/${TNAME} -c yes -m geocolumns > ${DATANAME}.n3
#diff ${DATANAME}.n3 ${DATANAME}.n3.bak
#python ./processMuseums.py  ${WDIR}/${INFILE} ${WDIR}/${TNAME} -c yes > ${DATANAME}.n3
ls -lh ${WDIR}/${DATANAME}.n3 
cat ${WDIR}/${DATANAME}.n3|wc -l
cat ${DATANAME}.n3 | grep -v '""^^xsd' > ${WDIR}/xx
mv -v ${WDIR}/xx ${WDIR}/${DATANAME}.n3
#cat ${WDIR}/${DATANAME}.n3|sed 's/City of London (London Borough)/City of London/g' > xx; mv -v  xx ${WDIR}/${DATANAME}.n3
#cat ${WDIR}/${DATANAME}.n3|sed 's/"London"/"Greater London"/g' > xx; mv -v  xx ${WDIR}/${DATANAME}.n3
#cat ${WDIR}/${DATANAME}.n3|sed 's/London (English Region)/Greater London/g' > xx; mv -v  xx ${WDIR}/${DATANAME}.n3
