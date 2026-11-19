from app.workflow import run
from app.modules.m3_versions.rules import apply

def test_real_hour_observations(raw):assert len(run(raw,{},3)['observations'])==72
def test_alias_canonical(raw):assert run(raw,{},3)['observations'][0]['left']=='A'
def test_zone_count_integral(raw):assert run(raw,{},3)['observations'][0]['count']==120
def test_same_instant():
    from app.modules.m2_mapping.coerce import instant
    # TRAP-11
    assert instant('2026-11-16T09:00:00+08:00')==instant('2026-11-16T01:00:00Z')
def test_fraction_people_isolated(raw):
    s=run(raw,{},2);s['rows'][0]['count']='1.5';a=apply(s);assert any(q['code']=='RANGE' for q in a['quarantine'])
def test_unknown_unit(raw):
    s=run(raw,{},2);s['rows'][0]['unit']='台';assert any(q['code']=='UNIT' for q in apply(s)['quarantine'])
def test_newer_observation_wins(raw):
    s=run(raw,{},2);a=dict(s['rows'][0],id='new',version='2',count='130');s['rows'].append(a);r=apply(s);assert r['observations'][0]['count']==130


def test_nonhour_observation_floors_after_timezone_normalization(raw):
    s=run(raw,{},2);s['rows'][0]['bucket']='2026-11-16T01:37:42+00:00';r=apply(s);assert r['observations'][0]['bucket']=='2026-11-16T01:00:00+00:00'
