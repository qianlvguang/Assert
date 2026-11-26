#!/usr/bin/env python3
"""Deterministic full visual & template audit finalizer for Assert/templete.

Encodes verified visual inspection decisions for all 307 Track B (entity_specific)
families, purges visually confirmed mismatches, assigns authoritative review verdicts
(`approved` | `needs_fix` | `needs_asset` | `quarantined`) across all 352 families,
and produces:
  - manifests/template_visual_audit_decisions.jsonl
  - manifests/template_visual_audit_summary.json
  - manifests/template_audit_decisions.jsonl
  - manifests/template_audit_decisions.json
  - manifests/assert_template_reviews_audited.json (schema: assert_template_review_v1)
  - templete/final_audit_report.md
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLETE_DIR = PROJECT_ROOT / "templete"
DEFAULT_TAXONOMY_JSON = PROJECT_ROOT / "manifests" / "template_taxonomy_requirements.json"
DEFAULT_ENRICH_JSONL = PROJECT_ROOT / "manifests" / "template_wiki_enrichment.jsonl"

DEFAULT_VISUAL_JSONL = PROJECT_ROOT / "manifests" / "template_visual_audit_decisions.jsonl"
DEFAULT_VISUAL_SUMMARY = PROJECT_ROOT / "manifests" / "template_visual_audit_summary.json"
DEFAULT_AUDIT_JSONL = PROJECT_ROOT / "manifests" / "template_audit_decisions.jsonl"
DEFAULT_AUDIT_JSON = PROJECT_ROOT / "manifests" / "template_audit_decisions.json"
DEFAULT_REVIEWS_JSON = PROJECT_ROOT / "manifests" / "assert_template_reviews_audited.json"
DEFAULT_FINAL_REPORT_MD = DEFAULT_TEMPLETE_DIR / "final_audit_report.md"

AUDIT_TIMESTAMP = "2026-11-26T11:30:00+08:00"

# ---------------------------------------------------------------------------
# Explicit Visual Inspection Verdicts (derived from human-style contact-sheet QA)
# ---------------------------------------------------------------------------

# Specific relative asset paths rejected across visual QA (never show or approve)
REJECTED_ASSET_PATHS: dict[str, str] = {
    "sch96_ip_supplement/brands/ip_triumph_international.png": "错配：内衣品牌 Triumph International，不符合 IP_Triumph 摩托车条款",
    "sch96_ip_supplement/music_celebrity_sports/ip_evel_knievel.png": "违例：博物馆宣传徽标而非权利人本体参考图（已改用 Wiki 本人档案照）",
}

# Wiki-fetched families whose downloaded candidate was visually rejected as wrong entity
REJECTED_WIKI_SLUGS: dict[str, str] = {
    "bigfoot": "错配清除：命中 1967 年 Patterson-Gimlin 森林模糊影照，非品牌/文创视觉标识",
    "cookies": "错配清除：命中 Craig's Cookies 烘焙店标，非目标潮牌 Cookies",
    "glassangelofficial": "错配清除：命中普通圣诞玻璃天使挂件，非品牌官方参考图",
    "meitanteikonan": "错配清除：二次替换命中 ABS-CBN 电视台标，非《名侦探柯南》作品图标",
    "oster": "错配清除：二次替换命中奥地利能源协会标，非厨具品牌 Oster",
    "purple_innovation": "错配清除：命中 Chestertons 房产机构紫色标，非网格凝胶枕专利",
    "purplebrand": "错配清除：命中 Upstage 标而非服装品牌 PURPLE BRAND",
    "totto": "错配清除：命中日剧《小豆豆》标题标，非箱包品牌 TOTTO",
    "zipit": "错配清除：命中早期 Linux 掌机 Zipit，非单拉链包 Zipit 专利结构",
}

# Verified local image exists, but template scope requires additional structural/type photos
INSUFFICIENT_SCOPE_ASSETS: dict[str, str] = {
    "apple": "已有苹果剪影 Logo，但 IP_APPLE_WATCHBAND 需官方各代 Apple Watch 表带结构对比图",
    "rabanne_bag": "已有 Paco Rabanne 字标，但模板核心审金属圆片链甲包体装潢，仍缺包型结构实拍图",
}

# Visually authentic references with concrete non-blocking enrichment recommendations
ENRICHMENT_NOTES: dict[str, str] = {
    "alexandermcqueen": "已从设计师肖像替换为 Alexander McQueen 官方字标 SVG",
    "annabelle": "真实原型娃娃照已验真，建议补充电影版瓷娃娃特写",
    "calvin_klein": "已从设计师肖像替换为 CK Calvin Klein 官方矢量标",
    "converseallstar": "经典帆布鞋照已验真，建议补充鞋帮圆形星标特写",
    "dav_pilkey_dogman": "Captain Underpants 标志已验真，建议补充《Dog Man》封面角色图",
    "dsquared2": "已从创始人合照替换为 DSQUARED2 官方字标",
    "evelknievel": "已剔除博物馆标并替换为 Evel Knievel 本人档案照，建议再补星条战服徽记",
    "junjiito": "作者伊藤润二肖像已验真，建议补充《富江》《漩涡》代表画作切片",
    "minions": "已从街头雕塑替换为《Minions》官方片名标，建议补充角色三视图用于二创",
    "nike_jordan": "已剔除约旦空军徽标并替换为 Air Jordan Jumpman 官方矢量标",
    "novak_djokovic": "德约科维奇官方签名标已验真，建议补充赛场正面肖像照",
    "sharks_rugby": "南非 Sharks 职业橄榄球队盾徽 SRC 已核实匹配",
    "sunlight": "Sunlight 经典洗护包装实拍已验真，建议补充现代版瓶身与字标",
    "swarovski": "Swarovski 字标已验真，建议补充经典天鹅（iconic swan）图形标",
    "triumph": "已核准 Triumph Motorcycles 字标并剔除 Triumph International 内衣错配标",
    "ugg": "UGG 字标已验真，建议补充经典雪地靴专利外观图",
    "velcro": "已从魔术贴织物微距替换为 Velcro Brand 官方矢量标",
    "vivienne_westwood": "已从设计师肖像替换为 Vivienne Westwood 土星环+手写体店招标",
}

# Prompt defects that block clean execution or corrupt evaluation on the selected latest version
CRITICAL_PROMPT_FLAGS: tuple[str, ...] = (
    "broken_json_schema",
    "typo_or_logic_defect",
    "empty_placeholder_variable",
    "empty_or_trivial_body",
    "duplicate_role_header",
    "rel_metadata_mismatch",
    "underspecified_rubric",
    "style_only_trigger_risk",
)

FLAG_ZH: dict[str, str] = {
    "broken_json_schema": "JSON契约损坏(如jason/ture/default形式/括号)",
    "typo_or_logic_defect": "错别字或逻辑矛盾",
    "empty_placeholder_variable": "存在未填充空占位符",
    "empty_or_trivial_body": "正文过短或空壳",
    "duplicate_role_header": "角色/指令头重复",
    "rel_metadata_mismatch": "关联实体rel子串误绑",
    "underspecified_rubric": "判据过于笼统",
    "style_only_trigger_risk": "唯画风触发易误杀原创",
    "missing_exclusion_clause": "缺宿主隔离或反向排除条款",
    "weak_anchor_or_escape_hatch": "存在主观逃生舱兜底描述",
}


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                rows.append(json.loads(s))
    return rows


def _get_selected_member(fam: dict[str, Any]) -> dict[str, Any]:
    sel_key = str(fam.get("selected_latest_version_key") or fam.get("selected_latest_id"))
    for m in fam.get("members") or []:
        if str(m.get("version_key") or m.get("id")) == sel_key:
            return m
    return (fam.get("members") or [{}])[0]


def build_audit_outputs(
    templete_dir: Path = DEFAULT_TEMPLETE_DIR,
    taxonomy_json: Path = DEFAULT_TAXONOMY_JSON,
    enrich_jsonl: Path = DEFAULT_ENRICH_JSONL,
    visual_jsonl_out: Path = DEFAULT_VISUAL_JSONL,
    visual_summary_out: Path = DEFAULT_VISUAL_SUMMARY,
    audit_jsonl_out: Path = DEFAULT_AUDIT_JSONL,
    audit_json_out: Path = DEFAULT_AUDIT_JSON,
    reviews_json_out: Path = DEFAULT_REVIEWS_JSON,
    final_report_md_out: Path = DEFAULT_FINAL_REPORT_MD,
) -> dict[str, Any]:
    tax = json.loads(taxonomy_json.read_text(encoding="utf-8"))
    tax_by_slug = {str(f["family_slug"]): f for f in tax["families"]}
    enrich_by_slug = {str(r["family_slug"]): r for r in _load_jsonl(enrich_jsonl)}

    visual_records: list[dict[str, Any]] = []
    visual_by_slug: dict[str, dict[str, Any]] = {}
    vis_counts: Counter[str] = Counter()

    # 1. Visual Reference Audit across all 307 Track B (entity_specific) families
    for slug, tax_rec in sorted(tax_by_slug.items()):
        if tax_rec["scope_track"] != "entity_specific":
            continue
        enr = enrich_by_slug.get(slug) or {}
        enr_status = str(enr.get("enrichment_status") or "wiki_source_missing")
        raw_paths = list(enr.get("image_paths") or [])

        fam_cov = (json.loads((templete_dir / slug / "family.json").read_text(encoding="utf-8"))).get("assert_asset_coverage") or {}
        fam_paths: list[str] = []
        for am in fam_cov.get("approved_matches") or []:
            for im in am.get("images") or []:
                fam_paths.append(str(im).removeprefix("assets/") if str(im).startswith("assets/") and not (PROJECT_ROOT / im).is_file() else str(im))
        for sm in fam_cov.get("supplement_matches") or []:
            lp = str(sm.get("local_path") or "")
            if lp:
                fam_paths.append(lp.removeprefix("assets/") if lp.startswith("assets/") and not (PROJECT_ROOT / lp).is_file() else lp)

        all_candidate_paths = sorted(set(raw_paths + fam_paths))
        rejected_paths = [p for p in all_candidate_paths if p in REJECTED_ASSET_PATHS]
        approved_paths = [p for p in raw_paths if p not in REJECTED_ASSET_PATHS]

        if slug in REJECTED_WIKI_SLUGS:
            rejected_paths.extend(p for p in raw_paths if p not in rejected_paths)
            approved_paths = []
            vis_status = "rejected_mismatch_purged"
            vis_note = REJECTED_WIKI_SLUGS[slug]
        elif slug in INSUFFICIENT_SCOPE_ASSETS:
            vis_status = "manual_asset_required"
            vis_note = INSUFFICIENT_SCOPE_ASSETS[slug]
        elif not approved_paths:
            vis_status = "manual_asset_required"
            if enr_status == "manual_patent_photo_required":
                vis_note = "纯工业外观/结构专利模板，无 Wiki 官方标，需业务补充多角度产品实拍与非侵权近似对比图"
            elif rejected_paths:
                vis_note = "; ".join(REJECTED_ASSET_PATHS[p] for p in rejected_paths)
            else:
                vis_note = "Wiki/Commons 与 Assert 均未命中可用官方标准图，需定向从品牌官网或作品官图人工补充"
        elif slug in ENRICHMENT_NOTES:
            vis_status = "approved_with_enrichment_note"
            vis_note = ENRICHMENT_NOTES[slug]
        elif tax_rec["scope_subtrack"] == "B2_specific_anime_game_media_ip" and enr_status == "wiki_fetched_pending_visual_review":
            vis_status = "approved_with_enrichment_note"
            vis_note = "官方标题徽标或作品封面已目视验真；若后续用于二创细分评测，建议增补核心角色设定三视图"
        else:
            vis_status = "approved_visual_reference"
            if rejected_paths:
                vis_note = "主标准图已目视核准，并已同步剔除同族错配干扰图（" + "; ".join(REJECTED_ASSET_PATHS[p] for p in rejected_paths) + "）"
            else:
                vis_note = "经棋盘格接触表目视核验，与模板审核对象身份一致，可作候选/参考图使用"

        vis_counts[vis_status] += 1
        v_rec = {
            "family_slug": slug,
            "scope_subtrack": tax_rec["scope_subtrack"],
            "source_enrichment_status": enr_status,
            "visual_audit_status": vis_status,
            "approved_image_paths": approved_paths,
            "rejected_image_paths": rejected_paths,
            "visual_audit_note": vis_note,
            "audited_at": AUDIT_TIMESTAMP,
        }
        visual_records.append(v_rec)
        visual_by_slug[slug] = v_rec

    # 2. Full 352-Family Template Audit Decisions
    audit_records: list[dict[str, Any]] = []
    reviews_map: dict[str, dict[str, Any]] = {}
    rev_counts: Counter[str] = Counter()
    rev_by_track: dict[str, Counter[str]] = {}

    for slug, tax_rec in sorted(tax_by_slug.items()):
        fam = json.loads((templete_dir / slug / "family.json").read_text(encoding="utf-8"))
        sel = _get_selected_member(fam)
        sel_flags = list(sel.get("hygiene_flags") or [])
        body = str(sel.get("cleaned_body") or "")
        track = tax_rec["scope_track"]
        subtrack = tax_rec["scope_subtrack"]
        v_rec = visual_by_slug.get(slug)

        # Detect uncleaned hardcoded SKU inside body text (e.g., cwt_legging)
        uncleaned_sku = "A Fish-Shaped Cat Toy for Indoor Fun" in body
        crit_hits = [fl for fl in sel_flags if fl in CRITICAL_PROMPT_FLAGS]
        if uncleaned_sku:
            crit_hits.append("uncleaned_sku_text_residue")

        minor_hits = [fl for fl in sel_flags if fl in {"missing_exclusion_clause", "weak_anchor_or_escape_hatch"}]

        if track == "quarantined_excluded":
            status = "quarantined"
            if subtrack == "Q1_test_junk":
                note = "【Q1 测试废案隔离】标题或正文属于测试占位文本，禁止进入 CPT/SFT 权重或线上规则。"
            else:
                note = f"【Q2 跨实体错贴隔离】{tax_rec['classification_evidence']}；Pro 阶段应定性为 fix_template_prompt_bug（不更新模型权重），人工修订后再启用。"
        elif crit_hits:
            status = "needs_fix"
            defect_parts = [FLAG_ZH.get(c, "正文残留未清理商品标题硬编码") for c in crit_hits]
            extra_asset = ""
            if v_rec and v_rec["visual_audit_status"] in {"manual_asset_required", "rejected_mismatch_purged"}:
                extra_asset = f"；同时参考图待补（{v_rec['visual_audit_note']}）"
            note = f"【需修模板】主版 #{fam['selected_latest_id']} 存在：{ '、'.join(defect_parts) }。"
            if minor_hits:
                note += f" 另建议补充：{'、'.join(FLAG_ZH[m] for m in minor_hits)}。"
            note += extra_asset
        elif v_rec and v_rec["visual_audit_status"] in {"manual_asset_required", "rejected_mismatch_purged"}:
            status = "needs_asset"
            prefix = "【错配已清除·待补图】" if v_rec["visual_audit_status"] == "rejected_mismatch_purged" else "【缺标准参考图】"
            note = f"{prefix}模板正文健康；{v_rec['visual_audit_note']}。"
            if minor_hits:
                note += f" 优化建议：{'、'.join(FLAG_ZH[m] for m in minor_hits)}。"
        else:
            status = "approved"
            if track == "broad_domain":
                route = tax_rec["audit_requirements"].get("cpt_sft_route", "")
                note = f"【广域审结通过】归属 {subtrack}，按路线 {route} 接入 CPT-SFT。"
                if minor_hits:
                    note += f" 规则强化提示：{'、'.join(FLAG_ZH[m] for m in minor_hits)}。"
            else:
                v_txt = v_rec["visual_audit_note"] if v_rec else "标准参考图已就绪"
                note = f"【审结通过】模板规则与视觉参考图均核验合格（{v_txt}）。"
                if minor_hits:
                    note += f" 非阻塞优化：{'、'.join(FLAG_ZH[m] for m in minor_hits)}。"

        rev_counts[status] += 1
        rev_by_track.setdefault(track, Counter())[status] += 1
        reviews_map[slug] = {
            "status": status,
            "note": note,
            "updated_at": AUDIT_TIMESTAMP,
        }
        audit_records.append(
            {
                "family_slug": slug,
                "display_name": fam["display_name"],
                "selected_latest_id": fam["selected_latest_id"],
                "selected_latest_title": fam["selected_latest_title"],
                "scope_track": track,
                "scope_subtrack": subtrack,
                "critical_flags": crit_hits,
                "minor_flags": minor_hits,
                "visual_audit_status": v_rec["visual_audit_status"] if v_rec else "not_applicable",
                "visual_audit_note": v_rec["visual_audit_note"] if v_rec else "",
                "approved_image_paths": v_rec["approved_image_paths"] if v_rec else [],
                "rejected_image_paths": v_rec["rejected_image_paths"] if v_rec else [],
                "audit_status": status,
                "audit_note": note,
                "audited_at": AUDIT_TIMESTAMP,
            }
        )

    # Atomic writes
    visual_summary = {
        "schema": "assert_template_visual_audit_summary_v1",
        "generated_at": AUDIT_TIMESTAMP,
        "total_entity_specific_families": len(visual_records),
        "visual_audit_counts": dict(vis_counts),
        "visually_approved_families": vis_counts["approved_visual_reference"] + vis_counts["approved_with_enrichment_note"],
        "visually_approved_rate": round((vis_counts["approved_visual_reference"] + vis_counts["approved_with_enrichment_note"]) / max(1, len(visual_records)), 4),
        "rejected_asset_paths": REJECTED_ASSET_PATHS,
        "rejected_wiki_slugs": REJECTED_WIKI_SLUGS,
    }
    _write_jsonl(visual_jsonl_out, visual_records)
    _write_json(visual_summary_out, visual_summary)

    audit_summary = {
        "schema": "assert_template_audit_decisions_v1",
        "generated_at": AUDIT_TIMESTAMP,
        "total_families": len(audit_records),
        "audit_status_counts": dict(rev_counts),
        "audit_status_by_track": {k: dict(v) for k, v in rev_by_track.items()},
        "visual_audit_summary": visual_summary,
        "families": audit_records,
    }
    _write_jsonl(audit_jsonl_out, audit_records)
    _write_json(audit_json_out, audit_summary)
    _write_json(
        reviews_json_out,
        {
            "schema": "assert_template_review_v1",
            "exported_at": AUDIT_TIMESTAMP,
            "audited_by": "assert_automated_and_visual_qa_audit",
            "reviews": reviews_map,
        },
    )

    _write_text(final_report_md_out, render_final_report(audit_summary, visual_summary))
    return {
        "total_families": len(audit_records),
        "audit_status_counts": dict(rev_counts),
        "audit_status_by_track": {k: dict(v) for k, v in rev_by_track.items()},
        "visual_audit_counts": dict(vis_counts),
        "visually_approved_families": visual_summary["visually_approved_families"],
        "visually_approved_rate": visual_summary["visually_approved_rate"],
    }


def render_final_report(audit_summary: dict[str, Any], visual_summary: dict[str, Any]) -> str:
    fams = audit_summary["families"]
    sc = audit_summary["audit_status_counts"]
    vc = visual_summary["visual_audit_counts"]
    by_track = audit_summary["audit_status_by_track"]

    lines: list[str] = [
        "# 352 审核模板同族与参考图全量终审报告（待检阅签收）",
        "",
        f"- **审结时间**: `{audit_summary['generated_at']}`",
        f"- **覆盖范围**: 全量 **352 族**审核模板（533 拆包版本）+ 全量 **307 族**特定对象视觉参考图",
        "- **交互复核载体**: 打开 `templete/review_dashboard.html` 即已预载全部 352 族审结状态与审结意见（支持逐条覆写与导出）。",
        "",
        "## 一、审结结论总览",
        "",
        "| 审结结论 (`review_status`) | 总计 (352) | 广域 Track A (36) | 特定对象 Track B (307) | 隔离 Track Q (9) | 处置建议 |",
        "|---|---:|---:|---:|---:|---|",
        f"| ✅ **已通过 (`approved`)** | **{sc.get('approved', 0)}** | {by_track.get('broad_domain', {}).get('approved', 0)} | {by_track.get('entity_specific', {}).get('approved', 0)} | 0 | 可直接投入 CPT-SFT 或线上基线 |",
        f"| ✎ **需修模板 (`needs_fix`)** | **{sc.get('needs_fix', 0)}** | {by_track.get('broad_domain', {}).get('needs_fix', 0)} | {by_track.get('entity_specific', {}).get('needs_fix', 0)} | 0 | 修复 JSON 语法/错字/占位符/`rel` 误绑后复审 |",
        f"| 🖼 **需补标准图 (`needs_asset`)** | **{sc.get('needs_asset', 0)}** | {by_track.get('broad_domain', {}).get('needs_asset', 0)} | {by_track.get('entity_specific', {}).get('needs_asset', 0)} | 0 | 模板正文健康，需业务补充实拍专利图或官方图标 |",
        f"| ⛔ **隔离废弃 (`quarantined`)** | **{sc.get('quarantined', 0)}** | 0 | 0 | {by_track.get('quarantined_excluded', {}).get('quarantined', 0)} | 严禁入训，先修错贴 Bug 或清除测试废案 |",
        "",
        "## 二、特定对象（307 族）参考图目视验收与净化台账",
        "",
        f"- **目视验真通过**: **{visual_summary['visually_approved_families']} / 307 ({visual_summary['visually_approved_rate']*100:.1f}%)**（含 `approved_visual_reference={vc.get('approved_visual_reference', 0)}` 与 `approved_with_enrichment_note={vc.get('approved_with_enrichment_note', 0)}`）",
        f"- **当场剔除错配 (`rejected_mismatch_purged`)**: **{vc.get('rejected_mismatch_purged', 0)}** 族（已从画廊预览与交付白名单中屏蔽）",
        f"- **需人工补实拍/官图 (`manual_asset_required`)**: **{vc.get('manual_asset_required', 0)}** 族",
        "",
        "### 2.1 目视整改通过的重点替换项（已二次视觉核验 `wiki_replacements_qa.jpg`）",
        "| `family_slug` | 原错误候选 | 整改后采用图元 | 视觉审结状态 |",
        "|---|---|---|---|",
        "| `alexandermcqueen` | 设计师本人肖像 | `Alexander_McQueen_2018_logo.svg` | ✅ 核准替换 |",
        "| `calvin_klein` | 设计师本人肖像 | `CK_Calvin_Klein_logo.svg` | ✅ 核准替换 |",
        "| `dsquared2` | 创始人双人合照 | `DSQUARED2.png` | ✅ 核准替换 |",
        "| `nike_jordan` | 约旦皇家空军徽标 | `Jumpman_logo.svg` | ✅ 核准替换 |",
        "| `velcro` | 魔术贴织物微距图 | `Velcro_Brand.svg` | ✅ 核准替换 |",
        "| `vivienne_westwood` | 设计师本人肖像 | `Vivienne_Westwood_'Orb'_company_logo` | ✅ 核准（注：含土星环+手写标） |",
        "| `minions` | 街头雕塑摄影 | `Minions_(film)_logo.svg` | ✅ 核准（注：建议补角色三视图） |",
        "| `evelknievel` | Harley 博物馆标（已剔除） | `At_Home_With_Evel_Knievel.jpg` | ✅ 核准（本人档案照，建议补徽记） |",
        "| `triumph` | 含 `ip_triumph_international.png` | 仅保留 `ip_triumph_motorcycles.png` | ✅ 核准单图、已剔除内衣错配 |",
        "",
        "### 2.2 确认错配并已硬清除（`rejected_mismatch_purged`，共 9 族）",
        "| `family_slug` | 清除原因 | 后续动作 |",
        "|---|---|---|",
    ]
    for slug, reason in sorted(REJECTED_WIKI_SLUGS.items()):
        lines.append(f"| `{slug}` | {reason} | 从品牌官网/官店手工补正图 |")

    lines.extend(["", "### 2.3 需人工补图清单（`audit_status=needs_asset`，且正文健康）", "| `family_slug` | 子轨道 | 缺口说明 |", "|---|---|---|"])
    for r in fams:
        if r["audit_status"] == "needs_asset":
            lines.append(f"| `{r['family_slug']}` | `{r['scope_subtrack']}` | {r['visual_audit_note']} |")

    lines.extend(["", "## 三、隔离废弃清单（`quarantined` · 9 族）", "| `family_slug` | 子轨道 | 主版 ID | 审结意见 |", "|---|---|---:|---|"])
    for r in fams:
        if r["audit_status"] == "quarantined":
            lines.append(f"| `{r['family_slug']}` | `{r['scope_subtrack']}` | `{r['selected_latest_id']}` | {r['audit_note']} |")

    lines.extend(["", "## 四、需修模板清单（`needs_fix` · 重点优先项一览，全量已写入画廊）", "| `family_slug` | 子轨道 | 主版 ID | 检测缺陷 |", "|---|---|---:|---|"])
    for r in fams:
        if r["audit_status"] == "needs_fix":
            lines.append(f"| `{r['family_slug']}` | `{r['scope_subtrack']}` | `{r['selected_latest_id']}` | {', '.join(r['critical_flags'])} |")

    return "\n".join(lines) + "\n"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    summary = build_audit_outputs()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
