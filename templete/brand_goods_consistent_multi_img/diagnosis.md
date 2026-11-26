# 审核模板诊断报告：多图商品品牌一致性审核 (`brand_goods_consistent_multi_img`)

## 1. 同族与版本选择概览

- **同族成员数**: 3 个独立版本（来源记录 ID: 365, 366）
- **默认采用版本**: `id=366` (`ip_brand_goods_consistent_multi_imgV2`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v2；含生产专项/迭代后缀（加权 +2）；清洗后正文长度 chars=3301
- **导出商品硬编码清理**: 共自动将 3 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `365::1` | `ip_brand_goods_consistent_multi_img` |  | 2126 | 1 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation` | `rel` 中的 `NSIS` 为 `consistent` 子串误匹配；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `365::2` | `ip_brand_goods_consistent_multi_img_test1` |  | 2126 | 1 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation` | `rel` 中的 `NSIS` 为 `consistent` 子串误匹配；缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。 |
| `366` | `ip_brand_goods_consistent_multi_imgV2` | ✅ | 3301 | 1 处 | `active_ip` | `subject_host_isolation, common_word_disambiguation` | `rel` 中的 `NSIS` 为 `consistent` 子串误匹配 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `common_word_disambiguation`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `missing_exclusion_clause`, `rel_metadata_mismatch`

### 规则与数据构造建议

- 【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。
- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (2 条展示)**:
  - `kb_00312_ip_brand_goods_consistent_multi_img` · `ip_brand_goods_consistent_multi_img` · status=`needs_identity_review`
  - `kb_00313_ip_brand_goods_consistent_multi_imgV2` · `ip_brand_goods_consistent_multi_imgV2` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/365_ip_brand_goods_consistent_multi_img.md`](versions/365_ip_brand_goods_consistent_multi_img.md) — `365::1`, `chars=2126` 
- [`versions/365_ip_brand_goods_consistent_multi_img_test1.md`](versions/365_ip_brand_goods_consistent_multi_img_test1.md) — `365::2`, `chars=2126` 
- [`versions/366_ip_brand_goods_consistent_multi_imgV2.md`](versions/366_ip_brand_goods_consistent_multi_imgV2.md) — `366`, `chars=3301` （默认采用）
