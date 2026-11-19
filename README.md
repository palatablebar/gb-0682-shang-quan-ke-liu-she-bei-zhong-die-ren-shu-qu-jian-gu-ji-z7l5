# 商圈客流设备重叠与人数区间估计

面向商场经营数据分析员，处理采信、判定、核算、复核与归档。

## 启动

```bash
docker compose up --build -d
```

访问 http://localhost:18251 。初次启动自动运行脏样例，可切换 clean.csv 与 legacy.csv。顶部“运行批次”会重新计算，同源输入复用批次。

## 业务模块

- 设备采信：`/m1_ingest`、`/api/m1_ingest`
- 区域映射：`/m2_mapping`、`/api/m2_mapping`
- 观测分桶：`/m3_versions`、`/api/m3_versions`
- 重叠约束：`/m4_segments`、`/api/m4_segments`
- 人数估界：`/m5_calculate`、`/api/m5_calculate`
- 日汇对账：`/m6_reconcile`、`/api/m6_reconcile`
- 报告归档：`/m7_archive`、`/api/m7_archive`

## 核心规则

无法识别个人时只输出满足区域交集约束的人数上下界；矛盾观测隔离而非伪造精确人数。完整数值、边界和异常定义见 `docs/DATA-DICTIONARY.md`。

导入异常清单与对账计数以**逻辑记录**为正式单位：引号内换行折叠进同一条记录，含换行备注的坏记录横跨多物理行也只计一次；每条逻辑记录标注来源物理行起止区间与原文切片，物理行仅用于回溯，不参与计数。同一文件重跑命中同一幂等批次，不重复计入。

## 验证

```bash
docker compose exec -T app pytest -q
docker compose config --quiet
```

原始样例在 `sample_data/`。测试在 `tests/`。封存文件是单份CSV，含运行清单、计算证据、隔离原因与对账。复核需提交当前版本，陈旧复核返回409。

## 数据与限制

SQLite保存在records命名卷，普通重启与构建不会清除。确认可丢弃本项目数据后，运行 `docker compose down -v` 再启动可重置。单文件上限2MB；不接入外部业务系统；历史规则由本项目样例定义，不代表实际行业标准。
