#!/bin/bash

cd `dirname $0`

FILES=$(find -iname '*.dia')
if [ `echo $FILES | wc -l` -gt 0 ]; then
for f in $FILES; do
  feps=$(echo $f | sed 's/.dia$/.eps/i');
  fpdf=$(echo $f | sed 's/.dia$/.pdf/i');
  if [ ! "$fpdf" -ot "$f" ]; then continue; fi # skip if pdf is newer than source
  echo "$f --> $feps"
  dia -e "$feps" -t eps "$f"
done
fi

FILES=$(find -iname '*.svg')
if [ `echo $FILES | wc -l` -gt 0 ]; then
for f in $FILES; do
#   feps=`basename "$f" .svg`.eps;
  fpdf=$(echo $f | sed 's/.svg$/.pdf/i');
  if [ ! "$fpdf" -ot "$f" ]; then continue; fi # skip if pdf is newer than source
  echo "$f --> $fpdf"
  #inkscape "$f" --export-text-to-path --export-eps "$feps" --without-gui --export-area-drawing --vacuum-defs;
  inkscape "$f" --export-text-to-path --export-pdf "$fpdf" --without-gui --export-area-drawing --vacuum-defs;
done
fi

FILES=$(find -iname '*.eps')
if [ `echo $FILES | wc -l` -gt 0 ]; then
for feps in $FILES; do
  fpdf=$(echo $feps | sed 's/.eps$/.pdf/i');
  if [ ! "$fpdf" -ot "$feps" ]; then continue; fi # skip if pdf is newer than source
  echo "$feps --> $fpdf"
  epstopdf "$feps";
done
fi

FILES=$(find -iname '*.pdf' | grep -v "\-crop.pdf")
if [ `echo $FILES | wc -l` -gt 0 ]; then
for fpdf in $FILES; do
  pdf2crop=$(echo "$fpdf" | sed 's/.pdf$/-crop.pdf/i');
  if [ ! "$pdf2crop" -ot "$fpdf" ]; then continue; fi # skip if pdf2crop is newer than source
  echo "$fpdf --> $pdf2crop"
  pdfcrop "$fpdf";
done
fi
