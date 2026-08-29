import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
df=pd.read_parquet("https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet",columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"]);g=df.groupby("Ticker",group_keys=False)
df["r63"]=g["Value"].pct_change(63);df["f126"]=g["Value"].shift(-126)/df["Value"]-1;df["month"]=df.Date.dt.to_period("M")
s=df.groupby(["Ticker","month"],as_index=False).tail(1).dropna(subset=["r63","f126"]).copy()
s=s[(s.Date>=pd.Timestamp("2023-01-01"))&(s.Date<pd.Timestamp("2027-01-01"))]
s["score"]=s.groupby("month")["r63"].transform(lambda x:x.rank(pct=True))
s["bucket"]=s.groupby("month")["score"].transform(lambda x:pd.qcut(x.rank(method="first"),10,labels=False)+1)
dec=s.groupby(["month","bucket"]).f126.mean().reset_index()
ds=dec.groupby("bucket").f126.agg(["mean","median","count"]).reset_index().rename(columns={"mean":"mean_return","median":"median_return","count":"months"})
ds.to_csv("outputs/s5_holdout_deciles.csv",index=False)
top=s[s.bucket==10].copy();ticker=top.groupby("Ticker").f126.agg(["mean","count","sum"]).sort_values("sum",ascending=False)
total=ticker["sum"].sum();top10_share=float(ticker.head(10)["sum"].sum()/total) if total else np.nan
monthly=top.groupby("month").f126.mean();base=float(monthly.mean());imp=[]
for t in ticker.index[:50]:
 z=top[top.Ticker!=t].groupby("month").f126.mean()
 imp.append({"ticker":t,"excess_removal":base-float(z.mean()),"count":int(ticker.loc[t,"count"])})
impact=pd.DataFrame(imp).sort_values("excess_removal",ascending=False);impact.to_csv("outputs/s5_ticker_impact.csv",index=False)
bins=pd.to_datetime(["2022-12-31","2023-12-31","2024-12-31","2025-12-31","2026-12-31"])
labels=["2023","2024","2025","2026"]
top["period"]=pd.cut(top.Date,bins=bins,labels=labels)
s["period"]=pd.cut(s.Date,bins=bins,labels=labels)
sub=top.groupby("period",observed=True).f126.agg(["mean","median","count"]).reset_index()
u=s.groupby("period",observed=True).f126.mean().rename("universe_mean").reset_index()
sub=sub.merge(u,on="period",how="left");sub["excess"]=sub["mean"]-sub["universe_mean"];sub.to_csv("outputs/s5_subperiods.csv",index=False)
report={"holdout":"2023-2026","decile_returns":ds.to_dict(orient="records"),"monotonicity_spearman":float(ds["bucket"].corr(ds["mean_return"],method="spearman")),"top_decile_monthly_mean":base,"unique_top_tickers":int(top.Ticker.nunique()),"top10_ticker_share_of_sum_returns":top10_share,"largest_single_ticker_removal_impact":impact.head(1).to_dict(orient="records"),"subperiods":sub.to_dict(orient="records")}
open("outputs/s5_report.json","w").write(json.dumps(report,indent=2,default=str));print(json.dumps(report,indent=2,default=str))