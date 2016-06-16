import csv
from datetime import datetime
import re

from ofxstatement import statement
from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement.statement import Statement


class UniCreditCZPlugin(Plugin):
    """UniCreditCZ plugin
    """


    def get_parser(self, filename):
        UniCreditCZPlugin.encoding = self.settings.get('charset', 'utf-8')
        f = open(filename, "r", encoding=UniCreditCZPlugin.encoding)
        parser = UniCreditCZParser(f)
        parser.statement.currency = self.settings.get('currency', 'CZK')
        parser.statement.bank_id = self.settings.get('bank', 'BACXCZPP')
        parser.statement.account_id = self.settings.get('account', '')
        parser.statement.account_type = self.settings.get('account_type', 'CHECKING')
        parser.statement.trntype = "OTHER"
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

    mappings = {"date_user": 3,
                "date": 4,
                "memo": 13,
                "payee": 9,
                "amount": 1,
                "check_no": 20,
                "refnum": 23, }

    date_format = "%Y-%m-%d"


    def split_records(self):
        return csv.reader(self.fin, delimiter=';', quotechar='"')


    def parse_record(self, line):
        if self.cur_record <= 3:
            return None

        sl = super(UniCreditCZParser, self).parse_record(line)
        sl.date_user = datetime.strptime(sl.date_user, self.date_format)

        sl.id = statement.generate_transaction_id(sl)

        if line[13].startswith("SRÁŽKOVÁ DAŇ"):
            sl.trntype = "DEBIT"
        if line[7].startswith("ÚROKY"):
            sl.trntype = "INT"
        if line[7].startswith("Poplatek za "):
            sl.trntype = "FEE"
        if line[7].startswith("VRÁCENÍ POPLATKU ZA "):
            sl.trntype = "FEE"

        # sl.payee is imported as "Description" in GnuCash
        # sl.memo is imported as "Notes" in GnuCash
        # When sl.payee is empty, GnuCash imports sl.memo to "Description" and keeps "Notes" empty
        sl.memo = sl.memo + line[14] + line[15] + line[16] + line[17] + line[18]
        sl.memo = sl.memo + "|ÚČ: "  + line[8]  + "/"      + line[5]
        sl.memo = sl.memo + "|VS: "  + line[20] + "|KS: "  + line[19] + "|SS: " + line[21]

        if sl.amount == 0:
            return None

        return sl


    def parse_float(self, value):
        value = re.sub(",", ".", value)
        value = re.sub("[ a-zA-Z]", "", value)
        return super(UniCreditCZParser, self).parse_float(value)
