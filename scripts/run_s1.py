import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
url="https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet"
df=pd.read_parquet(url,columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]); df=df.sort_values(["Ticker","Date"])
g=df.groupby("Ticker",group_keys=False)
df["r21"]=g["Value"].pct_change(21); df["r63"]=g["Value"].pct_change(63); df["r126"]=g["Value"].pct_change(126)
df["sma20"]=g["Value"].transform(lambda s:s.rolling(20,min_periods=20).mean())
df["sma50"]=g["Value"].transform(lambda s:s.rolling(50,min_periods=50).mean())
df["sma200"]=g["Value"].transform(lambda s:s.rolling(200,min_periods=200).mean())
df["sma50_slope"]=df.groupby("Ticker")["sma50"].diff(20)/df["sma50"].shift(20)
df["f20"]=g["Value"].shift(-20)/df["Value"]-1
df["f60"]=g["Value"].shift(-60)/df["Value"]-1
df["f126"]=g["Value"].shift(-126)/df["Value"]-1
# monthly snapshots: last available trading date per ticker-month
df["month"]=df["Date"].dt.to_period("M")
snap=df.groupby(["Ticker","month"],as_index=False).tail(1).copy()
req=["r21","r63","r126","sma20","sma50","sma200","sma50_slope"]
snap=snap.dropna(subset=req)
# cross-sectional components per month
def pct(s): return s.rank(pct=True)
for c in ["r21","r63","r126"]: snap[c+"_p"]=snap.groupby("month")[c].transform(pct)
snap["mom"]=(snap["r21_p"]+snap["r63_p"]+snap["r126_p"])/3
snap["rs"]=(snap["r63"]-snap.groupby("month")["r63"].transform("median"))
snap["rs_p"]=snap.groupby("month")["rs"].transform(pct)
trend_raw=((snap.Value>snap.sma20).astype(float)+(snap.Value>snap.sma50).astype(float)+(snap.Value>snap.sma200).astype(float)+(snap.sma50>snap.sma200).astype(float)+(snap.sma50_slope>0).astype(float))/5
snap["trend"]=trend_raw
ext=((snap.Value/snap.sma20-1).clip(lower=0)+(snap.Value/snap.sma50-1).clip(lower=0))/2
snap["extension"]=1-snap.groupby("month")["ext"].transform(pct)
snap["score"]=25*snap.trend+30*snap.mom+25*snap.rs_p+20*snap.extension
snap["bucket"]=snap.groupby("month")["score"].transform(lambda s:pd.qcut(s.rank(method="first"),10,labels=False,duplicates="drop")+1)
rows=[]
for h,col in [(20,"f20"),(60,"f60"),(126,"f126")]:
 x=snap.dropna(subset=[col])
 u=x.groupby("month")[col].mean().rename("universe")
 b=x.groupby(["month","bucket"])[col].agg(["mean","median","count"]).reset_index().merge(u,on="month")
 b["horizon"]=h;b["excess_vs_universe"]=b["mean"]-b["universe"];rows.append(b)
out=pd.concat(rows,ignore_index=True)
summary=out.groupby(["horizon","bucket"]).agg(mean_return=("mean","mean"),median_return=("median","mean"),avg_excess=("excess_vs_universe","mean"),observations=("count","sum")).reset_index()
ic=[]
for h,col in [(20,"f20"),(60,"f60"),(126,"f126")]:
 z=snap.dropna(subset=[col]).groupby("month").apply(lambda x:x.score.corr(x[col],method="spearman"),include_groups=False).dropna()
 ic.append({"horizon":h,"mean_monthly_spearman_ic":float(z.mean()),"median_monthly_spearman_ic":float(z.median()),"months":int(z.size)})
summary.to_csv("outputs/s1_bucket_summary.csv",index=False)
pd.DataFrame(ic).to_csv("outputs/s1_information_coefficient.csv",index=False)
top=summary[summary.bucket==10].set_index("horizon")
report={"label":"HISTORICAL AVAILABLE-UNIVERSE RESEARCH","rebalance":"monthly","score_weights":{"trend":25,"momentum":30,"relative_strength":25,"extension":20},"top_decile":top.to_dict(orient="index"),"ic":ic}
with open("outputs/s1_report.json","w") as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))