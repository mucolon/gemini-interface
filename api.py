#!./.venv/bin/python
import gemini
import pandas as pd
import math
import sys
import config


def floor(number, digits):
    factor = 10 ** digits
    return math.floor(number * factor) / factor


def ceil(number, digits):
    factor = 10 ** digits
    return math.ceil(number * factor) / factor


class API:
    def __init__(self, keys, sandbox=False):
        """Interface module that interacts with the Gemini API"""
        cryptos = pd.read_csv("cryptos.csv", index_col="Pairs").to_dict()
        _ = list(cryptos.keys())
        self.str_price_r = _[0]
        self.str_qty_r = _[1]
        self.pairs = list(cryptos[self.str_price_r].keys())
        self.cryptos = cryptos
        if sandbox:
            pub_key = keys["sandbox"]["pub_key"]
            priv_key = keys["sandbox"]["priv_key"]
        else:
            pub_key = keys["real"]["pub_key"]
            priv_key = keys["real"]["priv_key"]
        self.trader = gemini.PrivateClient(pub_key, priv_key, sandbox)

    def pair_price_rounding(self, pair):
        """Return pair price decimal rounding"""
        price_round = self.cryptos[self.str_price_r][pair]
        return price_round

    def pair_denomination(self, pair):
        """Return the denomination symbol of the pair"""
        if pair[-3:] == "USD":
            sign = "$"
        elif pair[-3:] == "BTC":
            sign = "₿"  # \u20BF
        elif pair[-3:] == "ETH":
            sign = "Ξ"  # \u039E
        return sign

    def separate_pair(self, pair):
        """Separate pair symbol into list with individual string symbols"""
        symbols = ["USD", "ETH", "BTC"]
        pair_symbols = []
        i = 0
        while len(pair_symbols) != 2:
            try:
                pair_symbols = pair.rsplit(symbols[i], 1)
            except IndexError:
                print("ERROR: Cannot split pair into symbols.")
                sys.exit(1)
            if len(pair_symbols) == 2:
                if pair_symbols[0] == "":
                    pair_symbols[0] = symbols[i]
                else:
                    pair_symbols[1] = symbols[i]
            else:
                i += 1
        return pair_symbols

    def balance(self, pair=None, symbol_return=None):
        """Display available symbol balances to trade.
        pair parameter prints only pair balances.
        symbol_return parameter returns the quantity of the symbol.
        """
        balances = self.trader.get_balance()
        symbols = [balances[i]["currency"] for i in range(len(balances))]
        qty = [float(balances[i]["available"]) for i in range(len(balances))]
        str_available = "".join(
            [i + "\t" + str(j) + "\n" for i, j in zip(symbols, qty)]
        )
        str_available = str_available[:-1]
        if symbol_return is not None:
            index = symbols.index(symbol_return)
            symbol_qty = qty[index]
            return symbol_qty
        else:
            if pair == None:
                print("\nAvailable Balances:")
                print(str_available)
            else:
                pair_symbols = self.separate_pair(pair)
                index_symbols = [symbols.index(i) for i in pair_symbols]
                pair_qty = [qty[i] for i in index_symbols]
                str_available = "".join(
                    [i + "\t" + str(j) + "\n" for i, j in zip(pair_symbols, pair_qty)]
                )
                str_available = str_available[:-1]
                print("\nAvailable Balances:")
                print(str_available)
                self.pair_symbols = pair_symbols
                self.pair_qty = pair_qty

    def breakeven(self, pair, amount, cost, fee=10):
        """Return the sell price to breakeven after trading fees"""
        fee = fee * 1e-4  # bps * 1e-4 = percent * 1e-2 = float
        ave_buy = cost / amount
        _breakeven = ave_buy / (1 - fee)
        _breakeven = ceil(_breakeven, self.pair_price_rounding(pair))
        sign = self.pair_denomination(pair)
        print(f"\n{pair} Breakeven Price: {sign} {_breakeven}")

    def trade(
        self, pair, side, size, limit_price=None, fee=35, option="maker-or-cancel"
    ):
        """Trade any supported pair at spot or at limit price.
        pair [str]: string trading pair. eg. 'ETHUSD'
        side ['buy', 'sell']: trade side
        size [int|float]: size of trade in pair denomination eg. $50 if buying or Ξ0.05 if selling
        limit_price [int|float|None]: limit price or None for spot price
        fee [int|float]: trading fee in bps. eg. 10bps = 0.10%. NOTE: API limit orders cost 10bps but API may require trade to account for normal 35bps fee. At the time of the trade you'll be charged 10bps and be left with 25bps difference in cash.
        option ['maker-or-cancel']: type of trade. NOTE: Leave this alone.
        """
        price_round = self.cryptos[self.str_price_r][pair]
        qty_round = self.cryptos[self.str_qty_r][pair]
        if limit_price == None:
            ask = self.trader.get_ticker(pair)["ask"]
            bid = self.trader.get_ticker(pair)["bid"]
            if side == "sell":
                cte = 1.0005  # 0.05% above ask
                price = ask
                if ask == None:  # sometimes ask isn't available
                    cte = 1.003  # 0.3% above bid
                    price = bid
            else:
                cte = 0.9995  # 0.05% below bid
                price = bid
                if bid == None:  # sometimes bid isn't available
                    cte = 0.997  # 0.3% below ask
                    price = ask
            try:
                price = round(float(price) * cte, price_round)
            except TypeError:
                print("\nERROR: Market lacks liquidity around spot price.")
        else:
            price = limit_price
        size = floor(size, qty_round)
        if side == "buy":
            cte = 1 - (fee / 1e4)
            qty = floor((size * cte) / price, qty_round)
        else:
            qty = floor(size, qty_round)
        trade = self.trader.new_order(pair, str(qty), str(price), side, [option])

        sign = self.pair_denomination(pair)
        pair_symbols = self.separate_pair(pair)
        num = pair_symbols[0]
        den = pair_symbols[1]

        try:
            if trade["result"] == "error":
                print("\n" + trade["reason"])
                print(trade["message"] + ". Try 35bps fee.")
                print(f"\n{fee = }")
        except KeyError:
            if trade["is_live"]:
                if side == "sell":
                    print(f"\n{size} {num} listed to sell at {sign}{price} for {den}")
                else:
                    print(f"\n{size} {den} listed to buy {num} at {sign}{price}")
            else:
                if trade["reason"] == "MakerOrCancelWouldTake":
                    if side == "sell":
                        print(
                            f"\nYour limit price: {limit_price} is lower than the current spot price. Please set a limit price higher than the current spot price."
                        )
                    else:
                        print(
                            f"\nYour limit price: {limit_price} is higher than the current spot price. Please set a limit price lower than the current spot price."
                        )


if __name__ == "__main__":
    # api = API(config.keys, sandbox=True)  # Sandbox mode
    api = API(config.keys)  # Real mode
    # maker: 10bps
    # taker: 35bps
    # fee = 35
    # fee = 10

    """ Examples
    api.trade("ETHUSD", "buy", 50, 1500)  # Buy $50 of ETH at $1500 price
    api.trade("ETHUSD", "buy", 50)        # Buy $50 of ETH at slightly below spot price
    api.trade("ETHUSD", "sell", 1)        # Sell Ξ1 at slightly above spot price for USD
    """

    api.balance()
    # api.trade("ETHUSD", "buy", 4.51)
    # api.trade("ETHUSD", "buy", 300, limit_price=2989.49)

    # api.trade("ETHBTC", "buy", api.balance(symbol_return="BTC"))

    # api.trade("YFIUSD", "buy", 196.62)
    # api.trade("YFIUSD", "buy", 200.01, limit_price=30500)

    # api.trade("USDCUSD", "buy", api.balance(symbol_return="USD"), limit_price=0.9985)
    # api.trade("USDCUSD", "sell", api.balance(symbol_return="USDC"), limit_price=1.0015)

    # api.trade("BATETH", "sell", api.balance(symbol_return="BAT"))
    # api.trade("BATUSD", "sell", api.balance(symbol_return="BAT"))
