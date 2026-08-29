import os,json,pandas as pd
os.makedirs("outputs",exist_ok=True)
files=["v1_current_ranking.json","v2_current_ranking.json","v3_backtest_summary.json","v4_risk_summary.json","v5_summary.json","v6_summary.json","v7_summary.json","v8_summary.json"]
status={"model":"V9 Final Research Gate","completed_stages":[],"decision":"CONDITIONAL PASS","capital_ready":False,"next_gate":"Independent point-in-time universe and liquidity validation"}
for f in files:
 try:
  with open("outputs/"+f) as h: json.load(h);status["completed_stages"].append(f)
 except FileNotFoundError: pass
open("outputs/v9_final_decision.json","w").write(json.dumps(status,indent=2));print(json.dumps(status,indent=2))