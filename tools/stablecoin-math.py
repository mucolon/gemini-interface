import math


# variables
daiusd = 0.999  # .999 is the breakeven point
int_gusd = 7.5e-2  # decimal
int_dai = 8.5e-2  # decimal

# arithmetic
fee = 0.1e-2  # decimal
dai = (1 - fee) / daiusd
freq = 12
c_gusd = 1 + (int_gusd / freq)
c_dai = 1 + (int_dai / freq)
c = c_gusd / c_dai
time_m = math.log(dai) / math.log(c)
time_d = (math.log(dai) / math.log(c)) * (365.25 / 12)
print(f"\nusd = 1")
print(f"{dai = }")
print(f"{time_m = }\t[months]")
print(f"{time_d = }\t[days]\n")
