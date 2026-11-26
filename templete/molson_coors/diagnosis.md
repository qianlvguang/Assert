# 审核模板诊断报告：莫尔森库尔斯啤酒 (Molson Coors / Miller) (`molson_coors`)

## 1. 同族与版本选择概览

- **同族成员数**: 5 个独立版本（来源记录 ID: 376, 397, 398, 399, 400）
- **默认采用版本**: `id=400` (`ip_molson_mianshen4`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v4；清洗后正文长度 chars=439
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `376` | `ip_coors` |  | 302 | 0 处 | `active_ip` | `subject_host_isolation` | 无明显模板缺陷 |
| `397` | `ip_molson_mianshen` |  | 18 | 0 处 | `needs_body_completion` | `brand_logo_trademark` | 正文过短（清洗后 18 字），实质仅为标题占位，无法用于审核执行。 |
| `398` | `ip_molson_mianshen2` |  | 492 | 0 处 | `active_ip` | `boolean_rule_reverse_elim` | 布尔逻辑高危缺陷：Molson 多个子品牌（Miller / Lite 等）本应为“满足任一 (OR)”，模板误写成“满足以下所有条件 (AND)”。 |
| `399` | `ip_molson_mianshen3` |  | 491 | 0 处 | `active_ip` | `boolean_rule_reverse_elim` | 布尔逻辑高危缺陷：Molson 多个子品牌（Miller / Lite 等）本应为“满足任一 (OR)”，模板误写成“满足以下所有条件 (AND)”。 |
| `400` | `ip_molson_mianshen4` | ✅ | 439 | 0 处 | `active_ip` | `boolean_rule_reverse_elim` | 布尔逻辑高危缺陷：Molson 多个子品牌（Miller / Lite 等）本应为“满足任一 (OR)”，模板误写成“满足以下所有条件 (AND)”。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `brand_logo_trademark`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: `empty_or_trivial_body`, `typo_or_logic_defect`

### 规则与数据构造建议

- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (6 条展示)**:
  - `kb_05116_ip_coors` · `ip_coors` · status=`needs_identity_review`
  - `kb_00444_酷尔斯啤酒及摩森康胜旗下品牌_Coors_Molson_Coors_` · `酷尔斯啤酒及摩森康胜旗下品牌（Coors / Molson Coors）` · status=`needs_identity_review`
  - `kb_05118_ip_molson_mianshen` · `ip_molson_mianshen` · status=`needs_identity_review`
  - `kb_05120_ip_molson_mianshen2` · `ip_molson_mianshen2` · status=`needs_identity_review`
  - `kb_05121_ip_molson_mianshen3` · `ip_molson_mianshen3` · status=`needs_identity_review`
  - `kb_05119_ip_molson_mianshen4` · `ip_molson_mianshen4` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/376_ip_coors.md`](versions/376_ip_coors.md) — `376`, `chars=302` 
- [`versions/397_ip_molson_mianshen.md`](versions/397_ip_molson_mianshen.md) — `397`, `chars=18` 
- [`versions/398_ip_molson_mianshen2.md`](versions/398_ip_molson_mianshen2.md) — `398`, `chars=492` 
- [`versions/399_ip_molson_mianshen3.md`](versions/399_ip_molson_mianshen3.md) — `399`, `chars=491` 
- [`versions/400_ip_molson_mianshen4.md`](versions/400_ip_molson_mianshen4.md) — `400`, `chars=439` （默认采用）
