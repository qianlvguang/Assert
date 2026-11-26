# 审核模板诊断报告：耐克 (Nike) (`nike`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 125, 248）
- **默认采用版本**: `id=125` (`IP_Nikelogo_strategy_prompt`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +2）；清洗后正文长度 chars=1184
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `125` | `IP_Nikelogo_strategy_prompt` | ✅ | 1184 | 2 处 | `active_ip` | `subject_host_isolation, boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `248` | `IP组-nike-关键词召回识别` |  | 128 | 0 处 | `quarantine_paste_bug` | `multi_image_open_set` | 标题为 IP组-nike-关键词召回识别，正文却是通用未限定 IP 字典模板。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `multi_image_open_set`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: `cross_entity_paste_bug`

### 规则与数据构造建议

- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_00390_IP组_nike_关键词召回识别` · `IP组-nike-关键词召回识别` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/125_IP_Nikelogo_strategy_prompt.md`](versions/125_IP_Nikelogo_strategy_prompt.md) — `125`, `chars=1184` （默认采用）
- [`versions/248_IP组-nike-关键词召回识别.md`](versions/248_IP组-nike-关键词召回识别.md) — `248`, `chars=128` 
