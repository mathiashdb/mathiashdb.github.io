#!/bin/bash

python3 generate_grants_table.py

rm *.bbl *.aux
xelatex cv-hudoba-de-badyn.tex
xelatex cv-hudoba-de-badyn.tex
biber cv-hudoba-de-badyn
xelatex cv-hudoba-de-badyn.tex
xelatex cv-hudoba-de-badyn.tex

xelatex yr-1-report-hudoba-de-badyn.tex
xelatex yr-1-report-hudoba-de-badyn.tex
biber yr-1-report-hudoba-de-badyn
xelatex yr-1-report-hudoba-de-badyn.tex
xelatex yr-1-report-hudoba-de-badyn.tex
