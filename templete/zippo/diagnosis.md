# 审核模板诊断报告：Zippo 打火机 (`zippo`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 24, 25）
- **默认采用版本**: `id=24` (`IP-zippo`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=334
- **导出商品硬编码清理**: 共自动将 4 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `24` | `IP-zippo` | ✅ | 334 | 3 处 | `active_ip` | `boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `25` | `IP-zippo us` |  | 243 | 1 处 | `active_ip` | `boolean_rule_reverse_elim` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `low`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (3 条展示)**:
  - `kb_00251_芝宝_Zippo_` · `芝宝（Zippo）` · status=`needs_identity_review`
  - `kb_05125_IP_zippo` · `IP-zippo` · status=`needs_identity_review`
  - `kb_05124_IP_zippo_us` · `IP-zippo us` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/024_IP-zippo.md`](versions/024_IP-zippo.md) — `24`, `chars=334` （默认采用）
- [`versions/025_IP-zippo_us.md`](versions/025_IP-zippo_us.md) — `25`, `chars=243` 
