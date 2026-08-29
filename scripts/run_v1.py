import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
URL="https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet"
df=pd.read_parquet(URL,columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"])
g=df.groupby("Ticker",group_keys=False);df["r63"]=g["Value"].pct_change(63)
latest=df.Date.max()
snap=df[df.Date==latest].dropna(subset=["r63"]).copy()
# Require sufficiently recent observations and positive prices
snap=snap[snap.Value>0].copy()
snap["rs_percentile"]=snap.r63.rank(pct=True,method="average")
snap=snap.sort_values(["rs_percentile","Ticker"],ascending=[False,True]).reset_index(drop=True)
snap["rank"]=np.arange(1,len(snap)+1)
n=max(1,int(np.ceil(len(snap)*0.10)))
snap["selected_top_decile"]=snap["rank"]<=n
out=snap[["rank","Ticker","Date","Value","r63","rs_percentile","selected_top_decile"]]
out.to_csv("outputs/v1_current_ranking.csv",index=False)
selected=out[out.selected_top_decile]
summary={"model":"V1.0 RS63 Technical Selector","as_of_date":str(latest.date()),"universe_size":int(len(out)),"selected_count":int(len(selected)),"selection_rule":"Top 10% by 63-session return percentile; monthly research rebalance; target horizon 126 sessions","top20":selected.head(20).assign(Date=lambda x:x.Date.astype(str)).to_dict(orient="records")}
open("outputs/v1_current_ranking.json","w").write(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
