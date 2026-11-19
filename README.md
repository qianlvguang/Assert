# 体育联赛队徽 + 96 模板 IP 官标独立补充包 (`sports_ip_supplement`)

本目录为完全独立、可随时插拔至 `Datawheel` 与 `CPT-SFT` 的真实官方图标补充包，不会改写或污染原有核心数据集。

## 产物清单

| 文件 | 用途 |
|---|---|
| `cpt_sports_crests_supplement.jsonl` | 五大联赛 / NBA / NFL / MLB / NHL / NCAA 球队单图锚定 + 同联赛德比/近邻双图辨析 + 分组图谱行（`is_synthetic_image=false`, `synthetic_image_count=0`） |
| `cpt_sch96_ip_supplement.jsonl` | 96 模板中可定位品牌/乐队/动漫游戏官方图标锚定与同名消歧行（`is_synthetic_image=false`） |
| `cpt_all_supplement.jsonl` | 上述两部分合集，可直接传入 `CPT-SFT/training/flash/build_mm_wiki_cpt.py --mode midtrain` |
| `v2_entities_sports_and_ip_supplement.jsonl` | 直接传入 `CPT-SFT/training/flash/build_v2_image_pipeline.py --entities ...`，全部绑定真实 `ref_images`，强制走 Edit 保真路线、杜绝纯 T2I 幻觉 |
| `sch96_template_coverage.{json,md}` | 96 模板逐条覆盖审计台账（含重名模板归并、多义待确认与泛化类目说明） |
| `contact_sheets/*.jpg` | 棋盘格透明底可视化质检拼图 |

## 接入 `CPT-SFT` 示例命令

```bash
# 1. 接入 ImageGen v2（以官方参考图驱动 Edit，禁止纯 T2I）
python3 ../CPT-SFT/training/flash/build_v2_image_pipeline.py \
  --entities output/sports_ip_supplement/v2_entities_sports_and_ip_supplement.jsonl \
  --output-dir /tmp/sports_v2_out --mode mock

# 2. 接入 Flash Mid-Training（与主池混合；本包图元均标记为真实参考图，不计入 25% 合成图配额）
python3 ../CPT-SFT/training/flash/build_mm_wiki_cpt.py \
  --mode midtrain \
  --inputs output/sports_ip_supplement/cpt_all_supplement.jsonl \
  --output-dir /tmp/sports_midtrain_out
```
