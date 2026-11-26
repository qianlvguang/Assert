# 审核模板诊断报告：鬼灭之刃 (Demon Slayer) (`demon_slayer`)

## 1. 同族与版本选择概览

- **同族成员数**: 6 个独立版本（来源记录 ID: 187, 188, 189）
- **默认采用版本**: `id=188` (`IP_demonslayer_huawen`)
- **版本判定置信度**: `high`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=1717
- **导出商品硬编码清理**: 共自动将 5 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `187::1` | `IP_demonslayer` |  | 1571 | 1 处 | `active_ip` | `anime_derivative_two_step` | 无明显模板缺陷 |
| `187::2` | `IP_demonslayer_ceshi` |  | 1566 | 0 处 | `active_ip` | `anime_derivative_two_step` | 无明显模板缺陷 |
| `187::3` | `IP_demonslayer_ceshi_1` |  | 1651 | 1 处 | `active_ip` | `anime_derivative_two_step` | 无明显模板缺陷 |
| `187::4` | `IP_demonslayer_ceshi_BUSHANGXIAN` |  | 1571 | 1 处 | `active_ip` | `anime_derivative_two_step` | 无明显模板缺陷 |
| `188` | `IP_demonslayer_huawen` | ✅ | 1717 | 1 处 | `active_ip` | `anime_derivative_two_step` | 无明显模板缺陷 |
| `189` | `IP_demonslayer_zhuanshentizhun` |  | 1712 | 1 处 | `active_ip` | `anime_derivative_two_step` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `anime_derivative_two_step`
- **是否显式涉及二创/同人/借鉴**: 是
- **类间混淆风险等级**: `high`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_demon_slayer` (鬼灭之刃 Demon Slayer / Demon Slayer: Kimetsu no Yaiba) · fetch_ok=`True` · `assets/sch96_ip_supplement/anime_games_entertainment/ip_demon_slayer.png`
- **1119 待办清单命中 (1 条展示)**:
  - `kb_00200_鬼灭之刃_Demon_Slayer_鬼滅の刃_` · `鬼灭之刃（Demon Slayer / 鬼滅の刃）` · status=`needs_identity_review`

## 5. 同族版本文件索引

- [`versions/187_IP_demonslayer.md`](versions/187_IP_demonslayer.md) — `187::1`, `chars=1571` 
- [`versions/187_IP_demonslayer_ceshi.md`](versions/187_IP_demonslayer_ceshi.md) — `187::2`, `chars=1566` 
- [`versions/187_IP_demonslayer_ceshi_1.md`](versions/187_IP_demonslayer_ceshi_1.md) — `187::3`, `chars=1651` 
- [`versions/187_IP_demonslayer_ceshi_BUSHANGXIAN.md`](versions/187_IP_demonslayer_ceshi_BUSHANGXIAN.md) — `187::4`, `chars=1571` 
- [`versions/188_IP_demonslayer_huawen.md`](versions/188_IP_demonslayer_huawen.md) — `188`, `chars=1717` （默认采用）
- [`versions/189_IP_demonslayer_zhuanshentizhun.md`](versions/189_IP_demonslayer_zhuanshentizhun.md) — `189`, `chars=1712` 
