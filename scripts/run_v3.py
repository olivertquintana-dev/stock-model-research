import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
URL="https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet"
df=pd.read_parquet(URL,columns=["Date","Ticker","Value"]);df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"])
g=df.groupby("Ticker",group_keys=False);df["r63"]=g["Value"].pct_change(63);df["f21"]=g["Value"].shift(-21)/df["Value"]-1
df["month"]=df.Date.dt.to_period("M")
s=df.groupby(["Ticker","month"],as_index=False).tail(1).copy()
s=s[(s.Date>=pd.Timestamp("2016-01-01"))&(s.Date<pd.Timestamp("2026-08-01"))].dropna(subset=["r63","f21"])
s=s[s.Value>=5].copy();s["rank"]=s.groupby("month")["r63"].rank(method="first",ascending=False)
s["selected"]=s["rank"]<=20
# monthly equal-weight portfolio, with simple one-way transaction cost applied to turnover proxy
port=s[s.selected].groupby("month").f21.mean().rename("gross").to_frame()
# universe benchmark
bench=s.groupby("month").f21.mean().rename("benchmark");port=port.join(bench)
sel=s[s.selected].groupby("month").Ticker.apply(lambda x:set(x))
turn=[];prev=None
for m,x in sel.items():
 turn.append(np.nan if prev is None else 1-len(x&prev)/20);prev=x
port["turnover"]=turn;cost_rate=0.001
port["net"]=port["gross"]-port["turnover"].fillna(0)*cost_rate
port["cum_gross"]=(1+port.gross).cumprod()-1;port["cum_net"]=(1+port.net).cumprod()-1;port["cum_benchmark"]=(1+port.benchmark).cumprod()-1
n=len(port);ann=lambda r:(1+r).prod()**(12/n)-1
vol=lambda r:r.std()*np.sqrt(12)
summary={"model":"V3 Top20 RS63 Portfolio Backtest","period_start":str(port.index.min()),"period_end":str(port.index.max()),"months":int(n),"gross_annualized_return":float(ann(port.gross)),"net_annualized_return":float(ann(port.net)),"benchmark_annualized_return":float(ann(port.benchmark)),"gross_annualized_volatility":float(vol(port.gross)),"net_annualized_volatility":float(vol(port.net)),"average_monthly_turnover":float(port.turnover.mean()),"transaction_cost_assumption_per_turnover":cost_rate,"net_cumulative_return":float(port.cum_net.iloc[-1]),"benchmark_cumulative_return":float(port.cum_benchmark.iloc[-1])}
port.reset_index().to_csv("outputs/v3_backtest_monthly.csv",index=False);open("outputs/v3_backtest_summary.json","w").write(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))