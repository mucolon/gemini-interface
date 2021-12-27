import math


def deposit2recoup(days, _yield, fee):
    """Desposit required to overcome fee costs with days and _yield constraints.
    days [int|float]: Number of days for fee cost to be offset
    _yield [int|float]: Investment yield as a percent, method will convert to decimal form
    fee [int|float]: Fee cost in USD
    """
    c1 = 365.25
    _yield = _yield / 100

    l1 = math.log(1 + _yield) / c1
    l2 = math.exp(days * l1) - 1
    amount = fee / l2
    fee_percent = 100 * fee / amount

    print(f"\nDays: {days}")
    print(f"Deposit needed to offset costs from fees: {round(amount, 2)}")
    print(f"Fee cost: -{round(fee_percent, 2)}%")


def days2recoup(amount, _yield, fee):
    """Days required to overcome fee costs with amount and _yield constraints.
    amount [int|float]: Initial investment amount
    _yield [int|float]: Investment yield as a percent, method will convert to decimal form
    fee [int|float]: Fee cost in USD
    """
    c1 = 365.25
    _yield = _yield / 100

    k1 = (amount + fee) / amount
    k2 = math.log(k1)
    k3 = math.log(1 + _yield)
    days = c1 * k2 / k3
    fee_percent = 100 * fee / amount

    print(f"\nInitial Investment: {amount}")
    print(f"Days needed to offset costs from fees: {round(days, 2)}")
    print(f"Fee cost: -{round(fee_percent, 2)}%")


if __name__ == "__main__":
    day_offset = 30
    investment = 0.13
    _yield = 20
    fee = 0.0025

    deposit2recoup(day_offset, _yield, fee)
    days2recoup(investment, _yield, fee)
    print()
