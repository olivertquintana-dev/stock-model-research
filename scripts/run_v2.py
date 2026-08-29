import os,json,pandas as pd,numpy as np
os.makedirs("outputs",exist_ok=True)
URL="https://raw.githubusercontent.com/fcester/Data_Stock/main/Actual_Stock.parquet"
df=pd.read_parquet(URL,columns=["Date","Ticker","Value"])
df["Date"]=pd.to_datetime(df["Date"]);df=df.sort_values(["Ticker","Date"])
g=df.groupby("Ticker",group_keys=False)
df["r63"]=g["Value"].pct_change(63)
latest=df.Date.max()
snap=df[df.Date==latest].dropna(subset=["r63"]).copy()
# V2 operational eligibility: avoid penny-priced names and retain only positive-price observations.
snap["eligible_price"]=snap["Value"]>=5
eligible=snap[snap.eligible_price].copy()
eligible["rs_percentile"]=eligible["r63"].rank(pct=True,method="average")
eligible=eligible.sort_values(["rs_percentile","Ticker"],ascending=[False,True]).reset_index(drop=True)
eligible["rank"]=np.arange(1,len(eligible)+1)
n=max(1,int(np.ceil(len(eligible)*0.10)))
eligible["selected_top_decile"]=eligible["rank"]<=n
# Diversified research basket: top 20 eligible names, equal-weight placeholder.
eligible["target_weight"]=0.0
eligible.loc[eligible.index<min(20,len(eligible)),"target_weight"]=1/min(20,len(eligible))
out=eligible[["rank","Ticker","Date","Value","r63","rs_percentile","eligible_price","selected_top_decile","target_weight"]]
out.to_csv("outputs/v2_current_ranking.csv",index=False)
sel=out[out.target_weight>0]
summary={"model":"V2 RS63 Operational Research Selector","as_of_date":str(latest.date()),"raw_universe_size":int(len(snap)),"eligible_universe_size":int(len(out)),"selected_top_decile_count":int(eligible.selected_top_decile.sum()),"portfolio_count":int(len(sel)),"eligibility_rule":"Price >= 5 at latest observation","selection_rule":"Rank eligible universe by 63-session return; retain top decile; publish top 20 equal-weight research basket","target_weighting":"Equal weight across top 20; research placeholder, not execution advice","top20":sel.assign(Date=lambda x:x.Date.astype(str)).to_dict(orient="records")}
open("outputs/v2_current_ranking.json","w").write(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))