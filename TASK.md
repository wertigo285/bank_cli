Написать небольшой сервис на языке Python, имитирующий работу банка со счетами клиентов.
#### Требования к сервису:
* работа с сервисом должна осуществляться через Interactive CLI
* состояние счетов хранится только в рамках одной сессии
* у клиента может быть только один счет
* валюта у всех счетов одинаковая - USD
#### Поддерживаемые операции:
* **deposit** - операция пополнения счета на сумму, аргументы: **client, amount, description**
* **withdraw** - операция снятия со счета, аргументы: **client, amount, description**
* **show_bank_statement** - вывод на экран выписки со счета за период, аргументы:
**client, since, till**


Пример использования сервиса:
```
~$ ./bank.py
Service started!
> deposit --client="John Jones" --amount=100 --description="ATM Deposit"
Deposit operation was successful!
> withdraw --client="John Jones" --amount=100 --description="ATM Withdrawal"
Withdrawal operation was successful!
> show_bank_statement --client="John Jones" --since="2021-01-01 00:00:00" --till="2021-02-01 00:00:00"

|        Date       |    Description    |   Withdrawals  |    Deposits    |     Balance    |
|-------------------|-------------------|----------------|----------------|----------------|
|                   |  Previous balance |                |                |           $0.00|
|-------------------|-------------------|----------------|----------------|----------------|
|2021-01-02 12:30:00| ATM Deposit       |                |         $100.00|         $100.00|
|2021-01-03 12:30:00| ATM Withdrawal    |         $100.00|                |           $0.00|
|-------------------|-------------------|----------------|----------------|----------------|
|                   | Totals            |         $100.00|         $100.00|           $0.00|
> ...
```