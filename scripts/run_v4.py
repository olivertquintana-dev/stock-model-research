import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
df=pd.read_parquet("https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet",columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"]);g=df.groupby("Ticker",group_keys=False)
df["r63"]=g["Value"].pct_change(63);df["f21"]=g["Value"].shift(-21)/df["Value"]-1;df["month"]=df.Date.dt.to_period("M")
s=df.groupby(["Ticker","month"],as_index=False).tail(1);s=s[(s.Date>="2016-01-01")&(s.Date<"2026-08-01")].dropna(subset=["r63","f21"]);s=s[s.Value>=5]
s["rank"]=s.groupby("month")["r63"].rank(method="first",ascending=False);s["selected"]=s["rank"]<=20
p=s[s.selected].groupby("month").f21.mean().rename("gross").to_frame();p["benchmark"]=s.groupby("month").f21.mean()
sets=s[s.selected].groupby("month").Ticker.apply(set);prev=None;turn=[]
for m,x in sets.items(): turn.append(np.nan if prev is None else 1-len(x&prev)/20);prev=x
p["turnover"]=turn
for c in [0.001,0.003,0.005]:p[f"net_{int(c*10000)}bps"]=p.gross-p.turnover.fillna(0)*c
def metrics(r):
 wealth=(1+r).cumprod();dd=wealth/wealth.cummax()-1;n=len(r);ann=(wealth.iloc[-1])**(12/n)-1;vol=r.std()*np.sqrt(12);sh=ann/vol if vol else np.nan;down=r[r<0].std()*np.sqrt(12);sort=ann/down if down else np.nan
 return {"annualized_return":float(ann),"annualized_volatility":float(vol),"sharpe_zero_rf":float(sh),"sortino_zero_rf":float(sort),"max_drawdown":float(dd.min()),"worst_month":float(r.min()),"best_month":float(r.max()),"negative_months":int((r<0).sum()),"months":int(n)}
rows=[]
for name in ["gross","net_10bps","net_30bps","net_50bps","benchmark"]:rows.append({"series":name,**metrics(p[name])})
pd.DataFrame(rows).to_csv("outputs/v4_risk_metrics.csv",index=False)
p["year"]=p.index.astype(str).str[:4]
annual=p.groupby("year")["net_10bps"].apply(lambda r:(1+r).prod()-1).rename("net_return").to_frame();annual["benchmark_return"]=p.groupby("year")["benchmark"].apply(lambda r:(1+r).prod()-1);annual.to_csv("outputs/v4_annual_returns.csv")
report={"model":"V4 Risk & Cost Analysis","average_monthly_turnover":float(p.turnover.mean()),"metrics":rows,"annual_returns":annual.reset_index().to_dict(orient="records")}
open("outputs/v4_risk_summary.json","w").write(json.dumps(report,indent=2));print(json.dumps(report,indent=2))