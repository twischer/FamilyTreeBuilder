#! /bin/bash
while [ 1 ]
do
	./family2latex.py ./family.xml > family.tex
	pdflatex ./template.tex
	okular ./template.pdf
done
