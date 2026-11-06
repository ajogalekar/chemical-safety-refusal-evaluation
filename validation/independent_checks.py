"""Independent arithmetic/data-integrity checks; no new model calls or fabricated items.

Run from any directory with Python 3. Standard library only.
This validates calculations conditional on the released labels and stated sampling
assumptions; it cannot validate original labels or unobserved dependence.
"""
from pathlib import Path
import csv, json, math, statistics, collections

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'reanalysis/data'
ANALYSIS = ROOT / 'reanalysis/analysis'

def read_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))

def exact_p(b, c):
    # Integer binomial coefficients, independently of the ChemID log-gamma implementation.
    n = b + c
    return min(1., math.ldexp(float(2 * sum(math.comb(n, k) for k in range(min(b, c) + 1))), -n))

def holm(ps):
    # Direct definition: max of preceding multiplicity-weighted ordered p-values.
    order = sorted(range(len(ps)), key=ps.__getitem__)
    result = [0.] * len(ps)
    for rank, i in enumerate(order):
        result[i] = min(1., max((len(ps)-j)*ps[order[j]] for j in range(rank+1)))
    return result

def paired_summary(n, b, c):
    # Known counts of differences only; no n11/n00 or molecular identities invented.
    mean = (b-c)/n
    sum_centered_squares = b*(1-mean)**2+c*(-1-mean)**2+(n-b-c)*mean**2
    se = math.sqrt(sum_centered_squares/(n-1)/n)
    z = statistics.NormalDist().inv_cdf(.975)
    return 100*mean, [100*(mean-z*se), 100*(mean+z*se)], exact_p(b,c)

chem = read_csv(ANALYSIS/'chemid_paired_reanalysis.csv')
ps = []
for row in chem:
    d, ci, p = paired_summary(int(row['n']), int(row['n10']), int(row['n01']))
    assert math.isclose(d, float(row['difference_pp']), abs_tol=1e-10)
    assert math.isclose(ci[0], float(row['paired_normal95_low_pp']), abs_tol=1e-9)
    assert math.isclose(ci[1], float(row['paired_normal95_high_pp']), abs_tol=1e-9)
    assert math.isclose(p, float(row['exact_mcnemar_p']), rel_tol=1e-10)
    ps.append(p)
for row, p in zip(chem, holm(ps)):
    assert math.isclose(p, float(row['holm14_exact_p']), rel_tol=1e-10)

xstest = json.loads((ANALYSIS/'xstest_paired_contrasts.json').read_text())['results']
xs_checks = []
for result in xstest:
    before = read_csv(DATA/f"xstest_v2_completions_{result['before']}.csv")
    after = read_csv(DATA/f"xstest_v2_completions_{result['after']}.csv")
    valid = {'1_full_compliance','2_full_refusal','3_partial_refusal'}
    assert {r['final_label'] for r in before+after} <= valid
    A = {r['id']:r for r in before if not r['type'].startswith('contrast_')}
    B = {r['id']:r for r in after if not r['type'].startswith('contrast_')}
    assert A.keys() == B.keys() and len(A) == 250
    assert all(A[k]['type'] == B[k]['type'] for k in A)
    prompt_fields = [k for k in ['prompt','text','prompt_sha256'] if k in before[0]]
    assert all(A[k][f] == B[k][f] for k in A for f in prompt_fields)
    refused = {'2_full_refusal'} if result['outcome']=='full_refusal' else valid-{'1_full_compliance'}
    differences = [int(B[k]['final_label'] in refused)-int(A[k]['final_label'] in refused) for k in A]
    b, c = differences.count(1), differences.count(-1)
    assert b == result['n10'] and c == result['n01']
    assert math.isclose(statistics.mean(differences), result['difference'], abs_tol=1e-12)
    assert math.isclose(exact_p(b,c), result['exact_mcnemar_p'], rel_tol=1e-12)
    xs_checks.append({'before':result['before'],'after':result['after'],'outcome':result['outcome'],'pairs':len(A),'prompt_fields_checked':prompt_fields,'discordance':[b,c]})
for result, p in zip(xstest, holm([x['exact_mcnemar_p'] for x in xstest])):
    assert math.isclose(p, result['holm4_p'], rel_tol=1e-12)

rb = read_csv(DATA/'hf-adjudicated.csv')
rb_saved = json.loads((ANALYSIS/'refusalbench_audit.json').read_text())
exclusions = set(rb_saved['excluded_post_frozen_models'])
rb = [r for r in rb if r['model'] not in exclusions]
assert len(rb)==13389 and len({(r['model'],r['prompt_id'],r['trial_idx']) for r in rb})==len(rb)
cfg = {'table_matching_direct_plus_indirect':{'direct_refusal','indirect_refusal'},'stated_methods_direct_plus_nonresponsive':{'direct_refusal','non_responsive'},'direct_only':{'direct_refusal'}}
trial_counts = []
for result in rb_saved['bootstraps']:
    groups = collections.defaultdict(list)
    for r in rb:
        if r['tier']=='benign' and r['model'] in ['anthropic/claude-opus-4.6','anthropic/claude-opus-4.7']:
            groups[r['prompt_id'],r['model']].append(int(r['modal_compliance'] in cfg[result['convention']]))
    ids = sorted({k[0] for k in groups})
    assert len(ids)==47
    counts = sorted(set(map(len,groups.values())))
    assert counts == [4,5]
    incomplete = [(key,values) for key,values in groups.items() if len(values)!=5]
    assert len(incomplete)==1 and incomplete[0][0][1]=='anthropic/claude-opus-4.6'
    assert incomplete[0][1]==[0,0,0,0]
    differences = [statistics.mean(groups[p,'anthropic/claude-opus-4.7'])-statistics.mean(groups[p,'anthropic/claude-opus-4.6']) for p in ids]
    assert math.isclose(statistics.mean(differences),result['delta'],abs_tol=1e-12)
    observed = statistics.mean(differences)
    # Exhaust the missing binary outcome's two possibilities; not observed data.
    sensitivity = [100*(observed-1/(5*len(ids))),100*observed]
    trial_counts.append({'convention':result['convention'],'prompts':len(ids),'trials_per_prompt_model':counts,'difference_pp':100*observed,'one_missing_trial_sensitivity_pp':sensitivity,'reporting_correction':'One prompt/model group has four available repeats; 93 have five. Say up to five or available repeats.'})

dual = json.loads((ROOT/'results/dualchem_aggregate_sensitivity.json').read_text())
human = dual['human_question_paired']
d,ci,p = paired_summary(600,160,64)
assert math.isclose(p,human['exact_two_sided_mcnemar_p'],rel_tol=1e-12)
assert math.isclose(ci[0],human['paired_normal95_pp'][0],abs_tol=1e-9)
web = dual['web_search_denominator']
assert math.isclose(web['all_initiated_accuracy_percent_approx'],54.6*(1-175/600),abs_tol=1e-12)
assert math.isclose(web['difference_all_initiated_minus_no_tool_pp_approx'],54.6*(1-175/600)-52.3,abs_tol=1e-12)

output = {'status':'passed','chemid_comparisons':len(chem),'chemid_max_holm_p':max(holm(ps)),'xstest':xs_checks,'refusalbench':trial_counts,'dualchem_arithmetic':'matched','statistical_boundaries':['Tests and intervals depend on the stated independent/exchangeable item assumptions.','No original response labels independently validated.','ChemID family dependence and DualChem participant dependence remain unresolvable from examined inputs.','Bootstrap reruns reproduce the saved seed and results; they do not establish that curated prompts form a probability sample.','No inference of significance for the DualChem +2.3-point tool comparison.']}
(OUT/'independent-check-results.json').write_text(json.dumps(output,indent=2))
print(json.dumps(output,indent=2))
