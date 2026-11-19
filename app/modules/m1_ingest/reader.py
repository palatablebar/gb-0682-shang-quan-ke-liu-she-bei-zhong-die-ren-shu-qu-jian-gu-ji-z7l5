import csv,io
from app.errors import DomainError
from app.config import REQUIRED
from app.modules.m1_ingest.decode import decode

BOM='﻿'

def source_text(lines,start,end):
    # 物理行切片按原始换行拼回，保留引号内换行的完整原文（去掉行尾 CR）
    return '\n'.join(line.rstrip('\r') for line in lines[start-1:end])

def logical_records(reader):
    # csv.reader 把引号内换行折叠进同一条逻辑记录；
    # 每次 next 前后记录物理行号，得到该逻辑记录覆盖的物理行起止区间
    while True:
        start=reader.line_num+1
        try:row=next(reader)
        except StopIteration:return
        yield start,reader.line_num,row

def read(raw):
    text,encoding=decode(raw)
    if not text:raise DomainError('EMPTY_FILE','文件为空')
    if not text.strip():raise DomainError('BLANK_FILE','文件仅含空行')
    physical_lines=text.split('\n')
    reader=csv.reader(io.StringIO(text,newline=''))
    try:header=[s.strip().lstrip(BOM) for s in next(reader)]
    except (StopIteration,csv.Error):raise DomainError('HEADER','无法读取表头')
    if len(set(header))!=len(header) or not set(REQUIRED)<=set(header):raise DomainError('HEADER','表头缺失或重复')
    out={'rows':[],'quarantine':[],'input_count':0,'blank_count':0,'header_count':0,'duplicate_count':0,
        'encoding':encoding,'logical_count':0,'physical_count':len(text.splitlines())}
    try:
        for start,line,row in logical_records(reader):
            out['input_count']+=1
            if not row or not any(s.strip() for s in row):out['blank_count']+=1;continue
            if row==header:out['header_count']+=1;continue
            if len(row)!=len(header):
                out['quarantine'].append({'line':line,'line_start':start,'line_end':line,'id':'','code':'WIDTH',
                    'raw':{h:(row[i] if i<len(row) else '') for i,h in enumerate(header)},
                    'source_text':source_text(physical_lines,start,line)});continue
            item=dict(zip(header,row))
            item['_line']=line;item['_line_start']=start;item['_line_end']=line
            item['_source_text']=source_text(physical_lines,start,line)
            item['_raw']=dict(item)
            out['rows'].append(item)
    except csv.Error as exc:raise DomainError('CSV',str(exc))
    if out['input_count']==0:raise DomainError('HEADER_ONLY','文件仅含表头')
    # 逻辑记录总数含表头；input_count 仅统计数据逻辑记录
    out['logical_count']=out['input_count']+1
    return out
