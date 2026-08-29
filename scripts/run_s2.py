import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
df=pd.read_parquet("https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet",columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"]);g=df.groupby("Ticker",group_keys=False)
for n in (21,63,126): df[f"r{n}"]=g["Value"].pct_change(n);df[f"f{n}"]=g["Value"].shift(-n)/df["Value"]-1
for n in (20,50,200): df[f"sma{n}"]=g["Value"].transform(lambda x:x.rolling(n,min_periods=n).mean())
df["sma50_lag20"]=g["sma50"].shift(20);df["sma50_slope"]=df["sma50"]/df["sma50_lag20"]-1;df["month"]=df.Date.dt.to_period("M")
s=df.groupby(["Ticker","month"],as_index=False).tail(1).dropna(subset=["r21","r63","r126","sma20","sma50","sma200","sma50_slope"]).copy()
for c in ["r21","r63","r126"]:s[c+"_p"]=s.groupby("month")[c].transform(lambda x:x.rank(pct=True))
s["Momentum"]=(s.r21_p+s.r63_p+s.r126_p)/3;s["RS"]=s.groupby("month")["r63"].transform(lambda x:x.rank(pct=True))
s["Trend"]=((s.Value>s.sma20).astype(float)+(s.Value>s.sma50).astype(float)+(s.Value>s.sma200).astype(float)+(s.sma50>s.sma200).astype(float)+(s.sma50_slope>0).astype(float))/5
s["ext_raw"]=((s.Value/s.sma20-1).clip(lower=0)+(s.Value/s.sma50-1).clip(lower=0))/2;s["Extension"]=1-s.groupby("month")["ext_raw"].transform(lambda x:x.rank(pct=True))
features=["Trend","Momentum","RS","Extension"]
models={"Full":features,"Trend_only":["Trend"],"Momentum_only":["Momentum"],"RS_only":["RS"],"Extension_only":["Extension"],"No_Trend":["Momentum","RS","Extension"],"No_Momentum":["Trend","RS","Extension"],"No_RS":["Trend","Momentum","Extension"],"No_Extension":["Trend","Momentum","RS"]}
rows=[];ics=[]
for name,fs in models.items():
    s["score"]=sum(s[f] for f in fs)/len(fs)
    for n in (21,63,126):
        x=s.dropna(subset=[f"f{n}"]).copy();u=x.groupby("month")[f"f{n}"].mean()
        x["bucket"]=x.groupby("month")["score"].transform(lambda z:pd.qcut(z.rank(method="first"),10,labels=False)+1)
        top=x[x.bucket==10].groupby("month")[f"f{n}"].mean().rename("top")
        z=pd.concat([top,u.rename("u")],axis=1).dropna()
        ic=x.groupby("month").apply(lambda a:a.score.corr(a[f"f{n}"],method="spearman"),include_groups=False).dropna()
        rows.append({"model":name,"horizon":n,"top_mean_return":float(z.top.mean()),"mean_excess":float((z.top-z.u).mean()),"months":int(len(z)),"mean_ic":float(ic.mean()),"median_ic":float(ic.median())})
out=pd.DataFrame(rows);out.to_csv("outputs/s2_ablation_summary.csv",index=False)
report=out[out.horizon==126].sort_values("mean_excess",ascending=False).to_dict(orient="records")
open("outputs/s2_report.json","w").write(json.dumps(report,indent=2));print(out.to_string(index=False));print(json.dumps(report,indent=2))