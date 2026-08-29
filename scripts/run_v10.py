import os,json,pandas as pd
os.makedirs("outputs",exist_ok=True)
REQUIRED=["Date","Ticker","Value","UniverseDate","Liquidity"]
path=os.environ.get("POINT_IN_TIME_DATA","data/point_in_time_universe.parquet")
status={"model":"V10 Independent Validation Gate","data_path":path,"required_columns":REQUIRED,"status":"BLOCKED_MISSING_INDEPENDENT_DATA","capital_ready":False,"message":"Provide an independently sourced point-in-time universe with liquidity data before V10 can run."}
if os.path.exists(path):
 d=pd.read_parquet(path)
 missing=[c for c in REQUIRED if c not in d.columns]
 if missing: status.update({"status":"BLOCKED_SCHEMA","missing_columns":missing})
 else: status.update({"status":"READY_FOR_VALIDATION","rows":int(len(d))})
open("outputs/v10_validation_gate.json","w").write(json.dumps(status,indent=2));print(json.dumps(status,indent=2))