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
# 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - # 
set -ex # set trace
WDIR=/home/nlarsson/bbk/python/aux/visitornumbers
GFILE=VisitorNumbers.graphml
INFILE=splitline.csv
FNAME=${INFILE}
TNAME=visitors.template
VERSION=5
DATANAME="Visitors"
cd ${WDIR}
../../fixgraphmlfile.ksh ${WDIR}/${GFILE}
iconv -f ascii -t utf8 -c  ${WDIR}/${INFILE} > xx; mv -v xx ${WDIR}/${INFILE}
python ../../readontology.py ${WDIR}/${GFILE} visitornumbers > ${WDIR}/${TNAME}
python ../../processMuseums.py ${WDIR}/${FNAME} ${WDIR}/${TNAME} > ${DATANAME}.n3
cat ${DATANAME}.n3 | grep -v '""^^xsd' > ${WDIR}/xx
mv -v ${WDIR}/xx ${WDIR}/${DATANAME}.n3
rdf2rdf ${WDIR}/${DATANAME}.n3 ${WDIR}/${DATANAME}.rdf
mv -v ${WDIR}/${DATANAME}.rdf ${WDIR}/../../RDF/V${VERSION}/${DATANAME}.rdf
