#!/usr/bin/env python3
"""Reproduce four secondary analyses offline and compare with frozen results.

Python >=3.10, standard library only. Does not call model APIs or retrieve data.
"""
from pathlib import Path
import csv, hashlib, json, math, platform, subprocess, sys

ROOT=Path(__file__).resolve().parent
LOG=ROOT/'validation/run-logs';LOG.mkdir(parents=True,exist_ok=True)
sources=json.loads((ROOT/'DATA_SOURCES.json').read_text())
for src in sources:
    expected=src.get('released_sha256',src.get('sha256'))
    actual=hashlib.sha256((ROOT/src['file']).read_bytes()).hexdigest()
    if actual!=expected:raise RuntimeError('Input hash mismatch: '+src['file'])

steps=['reanalysis/code/reanalyse.py','reanalysis/code/reanalyse_xstest.py','reanalysis/code/reanalyse_refusalbench.py','code/reanalyse_dualchem_aggregates.py','validation/independent_checks.py']
for script in steps:
    run=subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,text=True,capture_output=True)
    (LOG/(Path(script).stem+'.log')).write_text(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError(f'{script} failed; see validation/run-logs')

ignored=[]
def compare(a,b,path):
    if path.endswith('/python'):
        ignored.append({'field':path,'reason':'Recorded Python version varies by environment'});return
    if path.startswith('reanalysis/analysis/refusalbench_audit.json/bootstraps/') and path.endswith('/estimand'):
        assert '93 groups have five and one has four' in b
        ignored.append({'field':path,'reason':'Corrected repeat-count wording only'});return
    if isinstance(a,dict):
        assert a.keys()==b.keys(),path
        for k in a:compare(a[k],b[k],path+'/'+k)
    elif isinstance(a,list):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
    elif isinstance(a,(float,int)) and not isinstance(a,bool):
        assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-14),(path,a,b)
    else:assert a==b,(path,a,b)

comparisons=[]
for old in sorted((ROOT/'expected').rglob('*')):
    if not old.is_file():continue
    rel=old.relative_to(ROOT/'expected');new=ROOT/rel
    if old.suffix=='.json':compare(json.loads(old.read_text()),json.loads(new.read_text()),str(rel))
    elif old.suffix=='.csv':
        a=list(csv.DictReader(old.open()));b=list(csv.DictReader(new.open()));assert len(a)==len(b)
        for i,(x,y) in enumerate(zip(a,b)):
            for k in x:
                try:compare(float(x[k]),float(y[k]),str(rel)+f'/{i}/{k}')
                except ValueError:assert x[k]==y[k]
    else:assert old.read_bytes()==new.read_bytes()
    comparisons.append(str(rel))

pat=subprocess.run([sys.executable,str(ROOT/'patagent/server.py'),'smoke-test'],cwd=ROOT,text=True,capture_output=True)
(LOG/'patagent-smoke.log').write_text(pat.stdout+pat.stderr)
assert pat.returncode==0,'PatAgent smoke test failed'
status={'status':'passed','python':platform.python_version(),'analysis_files_compared':comparisons,'documented_metadata_differences':ignored,'input_hashes_verified':len(sources),'patagent_smoke_test':'passed','interpretation':'Computational reproduction and arithmetic/data-integrity checks only. Source labels, causal interpretations, and sampling assumptions are not independently validated.'}
(ROOT/'validation/reproduction-status.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2))
