# 审核模板诊断报告：Tommy Hilfiger (`tommy_hilfiger`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 155, 156）
- **默认采用版本**: `id=156` (`IP_TOMMYHILFIGER_TOMMY2`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；显式版本号 v2；清洗后正文长度 chars=444
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `155` | `IP_TOMMYHILFIGER_TOMMY` |  | 504 | 0 处 | `active_ip` | `subject_host_isolation, image_title_conflict, common_word_disambiguation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |
| `156` | `IP_TOMMYHILFIGER_TOMMY2` | ✅ | 444 | 0 处 | `active_ip` | `subject_host_isolation` | JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `common_word_disambiguation`, `image_title_conflict`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: `broken_json_schema`

### 规则与数据构造建议

- 【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。
- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【图文冲突优先视觉】加入“标题堆砌品牌词但图片主体完全干净”的负例，绑定 `image_overrides_title` 规则避免标题关键词抢答。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `backlog_needs_review`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_00176_汤美费格_Tommy_Hilfiger_` · `汤美费格（Tommy Hilfiger）` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/155_IP_TOMMYHILFIGER_TOMMY.md`](versions/155_IP_TOMMYHILFIGER_TOMMY.md) — `155`, `chars=504` 
- [`versions/156_IP_TOMMYHILFIGER_TOMMY2.md`](versions/156_IP_TOMMYHILFIGER_TOMMY2.md) — `156`, `chars=444` （默认采用）
