This is a parser for CSV statements produced by UniCredit Bank Czech Republic and Slovakia a.s. from account transaction history. It is a plugin for `ofxstatement`_.

.. _ofxstatement: https://github.com/kedder/ofxstatement

It supports two formats of CSV files:
::

-t unicreditcz16      CSV (called as "UNICREDIT") used till 2016
-t unicreditcz        CSV used since 2017

Usage
=====
::

$   ofxstatement convert -t unicreditcz export.csv export.ofx
$   ofxstatement convert -t unicreditcz:EUR export.csv export.ofx

Configuration
=============

To edit the configuration file run::

$ ofxstatement edit-config

and set any options you wish::

 [unicreditcz:EUR]
 plugin = unicreditcz
 currency = EUR
 account = Uni EUR
