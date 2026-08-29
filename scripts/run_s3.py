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
models={"RS_only":["RS"],"Momentum_only":["Momentum"],"RS_Momentum":["RS","Momentum"],"Full":["Trend","Momentum","RS","Extension"],"No_Trend":["Momentum","RS","Extension"]}
s["year"]=s.Date.dt.year
rows=[]
for name,fs in models.items():
 s["score"]=sum(s[f] for f in fs)/len(fs)
 for yr,x0 in s.groupby("year"):
  x=x0.dropna(subset=["f126"]).copy()
  if len(x)<50: continue
  x["bucket"]=x.groupby("month")["score"].transform(lambda z:pd.qcut(z.rank(method="first"),10,labels=False)+1)
  top=x[x.bucket==10].groupby("month").f126.mean();u=x.groupby("month").f126.mean();z=pd.concat([top.rename("top"),u.rename("u")],axis=1).dropna()
  ic=x.groupby("month").apply(lambda a:a.score.corr(a.f126,method="spearman"),include_groups=False).dropna()
  rows.append({"model":name,"test_year":int(yr),"months":len(z),"top_return":float(z.top.mean()),"excess":float((z.top-z.u).mean()),"mean_ic":float(ic.mean()),"median_ic":float(ic.median())})
out=pd.DataFrame(rows);out.to_csv("outputs/s3_walkforward_by_year.csv",index=False)
summary=out.groupby("model").agg(years=("test_year","count"),positive_years=("excess",lambda x:int((x>0).sum())),mean_excess=("excess","mean"),median_excess=("excess","median"),worst_year=("excess","min"),mean_ic=("mean_ic","mean")).reset_index().sort_values("mean_excess",ascending=False)
summary.to_csv("outputs/s3_walkforward_summary.csv",index=False)
report=summary.to_dict(orient="records");open("outputs/s3_report.json","w").write(json.dumps(report,indent=2));print(out.to_string(index=False));print(json.dumps(report,indent=2))