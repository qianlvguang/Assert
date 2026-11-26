# 审核模板诊断报告：IP_toyota_llm (`toyota`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 232）
- **默认采用版本**: `id=232` (`IP_toyota_llm`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1455
- **导出商品硬编码清理**: 共自动将 3 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `232::1` | `IP_toyota_llm` | ✅ | 1455 | 2 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation, auto_parts_compatibility_obfuscation, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `232::2` | `ip-toyota-llm-black` |  | 1142 | 1 处 | `active_ip` | `subject_host_isolation, auto_parts_compatibility_obfuscation, boolean_rule_reverse_elim, fuzzy_ocr_deformation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `auto_parts_compatibility_obfuscation`, `boolean_rule_reverse_elim`, `common_word_disambiguation`, `fuzzy_ocr_deformation`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `broken_json_schema`

### 规则与数据构造建议

- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【汽配适配豁免 vs 涂抹规避】区分标题中合理的 `for / fits / suitable for <品牌>` 适配说明（主体干净 -> false）与主体实物商标/涂抹马赛克规避（-> true）。
- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `no_assert_match`
- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。

## 5. 同族版本文件索引

- [`versions/232_IP_toyota_llm.md`](versions/232_IP_toyota_llm.md) — `232::1`, `chars=1455` （默认采用）
- [`versions/232_ip-toyota-llm-black.md`](versions/232_ip-toyota-llm-black.md) — `232::2`, `chars=1142` 
