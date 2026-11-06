"""Dependency-free reanalysis of PUBLISHED SUFFICIENT COUNTS, not recovered raw items.
Run python3 code/reanalyse.py. No model calls, invented paired outcomes, or APIs.
"""
import csv,json,math,platform
from pathlib import Path
P=Path(__file__).resolve().parents[1];OUT=P/'analysis';OUT.mkdir(exist_ok=True)
# Transcribed from ChemIDBench 2610.30903v1 Appendix B.3 Table 14.
source=json.loads((P/'data/chemid_table14_transcription.json').read_text())
rows=source['rows']; assert source['n']==896
def binom_two(b,c):
 n=b+c;m=min(b,c)
 logs=[math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)-n*math.log(2) for k in range(m+1)]
 a=max(logs)
 return min(1.,2*math.exp(a)*sum(math.exp(x-a) for x in logs))
res=[]
for model,b,c,d,e in rows:
 for task,x,y in [('Indication: name minus SMILES',b,c),('Benzene: SMILES minus name',d,e)]:
  n=896;delta=(x-y)/n;var=((x+y)-n*delta**2)/(n-1);se=math.sqrt(var/n)
  stat=(abs(x-y)-1)**2/(x+y)
  res.append(dict(model=model,comparison=task,n=n,n10=x,n01=y,difference_pp=100*delta,paired_normal95_low_pp=100*(delta-1.95996398454*se),paired_normal95_high_pp=100*(delta+1.95996398454*se),mcnemar_cc_chisq=stat,mcnemar_cc_p=math.erfc(math.sqrt(stat/2)),exact_mcnemar_p=binom_two(x,y)))
order=sorted(range(len(res)),key=lambda i:res[i]['exact_mcnemar_p']);prev=0
for k,i in enumerate(order):
 prev=max(prev,min(1,(len(res)-k)*res[i]['exact_mcnemar_p']));res[i]['holm14_exact_p']=prev
with (OUT/'chemid_paired_reanalysis.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(res[0]));w.writeheader();w.writerows(res)
# Algebraic audit of normalized bisector geometry; deterministic identities only.
geom=[dict(cosine=c,common_norm=math.sqrt((1+c)/2),residual_norm=math.sqrt((1-c)/2)) for c in [.699,.794]]
# Precision calculation is design-based, NOT an observed onepot confidence interval.
precision=[dict(independent_pairs=n,approx95_halfwidth_at_p05=1.95996398454*math.sqrt(.25/n)) for n in [95,385,60,120]]
(OUT/'algebra_and_precision.json').write_text(json.dumps({'geometry':geom,'planning_precision_only':precision,'python':platform.python_version(),'assumptions':'ChemID normal intervals and tests assume independent exchangeable molecules, conditional on chosen models and scorer. No analog/scaffold correction possible from these counts. No n11/n00 or item identities fabricated.'},indent=2))
print(json.dumps(res,indent=2));print(json.dumps(geom,indent=2))
