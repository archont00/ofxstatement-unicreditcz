#!/bin/bash
in=export-2019 # Name of CSV export from the bank 'export-2019.csv'

if [[ ! -d .venv ]]; then
  virtualenv -p python3 --no-site-packages .venv
fi
. .venv/bin/activate
python setup.py develop
ofxstatement convert -t unicreditcz:CZK $in.csv $in.ofx
cat $in.ofx | xmllint --format --encode UTF-8 - > $in-2.ofx && mv $in-2.ofx $in.ofx
