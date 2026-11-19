from decimal import Decimal

# 计数口径：所有计数均以逻辑记录（CSV 引号内换行折叠后的一条记录）为单位；
# 物理行只用于在隔离清单中回溯每条逻辑记录覆盖的来源行区间。
def balance(state):
    accepted=len(state['rows']);isolated=len(state['quarantine'])
    accounted=accepted+isolated+state['blank_count']+state['header_count']+state['duplicate_count']
    return {'input':state['input_count'],'accepted':accepted,'isolated':isolated,
        'blank':state['blank_count'],'headers':state['header_count'],'duplicates':state['duplicate_count'],
        'accounted':accounted,'balanced':accounted==state['input_count'],
        'unit':'logical_record','logical_count':state.get('logical_count',state['input_count']+1),
        'physical_count':state.get('physical_count',0),
        'business':state.get('business',{})}
