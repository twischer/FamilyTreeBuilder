#! /bin/bash
TEMPLATE="templateFading"
#TEMPLATE="templateGolden"
#TEMPLATE="templateOverlappingRect"


while [ 1 ]
do
	./family2latex.py ./data/family.xml > family.tex
	pdflatex ./${TEMPLATE}.tex
	read
done
