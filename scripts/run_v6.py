import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
df=pd.read_parquet("https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet",columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"]);g=df.groupby("Ticker",group_keys=False)
df["r63"]=g["Value"].pct_change(63);df["f21"]=g["Value"].shift(-21)/df["Value"]-1;df["month"]=df.Date.dt.to_period("M")
s=df.groupby(["Ticker","month"],as_index=False).tail(1);s=s[(s.Date>="2016-01-01")&(s.Date<"2026-08-01")].dropna(subset=["r63","f21"]);s=s[s.Value>=5];s["rank"]=s.groupby("month")["r63"].rank(method="first",ascending=False)
# Equal-weight benchmark and its trailing 6-month regime signal, shifted to avoid same-month lookahead.
b=s.groupby("month").f21.mean().rename("benchmark")
bdf=b.to_frame();bdf["regime"]=((1+b).rolling(6).apply(np.prod,raw=True)-1).shift(1)>0
p=s[s["rank"]<=30].groupby("month").f21.mean().rename("gross").to_frame().join(bdf)
sets=s[s["rank"]<=30].groupby("month").Ticker.apply(set);prev=None;turn=[]
for _,x in sets.items():turn.append(np.nan if prev is None else 1-len(x&prev)/30);prev=x
p["turnover"]=turn;p["base_net"]=p.gross-p.turnover.fillna(0)*.001
# Defensive overlay: risk-on = portfolio; risk-off = cash proxy 0.
p["overlay_net"]=np.where(p.regime.fillna(False),p.base_net,0.0)
def met(r):
 r=pd.Series(r).dropna();w=(1+r).cumprod();n=len(r);ann=w.iloc[-1]**(12/n)-1;vol=r.std()*np.sqrt(12);dd=(w/w.cummax()-1).min()
 return {"annualized_return":float(ann),"annualized_volatility":float(vol),"sharpe_zero_rf":float(ann/vol) if vol else None,"max_drawdown":float(dd),"negative_months":int((r<0).sum()),"months":int(n)}
rows=[{"strategy":"Top30 baseline",**met(p.base_net)},{"strategy":"Top30 regime overlay",**met(p.overlay_net)},{"strategy":"Benchmark",**met(p.benchmark)}]
pd.DataFrame(rows).to_csv("outputs/v6_regime_comparison.csv",index=False)
p.reset_index().to_csv("outputs/v6_monthly.csv",index=False)
report={"model":"V6 Regime Filter & Defensive Overlay","regime_rule":"Risk-on when prior 6-month equal-weight benchmark return > 0; otherwise 0% cash proxy","cost_assumption":"10 bps x Top30 constituent turnover","results":rows,"risk_on_months":int(p.regime.fillna(False).sum()),"risk_off_months":int((~p.regime.fillna(False)).sum())}
open("outputs/v6_summary.json","w").write(json.dumps(report,indent=2));print(json.dumps(report,indent=2))