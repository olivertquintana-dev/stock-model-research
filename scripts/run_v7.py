import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
df=pd.read_parquet("https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet",columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"]);g=df.groupby("Ticker",group_keys=False)
df["r63"]=g["Value"].pct_change(63);df["f21"]=g["Value"].shift(-21)/df["Value"]-1;df["month"]=df.Date.dt.to_period("M")
s=df.groupby(["Ticker","month"],as_index=False).tail(1).dropna(subset=["r63","f21"]);s=s[s.Value>=5];s["rank"]=s.groupby("month")["r63"].rank(method="first",ascending=False)
periods={"train_2016_2019":("2016-01-01","2020-01-01"),"test_2020_2022":("2020-01-01","2023-01-01"),"holdout_2023_2026":("2023-01-01","2026-08-01")}
def met(d,n):
 p=d[d["rank"]<=n].groupby("month").f21.mean().rename("gross").to_frame()
 sets=d[d["rank"]<=n].groupby("month").Ticker.apply(set);prev=None;turn=[]
 for _,x in sets.items():turn.append(np.nan if prev is None else 1-len(x&prev)/n);prev=x
 p["net"]=p.gross-np.array([0 if pd.isna(x) else x for x in turn])*.001
 r=p.net;w=(1+r).cumprod();m=len(r);ann=w.iloc[-1]**(12/m)-1;vol=r.std()*np.sqrt(12);dd=(w/w.cummax()-1).min()
 return {"annualized_return":float(ann),"annualized_volatility":float(vol),"sharpe_zero_rf":float(ann/vol) if vol else None,"max_drawdown":float(dd),"months":int(m)}
rows=[]
for name,(a,b) in periods.items():
 d=s[(s.Date>=a)&(s.Date<b)]
 for n in [20,30,50,100]: rows.append({"period":name,"portfolio_size":n,**met(d,n)})
pd.DataFrame(rows).to_csv("outputs/v7_walkforward.csv",index=False)
report={"model":"V7 Walk-Forward Robustness","periods":periods,"cost_assumption":"10 bps x constituent turnover","results":rows}
open("outputs/v7_summary.json","w").write(json.dumps(report,indent=2));print(json.dumps(report,indent=2))