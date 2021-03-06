This is a parser for CSV statements produced by UniCredit Bank Czech Republic and Slovakia a.s. from account transaction history. It is a plugin for `ofxstatement`_.

.. _ofxstatement: https://github.com/kedder/ofxstatement

It supports multiple formats of CSV files (blame the bank management)::

-t unicreditcz16      CSV (called as "UNICREDIT") used till 07-Oct-17 (old banking)
-t unicreditcz17      CSV (called as "UNICREDIT") used till 07-Oct-17 (new banking)
-t unicreditcz18      CSV used since 08-Oct-2017 till cca half year 2019 (new banking)
-t unicreditcz        CSV used since cca half year 2019 (new banking)

Installation
============

Get ofxstatement installed and working. Then, you can check the test.sh script for inspiration. System-wide installation is out of scope of this README.

Usage
=====
::

  $ ofxstatement convert -t unicreditcz export.csv export.ofx
  $ ofxstatement convert -t unicreditcz:EUR export.csv export.ofx

Configuration
=============

To edit the configuration file run::

  $ ofxstatement edit-config

and set any options you wish::

  [unicreditcz:EUR]
  plugin = unicreditcz
  currency = EUR
  account = Uni EUR
