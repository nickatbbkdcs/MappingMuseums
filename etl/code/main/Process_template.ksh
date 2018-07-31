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
cp -v ${WDIR}/${NNAME} ${WDIR}/${NNAME}.bak||true
#python ${XBIN}/processMuseums.py ${WDIR}/${FNAME_GEONAMES} ${WDIR}/${TNAME} |tee  ${WDIR}/${NNAME}
python ${XBIN}/processMuseums.py ${WDIR}/${FNAME_GEONAMES} ${WDIR}/${TNAME}  -m main >  ${WDIR}/${NNAME}
#diff ${WDIR}/${NNAME} ${WDIR}/${NNAME}.bak
#
ls -lh ${WDIR}/${NNAME}
cat ${WDIR}/${NNAME}|wc -l
#
cat ${WDIR}/${NNAME} |grep -v '"000000"^^xsd:integer'  |grep -v '""^^xsd' > ${WDIR}/xx
#
ls -lh ${WDIR}/xx
cat ${WDIR}/xx|wc -l
#
mv -v ${WDIR}/xx ${WDIR}/${NNAME}
ls -lh ${WDIR}/${NNAME}
cat ${WDIR}/${NNAME}|wc -l
