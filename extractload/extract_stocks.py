import os
import yfinance as yf
import pandas as pd
from config.settings import Config

def extract_stock_data(tickers=None, start='2018-01-01', end=None, interval='1d'):
    Config.ensure_directories()

    if tickers is None:
        tickers = Config.TICKERS

    if end is None:
        end = pd.Timestamp.today().strftime('%Y-%m-%d')

    files = []
    errors = {}

    output_dir = os.path.join(Config.RAW_DATA_DIR, 'yahoo_finance')
    os.makedirs(output_dir, exist_ok=True)

    for t in tickers:
        try:
            print(f"Downloading {t} ({start} -> {end})...")
            df = yf.download(t, start=start, end=end, interval=interval, progress=False)

            if df is None or df.empty:
                print(f"No data for {t}")
                errors[t] = "no data"
                continue

            fname = f"stock_{t}_{start}_to_{end}.csv"
            path = os.path.join(output_dir, fname)

            df.to_csv(path)
            files.append(path)
            print(f"Saved raw payload to {path}")
        except Exception as e:
            print(f"Failed to download {t}: {e}")
            errors[t] = str(e)

    return {"files": files, "errors": errors}
