import pytest
from app.errors import DomainError
from app.workflow import run
from app.modules.m4_segments.rules import model

def test_real_model_count(raw):assert len(run(raw,{},4)['models'])==12
def test_real_zone_map(raw):assert run(raw,{},4)['models'][0]['model']['zones']=={'A':120,'B':110,'C':90}
def test_real_pair_map(raw):assert run(raw,{},4)['models'][0]['model']['pairs']['A|B']==40
def test_pair_exceeds_zone():
    with pytest.raises(DomainError):model([{'kind':'zone','left':'A','count':10},{'kind':'zone','left':'B','count':20},{'kind':'pair','left':'A','right':'B','count':11}])
def test_self_pair_rejected():
    with pytest.raises(DomainError):model([{'kind':'zone','left':'A','count':10},{'kind':'pair','left':'A','right':'A','count':5}])
def test_missing_third_pairs_rejected():
    with pytest.raises(DomainError):model([{'kind':'zone','left':x,'count':10} for x in 'ABC'])
def test_two_zones_missing_pair_supported():
    m=model([{'kind':'zone','left':'A','count':10},{'kind':'zone','left':'B','count':20}]);assert m['pairs']=={}


def test_triple_without_three_regions_rejected():
    with pytest.raises(DomainError) as e:model([{'kind':'zone','left':'A','count':10},{'kind':'triple','left':'ABC','right':'','count':1}])
    assert e.value.code=='CONSTRAINT'

def test_triple_label_must_match_regions():
    observations=[{'kind':'zone','left':x,'count':10} for x in 'ABC']+[{'kind':'pair','left':a,'right':b,'count':2} for a,b in [('A','B'),('A','C'),('B','C')]]+[{'kind':'triple','left':'ABD','right':'','count':1}]
    with pytest.raises(DomainError) as e:model(observations)
    assert e.value.code=='CONSTRAINT'


def test_unknown_region_rejected():
    with pytest.raises(DomainError):model([{'kind':'zone','left':'D','count':10}])
