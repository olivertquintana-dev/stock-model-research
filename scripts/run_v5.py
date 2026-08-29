import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
df=pd.read_parquet("https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet",columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"]);g=df.groupby("Ticker",group_keys=False)
df["r63"]=g["Value"].pct_change(63);df["f21"]=g["Value"].shift(-21)/df["Value"]-1;df["month"]=df.Date.dt.to_period("M")
s=df.groupby(["Ticker","month"],as_index=False).tail(1);s=s[(s.Date>="2016-01-01")&(s.Date<"2026-08-01")].dropna(subset=["r63","f21"]);s=s[s.Value>=5]
s["rank"]=s.groupby("month")["r63"].rank(method="first",ascending=False)
bench=s.groupby("month").f21.mean()
def calc(n):
 p=s[s["rank"]<=n].groupby("month").f21.mean().rename("gross").to_frame().join(bench.rename("benchmark"))
 sets=s[s["rank"]<=n].groupby("month").Ticker.apply(set);prev=None;turn=[]
 for _,x in sets.items():turn.append(np.nan if prev is None else 1-len(x&prev)/n);prev=x
 p["turnover"]=turn;p["net"]=p.gross-p.turnover.fillna(0)*.001
 w=(1+p.net).cumprod();dd=w/w.cummax()-1;m=len(p);ann=w.iloc[-1]**(12/m)-1;vol=p.net.std()*np.sqrt(12);sh=ann/vol
 return {"portfolio_size":n,"annualized_return":float(ann),"annualized_volatility":float(vol),"sharpe_zero_rf":float(sh),"max_drawdown":float(dd.min()),"average_monthly_turnover":float(p.turnover.mean()),"negative_months":int((p.net<0).sum()),"months":int(m)}
rows=[calc(n) for n in [10,20,30,50,100]]
# benchmark metrics
w=(1+bench).cumprod();m=len(bench);bann=w.iloc[-1]**(12/m)-1;bvol=bench.std()*np.sqrt(12);bdd=(w/w.cummax()-1).min()
summary={"model":"V5 Portfolio Construction Comparison","cost_assumption":"10 bps x constituent turnover","portfolios":rows,"benchmark":{"annualized_return":float(bann),"annualized_volatility":float(bvol),"sharpe_zero_rf":float(bann/bvol),"max_drawdown":float(bdd)}}
pd.DataFrame(rows).to_csv("outputs/v5_portfolio_comparison.csv",index=False);open("outputs/v5_summary.json","w").write(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))