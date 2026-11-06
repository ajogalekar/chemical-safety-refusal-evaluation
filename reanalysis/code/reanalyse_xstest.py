from pathlib import Path
import csv,json,collections,random,statistics,math
P=Path(__file__).resolve().parents[1];D=P/'data';O=P/'analysis';rng=random.Random(20261030)
O.mkdir(parents=True,exist_ok=True)
models=['llama2orig','llama2new','mistralinstruct','mistralguard','gpt4'];data={m:list(csv.DictReader((D/f'xstest_v2_completions_{m}.csv').open())) for m in models}
summary=[]
for m,rows in data.items():
 assert len(rows)==450 and len({x['id'] for x in rows})==450
 assert {x['final_label'] for x in rows} <= {'1_full_compliance','2_full_refusal','3_partial_refusal'}
 for safe in [True,False]:
  r=[x for x in rows if (not x['type'].startswith('contrast_'))==safe];c=collections.Counter(x['final_label'] for x in r)
  summary.append(dict(model=m,subset='safe' if safe else 'unsafe',n=len(r),full_refusal=c['2_full_refusal']/len(r),partial_refusal=c['3_partial_refusal']/len(r),any_refusal=(c['2_full_refusal']+c['3_partial_refusal'])/len(r)))
print(json.dumps(summary,indent=2))
(O/'xstest_reproduced_rates.json').write_text(json.dumps(summary,indent=2))
def binom(b,c):
 n=b+c;k=min(b,c);return min(1,2*sum(math.comb(n,i) for i in range(k+1))/2**n)
res=[]
for a,b in [('llama2orig','llama2new'),('mistralinstruct','mistralguard')]:
 A={x['id']:x for x in data[a] if not x['type'].startswith('contrast_')};B={x['id']:x for x in data[b] if not x['type'].startswith('contrast_')}
 assert A.keys()==B.keys()
 assert all(A[k]['type']==B[k]['type'] for k in A)
 assert all(A[k].get('prompt_sha256')==B[k].get('prompt_sha256') for k in A)
 for full in [True,False]:
  f=lambda x: x['final_label']=='2_full_refusal' if full else x['final_label']!='1_full_compliance'
  groups=collections.defaultdict(list);n10=n01=0
  for k,x in A.items():
   y=B[k];fx=int(f(x));fy=int(f(y));groups[x['type']].append(fy-fx);n10+=int(fy==1 and fx==0);n01+=int(fy==0 and fx==1)
  deltas=[z for v in groups.values() for z in v];boots=sorted(sum(sum(rng.choices(v,k=len(v))) for v in groups.values())/len(deltas) for _ in range(10000))
  res.append(dict(before=a,after=b,outcome='full_refusal' if full else 'any_refusal',n=len(deltas),n10=n10,n01=n01,difference=statistics.mean(deltas),exact_mcnemar_p=binom(n10,n01),stratified_prompt_bootstrap95=[boots[249],boots[9749]]))
prev=0
for rank,i in enumerate(sorted(range(len(res)),key=lambda i:res[i]['exact_mcnemar_p'])):
 prev=max(prev,min(1,(len(res)-rank)*res[i]['exact_mcnemar_p']));res[i]['holm4_p']=prev
(O/'xstest_paired_contrasts.json').write_text(json.dumps({'results':res,'seed':20261030,'replicates':10000,'estimand':'Same-item system-prompt difference on sampled safe prompts. Percentile bootstrap resamples prompts within each of the ten fixed types, with same item resampled jointly across the two configurations. It does not quantify future model versions, new prompt types, or decoding variance. Exact tests assume exchangeable independent prompt pairs; related wording can reduce effective n.'},indent=2));print(json.dumps(res,indent=2))
agree={m:sum(x['annotation_1']==x['annotation_2'] for x in rows)/len(rows) for m,rows in data.items()};(O/'xstest_annotation_agreement.json').write_text(json.dumps(agree,indent=2));print(agree)
