"""逻辑记录 vs 物理行口径裁决的专项测试。

裁决：导入异常清单与全部计数以逻辑记录为正式单位；物理行仅用于回溯
每条逻辑记录覆盖的来源区间（line_start-line_end）与原文切片。
"""
from app.workflow import load,run
from app.modules.m1_ingest.reader import read

HEADER='id,bucket,version,kind,left,right,count,unit,note\n'

def test_physical_vs_logical_counts(raw):
    r=read(raw)
    # 脏样例 93 个物理行，但只有 80 条逻辑记录（含表头），数据逻辑记录 79 条
    assert r['physical_count']==93
    assert r['logical_count']==80
    assert r['input_count']==79

def test_multiline_record_has_full_span_and_source(raw):
    r=read(raw)
    first=r['rows'][0]
    # 00001 的备注含换行，横跨物理行 2-3，仍是一条逻辑记录
    assert first['id']=='00001'
    assert (first['_line_start'],first['_line_end'],first['_line'])==(2,3,3)
    assert '\n' in first['note']
    assert first['_source_text'].startswith('00001,')
    assert len(first['_source_text'].splitlines())==2

def test_multiline_bad_record_counts_once():
    # 构造一条备注跨行、且数值缺失的坏记录：物理上占 3 行，逻辑上只算 1 条隔离
    bad=('00700,2026-11-16T09:00:00+08:00,1,zone,东门,,-,人,"第一行备注\n第二行备注\n第三行备注"\n')
    r=read((HEADER+bad).encode())
    assert r['physical_count']==4          # 表头1 + 坏记录横跨3 行
    assert r['input_count']==1
    s=run((HEADER+bad).encode(),{})
    assert s['reconcile']['balanced'] is True
    assert s['reconcile']['isolated']==1   # 不按物理行重复计数
    q=s['quarantine'][0]
    assert q['line_start']==2 and q['line_end']==4 and q['line']==4
    assert q['code']=='MISSING'
    assert q['source_text'].splitlines()==['00700,2026-11-16T09:00:00+08:00,1,zone,东门,,-,人,"第一行备注',
                                           '第二行备注',
                                           '第三行备注"']
    # raw 保留折叠后的完整备注原文，审计可检索到全部三行文字
    assert q['raw']['note']=='第一行备注\n第二行备注\n第三行备注'

def test_rejoined_broken_line_loses_no_record():
    # 同一坏文件：断行补回后每条逻辑记录都有归属，守恒必须为平
    s=run(load('dirty.csv'),{})
    rec=s['reconcile']
    assert rec['balanced'] is True
    assert rec['input']==rec['accepted']+rec['isolated']+rec['blank']+rec['headers']+rec['duplicates']
    # 隔离条目全部带完整区间与原文，不存在只有结束行的条目
    assert all('line_start' in q and 'line_end' in q and q['source_text'] for q in s['quarantine'])

def test_rerun_same_file_is_idempotent(tmp_path,monkeypatch):
    monkeypatch.setenv('DB_PATH',str(tmp_path/'id.db'))
    from app import store
    content=load('dirty.csv')
    a=run(content,{});b=run(content,{})
    assert a['run_id']==b['run_id']
    store.save(a['run_id'],a);store.save(b['run_id'],b)
    assert len(store.history())==1
    assert store.get(a['run_id'])['reconcile']['isolated']==4

def test_width_quarantine_carries_span_and_source():
    payload=(HEADER+'only,two\n').encode()
    r=read(payload)
    q=r['quarantine'][0]
    assert q['code']=='WIDTH' and (q['line_start'],q['line_end'])==(2,2)
    assert q['source_text']=='only,two'
    assert set(q['raw'])==set(read(load('dirty.csv'))['rows'][0].keys())-{'_line','_line_start','_line_end','_source_text','_raw'}
