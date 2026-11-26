# 审核模板诊断报告：福特汽车 (Ford) (`ford`)

## 1. 同族与版本选择概览

- **同族成员数**: 5 个独立版本（来源记录 ID: 383, 384, 385）
- **默认采用版本**: `id=385` (`ip_ford_mat`)
- **版本判定置信度**: `parallel_sub_scopes`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1027
- **导出商品硬编码清理**: 共自动将 1 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 是（该审核对象下存在不同品类/任务边界的子模板，请结合 `versions/` 一并查看）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `383::1` | `ip_ford` |  | 607 | 0 处 | `active_ip` | `auto_parts_compatibility_obfuscation` | 无明显模板缺陷 |
| `383::2` | `ip_ford_copy` |  | 668 | 0 处 | `active_ip` | `auto_parts_compatibility_obfuscation` | 无明显模板缺陷 |
| `383::3` | `ip_ford_prompt` |  | 948 | 1 处 | `active_ip` | `auto_parts_compatibility_obfuscation` | 无明显模板缺陷 |
| `384` | `ip_ford_carparts` |  | 1027 | 0 处 | `active_ip` | `common_word_disambiguation, auto_parts_compatibility_obfuscation` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `385` | `ip_ford_mat` | ✅ | 1027 | 0 处 | `active_ip` | `common_word_disambiguation, auto_parts_compatibility_obfuscation` | 缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `auto_parts_compatibility_obfuscation`, `common_word_disambiguation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `missing_exclusion_clause`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【汽配适配豁免 vs 涂抹规避】区分标题中合理的 `for / fits / suitable for <品牌>` 适配说明（主体干净 -> false）与主体实物商标/涂抹马赛克规避（-> true）。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_ford` (福特汽车 Ford / Ford) · fetch_ok=`True` · `assets/sch96_ip_supplement/brands/ip_ford.png`
- **1119 待办清单命中 (3 条展示)**:
  - `kb_00286_ip_ford` · `ip_ford` · status=`needs_identity_review`
  - `kb_00287_ip_ford_carparts` · `ip_ford_carparts` · status=`needs_identity_review`
  - `kb_00288_ip_ford_mat` · `ip_ford_mat` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/383_ip_ford.md`](versions/383_ip_ford.md) — `383::1`, `chars=607` 
- [`versions/383_ip_ford_copy.md`](versions/383_ip_ford_copy.md) — `383::2`, `chars=668` 
- [`versions/383_ip_ford_prompt.md`](versions/383_ip_ford_prompt.md) — `383::3`, `chars=948` 
- [`versions/384_ip_ford_carparts.md`](versions/384_ip_ford_carparts.md) — `384`, `chars=1027` 
- [`versions/385_ip_ford_mat.md`](versions/385_ip_ford_mat.md) — `385`, `chars=1027` （默认采用）
