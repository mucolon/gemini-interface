import gemini
import pandas as pd
import config


class API:

    def __init__(self, keys, sandbox=False):
        cryptos = pd.read_csv("cryptos.csv", index_col="Symbol").to_dict()
        _ = list(cryptos.keys())
        self.str_price_r = _[0]
        self.str_qty_r = _[1]
        self.symbols = list(cryptos[self.str_price_r].keys())
        self.cryptos = cryptos
        self.sandbox = sandbox
        if sandbox:
            self.pub_key = keys["sandbox"]["pub_key"]
            self.priv_key = keys["sandbox"]["priv_key"]
        else:
            self.pub_key = keys["real"]["pub_key"]
            self.priv_key = keys["real"]["priv_key"]

    def buy(self, symbol, buy_size, limit_price=None):
        if symbol[-3:] == "USD":
            sign = "$"
        if symbol[-3:] == "BTC":
            sign = "\u20BF"
        if symbol[-3:] == "ETH":
            sign = "\u039E"
        price_round = self.cryptos[self.str_price_r][symbol]
        qty_round = self.cryptos[self.str_qty_r][symbol]
        trader = gemini.PrivateClient(
            self.pub_key, self.priv_key, sandbox=self.sandbox)
        if limit_price == None:
            ask = trader.get_ticker(symbol)['ask']
            bid = trader.get_ticker(symbol)['bid']
            trade = bid
            if bid == None:
                trade = ask
            try:
                price = round(float(trade)*.998, price_round)
            except TypeError:
                print("\nERROR: Market lacks liquidity around spot price")
        else:
            price = limit_price

        # most precise rounding + *.999 for fee inclusion
        quantity = round((buy_size*.999)/price, qty_round)

        # execute maker buy, round to _ decimal places for precision
        buy = trader.new_order(symbol, str(quantity),
                               str(price), "buy", ["maker-or-cancel"])
        try:
            if buy['result'] == 'error':
                print("\n" + buy['message'])
        except KeyError:
            if buy['is_live']:
                print(f'\n{sign}{buy_size} buy order posted for {sign}{price}')
            else:
                if buy['reason'] == 'MakerOrCancelWouldTake':
                    print(
                        f'\nYour limit price: {limit_price} is higher than the current spot price. Please set a limit price lower than the current spot price.')

    def ui_buy(self):
        symbol = self.ask_symbol()
        amount = self.ask_amount()
        limit = self.ask_limit()
        self.buy(symbol, amount, limit)

    def ask_symbol(self):
        str_symbols = "\n".join(self.symbols)
        while True:
            try:
                symbol = str(
                    input(f"\nEnter crypto symbol [Choose from below]\n{str_symbols}\t: ")).upper()
            except ValueError:
                print("\nERROR: Invalid Input")
                continue
            if symbol not in self.symbols:
                print("\nERROR: Symbol not supported, input from provided list")
                continue
            else:
                break
        self.symbol = symbol
        return symbol

    def ask_amount(self):
        while True:
            try:
                buy_size = float(
                    input(f"\nEnter buy amount in {self.symbol} denomination: "))
            except ValueError:
                print("\nERROR: Invalid Input")
                continue
            if buy_size < 0:
                print("\nERROR: Buy amount cannot be negative")
                continue
            elif buy_size == 0:
                print("\nERROR: Buy amount cannot be zero")
                continue
            else:
                break
        return buy_size

    def ask_limit(self):
        while True:
            try:
                limit_price = str(
                    input(f"\nEnter limit price in {self.symbol} denomination\nor Press [Enter] to place order slightly below spot: "))
            except ValueError:
                print("\nERROR: Invalid Input")
                continue
            if limit_price == "":
                limit_price = None
                break
            elif float(limit_price) < 0:
                print("\nERROR: Limit price cannot be negative")
                continue
            elif float(limit_price) == 0:
                print("\nERROR: Limit price cannot be zero")
                continue
            else:
                limit_price = float(limit_price)
                break
        return limit_price


if __name__ == '__main__':
    api = API(config.keys, sandbox=True)  # Sandbox mode
    # api = API(config.keys)  # Real mode
    # api.buy("ETHUSD", 50, 1500)  # Buy $50 of ETH at $1500 price
    # api.buy("ETHUSD", 50)  # Buy $50 of ETH at slightly below spot price
    api.ui_buy()  # Buy what you want by answering the given questions
