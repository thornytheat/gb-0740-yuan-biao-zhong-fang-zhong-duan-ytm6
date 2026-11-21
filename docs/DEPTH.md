# 深度登记 编码切换准入终端

- 规模：中型
- 核心规则：先登记来源与证据并隔离坏行，再按来源判定准入状态，发布、回查、补数同读一份准入，演练已交付结果回退到原区域。

## 功能模块

| 模块 | 使用者动作 | 入口 | 核心文件 | 测试 |
|---|---|---|---|---|
| M1 来源登记 | 采集快照并逐源行隔离坏行 | `GET /api/intake/{id}` | `app/modules/m1_intake/service.py` | `tests/test_intake.py` |
| M2 映射证据 | 核对键映射齐全与对照留存 | `GET /api/mapping/{id}` | `app/modules/m2_mapping/service.py` | `tests/test_mapping.py` |
| M3 准入判定 | 按来源判定三态并圈未切换范围 | `GET /api/admission/{id}` | `app/modules/m3_admission/service.py` | `tests/test_admission.py` |
| M4 三务口径 | 发布、回查、补数同读一准入 | `GET /api/operations/{id}` | `app/modules/m4_operations/service.py` | `tests/test_operations.py` |
| M5 回退演练 | 校验锚点并演练回退原区域 | `GET /api/rollback/{id}` | `app/modules/m5_rollback/service.py` | `tests/test_rollback.py` |
| M6 覆盖勾稽 | 守恒核对来源、映射、对照、交付 | `GET /api/reconcile/{id}` | `app/modules/m6_reconcile/service.py` | `tests/test_reconcile.py` |
| M7 准入签发 | 幂等签发并下载准入文档 | `GET /api/issue/{id}` | `app/modules/m7_issue/service.py` | `tests/test_issue.py` |

## 准入判定

按来源依次判定，命中即落态：

1. 不可放行：映射证据不全（`MAPPING_GAP`，含未映射、未核、冲突、多旧键共用一新键）、旧键对照缺失（`COMPARE_LOST`，含未登记、丢失、无校验锚、保留期早于上线日）、新键交付缺回退锚点（`ANCHOR_BROKEN`）。
2. 旧键对照：证据齐备但消费者未全升级（`CONSUMERS_PENDING`）或新键到达行数低于旧键在途（`NEWKEY_PARTIAL`）。
3. 独立交付：证据齐备、消费者全部升级、新键覆盖完整、锚点完整、对照保留至上线日后。

三务口径随状态派生：独立交付仅发新键、仅按新键补数（禁旧键补，防同一订单算进两个区域）；旧键对照新旧双发、仅按旧键补并映射换算、新旧不得同补；不可放行维持旧键、禁止补数。旧键对照数据丢失时，已切换区域的回查口径降为「无法复核」。

## 陷阱登记

| TRAP | 现象 | 朴素实现会怎样 | 本项目处理 | 处理位置 | 测试 |
|---|---|---|---|---|---|
| TRAP-02 | 快照加 BOM | 首字段异常 | UTF-8 BOM 解码 | `app/modules/m1_intake/reader.py` | `tests/test_intake.py::test_bom` |
| TRAP-06 | 行数全角千分位 | 按原文解析失败 | 正则后归一 | `app/keys.py` | `tests/test_intake.py::test_fullwidth_grouping` |
| TRAP-07 | 消费者数 N/A | 当作零放行 | 隔离无效来源行 | `app/modules/m1_intake/service.py` | `tests/test_intake.py::test_missing_value_isolated` |
| TRAP-09 | 超大行数汇总 | 浏览器舍入 | 安全范围外用字符串 | `app/modules/m6_reconcile/service.py` | `tests/test_reconcile.py::test_aggregated_large_counts_are_exact_strings` |
| TRAP-14 | 同旧键两条不同映射 | 最后一次覆盖 | 整组隔离并判证据不全 | `app/modules/m1_intake/service.py` | `tests/test_intake.py::test_conflict_both_reviewed` |
| TRAP-16 | 快照尾部截断 | 保留半表 | 结构完整才计算 | `app/modules/m1_intake/reader.py` | `tests/test_intake.py::test_truncated_input_rejected` |
| TRAP-17 | 旧字段 count | 字段缺失 | 择一读取旧别名 | `app/modules/m1_intake/service.py` | `tests/test_intake.py::test_legacy_count` |
| TRAP-23 | 交付日晚于数据截止 | 越界采信 | 截止日显式切界 | `app/modules/m1_intake/service.py` | `tests/test_intake.py::test_date_limit_isolated` |
| TRAP-31 | 已升级数超过消费者数 | 当作全部升级 | 隔离该来源行 | `app/modules/m1_intake/service.py` | `tests/test_intake.py::test_upgraded_over_consumers_isolated` |
| TRAP-32 | 新键交付缺回退锚点 | 切换失败无法回退 | 不隔离但判 ANCHOR_BROKEN 阻断 | `app/modules/m5_rollback/service.py` | `tests/test_rollback.py::test_broken_anchor_listed` |
| TRAP-33 | 对照保留期早于上线日 | 已切换区域无法复核 | 判 COMPARE_LOST 阻断 | `app/modules/m2_mapping/service.py` | `tests/test_mapping.py::test_retention_states` |
| TRAP-34 | 多旧键共用一新键 | 回查时区域合并双算 | 判映射证据不全 | `app/modules/m2_mapping/service.py` | `tests/test_mapping.py::test_west_evidence_incomplete` |

## 已知边界

准入按来源粒度判定，覆盖登记来源在数据截止前的在途交付与已声明旧键；未登记来源与截止日后的交付不在范围内。回退演练作用于清单中的交付指针副本，实际仓库的切换与执行另由值班系统负责。页面只读展示，不含权限与批量运营。
