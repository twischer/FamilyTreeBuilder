#! /bin/bash
while [ 1 ]
do
	./family2latex.py ./data/family.xml > family.tex
	pdflatex ./template.tex
	read
done
