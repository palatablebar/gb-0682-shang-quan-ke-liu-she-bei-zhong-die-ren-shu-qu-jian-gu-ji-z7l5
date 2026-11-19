TITLE='商圈客流设备重叠与人数区间估计'
SHORT='footfallbounds'
RULE_VERSION='2026.11.17-v1'
MODULES=[('m1_ingest', '设备采信'), ('m2_mapping', '区域映射'), ('m3_versions', '观测分桶'), ('m4_segments', '重叠约束'), ('m5_calculate', '人数估界'), ('m6_reconcile', '日汇对账'), ('m7_archive', '报告归档')]
REQUIRED=['id', 'bucket', 'version', 'kind', 'left', 'count', 'unit']
NUMERIC=['version', 'count']
DATES=[]
TIMES=['bucket']
