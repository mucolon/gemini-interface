# gemini-interface

A repo to execute Gemini Exchange trades at lower fees than their Web App.

## How to make this repo work for you

1. Create a `config.py` file this format
   ```python
   keys = {
      "real": {
         "pub_key": "account-xxxxxxxxxxxxxxxxxxxx",
         "priv_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      },
      "sandbox": {
         "pub_key": "account-xxxxxxxxxxxxxxxxxxxx",
         "priv_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      },
   }
   ```
   *Create a Sandbox Exchange Account for its respective API*
   *[https://exchange.sandbox.gemini.com/](https://exchange.sandbox.gemini.com/)*

2. Add missing pairs to trade on `cryptos.csv`
   * `Price_round`: The amount of significant figures after the decimal point for any given pair's price.
   * `Qty_round`: The amount of significant figures after the decimal point for any given pair's quantity.

3. Read `api.py` script. Most importantly read after `if __name__ == '__main__':` for a brief explanation how to execute orders.

4. Never share your API Keys or `config.py` as anyone with your keys can control your account. I would recommend making sure `config.py` is in your `.gitignore` file.

## Dependencies

Run this command to download all required python dependencies.

```python
python3 -m pip install pandas, math, sys, gemini_python
```
