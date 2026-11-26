#!/usr/bin/env python3
"""Objective MECE template taxonomy & audit-requirement extractor for Assert/templete.

Classifies all 352 template families along two orthogonal axes:
  Axis 1 — Rights-holder cardinality & generalization scope:
    - broad_domain (Track A: open-set, vertical multi-entity, pairwise comparison, or auxiliary workflow)
    - entity_specific (Track B: single brand, anime/game IP, sport/university, celebrity/artist, or design patent)
    - quarantined_excluded (Track Q: test junk or cross-entity paste bugs)
  Axis 2 — Structured audit requirements extracted from full template text (no truncation):
    - input_modalities & modality_decision_policy
    - visual_cues_required
    - boundary_and_exclusion_mechanisms
    - output_contract
    - asset_enrichment_requirement & CPT-SFT routing track

Outputs:
  - manifests/template_taxonomy_requirements.json
  - manifests/template_taxonomy_requirements.jsonl
  - templete/taxonomy_and_requirements.md
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLETE_DIR = PROJECT_ROOT / "templete"
DEFAULT_OUT_JSON = PROJECT_ROOT / "manifests" / "template_taxonomy_requirements.json"
DEFAULT_OUT_JSONL = PROJECT_ROOT / "manifests" / "template_taxonomy_requirements.jsonl"
DEFAULT_OUT_MD = PROJECT_ROOT / "templete" / "taxonomy_and_requirements.md"

# ---------------------------------------------------------------------------
# MECE Track Definitions (verified against full cleaned bodies of 352 families)
# ---------------------------------------------------------------------------

A1_OPEN_SET_CROSS_DOMAIN: set[str] = {
    "brand_gemini_general",
    "brand_goods_consistent_multi_img",
    "cluster_gemini",
    "general_ip_model_nxy",
    "general_rihe",
    "infringement_detection",
    "logo_similar_judge",
    "risk_evaluation",
    "riskdata_iplogo_brand_gemini",
    "tro_anly",
}

A2_VERTICAL_OPEN_SET_OR_MULTI_ENTITY: set[str] = {
    "artist",
    "band_music_general",
    "cars_automotive_general",
    "counterfeit_jerseys",
    "counterfeit_watch",
    "hemier_league",
    "household",
    "infringementcards",
    "kpop",
    "merchtraffic",
    "nin1_game_console",
    "spainish_celebrity",
    "sport_star",
    "sports_ball_general",
}

A3_PAIRWISE_VISUAL_MECHANISM: set[str] = {
    "twizler",
}

# Track B subtrack sets (for entity_specific active_ip families)
B5_SPECIFIC_DESIGN_PATENT_PRODUCT: set[str] = {
    "ajsnifty",
    "apple",  # IP_APPLE_WATCHBAND: watch band shapes & designs
    "crocs_charms",
    "cucu",
    "cwt_legging",
    "doubleendedhandtool",
    "genies_perfume_atomizer",
    "jiaxiangye",
    "parkerbabyco",
    "pickulsgizmo",
    "purple_innovation",
    "rabanne_bag",
    "shingbright",
    "tangle",
    "ugg",  # IP_ugg_patent
    "wondermachines",
    "yanding",
    "zipit",
}

B3_SPECIFIC_SPORTS_UNIVERSITY: set[str] = {
    "alabama",
    "alemannia_aachen",
    "all_blacks",
    "apf",
    "arizona_university",
    "cbf",
    "duke_university",
    "florida",
    "hendrickmotorsports",
    "libertyuniversity",
    "maryland",
    "michigan_state",
    "nba",
    "nebraska",
    "nhl",
    "ohio",
    "oklahoma_university",
    "olympic",
    "oregon",
    "rbfa",
    "rfef",
    "sharks_rugby",
    "ucl_wenzi",
    "uga",
    "university_of_michigan",
    "university_of_utah",
    "universityofkentucky",
    "wku",
    "wwe_wrestle",
}

B4_SPECIFIC_CELEBRITY_BAND_ARTIST: set[str] = {
    "abba",
    "acdcllm",
    "bensonboone",
    "beyonce",
    "courtneymorgenstern",
    "elvis",
    "evelknievel",
    "glassangelofficial",
    "greenday",
    "gunsnroses",
    "higuchi_yuko",
    "jenny_urquhart",
    "juicewrld",
    "junjiito",
    "ledzeppelin",
    "lindseyferrell",
    "lionel_messi",
    "maradona",
    "marilyn_monroe",
    "metallica",
    "michael_jackson",
    "muhammad_ali",
    "neymar",
    "nirvana",
    "novak_djokovic",
    "one_direction",
    "pitbull",
    "postyaustin",
    "ratt",
    "rundmc",
    "slayer",
    "taylorswift",
    "twentyonepilots",
    "yamal",
}

B2_SPECIFIC_ANIME_GAME_MEDIA_IP: set[str] = {
    "adventuretime",
    "amongus",
    "angry_birds",
    "annabelle",
    "anpanman",
    "atari",
    "attack_on_titan",
    "badcutebunny",
    "berserk",
    "bleach",
    "brawl_stars",
    "chainsawman",
    "clash_royale",
    "cobra",
    "cookie_run",
    "coraline",
    "cowboybebop",
    "crayonshinchan",
    "dandys_world",
    "dav_pilkey_dogman",
    "dc_comics",
    "demon_slayer",
    "disney",
    "dragonball",
    "dune",
    "et",
    "fallout",
    "forza",
    "friends",
    "godzilla",
    "harrypotter",
    "hatsune_miku",
    "hotstuff",
    "itmovie",
    "jujutsukaisen",
    "kirby",
    "legorelated",
    "lupinthethird",
    "marvel",
    "megaman",
    "meitanteikonan",
    "miffyrabbit",
    "minions",
    "monchhichi",
    "money_heist_la_casa_de_papel",
    "monopoly",
    "monsterhigh",
    "mr_men_little_miss",
    "my_dress",
    "my_hero_academia",
    "naruto",
    "ohayou_spank",
    "one_piece",
    "pandorobo",
    "paw_patrol",
    "peanuts",
    "pikmin",
    "pinkpanther",
    "pokemon",
    "rezero",
    "rickandmorty",
    "rilakkuma",
    "rockybalboa",
    "sandmaennchen",
    "scoobydoo",
    "sesame_street",
    "sevendeadlysins",
    "slamdunk",
    "spirit",
    "spongebobsquarepants",
    "spotit",
    "squishmallows",
    "startrek",
    "stealabrainrot",
    "strawberryshortcake",
    "streetfighter",
    "super_mario",
    "thebadguys",
    "thesecretlifeofpets",
    "thesimpsonver2",
    "thomasandfriends",
    "tokyoghoul",
    "tomandjerry",
    "trolls",
    "underdog",
    "warhammer",
    "zelda",
}

TRACK_LABELS: dict[str, str] = {
    "broad_domain": "广域识别模板 (Track A)",
    "entity_specific": "特定产品/IP/品牌识别模板 (Track B)",
    "quarantined_excluded": "隔离异常模板 (Track Q)",
}

SUBTRACK_LABELS: dict[str, str] = {
    "A1_open_set_cross_domain_ip": "A1 跨域开放集商标/IP/宿主隔离识别",
    "A2_vertical_open_set_or_multi_entity": "A2 垂直品类/多实体列表联合审核",
    "A3_pairwise_visual_mechanism": "A3 双图对比防二创/规避机制",
    "A4_auxiliary_governance_workflow": "A4 非视觉商品辅助治理与法务合规流",
    "B1_specific_brand_trademark": "B1 特定商业品牌/商标识别",
    "B2_specific_anime_game_media_ip": "B2 特定动漫/游戏/影视/玩具IP识别",
    "B3_specific_sports_university": "B3 特定体育联盟/球队/高校IP识别",
    "B4_specific_celebrity_band_artist": "B4 特定名人/乐队/球星/艺术家识别",
    "B5_specific_design_patent_product": "B5 特定产品外观专利/结构装潢识别",
    "Q1_test_junk": "Q1 测试占位/废案隔离",
    "Q2_cross_entity_paste_bug": "Q2 跨实体错贴 Bug 隔离",
}

VISUAL_CUE_LABELS: dict[str, str] = {
    "logo_wordmark": "品牌文字标/图形Logo拓扑",
    "character_mascot_likeness": "角色/吉祥物外观与特征组合",
    "derivative_fanart_style": "二创/Q版/重绘与风格边界判定",
    "3d_product_geometry_patent": "产品三维结构/功能件/专利几何",
    "trade_dress_pattern_packaging": "老花暗纹/拼接装潢/包装设计",
    "jersey_crest_colors": "队徽/球衣配色/号码与奖杯标识",
    "human_portrait_celebrity": "真人肖像/乐队舞台/公众人物特征",
    "ocr_deformed_or_obfuscated_text": "形变/遮挡/涂抹/谐音拼写OCR",
    "watermark_or_crop": "水印/小区域局部裁切检测",
    "document_or_webpage_screenshot": "凭证/法律文书/网页截图取证",
}

BOUNDARY_MECHANISM_LABELS: dict[str, str] = {
    "subject_host_isolation": "售卖主体锁定与宿主/背景隔离",
    "material_consistency_check": "图文载体/材质一致性核验",
    "compatibility_exemption": "适配/兼容词豁免（如适用于/for）",
    "common_word_disambiguation": "日常词汇/通用图案消歧",
    "generic_style_exclusion": "纯画风/通用元素排除（防误杀原创）",
    "reverse_elimination_fast_reject": "反向剔除快速免审机制",
    "boolean_compound_logic": "多条款布尔组合求值 (AND/OR)",
    "conservative_insufficient_evidence_abstain": "证据不足保守拒判（不强猜）",
}


def classify_family(fam: dict[str, Any]) -> dict[str, Any]:
    """Deterministically assigns MECE track, subtrack, cardinality, and evidence."""
    slug = str(fam["family_slug"])
    sel = _get_selected_member(fam)
    disp = str(sel.get("disposition") or "active_ip")

    if disp == "quarantine_test_junk":
        return {
            "scope_track": "quarantined_excluded",
            "scope_subtrack": "Q1_test_junk",
            "rights_holder_cardinality": "excluded",
            "classification_evidence": "disposition=quarantine_test_junk（测试占位或垃圾文本，禁止进入训练权重）",
        }
    if disp == "quarantine_paste_bug":
        return {
            "scope_track": "quarantined_excluded",
            "scope_subtrack": "Q2_cross_entity_paste_bug",
            "rights_holder_cardinality": "excluded",
            "classification_evidence": "disposition=quarantine_paste_bug（标题与正文权利实体矛盾，须人工修复模板后才能使用）",
        }
    if disp == "route_auxiliary_non_ip" or slug.startswith("aux_"):
        return {
            "scope_track": "broad_domain",
            "scope_subtrack": "A4_auxiliary_governance_workflow",
            "rights_holder_cardinality": "workflow",
            "classification_evidence": "非单品视觉IP模板：承担凭证核验/TRO法务节点/黑词/品牌关联/反馈优化/反爬截图判定",
        }
    if slug in A1_OPEN_SET_CROSS_DOMAIN:
        return {
            "scope_track": "broad_domain",
            "scope_subtrack": "A1_open_set_cross_domain_ip",
            "rights_holder_cardinality": "open_set",
            "classification_evidence": "开放集/通用IP审核模板：不绑定固定单一权利方，依赖动态列表/全图识别/宿主隔离/图搜链接归因",
        }
    if slug in A2_VERTICAL_OPEN_SET_OR_MULTI_ENTITY:
        return {
            "scope_track": "broad_domain",
            "scope_subtrack": "A2_vertical_open_set_or_multi_entity",
            "rights_holder_cardinality": "bounded_multi",
            "classification_evidence": "垂直领域广域/多实体联合审核模板：同时覆盖多品牌/多明星/多球队/多艺术家或整个高危品类边界",
        }
    if slug in A3_PAIRWISE_VISUAL_MECHANISM:
        return {
            "scope_track": "broad_domain",
            "scope_subtrack": "A3_pairwise_visual_mechanism",
            "rights_holder_cardinality": "open_set",
            "classification_evidence": "双图对比（敏感母本图 vs 待审风险图）视觉查重与AI二创规避机制模板",
        }

    # Remaining active_ip families are strictly entity_specific (Track B)
    if slug in B5_SPECIFIC_DESIGN_PATENT_PRODUCT:
        return {
            "scope_track": "entity_specific",
            "scope_subtrack": "B5_specific_design_patent_product",
            "rights_holder_cardinality": "1",
            "classification_evidence": "定向识别特定专利产品结构、功能造型或特定SKU视觉装潢",
        }
    if slug in B3_SPECIFIC_SPORTS_UNIVERSITY:
        return {
            "scope_track": "entity_specific",
            "scope_subtrack": "B3_specific_sports_university",
            "rights_holder_cardinality": "1",
            "classification_evidence": "定向识别单个体育联盟、单支俱乐部/国家队或单所高校/大学系统IP",
        }
    if slug in B4_SPECIFIC_CELEBRITY_BAND_ARTIST:
        return {
            "scope_track": "entity_specific",
            "scope_subtrack": "B4_specific_celebrity_band_artist",
            "rights_holder_cardinality": "1",
            "classification_evidence": "定向识别单一指定明星、乐队、运动员或独立艺术家肖像/署名权",
        }
    if slug in B2_SPECIFIC_ANIME_GAME_MEDIA_IP:
        return {
            "scope_track": "entity_specific",
            "scope_subtrack": "B2_specific_anime_game_media_ip",
            "rights_holder_cardinality": "1",
            "classification_evidence": "定向识别单一动漫、游戏、影视、绘本或玩具角色IP家族",
        }
    return {
        "scope_track": "entity_specific",
        "scope_subtrack": "B1_specific_brand_trademark",
        "rights_holder_cardinality": "1",
        "classification_evidence": "定向识别单一特定商业品牌、商标文字或官方图形徽标",
    }


def _get_selected_member(fam: dict[str, Any]) -> dict[str, Any]:
    sel_key = str(fam.get("selected_latest_version_key") or fam.get("selected_latest_id"))
    for m in fam.get("members") or []:
        if str(m.get("version_key") or m.get("id")) == sel_key:
            return m
    return (fam.get("members") or [{}])[0]


def _extract_output_contract(body: str) -> dict[str, Any]:
    has_json = bool(re.search(r'(json|"res"|\\"res\\")', body, re.I))
    has_tf = bool(re.search(r'(true\s*或\s*false|true/false|TRUE\s*或\s*FALSE|\btrue\b.*\bfalse\b)', body, re.I))
    has_yn = bool(re.search(r'(输出\s*[“"\[]?是|判断为是|答案为\s*“是”)', body))
    if "JudgmentReport" in body or "judgement" in body.lower():
        fmt = "legal_structured_json"
    elif has_json:
        fmt = "json_res_reason"
    elif has_tf:
        fmt = "boolean_true_false_with_reason"
    elif has_yn:
        fmt = "zh_yes_no_with_reason"
    else:
        fmt = "freeform_or_checklist"

    fields: list[str] = []
    for fld in ("res", "reason", "brand", "ip_names", "ip_content", "ip_products", "risk_level", "category", "entities"):
        if re.search(rf'["\']?{fld}["\']?', body):
            fields.append(fld)
    return {"format": fmt, "fields": fields}


def extract_audit_requirements(fam: dict[str, Any], tax: dict[str, Any]) -> dict[str, Any]:
    """Extracts structured audit requirements across full cleaned template text."""
    sel = _get_selected_member(fam)
    # Use selected latest version plus any parallel sub-scope members so multi-scope families do not lose constraints
    bodies = [str(sel.get("cleaned_body") or "")]
    if fam.get("parallel_sub_scopes"):
        for m in fam.get("members") or []:
            if m is not sel and str(m.get("disposition")) == "active_ip":
                bodies.append(str(m.get("cleaned_body") or ""))
    full_text = "\n".join(b for b in bodies if b)
    slug = str(fam["family_slug"])
    subtrack = tax["scope_subtrack"]

    # 1. Input modalities
    requires_image = not bool(
        slug in {"aux_black_word_risk_reviewer", "aux_brand_alliance", "aux_brand_collab", "aux_identifying_fake_brands", "aux_logos_review_verification_text", "aux_tro_brandname_alignment", "aux_tro_brandname_rec", "aux_tro_warning_case_process"}
    )
    requires_text = bool(
        re.search(r"(#GOODS_TEXT_INFO#|#GOODS_CONTEXT#|#GOODS_PROPERTIES#|#GOODS_SPEC#|#BRAND_LIST#|商品标题|商品名称|商品名|文本信息|案件进展|输入品牌)", full_text, re.I)
    ) or not requires_image
    requires_multi_image = bool(
        re.search(r"(商品主图.*轮播|轮播图|sku图|多张图片|两张图片|敏感图片.*风险图片|第\d+到第\d+张|多规格组合图|资质文件图片)", full_text, re.I)
    )
    requires_external_search_links = bool(
        re.search(r"(谷歌图搜|网站链接列表|允许联网检索|联网检索)", full_text, re.I)
    )

    # 2. Modality decision policy
    if not requires_image:
        modality_policy = "text_primary_or_only"
    elif subtrack == "A3_pairwise_visual_mechanism":
        modality_policy = "pairwise_image_comparison"
    elif re.search(r"(绝对不要.*参考.*标题|仅基于输入图片|只有商品文本.*未出现.*false|标题不可信|图片优先|未出现.*直接.*false)", full_text, re.I):
        modality_policy = "image_overrides_text"
    elif not requires_text:
        modality_policy = "image_only"
    else:
        modality_policy = "image_and_text_joint"

    # 3. Visual cues required
    visual_cues: list[str] = []
    if requires_image:
        if subtrack in {"B1_specific_brand_trademark", "A1_open_set_cross_domain_ip", "A2_vertical_open_set_or_multi_entity"} or re.search(r"(logo|商标|徽标|字样|wordmark|字母)", full_text, re.I):
            visual_cues.append("logo_wordmark")
        if subtrack in {"B2_specific_anime_game_media_ip"} or re.search(r"(角色|卡通|人物形象|吉祥物|精灵|动漫|动画|游戏)", full_text, re.I):
            visual_cues.append("character_mascot_likeness")
        if fam.get("supports_derivative") or re.search(r"(二创|同人|Q版|二次创作|核心角色档案)", full_text, re.I):
            visual_cues.append("derivative_fanart_style")
        if subtrack == "B5_specific_design_patent_product" or re.search(r"(外观专利|结构特征|球窝|悬臂|灯罩|表带|锥体|网格结构|拉链带|缝线|五金)", full_text, re.I):
            visual_cues.append("3d_product_geometry_patent")
        if re.search(r"(老花|monogram|花纹|格子|格纹|斜纹|包装|配色方案|图案布局|装潢|trade\s*dress)", full_text, re.I):
            visual_cues.append("trade_dress_pattern_packaging")
        if subtrack == "B3_specific_sports_university" or slug in {"counterfeit_jerseys", "hemier_league", "sports_ball_general"}:
            visual_cues.append("jersey_crest_colors")
        if subtrack == "B4_specific_celebrity_band_artist" or slug in {"spainish_celebrity", "sport_star", "band_music_general", "wwe_wrestle"} or re.search(r"(肖像|照片|真人|人脸|乐队|歌手|明星|艺术家)", full_text, re.I):
            visual_cues.append("human_portrait_celebrity")
        if re.search(r"(ocr|拼写|变形|遮挡|倒写|涂抹|打码|形似|变体字母|模糊)", full_text, re.I):
            visual_cues.append("ocr_deformed_or_obfuscated_text")
        if re.search(r"(watermark|水印|crop|局部裁切)", full_text, re.I):
            visual_cues.append("watermark_or_crop")
        if slug in {"aux_invoices", "aux_crawlplatform_anti_risk"}:
            visual_cues.append("document_or_webpage_screenshot")
    else:
        visual_cues.append("document_or_webpage_screenshot")
    visual_cues = sorted(set(visual_cues))

    # 4. Boundary & exclusion mechanisms
    boundaries: list[str] = []
    if re.search(r"(售卖主体|商品主体|宿主|背景|透出|展示道具|模特.*身上|不出现在背景)", full_text, re.I):
        boundaries.append("subject_host_isolation")
    if re.search(r"(材质|纹理|刺绣|印刷|丝印|浮雕|压花|无缝衔接)", full_text, re.I):
        boundaries.append("material_consistency_check")
    if re.search(r"(适用|适配|兼容|suitable\s+for|compatible\s+with|for\s+[a-z])", full_text, re.I):
        boundaries.append("compatibility_exemption")
    if re.search(r"(单独出现|唯一出现|普通|日常词汇|常见词|真实含义|大小写|单词里|不作为商标)", full_text, re.I):
        boundaries.append("common_word_disambiguation")
    if re.search(r"(纯画风|仅凭画风|通用元素|不要求|不属于.*元素|风格相似.*不)", full_text, re.I):
        boundaries.append("generic_style_exclusion")
    if re.search(r"(反向剔除|快速免审|排除标准|直接回答\s*false|可直接判定为\s*false|一旦满足.*false)", full_text, re.I):
        boundaries.append("reverse_elimination_fast_reject")
    if re.search(r"(规则\s*\d+|条件\s*\d+|全部条件|任意一条|当且仅当|Q\d+=true)", full_text, re.I):
        boundaries.append("boolean_compound_logic")
    if re.search(r"(不确定|无法判断|模糊不清|证据不足|宁缺毋滥|不提取)", full_text, re.I):
        boundaries.append("conservative_insufficient_evidence_abstain")
    boundaries = sorted(set(boundaries))

    # 5. Asset enrichment requirement & CPT-SFT routing
    cov_status = (fam.get("assert_asset_coverage") or {}).get("coverage_status", "no_assert_match")
    if tax["scope_track"] == "quarantined_excluded":
        enrichment = {
            "needs_reference_image": False,
            "required_asset_types": [],
            "enrichment_strategy": "quarantine_do_not_enrich",
        }
        cpt_sft_route = "quarantine_fix_template_prompt_bug"
    elif subtrack == "A4_auxiliary_governance_workflow":
        enrichment = {
            "needs_reference_image": slug in {"aux_invoices", "aux_crawlplatform_anti_risk"},
            "required_asset_types": ["document_or_webpage_samples"] if slug in {"aux_invoices", "aux_crawlplatform_anti_risk"} else ["structured_legal_text_cases"],
            "enrichment_strategy": "auxiliary_workflow_sft_only",
        }
        cpt_sft_route = "A4_doc_screenshot_sft" if slug in {"aux_invoices", "aux_crawlplatform_anti_risk"} else "A4_text_legal_sft_budgeted"
    elif subtrack in {"A1_open_set_cross_domain_ip", "A2_vertical_open_set_or_multi_entity", "A3_pairwise_visual_mechanism"}:
        enrichment = {
            "needs_reference_image": True,
            "required_asset_types": [
                "multi_brand_crest_anchor_pack",
                "host_vs_subject_contrast_pairs",
                "negative_distractor_and_derivative_pairs",
            ],
            "enrichment_strategy": "broad_domain_cpt_plus_rule_sft_curriculum",
        }
        cpt_sft_route = f"{subtrack[:2]}_broad_curriculum"
    else:
        if subtrack == "B5_specific_design_patent_product":
            req_types = ["multi_angle_product_patent_photos", "structural_detail_crops", "non_infringing_lookalike_negatives"]
            strat = "patent_structure_photo_or_wiki_if_branded"
        elif subtrack == "B2_specific_anime_game_media_ip":
            req_types = ["official_character_sheet_or_poster", "logo_wordmark", "fanart_vs_oc_contrast"]
            strat = "wiki_character_logo_plus_v2_derivative_pairs"
        elif subtrack == "B3_specific_sports_university":
            req_types = ["official_crest_or_seal_svg_png", "wordmark_and_mascot", "confusable_peer_teams"]
            strat = "ncaa_sports_supplement_plus_wiki_seal"
        elif subtrack == "B4_specific_celebrity_band_artist":
            req_types = ["portrait_or_stage_reference", "band_logo_or_signature", "lookalike_or_style_contrast"]
            strat = "wiki_portrait_or_band_logo"
        else:
            req_types = ["official_logo_wordmark_svg_png", "monogram_or_packaging_ref", "ocr_deformation_and_host_negatives"]
            strat = "assert_supplement_plus_wiki_logo"
        enrichment = {
            "needs_reference_image": True,
            "required_asset_types": req_types,
            "enrichment_strategy": strat,
            "current_assert_coverage": cov_status,
        }
        cpt_sft_route = f"{subtrack[:2]}_entity_cpt_anchor_plus_rule_sft"

    return {
        "input_modalities": {
            "requires_image": requires_image,
            "requires_text": requires_text,
            "requires_multi_image": requires_multi_image,
            "requires_external_search_links": requires_external_search_links,
        },
        "modality_decision_policy": modality_policy,
        "visual_cues_required": visual_cues,
        "boundary_and_exclusion_mechanisms": boundaries,
        "output_contract": _extract_output_contract(full_text),
        "asset_enrichment_requirement": enrichment,
        "cpt_sft_route": cpt_sft_route,
    }


def analyze_all_families(templete_dir: Path = DEFAULT_TEMPLETE_DIR) -> dict[str, Any]:
    index_data = json.loads((templete_dir / "index.json").read_text(encoding="utf-8"))
    profiles: list[dict[str, Any]] = []
    track_counts: Counter[str] = Counter()
    subtrack_counts: Counter[str] = Counter()
    policy_counts: Counter[str] = Counter()
    cue_counts: Counter[str] = Counter()
    boundary_counts: Counter[str] = Counter()
    output_fmt_counts: Counter[str] = Counter()

    for entry in index_data["families"]:
        slug = str(entry["family_slug"])
        fam = json.loads((templete_dir / slug / "family.json").read_text(encoding="utf-8"))
        sel = _get_selected_member(fam)
        tax = classify_family(fam)
        req = extract_audit_requirements(fam, tax)

        track_counts[tax["scope_track"]] += 1
        subtrack_counts[tax["scope_subtrack"]] += 1
        policy_counts[req["modality_decision_policy"]] += 1
        output_fmt_counts[req["output_contract"]["format"]] += 1
        for c in req["visual_cues_required"]:
            cue_counts[c] += 1
        for b in req["boundary_and_exclusion_mechanisms"]:
            boundary_counts[b] += 1

        profiles.append(
            {
                "family_slug": slug,
                "display_name": fam["display_name"],
                "selected_latest_id": fam["selected_latest_id"],
                "selected_latest_version_key": str(fam.get("selected_latest_version_key") or fam["selected_latest_id"]),
                "selected_latest_title": fam["selected_latest_title"],
                "member_count": fam["member_count"],
                "disposition": sel.get("disposition"),
                "current_assert_coverage": (fam.get("assert_asset_coverage") or {}).get("coverage_status"),
                "supports_derivative": bool(fam.get("supports_derivative")),
                "inter_class_risk": fam.get("inter_class_risk"),
                **tax,
                "audit_requirements": req,
            }
        )

    assert len(profiles) == 352, f"Expected 352 families, got {len(profiles)}"
    assert track_counts["broad_domain"] == 36, f"Expected 36 broad_domain, got {track_counts['broad_domain']}"
    assert track_counts["entity_specific"] == 307, f"Expected 307 entity_specific, got {track_counts['entity_specific']}"
    assert track_counts["quarantined_excluded"] == 9, f"Expected 9 quarantined_excluded, got {track_counts['quarantined_excluded']}"

    return {
        "schema": "assert_template_taxonomy_requirements_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_families": len(profiles),
        "track_counts": dict(track_counts),
        "subtrack_counts": dict(sorted(subtrack_counts.items())),
        "modality_decision_policy_counts": dict(policy_counts.most_common()),
        "visual_cue_counts": dict(cue_counts.most_common()),
        "boundary_mechanism_counts": dict(boundary_counts.most_common()),
        "output_format_counts": dict(output_fmt_counts.most_common()),
        "track_labels": TRACK_LABELS,
        "subtrack_labels": SUBTRACK_LABELS,
        "families": profiles,
    }


def render_markdown_report(summary: dict[str, Any]) -> str:
    fams = summary["families"]
    lines: list[str] = [
        "# 352 审核模板同族科学分类与审核需求全量提取报告",
        "",
        f"- **生成时间**: `{summary['generated_at']}`",
        f"- **样本范围**: 全量 `{summary['total_families']}` 个同族模板（来自 `templete/index.json`，基于完整未截断清洗文本解析）",
        "",
        "## 一、MECE 二维分类总表（权利方基数 × 审核机制）",
        "",
        "| 主分类 Track | 子分类 Subtrack | 含义 | 同族数 | 占比 |",
        "|---|---|---|---:|---:|",
    ]
    total = summary["total_families"]
    for st, cnt in summary["subtrack_counts"].items():
        if st.startswith("A"):
            tr = "广域识别模板 (`broad_domain`)"
        elif st.startswith("B"):
            tr = "特定产品/IP/品牌 (`entity_specific`)"
        else:
            tr = "隔离异常模板 (`quarantined_excluded`)"
        pct = f"{cnt / total * 100:.1f}%"
        lines.append(f"| {tr} | `{st}` | {SUBTRACK_LABELS.get(st, st)} | **{cnt}** | {pct} |")

    lines.extend(
        [
            "",
            f"> 合计：**广域识别模板 `36` 族 (10.2%)** · **特定产品/IP/品牌识别模板 `307` 族 (87.2%)** · **隔离异常模板 `9` 族 (2.6%)**，MECE 总计 `{total}` 族。",
            "",
            "## 二、广域识别模板全清单（36 族）与审计需求映射",
            "",
            "| Subtrack | `family_slug` | 默认主版标题 | 模态策略 | 关键机制/要求 | CPT-SFT 路由 |",
            "|---|---|---|---|---|---|",
        ]
    )
    for p in sorted([x for x in fams if x["scope_track"] == "broad_domain"], key=lambda x: (x["scope_subtrack"], x["family_slug"])):
        req = p["audit_requirements"]
        bnds = ", ".join(req["boundary_and_exclusion_mechanisms"][:3]) or "-"
        lines.append(
            f"| `{p['scope_subtrack']}` | `{p['family_slug']}` | `{p['selected_latest_title']}` | `{req['modality_decision_policy']}` | {bnds} | `{req['cpt_sft_route']}` |"
        )

    lines.extend(
        [
            "",
            "## 三、全量 352 族审核需求频次统计",
            "",
            "### 3.1 模态决策策略 (`modality_decision_policy`)",
            "| 策略 | 同族数 | 含义 |",
            "|---|---:|---|",
        ]
    )
    pol_desc = {
        "image_and_text_joint": "图文联合判定（结合商品标题与图像证据）",
        "image_overrides_text": "图片绝对优先（严防仅标题含词无视觉标时误杀）",
        "image_only": "纯视觉主导判断",
        "text_primary_or_only": "纯文本/案件元数据主判",
        "pairwise_image_comparison": "双图对比（敏感母本图 vs 待审风险图）",
    }
    for k, v in summary["modality_decision_policy_counts"].items():
        lines.append(f"| `{k}` | {v} | {pol_desc.get(k, k)} |")

    lines.extend(["", "### 3.2 视觉识别要素需求 (`visual_cues_required`)", "| 视觉线索 | 涉及同族数 | 说明 |", "|---|---:|---|"])
    for k, v in summary["visual_cue_counts"].items():
        lines.append(f"| `{k}` | {v} | {VISUAL_CUE_LABELS.get(k, k)} |")

    lines.extend(["", "### 3.3 边界防错与推理机制需求 (`boundary_and_exclusion_mechanisms`)", "| 机制 | 涉及同族数 | 说明 |", "|---|---:|---|"])
    for k, v in summary["boundary_mechanism_counts"].items():
        lines.append(f"| `{k}` | {v} | {BOUNDARY_MECHANISM_LABELS.get(k, k)} |")

    lines.extend(["", "### 3.4 输出协议形态 (`output_contract.format`)", "| 输出格式 | 同族数 |", "|---|---:|"])
    for k, v in summary["output_format_counts"].items():
        lines.append(f"| `{k}` | {v} |")

    return "\n".join(lines) + "\n"


def write_outputs(
    summary: dict[str, Any],
    out_json: Path = DEFAULT_OUT_JSON,
    out_jsonl: Path = DEFAULT_OUT_JSONL,
    out_md: Path = DEFAULT_OUT_MD,
) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    tmp_json = out_json.with_name(out_json.name + ".tmp")
    tmp_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_json.replace(out_json)

    tmp_jsonl = out_jsonl.with_name(out_jsonl.name + ".tmp")
    with tmp_jsonl.open("w", encoding="utf-8") as f:
        for row in summary["families"]:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    tmp_jsonl.replace(out_jsonl)

    out_md.parent.mkdir(parents=True, exist_ok=True)
    tmp_md = out_md.with_name(out_md.name + ".tmp")
    tmp_md.write_text(render_markdown_report(summary), encoding="utf-8")
    tmp_md.replace(out_md)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templete-dir", type=Path, default=DEFAULT_TEMPLETE_DIR)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-jsonl", type=Path, default=DEFAULT_OUT_JSONL)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = parser.parse_args()

    summary = analyze_all_families(args.templete_dir)
    write_outputs(summary, args.out_json, args.out_jsonl, args.out_md)
    print(
        json.dumps(
            {
                "total_families": summary["total_families"],
                "track_counts": summary["track_counts"],
                "subtrack_counts": summary["subtrack_counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
