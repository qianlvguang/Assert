# 审核模板诊断报告：穆罕默德·阿里 (Muhammad Ali) (`muhammad_ali`)

## 1. 同族与版本选择概览

- **同族成员数**: 7 个独立版本（来源记录 ID: 115, 116, 338）
- **默认采用版本**: `id=116` (`IP_MUHAMMADALI_ALI_V2`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v2；清洗后正文长度 chars=418
- **导出商品硬编码清理**: 共自动将 1 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `115::1` | `muhammadali` |  | 83 | 0 处 | `active_ip` | `brand_logo_trademark` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。；判据过于笼统（清洗后 83 字）：仅一句宽泛提问，缺少专属强锚点、排除词与宿主边界定义。 |
| `115::2` | `IP_MUHAMMADALI` |  | 138 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `115::3` | `IP_MUHAMMADALI_2` |  | 276 | 0 处 | `active_ip` | `fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `115::4` | `IP_MUHAMMADALI_01` |  | 451 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `116::1` | `IP_MUHAMMADALI_ALI` |  | 454 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |
| `116::2` | `IP_MUHAMMADALI_ALI_V2` | ✅ | 418 | 1 处 | `active_ip` | `boolean_rule_reverse_elim` | 无明显模板缺陷 |
| `338` | `ip_MUHAMMADAL_layla` |  | 164 | 0 处 | `active_ip` | `brand_logo_trademark` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `brand_logo_trademark`, `fuzzy_ocr_deformation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `broken_json_schema`, `underspecified_rubric`

### 规则与数据构造建议

- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。
- 【规则补全】当前主模板仅一句宽泛提问，类间边界完全未定义；建议先补充正例必需锚点清单与常见误召回排除条款，再进入训练或线上评测。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (3 条展示)**:
  - `kb_08632_muhammadali` · `muhammadali` · status=`needs_identity_review`
  - `kb_00209_穆罕默德_阿里_Muhammad_Ali_` · `穆罕默德·阿里（Muhammad Ali）` · status=`needs_identity_review`
  - `kb_08631_ip_MUHAMMADAL_layla` · `ip_MUHAMMADAL_layla` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/115_muhammadali.md`](versions/115_muhammadali.md) — `115::1`, `chars=83` 
- [`versions/115_IP_MUHAMMADALI.md`](versions/115_IP_MUHAMMADALI.md) — `115::2`, `chars=138` 
- [`versions/115_IP_MUHAMMADALI_2.md`](versions/115_IP_MUHAMMADALI_2.md) — `115::3`, `chars=276` 
- [`versions/115_IP_MUHAMMADALI_01.md`](versions/115_IP_MUHAMMADALI_01.md) — `115::4`, `chars=451` 
- [`versions/116_IP_MUHAMMADALI_ALI.md`](versions/116_IP_MUHAMMADALI_ALI.md) — `116::1`, `chars=454` 
- [`versions/116_IP_MUHAMMADALI_ALI_V2.md`](versions/116_IP_MUHAMMADALI_ALI_V2.md) — `116::2`, `chars=418` （默认采用）
- [`versions/338_ip_MUHAMMADAL_layla.md`](versions/338_ip_MUHAMMADAL_layla.md) — `338`, `chars=164` 
