import io,csv,json,hashlib

BOM='﻿'

def span(row):
    start,end=row.get('line_start',row.get('line')),row.get('line_end',row.get('line'))
    if start and end and start!=end:return f'{start}-{end}'
    return str(end or row.get('line',''))

def bundle(state):
    out=io.StringIO(newline='');writer=csv.writer(out)
    writer.writerow(['记录类型','批次','来源行(物理行)','业务ID','原因码','内容','来源原文'])
    rid=state.get('run_id','preview')
    writer.writerow(['运行清单',rid,'','','',json.dumps(state.get('manifest',{}),ensure_ascii=False,sort_keys=True),''])
    writer.writerow(['对账',rid,'','','',json.dumps(state.get('reconcile',{}),ensure_ascii=False,sort_keys=True),''])
    for row in state.get('calculations',[]):writer.writerow(['计算',rid,row.get('line',''),row.get('id',''),row.get('code',''),json.dumps(row,ensure_ascii=False,sort_keys=True),''])
    for row in state.get('quarantine',[]):
        writer.writerow(['隔离',rid,span(row),row.get('id',''),row['code'],
            json.dumps(row.get('raw',{}),ensure_ascii=False,sort_keys=True),row.get('source_text','')])
    return BOM+out.getvalue()

def checksum(state):
    return hashlib.sha256(bundle(state).encode('utf-8')).hexdigest()

def quarantine_rows(state):
    return [r for r in csv.reader(io.StringIO(bundle(state).lstrip(BOM))) if r and r[0]=='隔离']
