# 审核模板诊断报告：佐治亚大学斗牛犬队 (UGA) (`uga`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 164, 459）
- **默认采用版本**: `id=164` (`IP_UGA`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=302
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `164::1` | `IP_UGA` | ✅ | 302 | 0 处 | `active_ip` | `sports_collegiate_celebrity` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `164::2` | `IP_UGA_1` |  | 255 | 1 处 | `active_ip` | `sports_collegiate_celebrity` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `459` | `ugaa` |  | 1582 | 1 处 | `active_ip` | `sports_collegiate_celebrity, boolean_rule_reverse_elim` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: `broken_json_schema`, `missing_exclusion_clause`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_07678_ugaa` · `ugaa` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/164_IP_UGA.md`](versions/164_IP_UGA.md) — `164::1`, `chars=302` （默认采用）
- [`versions/164_IP_UGA_1.md`](versions/164_IP_UGA_1.md) — `164::2`, `chars=255` 
- [`versions/459_ugaa.md`](versions/459_ugaa.md) — `459`, `chars=1582` 
