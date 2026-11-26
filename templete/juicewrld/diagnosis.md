# 审核模板诊断报告：IP-juicewrld (`juicewrld`)

## 1. 同族与版本选择概览

- **同族成员数**: 1 个独立版本（来源记录 ID: 19）
- **默认采用版本**: `id=19` (`IP-juicewrld`)
- **版本判定置信度**: `single`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=244
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `19` | `IP-juicewrld` | ✅ | 244 | 0 处 | `active_ip` | `boolean_rule_reverse_elim` | 错别字：`以尺规则`（应为以下规则） |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `low`
- **模板自身缺陷标签**: `typo_or_logic_defect`

### 规则与数据构造建议

- 【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_08625_IP_juicewrld` · `IP-juicewrld` · status=`needs_identity_review`
  - `kb_05012_Juice_WRLD_杰拉德_安东尼_希金斯_Jarad_Anthony_Hig` · `Juice WRLD（杰拉德·安东尼·希金斯 / Jarad Anthony Higgins）` · status=`needs_identity_review`
