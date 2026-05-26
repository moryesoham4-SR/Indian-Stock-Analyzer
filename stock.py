import yfinance as yf
import pandas as pd
import mysql.connector

# =========================
# MYSQL CONNECTION
# =========================

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Soham@",
    database="stock_market_db"
)

cursor = connection.cursor()

print("✅ Connected to MySQL Database")

# =========================
# READ CSV FILE
# =========================

stocks = pd.read_csv("stocks.csv")

# Convert SYMBOL column to Yahoo Finance format
stock_symbols = stocks["SYMBOL"].astype(str) + ".NS"

print(f"📈 Total Stocks Found: {len(stock_symbols)}")

# =========================
# FETCH & STORE STOCK DATA
# =========================

success_count = 0
failed_count = 0

for symbol in stock_symbols:

    try:

        print(f"\n📊 Fetching data for {symbol}...")

        stock = yf.Ticker(symbol)

        # Get latest market data
        data = stock.history(period="1d")

        # Skip if no data found
        if data.empty:
            print(f"❌ No data found for {symbol}")
            failed_count += 1
            continue

        # Reset index
        data.reset_index(inplace=True)

        # Get latest row
        row = data.iloc[-1]

        # Extract values
        trade_date = row["Date"].date()

        open_price = float(row["Open"])
        high_price = float(row["High"])
        low_price = float(row["Low"])
        close_price = float(row["Close"])
        volume = int(row["Volume"])

        # =========================
        # INSERT INTO MYSQL
        # =========================

        query = """
        INSERT INTO historical_prices
        (
            stock_symbol,
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            symbol,
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume
        )

        cursor.execute(query, values)

        connection.commit()

        print(f"✅ {symbol} inserted successfully!")

        success_count += 1

    except Exception as e:

        print(f"❌ Error in {symbol}: {e}")

        failed_count += 1

# =========================
# CLOSE CONNECTION
# =========================

cursor.close()
connection.close()

# =========================
# FINAL SUMMARY
# =========================

print("\n==============================")
print("📊 STOCK FETCH SUMMARY")
print("==============================")

print(f"✅ Successful Stocks: {success_count}")
print(f"❌ Failed Stocks: {failed_count}")

print("\n🚀 All stock processing completed!")