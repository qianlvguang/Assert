# Assert — 独立标准参考图库

本项目独立负责标准参考图片的采集、来源记录、身份映射、文件校验与验收。使用本项目自己的代码、环境和资源；外部消费者通过导出的文件接入，不共享源码或虚拟环境。

## 独立环境

在本目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

体育／模板补图构建器已迁入 [scripts/build_sports_ip_supplement.py](scripts/build_sports_ip_supplement.py)，视觉工具位于 [scripts/asset_visual_helpers.py](scripts/asset_visual_helpers.py)。原始图片仍使用现有目录，新的构建结果写入 `output/sports_ip_supplement/`；不会重写根目录历史 JSONL 或原始 manifests。

```bash
.venv/bin/python scripts/build_sports_ip_supplement.py --build-pack
# 需要更新源图时才联网采集
.venv/bin/python scripts/build_sports_ip_supplement.py --fetch --retry-failed
```

原工作区的重复补图资源与产物已完整归档于 `.legacy/supplement_before_separation/`，逐文件迁移哈希见 [拆分记录](manifests/project_separation.json)。归档仅保存历史，不参与运行。

## 新增补图规范（1119 批次）

见 [补图规范与执行方案](docs/standard_image_policy.md)。已将新增清单解析为 4,668 条待办，建立 320 张已有 PNG 的初始资源索引，并为 48 条待办找到名称匹配候选。初始待办保留不变，后续下载与审核结果见下方「补图执行与当前结果」。

- [逐条补图待办](manifests/standard_images_1119/backlog.jsonl)
- [已有资源索引](manifests/standard_images_1119/existing_assets.jsonl)
- [批次统计与输入指纹](manifests/standard_images_1119/summary.json)
- [清单生成脚本](scripts/build_standard_image_backlog.py)

原 JSONL 的 `assets/` 路径及下方示例的 `output/sports_ip_supplement/` 是旧布局，直接在当前目录执行前需适配。新索引的 `local_path` 已按当前目录记录；原文件保持不变。

## 补图执行与当前结果

- [本次执行统计](manifests/standard_images_1119/execution_summary.json)
- [统一图片注册表](manifests/standard_image_assets.jsonl)
- [全部实体的当前映射与状态](manifests/standard_image_links.jsonl)
- [已批准的参考图映射](manifests/standard_images_1119/approved_references.jsonl)
- [48 条复用候选审核结果](manifests/standard_images_1119/reuse_review_decisions.jsonl)

已有图片复用审核：37 条按明确的标志用途批准，4 条错配拒绝，7 条版本待核。新立绘使用固定提交版本的 PokeAPI 镜像，保留原图、来源、哈希、尺寸及身份依据；下载／完整性通过与逐张视觉批准分别记录。新图目录与缓存已加入 Git 忽略规则，不自动提交大体积图片。

在本目录执行：

```bash
.venv/bin/python scripts/collect_pokemon_references.py --workers 4
.venv/bin/python scripts/finalize_standard_image_batch.py
```

下载器支持缓存续跑，源版本固定在 `manifests/standard_images_1119/pokemon_source_versions.json`。合并脚本会重新生成统一注册表、实体状态及参考图映射；人工后续更正应同步修改脚本内显式审核规则，避免续跑时被覆盖。已批准参考图文件是实体与图片映射，不是可以直接用于训练的成品数据集。

## 产物清单

| 文件 | 用途 |
|---|---|
| `cpt_sports_crests_supplement.jsonl` | 五大联赛 / NBA / NFL / MLB / NHL / NCAA 球队单图锚定 + 同联赛德比/近邻双图辨析 + 分组图谱行（`is_synthetic_image=false`, `synthetic_image_count=0`） |
| `cpt_sch96_ip_supplement.jsonl` | 96 模板中可定位品牌/乐队/动漫游戏官方图标锚定与同名消歧行（`is_synthetic_image=false`） |
| `cpt_all_supplement.jsonl` | 上述两部分合集，可直接传入 `CPT-SFT/training/flash/build_mm_wiki_cpt.py --mode midtrain` |
| `v2_entities_sports_and_ip_supplement.jsonl` | 直接传入 `CPT-SFT/training/flash/build_v2_image_pipeline.py --entities ...`，全部绑定真实 `ref_images`，强制走 Edit 保真路线、杜绝纯 T2I 幻觉 |
| `sch96_template_coverage.{json,md}` | 96 模板逐条覆盖审计台账（含重名模板归并、多义待确认与泛化类目说明） |
| `contact_sheets/*.jpg` | 棋盘格透明底可视化质检拼图 |

## 文件交付边界

`manifests/standard_image_assets.jsonl` 的 `local_path` 相对本项目根目录解析。外部消费者应显式指定收到的资源目录，不读取相邻仓库，不建立软链接，不导入本项目源码。`approved_references.jsonl` 只交付已批准映射，完整图片交付时按注册表相对路径打包。

根目录 `cpt_*.jsonl` 和 `v2_entities_*.jsonl` 为历史导出，保留原样；新导出位于 `output/sports_ip_supplement/`。历史清单仍可能含版本待核与错配条目，不能替代已批准参考图清单。

## 审核模板库与逐模板诊断 (`templete/`)

- 原始 461 条审核模板快照（全量完整版）：[manifests/audit_prompts_461_full_raw.jsonl](manifests/audit_prompts_461_full_raw.jsonl)
- 导出残留自动清洗版（还原硬编码商品为 `#GOODS_TEXT_INFO#` 等占位符）：[manifests/audit_prompts_461_full_cleaned.jsonl](manifests/audit_prompts_461_full_cleaned.jsonl)、[manifests/export_cleanup_report.json](manifests/export_cleanup_report.json)
- 可视化交互审核画廊：[templete/review_dashboard.html](templete/review_dashboard.html)（暖纸编辑部风格离线单页应用，支持多维检索、533 拆包版本并排对比、缺陷高亮、Assert 参考图预览及人工复核导出）
- 模板库总览与目录索引：[templete/README.md](templete/README.md)（按同审核对象归并至子目录，默认优选最新/健康主版本写入 `latest_template.md`，并附逐模板 `diagnosis.md` 与 `family.json`）
- 汇总统计与机器清单：[manifests/template_library_manifest.json](manifests/template_library_manifest.json)、[templete/diagnostics.jsonl](templete/diagnostics.jsonl)

重建命令：

```bash
.venv/bin/python scripts/build_template_library.py
.venv/bin/python scripts/build_template_review_html.py
```
