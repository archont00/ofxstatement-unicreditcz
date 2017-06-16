#!/bin/bash

# This is a wrapper for
#   ofxstatement convert -t unicreditcz:CZK input.csv output.ofx
# which:
# - reformats output.ofx to be human readable


# Dependency:
# - bash
# - ofxstatement
# - ofxstatement-unicreditcz (plugin)
# - uuidgen
# - xmllint


if [[ "x$1" = "x" ]]; then
  echo "Convert CSV (Finance // Účty // Historie - UNICREDIT format) export of"
  echo "transactional history from Unicredit bank to OFX format"
  echo "Usage:"
  echo "  $0 input.csv"
  exit 1
fi


# Change encoding to UTF-8
#fname="/tmp/$1-utf"
#cp "$1" "$fname"
#iconv -f WINDOWS-1250 -t UTF-8 < "$1" > "$fname"

d_out="`dirname "$1"`"
f_out="`basename "$1" .csv`.ofx"

/usr/bin/ofxstatement convert -t unicreditcz:CZK "$1" "${d_out}/${f_out}"

tmpf="$(uuidgen)"
cat "${d_out}/${f_out}" | xmllint --format --encode UTF-8 - > "${d_out}/${tmpf}"
mv "${d_out}/${tmpf}" "${d_out}/${f_out}"


echo "${d_out}/${f_out} file saved."
echo "Use GNU Cash File // Import // Transactions OFX."
