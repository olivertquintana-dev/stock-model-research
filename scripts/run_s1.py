import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
df=pd.read_parquet("https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet",columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"])
g=df.groupby("Ticker",group_keys=False)
for n in (21,63,126):
    df[f"r{n}"]=g["Value"].pct_change(n)
    df[f"f{n}"]=g["Value"].shift(-n)/df["Value"]-1
for n in (20,50,200): df[f"sma{n}"]=g["Value"].transform(lambda x:x.rolling(n,min_periods=n).mean())
df["sma50_lag20"]=g["sma50"].shift(20)
df["sma50_slope"]=df["sma50"]/df["sma50_lag20"]-1
df["month"]=df["Date"].dt.to_period("M")
s=df.groupby(["Ticker","month"],as_index=False).tail(1).dropna(subset=["r21","r63","r126","sma20","sma50","sma200","sma50_slope"]).copy()
pct=lambda x:x.rank(pct=True)
for c in ["r21","r63","r126"]: s[c+"_p"]=s.groupby("month")[c].transform(pct)
s["mom"]=(s["r21_p"]+s["r63_p"]+s["r126_p"])/3
s["rs_p"]=s.groupby("month")["r63"].transform(pct)
s["trend"]=((s.Value>s.sma20).astype(float)+(s.Value>s.sma50).astype(float)+(s.Value>s.sma200).astype(float)+(s.sma50>s.sma200).astype(float)+(s.sma50_slope>0).astype(float))/5
s["ext_raw"]=((s.Value/s.sma20-1).clip(lower=0)+(s.Value/s.sma50-1).clip(lower=0))/2
s["extension"]=1-s.groupby("month")["ext_raw"].transform(pct)
s["score"]=25*s.trend+30*s.mom+25*s.rs_p+20*s.extension
s["bucket"]=s.groupby("month")["score"].transform(lambda x:pd.qcut(x.rank(method="first"),10,labels=False)+1)
res=[];ics=[]
for n in (21,63,126):
    x=s.dropna(subset=[f"f{n}"]).copy();u=x.groupby("month")[f"f{n}"].mean()
    z=x.groupby(["month","bucket"])[f"f{n}"].agg(["mean","median","count"]).reset_index().merge(u.rename("universe"),on="month")
    z["horizon"]=n;z["excess"]=z["mean"]-z["universe"];res.append(z)
    ic=x.groupby("month").apply(lambda a:a.score.corr(a[f"f{n}"],method="spearman"),include_groups=False).dropna()
    ics.append({"horizon":n,"mean_ic":float(ic.mean()),"median_ic":float(ic.median()),"months":int(len(ic))})
o=pd.concat(res);summary=o.groupby(["horizon","bucket"]).agg(mean_return=("mean","mean"),median_return=("median","mean"),mean_excess=("excess","mean"),observations=("count","sum")).reset_index()
summary.to_csv("outputs/s1_bucket_summary.csv",index=False);pd.DataFrame(ics).to_csv("outputs/s1_information_coefficient.csv",index=False)
top=summary[summary.bucket==10]
report={"label":"HISTORICAL AVAILABLE-UNIVERSE RESEARCH","rebalance":"monthly","top_decile":top.to_dict(orient="records"),"information_coefficient":ics}
open("outputs/s1_report.json","w").write(json.dumps(report,indent=2));print(json.dumps(report,indent=2))