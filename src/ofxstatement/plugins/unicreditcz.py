import csv
from datetime import datetime

from ofxstatement import statement
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
#from ofxstatement.statement import Statement


class UniCreditCZPlugin(Plugin):
    """UniCredit Bank Czech Republic and Slovakia a.s. (CSV format since 08-Oct-2017, new banking)
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

    # The columns are:
    #  0 Účet
    #  1 Částka
    #  2 Měna
    #  3 Datum zaúčtování
    #  4 Valuta
    #  5 Banka
    #  6 Název banky
    #  7 Název banky
    #  8 Číslo účtu
    #  9 Název účtu
    # 10 Adresa
    # 11 Adresa
    # 12 Adresa
    # 13 Detaily transakce
    # 14 Detaily transakce
    # 15 Detaily transakce
    # 16 Detaily transakce
    # 17 Detaily transakce
    # 18 Detaily transakce
    # 19 Konstatní kód
    # 20 Variabilní kód
    # 21 Specifický kód
    # 22 Platební titul
    # 23 Reference
    # 24 Status

    mappings = {
        "amount": 1,
        "date": 3,
        "date_user": 4,
        "payee": 9,
        "memo": 13,
        "check_no": 20,
        "refnum": 23,
    }

    date_user_format = "%Y-%m-%d"
    date_format = "%Y-%m-%d"


    def split_records(self):
        return csv.reader(self.fin, delimiter=';', quotechar='"')


    def parse_record(self, line):
        # Ignore headers
        if self.cur_record <= 3:
            return None

        # Ignore incomplete lines
        if len(line) < 24:
            return None

        StatementLine = super(UniCreditCZParser, self).parse_record(line)

        StatementLine.date_user = datetime.strptime(StatementLine.date_user, self.date_user_format)

        StatementLine.id = statement.generate_transaction_id(StatementLine)

        if StatementLine.amount == 0:
            return None

        if   line[13].startswith("SRÁŽKOVÁ DAŇ"):
            StatementLine.trntype = "DEBIT"
        elif line[7].startswith("ÚROKY"):
            StatementLine.trntype = "INT"
        elif line[7].startswith("Poplatek za "):
            StatementLine.trntype = "FEE"
        elif line[7].startswith("VRÁCENÍ POPLATKU ZA "):
            StatementLine.trntype = "FEE"

        # .payee is imported as "Description" in GnuCash
        # .memo is imported as "Notes" in GnuCash
        # When .payee is empty, GnuCash imports .memo to "Description" and keeps "Notes" empty
        StatementLine.memo = StatementLine.memo + " " + line[14]
        StatementLine.memo = StatementLine.memo + " " + line[15]
        StatementLine.memo = StatementLine.memo + " " + line[16]
        StatementLine.memo = StatementLine.memo + " " + line[17]
        StatementLine.memo = StatementLine.memo + " " + line[18]
        StatementLine.memo = " ".join(StatementLine.memo.split())
        StatementLine.memo = StatementLine.memo.strip()

        StatementLine.payee = " ".join(StatementLine.payee.split())
        StatementLine.payee = StatementLine.payee.strip()

        if not (line[8]  == "" or line[8]  == " "):
            StatementLine.memo = StatementLine.memo + "|ÚČ: "  + line[8]  + "/" + line[5]

        if not (line[20] == "" or line[20] == " "):
            StatementLine.memo = StatementLine.memo + "|VS: "  + line[20]

        if not (line[19] == "" or line[19] == " "):
            StatementLine.memo = StatementLine.memo + "|KS: "  + line[19]

        if not (line[21] == "" or line[21] == " "):
            StatementLine.memo = StatementLine.memo + "|SS: " + line[21]

        return StatementLine

    # Substitute decimal point "," with "."
    # Remove thousands separator
    def parse_float(self, value):
        value = value.replace(".", "")
        value = value.replace(",", ".")
        return super(UniCreditCZParser, self).parse_float(value)
