"""V10-A: normalize independent point-in-time data into a canonical schema."""
import os,json,pandas as pd
os.makedirs("outputs",exist_ok=True); os.makedirs("data",exist_ok=True)
src=os.environ.get("PIT_SOURCE","data/raw_point_in_time.parquet")
out="data/point_in_time_universe.parquet"
aliases={"date":"Date","ticker":"Ticker","symbol":"Ticker","price":"Value","close":"Value","adjusted_close":"Value","universe_date":"UniverseDate","membership_date":"UniverseDate","dollar_volume":"Liquidity","volume":"Liquidity"}
status={"model":"V10-A PIT Data Adapter","source":src,"canonical_output":out,"status":"BLOCKED_NO_SOURCE"}
if os.path.exists(src):
 try:
  d=pd.read_parquet(src)
  rename={c:aliases[c.lower()] for c in d.columns if c.lower() in aliases};d=d.rename(columns=rename)
  req=["Date","Ticker","Value","UniverseDate","Liquidity"];missing=[c for c in req if c not in d.columns]
  if missing: status.update(status="BLOCKED_SCHEMA",missing_columns=missing,available_columns=list(d.columns))
  else:
   d=d[req].copy();d["Date"]=pd.to_datetime(d["Date"]);d["UniverseDate"]=pd.to_datetime(d["UniverseDate"])
   d=d.dropna(subset=req).sort_values(["Date","Ticker"]).drop_duplicates(["Date","Ticker"],keep="last")
   d.to_parquet(out,index=False)
   status.update(status="READY",rows=int(len(d)),date_start=str(d.Date.min().date()),date_end=str(d.Date.max().date()),tickers=int(d.Ticker.nunique()))
 except Exception as e: status.update(status="ERROR",error=str(e))
open("outputs/v10a_adapter_status.json","w").write(json.dumps(status,indent=2));print(json.dumps(status,indent=2))