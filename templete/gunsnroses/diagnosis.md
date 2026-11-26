# 审核模板诊断报告：IP_gunsnroses_strategy (`gunsnroses`)

## 1. 同族与版本选择概览

- **同族成员数**: 2 个独立版本（来源记录 ID: 81）
- **默认采用版本**: `id=81` (`IP_gunsnroses_strategy`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；含生产专项/迭代后缀（加权 +2）；清洗后正文长度 chars=1421
- **导出商品硬编码清理**: 共自动将 2 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `81::1` | `IP_GUNSNROSES` |  | 1311 | 2 处 | `active_ip` | `anime_derivative_two_step, sports_collegiate_celebrity` | 无明显模板缺陷 |
| `81::2` | `IP_gunsnroses_strategy` | ✅ | 1421 | 0 处 | `active_ip` | `anime_derivative_two_step, sports_collegiate_celebrity, boolean_rule_reverse_elim` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`, `boolean_rule_reverse_elim`, `sports_collegiate_celebrity`
- **是否显式涉及二创/同人/借鉴**: 是
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。
- 【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `approved_in_assert`
- **已批准标准参考图**:
  - `kb_00369_枪与玫瑰乐队_Guns_N_Roses_` (`artist:guns_n_roses`) → `['sch96_ip_supplement/music_celebrity_sports/ip_guns_n_roses.png']`
- **补充参考图（待正式批准入标）**:
  - `ip_guns_n_roses` (枪炮与玫瑰乐队 Guns N' Roses / Guns N' Roses) · fetch_ok=`True` · `assets/sch96_ip_supplement/music_celebrity_sports/ip_guns_n_roses.png`

## 5. 同族版本文件索引

- [`versions/081_IP_GUNSNROSES.md`](versions/081_IP_GUNSNROSES.md) — `81::1`, `chars=1311` 
- [`versions/081_IP_gunsnroses_strategy.md`](versions/081_IP_gunsnroses_strategy.md) — `81::2`, `chars=1421` （默认采用）
