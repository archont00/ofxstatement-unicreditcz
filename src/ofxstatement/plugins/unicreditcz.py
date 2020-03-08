import csv
from datetime import datetime

from ofxstatement import statement
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
#from ofxstatement.statement import Statement


class UniCreditCZPlugin(Plugin):
    """UniCredit Bank Czech Republic and Slovakia a.s. (CSV format since cca 2018, new banking)
    """

    def get_parser(self, filename):
        UniCreditCZPlugin.encoding = self.settings.get('charset', 'utf-8')
        f = open(filename, "r", encoding=UniCreditCZPlugin.encoding)
        parser = UniCreditCZParser(f)
        parser.statement.currency = self.settings.get('currency', 'CZK')
        parser.statement.bank_id = self.settings.get('bank', 'BACXCZPP')
        parser.statement.account_id = self.settings.get('account', '')
        parser.statement.account_type = self.settings.get('account_type', 'CHECKING')
        parser.statement.trntype = "XFER"
        return parser


class UniCreditCZParser(CsvStatementParser):

    # GnuCash recognises the following descriptive fields:
    # - Header for Transaction Journal:
    #   - Description
    #   - Notes
    # - Line item memo for each account in a single Transaction Journal:
    #   - Memo
    #
    # .payee is assigned to "Description" in GnuCash
    # .memo is assigned to "Memo" in GnuCash and also concatenated
    #       to "Notes" after "OFX ext. info" and "Trans type"
    #
    # When .payee is empty, GnuCash assigns .memo to:
    # - "Description" and does not concatenate to "Notes"
    # - "Memo"
    #
    # Although ofxstatement can create bank_account_to, GnuCash ignores it.
    #
    # In GnuCash, .check_no (if empty, then .refnum) is assigned to "Num".
    #
    # The approach is:
    # - merge counterparty name (.payee) + account number + bank code
    # - merge pmt reference (.memo) + other payment specifics (VS, KS, SS)

    # The columns are:
    #  0 Číslo účtu
    #  1 Částka
    #  2 Měna
    #  3 Datum rezervace
    #  4 Datum
    #  5 Kód banky protistrany : .payee 6
    #  6 Název banky protistrany 1 :
    #  7 Banka příjemce 2 :
    #  8 Číslo účtu protistrany : .payee 5
    #  9 Příjemce : .payee 1
    #  10 Adresa 1 : .payee 2
    #  11 Adresa 2 : .payee 3
    #  12 Adresa 3 : .payee 4
    #  13 Detaily transakce 1 : .memo 1
    #  14 Detaily transakce 2 : .memo 2
    #  15 Detaily transakce 3 : .memo 3
    #  16 Detaily transakce 4 : .memo 4
    #  17 Detaily transakce 5 : .memo 5
    #  18 Detaily transakce 6 : .memo 6
    #  19 KS : .memo 8
    #  20 VS : .memo 7 and .check_no
    #  21 SS : .memo 9
    #  22 Směnný kurz
    #  23 Referenční číslo
    #  24 Status
    #  25 Datum zamítnutí
    #  26 Detail zamítnutí
    #  27 Registrační číslo TPP
    #  28 Název TPP
    #  29 Reference příkazu TPP
    #  30 Země registrace
    #  31 Kód národní autority

    mappings = {
        "amount": 1,
        "date": 3,
        "date_user": 4,
        "payee": 9,
        "memo": 13,
        "check_no": 20,
        "refnum": 23,
    }

    #date_format = "%Y-%m-%d %H:%M:%S"
    date_format = "%Y-%m-%d"


    def split_records(self):
        return csv.reader(self.fin, delimiter=';', quotechar='"')


    def parse_record(self, line):
        # Ignore headers
        if self.cur_record <= 4:
            return None

        # Ignore incomplete lines
        if len(line) < 24:
            return None

        StatementLine = super(UniCreditCZParser, self).parse_record(line)

        StatementLine.id = statement.generate_transaction_id(StatementLine)

        if StatementLine.amount == 0:
            return None

        if   line[13].startswith("SRÁŽKOVÁ DAŇ"):
            StatementLine.trntype = "DEBIT"
        elif line[7].startswith("UROK DO"):
            StatementLine.trntype = "INT"
        elif line[7].startswith("Poplatek za "):
            StatementLine.trntype = "FEE"
        elif line[7].startswith("VRÁCENÍ POPLATKU ZA "):
            StatementLine.trntype = "FEE"

        StatementLine.memo = StatementLine.memo + " " + line[14]
        StatementLine.memo = StatementLine.memo + " " + line[15]
        StatementLine.memo = StatementLine.memo + " " + line[16]
        StatementLine.memo = StatementLine.memo + " " + line[17]
        StatementLine.memo = StatementLine.memo + " " + line[18]
        StatementLine.memo = StatementLine.memo.split()
        # Remove null items
        StatementLine.memo = [x for x in StatementLine.memo if x]
        StatementLine.memo = " ".join(StatementLine.memo)

        if not (line[20] == "" or line[20] == " "):
            StatementLine.memo = StatementLine.memo + "|VS:"  + line[20]

        if not (line[19] == "" or line[19] == " "):
            StatementLine.memo = StatementLine.memo + "|KS:"  + line[19]

        if not (line[21] == "" or line[21] == " "):
            StatementLine.memo = StatementLine.memo + "|SS:" + line[21]

        StatementLine.memo = StatementLine.memo.strip("|")

        # Counterparty name and address
        StatementLine.payee = StatementLine.payee + ", " + line[10].strip()
        StatementLine.payee = StatementLine.payee + ", " + line[11].strip()
        StatementLine.payee = StatementLine.payee + ", " + line[12].strip()
        StatementLine.payee = StatementLine.payee.split(", ")
        StatementLine.payee = [x for x in StatementLine.payee if x]
        StatementLine.payee = ", ".join(StatementLine.payee)

        # Bank account of counterparty
        StatementLine.payee = StatementLine.payee + "|" + line[8]
        StatementLine.payee = StatementLine.payee + "/" + line[5]
        StatementLine.payee = StatementLine.payee.strip("|")
        StatementLine.payee = StatementLine.payee.strip("/")

        return StatementLine

    # Remove thousands separator
    # Substitute decimal point "," with "."
    def parse_float(self, value):
        value = value.replace(".", "")
        value = value.replace(",", ".")
        return super(UniCreditCZParser, self).parse_float(value)
