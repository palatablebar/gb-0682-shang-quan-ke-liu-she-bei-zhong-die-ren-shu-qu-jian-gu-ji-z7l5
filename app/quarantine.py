"""隔离条目统一构造器。

正式计量单位是逻辑记录（CSV 引号内换行折叠后的一条记录），物理行号仅用于
回溯原文。每条隔离记录都携带：
- line / line_start / line_end：结束物理行（兼容旧字段）与起止物理行
- id：业务 ID
- code：原因码
- raw：解析后的字段原值（含换行备注的完整内容）
- source_text：起止物理行在来源文件中的原文切片，审计可直接核对
"""

def entry(row, code):
    return {
        'line': row['_line'],
        'line_start': row['_line_start'],
        'line_end': row['_line_end'],
        'id': row.get('id', ''),
        'code': code,
        'raw': row['_raw'],
        'source_text': row.get('_source_text', ''),
    }
