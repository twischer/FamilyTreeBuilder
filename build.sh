#! /bin/bash
./family2latex.py ./family.xml > family.tex
pdflatex ./template.tex
okular ./template.pdf
