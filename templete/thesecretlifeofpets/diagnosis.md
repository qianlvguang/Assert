# 审核模板诊断报告：IP_TheSecretLifeofPets_db (`thesecretlifeofpets`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 159）
- **默认采用版本**: `id=159` (`IP_TheSecretLifeofPets_db`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1195
- **导出商品硬编码清理**: 共自动将 3 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `159::1` | `IP_TheSecretLifeofPets` |  | 1158 | 1 处 | `active_ip` | `fuzzy_ocr_deformation` | 无明显模板缺陷 |
| `159::2` | `IP_TheSecretLifeofPets_db` | ✅ | 1195 | 2 处 | `active_ip` | `boolean_rule_reverse_elim, fuzzy_ocr_deformation` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `boolean_rule_reverse_elim`, `fuzzy_ocr_deformation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_secret_life_of_pets` (爱宠大机密 The Secret Life of Pets / The Secret Life of Pets) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_secret_life_of_pets.png`

## 5. 同族版本文件索引

- [`versions/159_IP_TheSecretLifeofPets.md`](versions/159_IP_TheSecretLifeofPets.md) — `159::1`, `chars=1158` 
- [`versions/159_IP_TheSecretLifeofPets_db.md`](versions/159_IP_TheSecretLifeofPets_db.md) — `159::2`, `chars=1195` （默认采用）
