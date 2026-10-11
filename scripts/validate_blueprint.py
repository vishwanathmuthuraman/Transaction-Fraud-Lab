#!/usr/bin/env python3
"""Check blueprint consistency; this does not run application tests."""
from pathlib import Path
from datetime import datetime, timezone
import csv, json, re
from urllib.parse import unquote, urlparse
from jsonschema import Draft202012Validator, FormatChecker
ROOT=Path(__file__).resolve().parents[1]
def read_json(p): return json.loads((ROOT/p).read_text())
def rows(p):
    with (ROOT/p).open(newline='') as f: return list(csv.DictReader(f))
def ts(s): return datetime.fromisoformat(s.replace('Z','+00:00'))
checks=[]
def check(test,message):
    if not test: raise AssertionError(message)
    checks.append(message)
req=rows('planning/requirements.csv');tests=rows('planning/acceptance-tests.csv')
reqids={r['id'] for r in req}
check(len(reqids)==len(req),'Unique requirement IDs')
check(len({r['id'] for r in tests})==len(tests),'Unique acceptance IDs')
check(all(x['status']=='not_started' for x in tests),'Planned application tests remain honestly unstarted')
check(set(' '.join(t['requirement_ids'] for t in tests).split())==reqids,'Every requirement maps to an acceptance test')
check(not (ROOT/'planning/tasks.csv').exists(),'Internal task schedule is excluded from this public edition')
check(not (ROOT/'planning/estimate-summary.json').exists(),'Internal effort estimates are excluded from this public edition')
for name in ['payment','label','case','expected']:
    Draft202012Validator.check_schema(read_json(f'schemas/{name}.schema.json'))
case_validator=Draft202012Validator(read_json('schemas/case.schema.json'),format_checker=FormatChecker())
expected_validator=Draft202012Validator(read_json('schemas/expected.schema.json'),format_checker=FormatChecker())
idx=read_json('examples/index.json')['cases']
for entry in idx:
    obj=read_json('examples/'+entry['case']);exp=read_json('examples/'+entry['expected'])
    case_validator.validate(obj);expected_validator.validate(exp)
    check(obj['case_id']==exp['case_id']==entry['id'],f"{entry['id']} IDs and schemas match")
    check(set(exp['requirement_ids'])<=reqids,f"{entry['id']} references existing requirements")
    check(exp['measured_model_result'] is None,f"{entry['id']} has no fabricated model result")
    observations=obj['observations'];ids={x['payment_id'] for x in observations}
    check(obj['current_payment_id'] in ids,f"{entry['id']} current payment exists")
    check(all(x['payment_id'] in ids for x in obj['labels']),f"{entry['id']} labels reference real synthetic events")
    if exp['expected_status']=='valid_input':
        current=next(x for x in observations if x['payment_id']==obj['current_payment_id'])
        eligible={x['payment_id'] for x in observations if x['organization_id']==obj['organization_id'] and ts(x['occurred_at'])<ts(current['occurred_at']) and ts(x['available_at'])<=ts(obj['scoring_at'])}
        check(eligible==set(exp['eligible_history_ids']),f"{entry['id']} specified historical eligibility is internally consistent")
        labels={x['payment_id'] for x in obj['labels'] if x['status']=='resolved' and ts(x['available_at'])<=ts(obj['training_cutoff'])}
        check(labels==set(exp['eligible_training_label_ids']),f"{entry['id']} specified label eligibility is internally consistent")
    else:
        has_scope_error=any(x['organization_id']!=obj['organization_id'] for x in observations)
        has_currency_error=len({x['currency'] for x in observations})>1
        seen={};conflict=False
        for x in observations:
            key=(x['organization_id'],x['payment_id'])
            if key in seen and seen[key]!=x:conflict=True
            seen[key]=x
        check(has_scope_error or has_currency_error or conflict,f"{entry['id']} has a specified input-error cause")
# Verify arithmetic and chronology in authored oracle specifications, not application behavior.
eval_spec=read_json('examples/evaluation-boundaries.json')
eval_schema=read_json('schemas/evaluation-boundaries.schema.json')
Draft202012Validator.check_schema(eval_schema)
Draft202012Validator(eval_schema,format_checker=FormatChecker()).validate(eval_spec)
check(eval_spec['measured_model_result'] is None,'Evaluation boundary fixtures contain no model results')
stages=eval_spec['stage_knowledge_boundaries']
check({x['stage'] for x in stages}=={'training','model_selection','calibration','policy'},'All supervised decision stages have cutoff specifications')
first_test=ts(next(x for x in stages if x['stage']=='policy')['next_scoring_at'])
for stage in stages:
    cutoff=ts(stage['knowledge_cutoff'])
    eligible={x['id'] for x in stage['labels'] if x['status']=='resolved' and ts(x['available_at'])<=cutoff}
    check(eligible==set(stage['expected_eligible_ids']),stage['stage']+' label eligibility respects its own knowledge cutoff')
    check(cutoff<=ts(stage['artifact_frozen_at'])<ts(stage['next_scoring_at']),stage['stage']+' freeze precedes its next scoring period')
    check(ts(stage['artifact_frozen_at'])<first_test,stage['stage']+' artifact freezes before first final-test score')
gate=eval_spec['coverage_gate']
gate_pass=gate['resolved_count']/gate['total_count']>=gate['minimum_resolved_fraction'] and gate['positive_count']>=gate['minimum_positive_count'] and gate['negative_count']>=gate['minimum_negative_count']
check(not gate_pass and gate['expected_outcome']=='insufficient_label_coverage','Authored inadequate-label example fails stage coverage gates')
x=eval_spec['unknown_capacity_cost']; rr=x['rows'];expected=x['expected']
selected=[r for r in rr if r['selected']];resolved_selected=[r for r in selected if r['class'] is not None]
pos_selected=sum(r['class']=='fraudulent' for r in selected);pos_all=sum(r['class']=='fraudulent' for r in rr)
us=sum(r['class'] is None for r in selected);uu=sum(not r['selected'] and r['class'] is None for r in rr)
cost_known=x['review_cost_minor']*len(selected)+x['false_alert_cost_minor']*sum(r['class']=='legitimate' for r in selected)+x['missed_loss_fraction']*sum(r['amount_minor'] for r in rr if not r['selected'] and r['class']=='fraudulent')
cost_upper=cost_known+x['false_alert_cost_minor']*us+x['missed_loss_fraction']*sum(r['amount_minor'] for r in rr if not r['selected'] and r['class'] is None)
computed={'selected_count':len(selected),'selected_resolved_count':len(resolved_selected),'selected_unknown_count':us,'unselected_unknown_count':uu,'precision_resolved':pos_selected/len(resolved_selected),'precision_population_lower':pos_selected/len(selected),'precision_population_upper':(pos_selected+us)/len(selected),'recall_resolved':pos_selected/pos_all,'recall_population_lower':pos_selected/(pos_all+uu),'recall_population_upper':(pos_selected+us)/(pos_all+us),'cost_known_minor':cost_known,'cost_lower_minor':cost_known,'cost_upper_minor':cost_upper}
for key,value in computed.items():check(abs(value-expected[key])<1e-12,'Hand-calculated unknown-boundary specification matches '+key)
import math
bs=eval_spec['bootstrap_rerank'];be=bs['expected'];orig=bs['rows'];original_k=math.floor(bs['review_fraction']*len(orig))
check(original_k==be['original_k'],'Bootstrap fixture original daily K matches')
original_chosen=[r['id'] for r in sorted(orig,key=lambda r:(-r['candidate_score'],r['id']))[:original_k]]
check(original_chosen==be['original_candidate_selected'],'Bootstrap fixture original queue matches')
clones=[]
for clone_index,component in enumerate(bs['component_draws']):
    clones.extend(dict(r,clone_id=r['id']+'#'+str(clone_index),clone_index=clone_index) for r in orig if r['component_id']==component)
k=math.floor(bs['review_fraction']*len(clones));check(k==be['resampled_k'],'Bootstrap fixture recalculates K over coherent clones')
for model in ['candidate','baseline']:
    chosen=sorted(clones,key=lambda r:(-r[model+'_score'],r['id'],r['clone_index']))[:k]
    check([r['clone_id'] for r in chosen]==be['resampled_'+model+'_selected'],model+' fixture reranks cloned daily rows')
    tp=sum(r['class']=='fraudulent' for r in chosen);all_pos=sum(r['class']=='fraudulent' for r in clones)
    check(tp/len(chosen)==be[model+'_precision_resolved'],model+' cloned precision specification matches')
    check(tp/all_pos==be[model+'_recall_resolved'],model+' cloned recall specification matches')
reused=sum(r['id'] in original_chosen for r in clones)
check(reused==be['selection_count_if_original_flags_reused'] and reused!=k,'Fixture proves retaining original selected flags gives wrong capacity')

link_count=0
for md in ROOT.rglob('*.md'):
    for dest in re.findall(r'\]\(([^)]+)\)',md.read_text()):
        if dest.startswith(('http:','https:','mailto:','#')):continue
        target=(md.parent/unquote(dest.split('#')[0])).resolve()
        check(target.exists(),f"Local documentation link resolves: {md.relative_to(ROOT)} -> {dest}")
        link_count+=1
sources=read_json('research/source-register.json')['sources']
check(len({s['id'] for s in sources})==len(sources),'Unique source IDs')
check(all(urlparse(s['url']).scheme=='https' and s['claim_supported'] and s['design_inference'] for s in sources),'Source register has direct URLs, claims and separate inferences')
report={'status':'passed','checked_at':datetime.now(timezone.utc).isoformat(),'scope':'Documentation consistency only; no application or predictive benchmark executed','requirements':len(req),'edition':'curated_public_specification','internal_delivery_plan_included':False,'planned_acceptance_tests':len(tests),'synthetic_case_pairs':len(idx),'evaluation_boundary_specifications':7,'schemas':5,'sources':len(sources),'local_markdown_links_checked':link_count,'checks':len(checks),'application_implemented':False,'model_performance_measured':False,'git_initialized':(ROOT/'.git').exists()}
(ROOT/'docs/blueprint-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
