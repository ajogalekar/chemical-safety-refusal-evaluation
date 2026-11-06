"""Published aggregate sensitivity only; no reconstructed item-level outcomes."""
import json, math
from pathlib import Path
root=Path(__file__).resolve().parents[1]
(root/'results').mkdir(parents=True,exist_ok=True)
n,b,c=600,160,64
p=min(1,2*sum(math.comb(b+c,k) for k in range(min(b,c)+1))/2**(b+c))
d=(b-c)/n
se=math.sqrt(((b+c)-n*d*d)/(n-1)/n)
result={
 'source':'DualChem official PDF, retrieved 2026-10-31; sections 5.1, 6.1 and Table 4 footnote',
 'human_question_paired':{'n_questions':n,'discordant_assisted_only':b,'discordant_control_only':c,'difference_pp':100*d,'exact_two_sided_mcnemar_p':p,'paired_normal95_pp':[100*(d-1.95996398454*se),100*(d+1.95996398454*se)],'limitation':'Question-only inference; participant assignment not randomized. Repeated participant dependence and selection cannot be addressed from these aggregates. Not a causal human-uplift estimate.'},
 'web_search_denominator':{'initiated':600,'no_final_answer':175,'completed':425,'published_completed_accuracy_percent':54.6,'published_no_tool_all_item_accuracy_percent':52.3,'all_initiated_accuracy_percent_approx':54.6*425/600,'difference_all_initiated_minus_no_tool_pp_approx':54.6*425/600-52.3,'rounding_interval_all_initiated_percent':[54.55*425/600,54.65*425/600],'interpretation':'Arithmetic from rounded published percent. Failure counted as not successfully answered. No raw correct count inferred; no CI or paired test for the tool contrast. Changes estimand, not correction of a hidden arithmetic error.'}}
(root/'results/dualchem_aggregate_sensitivity.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
