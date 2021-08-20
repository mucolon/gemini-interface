import math


def deposit2recoup(days, apy, fee):
    """Desposit required to overcome fee costs with days and apy constraints.
    days [int|float]: Number of days for fee cost to be offset
    apy [int|float]: Investment APY as a percent, method will convert to decimal form
    fee [int|float]: Fee cost in USD
    """
    c1 = 365.25
    apy = apy / 100

    l1 = math.log(1 + apy) / c1
    l2 = math.exp(days * l1)
    amount = (fee * l2) / (l2 - 1)
    fee_percent = 100 * fee / amount

    print(f"\nDays: {days}")
    print(f"Deposit needed to offset costs from fees: {round(amount, 2)}")
    print(f"Fee cost: -{round(fee_percent, 2)}%")


def days2recoup(amount, apy, fee):
    """Days required to overcome fee costs with amount and apy constraints.
    amount [int|float]: Initial investment amount
    apy [int|float]: Investment APY as a percent, method will convert to decimal form
    fee [int|float]: Fee cost in USD
    """
    c1 = 365.25
    apy = apy / 100

    k1 = amount / (amount - fee)
    k2 = math.log(k1)
    k3 = math.log(1 + apy)
    days = c1 * k2 / k3
    fee_percent = 100 * fee / amount

    print(f"\nInitial Investment: {amount}")
    print(f"Days needed to offset costs from fees: {round(days, 2)}")
    print(f"Fee cost: -{round(fee_percent, 2)}%")


if __name__ == "__main__":
    day_offset = 7
    investment = 1e4
    apy = 12
    fee = 70e-2

    deposit2recoup(day_offset, apy, fee)
    days2recoup(investment, apy, fee)
    print()
