import argparse
import cmd
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from shlex import split


def to_decimal(value):
    # Откинем разряды после центов и не будем их учитывать
    return Decimal(f'{float(value):.2f}')


class ArgumentParserNoExit(argparse.ArgumentParser):
    '''
    Парсер аргументов
    '''

    def error(self, message):
        raise Exception(message)


@dataclass
class Record:
    '''
    Запись на счете
    '''
    amount: float
    operation: str
    description: str
    date: datetime = datetime.now()
    balance: float = 0

    def __post_init__(self):
        # Не учитываем микросекунды для корректного отображения границ
        self.date = datetime.now().replace(microsecond=0)

    def get_prev_balance(self):
        if self.operation == 'withdraw':
            return self.balance + self.amount
        return self.balance - self.amount


class Database:
    '''
    Данные
    '''
    TABLE_HEADERS = ['Date', 'Description', 'Withdrawals',
                     'Deposits', 'Balance']
    HEADRER = '|{:<19}|{:<19}|{:<16}|{:<16}|{:<16}|'.format(*TABLE_HEADERS)
    LINE = '|{:-<19}|{:-<19}|{:-<16}|{:-<16}|{:-<16}|'.format(*(['-']*5))
    LINE_FORMAT = '|{:<19}|{:<19}|{:>16}|{:>16}|{:>16}|'

    def __init__(self):
        self._client_accounts = defaultdict(list)

    def deposite(self, client, amount, description):
        account = self._get_client_account(client)
        balance = account[-1].balance if account else 0
        balance += amount
        record = Record(amount=amount, operation='deposite',
                        description=description, balance=balance)
        account.append(record)
        print('Deposit operation was successful!\n')

    def withdraw(self, client, amount, description):
        account = self._get_client_account(client)
        balance = account[-1].balance if account else 0
        if amount > balance:
            print('Withdraw operation was failed!')
            print(f'Balance: {balance}\n')
            return
        balance -= amount
        record = Record(amount=amount, operation='withdraw',
                        description=description, balance=balance)
        account.append(record)
        print('Withdraw operation was successful!\n')

    def show_bank_statement(self, client, since, till):
        account = self._get_client_account(client)
        period_recs = [rec for rec in account if since <= rec.date <= till]
        balance_start, balance_end = 0, 0
        if period_recs:
            balance_start = period_recs[0].get_prev_balance()
            balance_end = period_recs[-1].balance
        table = self._generate_table(period_recs, balance_start, balance_end)
        self._print_table(table)

    def _get_client_account(self, client):
        return self._client_accounts[client]

    def _generate_table(self, recs, balance_start, balance_end):
        table = []
        table.append(['', 'Previouse balance', '', '', f'${balance_start}'])
        total_windr, total_dep = 0, 0
        for rec in recs:
            date = rec.date.strftime('%Y-%m-%d %H:%M:%S')
            t_line = [date, rec.description, '', '', f'${rec.balance}']
            if rec.operation == 'deposite':
                t_line[3] = f'${rec.amount}'
                total_dep += rec.amount
            elif rec.operation == 'withdraw':
                t_line[2] = f'${rec.amount}'
                total_windr += rec.amount
            table.append(t_line)
        table.append(['', 'Totals', f'${total_windr}',
                      f'${total_dep}', f'${balance_end}'])
        return table

    def _print_table(self, table):
        print()
        print(self.HEADRER)
        for line in table:
            if not line[0]:
                print(self.LINE)
            print(self.LINE_FORMAT.format(*line))
            if not line[0] and not line[1] == "Totals":
                print(self.LINE)
        print()


class BankShell(cmd.Cmd):
    '''
    Интерфейс командной строки
    '''
    intro = 'Service started.\nEnter "exit" for quit.'
    prompt = ''
    METHODS = {
        'deposite': {
            '--client': str,
            '--amount': to_decimal,
            '--description': str,
        },
        'withdraw': {
            '--client': str,
            '--amount': to_decimal,
            '--description': str,
        },
        'show_bank_statement': {
            '--client': str,
            '--since': datetime.fromisoformat,
            '--till': datetime.fromisoformat,
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build_parsers()
        self._database = Database()

    def emptyline(self):
        pass

    def do_deposit(self, args):
        args = self._parse(args, 'deposite')
        if args:
            self._database.deposite(**args)

    def do_withdraw(self, args):
        args = self._parse(args, 'withdraw')
        if args:
            self._database.withdraw(**args)

    def do_show_bank_statement(self, args):
        args = self._parse(args, 'show_bank_statement')
        if args:
            self._database.show_bank_statement(**args)

    def do_exit(self, args):
        return True

    def _parse(self, args, parser_name):
        try:
            parser = self._parsers[parser_name]
            args = parser.parse_args(split(args))
        except Exception as e:
            print('FAIL:', e)
            return None
        return args.__dict__

    def _build_parsers(self):
        parsers = {}
        for method, params in self.METHODS.items():
            parser = ArgumentParserNoExit(prog=method)
            for p_name, p_type in params.items():
                parser.add_argument(p_name, type=p_type, required=True)
            parsers[method] = parser
        self._parsers = parsers


if __name__ == '__main__':
    try:
        BankShell().cmdloop()
    except KeyboardInterrupt:
        print('Service terminated from keyboard.')
