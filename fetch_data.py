import yfinance as yf
import mysql.connector
import pandas as pd
import os

# =========================
# CLOUD MYSQL CONNECTION
# =========================

connection = mysql.connector.connect(
    host     = os.environ.get("MYSQL_HOST",     "zephyr.proxy.rlwy.net"),
    port     = int(os.environ.get("MYSQL_PORT", 18696)),
    user     = os.environ.get("MYSQL_USER",     "root"),
    password = os.environ.get("MYSQL_PASSWORD", "AOplgDCTnsCgkwOEiNrKaLtBhQqbzPxW"),
    database = os.environ.get("MYSQL_DATABASE", "railway")
)

cursor = connection.cursor()
print("✅ Connected to Cloud MySQL")

# =========================
# READ STOCKS FROM CSV
# =========================

stocks_df     = pd.read_csv("stocks.csv")
stock_symbols = (stocks_df["SYMBOL"].dropna().astype(str) + ".NS").tolist()

print(f"📈 Total Stocks: {len(stock_symbols)}")

success_count = 0
failed_count  = 0

for symbol in stock_symbols:
    try:
        print(f"Fetching {symbol}...")
        stock = yf.Ticker(symbol)
        data  = stock.history(period="1d")

        if data.empty:
            print(f"❌ No data for {symbol}")
            failed_count += 1
            continue

        data.reset_index(inplace=True)
        row = data.iloc[-1]

        trade_date  = str(row["Date"].date())
        open_price  = float(row["Open"])
        high_price  = float(row["High"])
        low_price   = float(row["Low"])
        close_price = float(row["Close"])
        volume      = int(row["Volume"])

        query = """
        INSERT IGNORE INTO historical_prices
        (stock_symbol, trade_date, open_price, high_price, low_price, close_price, volume)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (symbol, trade_date, open_price, high_price, low_price, close_price, volume))
        connection.commit()

        print(f"✅ {symbol} inserted!")
        success_count += 1

    except Exception as e:
        print(f"❌ Error {symbol}: {e}")
        failed_count += 1

cursor.close()
connection.close()

print(f"\n✅ Success: {success_count} | ❌ Failed: {failed_count}")
print("🚀 Done!")