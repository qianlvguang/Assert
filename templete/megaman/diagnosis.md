# 审核模板诊断报告：IP_megaman (`megaman`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 20）
- **默认采用版本**: `id=20` (`IP_megaman`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=256
- **导出商品硬编码清理**: 共自动将 6 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `20::1` | `IP-megaman` |  | 190 | 5 处 | `active_ip` | `anime_derivative_two_step, subject_host_isolation, boolean_rule_reverse_elim` | `rel` 中的 `MEGA` 为 `megaman` 子串误匹配，非 Mattel MEGA 积木；JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。；错别字：`Maga Man`（应为 Mega Man）；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `20::2` | `IP_megaman` | ✅ | 256 | 1 处 | `active_ip` | `anime_derivative_two_step` | `rel` 中的 `MEGA` 为 `megaman` 子串误匹配，非 Mattel MEGA 积木；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`, `boolean_rule_reverse_elim`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 是
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `broken_json_schema`, `missing_exclusion_clause`, `rel_metadata_mismatch`, `typo_or_logic_defect`

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。
- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_00299_IP_megaman` · `IP-megaman` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/020_IP-megaman.md`](versions/020_IP-megaman.md) — `20::1`, `chars=190` 
- [`versions/020_IP_megaman.md`](versions/020_IP_megaman.md) — `20::2`, `chars=256` （默认采用）
