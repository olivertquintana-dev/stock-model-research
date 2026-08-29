import os, json, pandas as pd, numpy as np
os.makedirs("outputs", exist_ok=True)
url="https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet"
df=pd.read_parquet(url)
df.columns=[str(c).strip() for c in df.columns]
required=["Date","Ticker","Value"]
missing=[c for c in required if c not in df.columns]
if missing: raise ValueError(f"Missing columns: {missing}; got {df.columns.tolist()}")
df["Date"]=pd.to_datetime(df["Date"], errors="coerce")
df["Ticker"]=df["Ticker"].astype("string")
df["Value"]=pd.to_numeric(df["Value"], errors="coerce")
rows=len(df); tickers=df["Ticker"].nunique(); dup=int(df.duplicated(["Date","Ticker"]).sum())
nulls={c:int(df[c].isna().sum()) for c in required}
invalid=int((df["Value"]<=0).fillna(False).sum())
clean=df.dropna(subset=required).sort_values(["Ticker","Date"])
coverage=clean.groupby("Ticker").agg(first_date=("Date","min"),last_date=("Date","max"),sessions=("Date","size")).reset_index()
coverage["ge_252"]=coverage.sessions>=252
monthly=clean.assign(month=clean.Date.dt.to_period("M").astype(str)).groupby("month").Ticker.nunique().reset_index(name="active_tickers")
report={"rows":int(rows),"unique_tickers":int(tickers),"date_min":str(clean.Date.min().date()),"date_max":str(clean.Date.max().date()),"duplicate_date_ticker":dup,"nulls":nulls,"nonpositive_prices":invalid,"tickers_ge_252":int(coverage.ge_252.sum()),"pct_tickers_ge_252":float(coverage.ge_252.mean()*100),"gate":"PASS" if dup==0 and invalid==0 and coverage.ge_252.sum()>=20 else "FAIL","label":"HISTORICAL AVAILABLE-UNIVERSE RESEARCH"}
with open("outputs/data_quality_report.json","w") as f: json.dump(report,f,indent=2)
coverage.to_csv("outputs/ticker_coverage.csv",index=False)
monthly.to_csv("outputs/universe_by_month.csv",index=False)
with open("outputs/data_quality_report.md","w") as f:
 f.write("# DQ-0 Data Quality Report\n\n")
 for k,v in report.items(): f.write(f"- **{k}**: {v}\n")
print(json.dumps(report,indent=2))