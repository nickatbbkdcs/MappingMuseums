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
. ../etl.def
. ./suite.env
#cd ${MAINXDIR}
# Generate the files
cd ${WDIR}
python ${WDIR}/location_Enumbers.py ${WDIR}/../main/${FNAME}| grep  \*\? | sed s/\*\?\#\?//g > ${WDIR}/${GEOBASE_U}
python ${WDIR}/england_Enumbers.py ${WDIR}/../main/${FNAME}| grep \*\? | cut -c 7- > ${WDIR}/${GEOBASE_E}
# make into one file
cat ${WDIR}/${GEOBASE_E} ${WDIR}/${GEOBASE_U} > ${WDIR}/${GEOBASE_A}
# add the quotes
cat ${WDIR}/${GEOBASE_A}|sed  s/,/\",\"/g|sed  s/$/\"/g|sed  s/^/\"/g|sed  s/\"\"//g  >  ${WDIR}/xx ; mv -v ${WDIR}/xx ${WDIR}/${GEOBASE_A}
# replace , with $
cat ${WDIR}/${GEOBASE_A}|sed s/,/\$/g > xx; mv -v xx ${WDIR}/${GEOBASE_A}
cat ${WDIR}/${GEOBASE_H} ${WDIR}/${GEOBASE_A} >  ${WDIR}/xx ; mv -v ${WDIR}/xx ${WDIR}/${GEOBASE_A}
ls -lh ${WDIR}/${GEOBASE_A}
mv -v  ${WDIR}/${GEOBASE_A} ${WDIR}/${INFILE}
