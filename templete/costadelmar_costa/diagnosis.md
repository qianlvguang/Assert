# 审核模板诊断报告：IP_costadelmar_COSTA (`costadelmar_costa`)

## 1. 同族与版本选择概览

- **同族成员数**: 1 个独立版本（来源记录 ID: 182）
- **默认采用版本**: `id=182` (`IP_costadelmar_COSTA`)
- **版本判定置信度**: `single`
- **版本选择理由**: 状态健康（非错贴/非空壳）；非 test/ceshi/copy 测试分支；清洗后正文长度 chars=869
- **导出商品硬编码清理**: 共自动将 0 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）
- **并行子场景标记**: 否（同族主要为同一任务的迭代版本或别名）

## 2. 逐版本完整诊断明细

| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |
|---|---|---:|---:|---:|---|---|---|
| `182` | `IP_costadelmar_COSTA` | ✅ | 869 | 0 处 | `active_ip` | `subject_host_isolation, image_title_conflict` | 无明显模板缺陷 |

## 3. 判断方案与类间区分风险评估

- **主要审核原型**: `image_title_conflict`, `subject_host_isolation`
- **是否显式涉及二创/同人/借鉴**: 否
- **类间混淆风险等级**: `medium`
- **模板自身缺陷标签**: 无

### 规则与数据构造建议

- 【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。
- 【图文冲突优先视觉】加入“标题堆砌品牌词但图片主体完全干净”的负例，绑定 `image_overrides_title` 规则避免标题关键词抢答。

## 4. Assert 标准图库资产对齐状态

- **覆盖状态**: `supplement_asset_available_pending_approval`
- **补充参考图（待正式批准入标）**:
  - `ip_costa_del_mar` (Costa Del Mar 偏光镜 / Costa Del Mar) · fetch_ok=`True` · `assets/sch96_ip_supplement/brands/ip_costa_del_mar.png`
