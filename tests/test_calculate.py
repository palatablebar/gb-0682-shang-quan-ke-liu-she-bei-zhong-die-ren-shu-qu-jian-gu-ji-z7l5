import pytest
from app.workflow import run
from app.errors import DomainError
from app.modules.m5_calculate.rules import bounds,apply

def test_two_zone_union():assert bounds({'zones':{'A':100,'B':80},'pairs':{'A|B':30},'triple':None})[:2]==(150,150)
def test_two_unknown_overlap():assert bounds({'zones':{'A':100,'B':80},'pairs':{},'triple':None})[:2]==(100,180)
def test_three_way_feasible():assert bounds({'zones':{'A':120,'B':110,'C':90},'pairs':{'A|B':40,'A|C':30,'B|C':20},'triple':None})[:2]==(230,250)
def test_three_way_contradiction():
    # TRAP-19
    with pytest.raises(DomainError) as e:bounds({'zones':{'A':100,'B':100,'C':100},'pairs':{'A|B':80,'A|C':80,'B|C':0},'triple':None})
    assert e.value.code=='CONSTRAINT'
def test_real_first_interval(raw):
    r=run(raw,{})['calculations'][0];assert r['lower']==230 and r['upper']==250 and r['code']=='INTERVAL'
def test_real_interval_totals(raw):
    s=run(raw,{});assert s['business']['total']==sum(r['lower'] for r in s['calculations']) and s['business']['upper_total']>s['business']['total']
def test_real_bad_bucket_isolated(raw):
    s=run(raw,{},4);s['models'][0]['model']['pairs']={'A|B':110,'A|C':90,'B|C':0};r=apply(s);assert len(r['calculations'])==11 and any(q['code']=='CONSTRAINT' for q in r['quarantine'])
