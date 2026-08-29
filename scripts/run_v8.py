import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
df=pd.read_parquet("https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet",columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"]);df["month"]=df.Date.dt.to_period("M")
m=df.groupby("month").agg(observations=("Ticker","size"),tickers=("Ticker","nunique"),median_price=("Value","median"),positive_prices=("Value",lambda x:int((x>0).sum()))).reset_index()
coverage=df.groupby("Ticker").Date.agg(["min","max","count"]).reset_index()
latest=df.Date.max();earliest=df.Date.min()
cohort={"total_tickers":int(coverage.Ticker.nunique()),"tickers_present_at_latest":int(df[df.Date==latest].Ticker.nunique()),"tickers_with_data_before_2017":int((coverage["min"]<pd.Timestamp("2017-01-01")).sum()),"tickers_starting_after_2020":int((coverage["min"]>=pd.Timestamp("2020-01-01")).sum()),"date_start":str(earliest.date()),"date_end":str(latest.date())}
m.to_csv("outputs/v8_universe_coverage.csv",index=False);coverage.to_csv("outputs/v8_ticker_coverage.csv",index=False)
report={"model":"V8 Universe & Bias Audit","cohort":cohort,"monthly_ticker_min":int(m.tickers.min()),"monthly_ticker_max":int(m.tickers.max()),"monthly_ticker_median":float(m.tickers.median()),"limitation":"This audit measures coverage and cohort changes but cannot eliminate survivorship bias because the source universe is not independently point-in-time reconstructed."}
open("outputs/v8_summary.json","w").write(json.dumps(report,indent=2));print(json.dumps(report,indent=2))