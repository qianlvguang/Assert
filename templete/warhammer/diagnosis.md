# 审核模板诊断报告：IP-Warhammer-llm-black (`warhammer`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 15）
- **默认采用版本**: `id=15` (`IP-Warhammer-llm-black`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=999
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `15::1` | `IP-Warhammer-llm-black` | ✅ | 999 | 1 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation, boolean_rule_reverse_elim` | `rel` 中的 `Black` 为后缀/队名子串误匹配 |
| `15::2` | `IP-Warhammer-llm-black_coarse_recall` |  | 1038 | 1 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation, boolean_rule_reverse_elim` | `rel` 中的 `Black` 为后缀/队名子串误匹配 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `common_word_disambiguation`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `rel_metadata_mismatch`

### 规则与数据构造建议

- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_warhammer` (战锤 Warhammer / Warhammer) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_warhammer.png`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_00270_IP_Warhammer_llm_black` · `IP-Warhammer-llm-black` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/015_IP-Warhammer-llm-black.md`](versions/015_IP-Warhammer-llm-black.md) — `15::1`, `chars=999` （默认采用）
- [`versions/015_IP-Warhammer-llm-black_coarse_recall.md`](versions/015_IP-Warhammer-llm-black_coarse_recall.md) — `15::2`, `chars=1038` 
