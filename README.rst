This is a parser for CSV statements produced by UniCredit Bank Czech Republic and Slovakia a.s.
from within the report in Account History (export in UNICREDIT format).

It is a plugin for `ofxstatement`_.

.. _ofxstatement: https://github.com/kedder/ofxstatement

Usage:

    ofxstatement convert -t unicreditcz bank-statement.csv bank-statement.ofx

    ofxstatement convert -t unicreditcz:EUR bank-statement.csv bank-statement.ofx

Configuration:

    ofxstatement edit-config

and set e.g. the following

    [unicreditcz:EUR]

    plugin = unicreditcz

    currency = EUR

    account = Uni EUR
