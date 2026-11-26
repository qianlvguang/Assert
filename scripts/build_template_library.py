#!/usr/bin/env python3
"""Build organized template library & full-text diagnoses inside Assert.

Reads `manifests/audit_prompts_461_full_raw.jsonl` plus read-only Assert asset
manifests, cleans export-residual hardcoded product titles/specs/attributes back
into canonical placeholders (`#GOODS_TEXT_INFO#`, `#GOODS_PROPERTIES#`,
`#GOODS_SPEC#`, `#GOODS_CONTEXT#`, `#BRAND_LIST#`) without blaming templates for
export artifacts, unpacks inline multi-version records (`461` raw -> `535`
individual versions), groups same-object templates under `templete/`, selects
the latest/best version per family by default, and writes structured JSON +
Chinese Markdown diagnostics for every version and family.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_PATH = PROJECT_ROOT / "manifests" / "audit_prompts_461_full_raw.jsonl"
DEFAULT_CLEANED_PATH = PROJECT_ROOT / "manifests" / "audit_prompts_461_full_cleaned.jsonl"
DEFAULT_CLEANUP_REPORT = PROJECT_ROOT / "manifests" / "export_cleanup_report.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "templete"
DEFAULT_MANIFEST_OUT = PROJECT_ROOT / "manifests" / "template_library_manifest.json"

# ---------------------------------------------------------------------------
# Curated Family Grouping (prevents false merges & captures cross-name groups)
# ---------------------------------------------------------------------------
EXPLICIT_FAMILY_BY_ID: dict[int, str] = {
    # Quarantined test / junk templates
    1: "test_5678",
    244: "test_general_ip",
    267: "test_nyetest",
    268: "test_nyetest",
    269: "test_nyetest",
    270: "test_nyetest",
    271: "test_nyetest",
    429: "test_lingjinglan",
    451: "test_111",
    # Auxiliary non-IP governance / legal / text-only templates
    254: "aux_identifying_fake_brands",
    255: "aux_invoices",
    277: "aux_black_word_risk_reviewer",
    292: "aux_crawlplatform_anti_risk",
    352: "aux_audit_feedback_optimizer",
    357: "aux_brand_alliance",
    358: "aux_brand_alliance",
    359: "aux_brand_collab",
    360: "aux_brand_collab",
    361: "aux_brand_collab",
    432: "aux_logos_review_verification_text",
    455: "aux_tro_brandname_alignment",
    456: "aux_tro_brandname_alignment",
    457: "aux_tro_brandname_rec",
    458: "aux_tro_warning_case_process",
    # Same-object multi-record families (with collision guards)
    345: "all_blacks",
    346: "all_blacks",
    174: "anpanman",
    274: "anpanman",
    34: "apple",
    35: "apple",
    36: "apple",
    37: "apple",
    38: "apple",
    245: "apple",
    335: "arizona_university",
    349: "arizona_university",
    2: "audi",
    3: "audi",
    351: "audi",
    49: "banana_republic",
    176: "banana_republic",
    4: "band_music_general",
    5: "band_music_general",
    46: "billionaire_boys_club",
    47: "billionaire_boys_club",
    278: "bleach",
    279: "bleach",
    51: "brawl_stars",
    280: "brawl_stars",
    453: "brawl_stars",
    362: "brand_gemini_general",
    363: "brand_gemini_general",
    364: "brand_gemini_general",
    365: "brand_goods_consistent_multi_img",
    366: "brand_goods_consistent_multi_img",
    55: "calvin_klein",
    56: "calvin_klein",
    62: "calvin_klein",
    284: "calvin_klein",
    285: "calvin_klein",
    286: "calvin_klein",
    287: "calvin_klein",
    288: "calvin_klein",
    368: "calvin_klein",
    17: "cars_automotive_general",
    180: "cars_automotive_general",
    298: "cars_automotive_general",
    282: "champion",
    370: "champion",
    372: "cluster_gemini",
    373: "cluster_gemini",
    374: "cluster_gemini",
    375: "cluster_gemini",
    9: "counterfeit_watch",
    26: "counterfeit_watch",
    184: "crocs_charms",
    185: "crocs_charms",
    72: "dandys_world",
    73: "dandys_world",
    74: "dav_pilkey_dogman",
    186: "dav_pilkey_dogman",
    190: "dav_pilkey_dogman",
    65: "dc_comics",
    66: "dc_comics",
    67: "dc_shoes",
    187: "demon_slayer",
    188: "demon_slayer",
    189: "demon_slayer",
    68: "dior",
    69: "dior",
    246: "disney",
    378: "duke_university",
    379: "duke_university",
    380: "duke_university",
    383: "ford",
    384: "ford",
    385: "ford",
    201: "guess",
    295: "guess",
    296: "guess",
    83: "hatsune_miku",
    84: "hatsune_miku",
    86: "hermes",
    89: "hermes",
    90: "hermes",
    91: "hermes",
    92: "hermes",
    93: "hermes",
    318: "higuchi_yuko",
    319: "higuchi_yuko",
    101: "loewe",
    103: "loewe",
    104: "maison_margiela",
    105: "maison_margiela",
    114: "maison_margiela",
    223: "maradona",
    306: "maradona",
    106: "marilyn_monroe",
    210: "marilyn_monroe",
    107: "marvel",
    108: "marvel",
    111: "michael_jackson",
    112: "michael_jackson",
    376: "molson_coors",
    397: "molson_coors",
    398: "molson_coors",
    399: "molson_coors",
    400: "molson_coors",
    313: "monopoly",
    333: "monopoly",
    337: "mr_men_little_miss",
    430: "mr_men_little_miss",
    115: "muhammad_ali",
    116: "muhammad_ali",
    338: "muhammad_ali",
    117: "my_hero_academia",
    215: "my_hero_academia",
    122: "nba",
    435: "nba",
    265: "nhl",
    437: "nhl",
    125: "nike",
    248: "nike",
    216: "nike_jordan",
    402: "nin1_game_console",
    403: "nin1_game_console",
    404: "nin1_game_console",
    405: "nirvana",
    406: "nirvana",
    126: "oakley",
    438: "oakley",
    452: "oakley",
    408: "oklahoma_university",
    421: "oklahoma_university",
    324: "one_piece",
    409: "one_piece",
    129: "paw_patrol",
    130: "paw_patrol",
    410: "pikmin",
    411: "pikmin",
    327: "ralph_lauren",
    328: "ralph_lauren",
    256: "rfef",
    412: "rfef",
    440: "risk_evaluation",
    441: "risk_evaluation",
    442: "risk_evaluation",
    443: "risk_evaluation",
    314: "sports_ball_general",
    354: "sports_ball_general",
    148: "super_mario",
    272: "super_mario",
    229: "supreme",
    251: "supreme",
    155: "tommy_hilfiger",
    156: "tommy_hilfiger",
    164: "uga",
    459: "uga",
    234: "ugg",
    235: "ugg",
    394: "university_of_michigan",
    395: "university_of_michigan",
    396: "university_of_michigan",
    433: "michigan_state",
    422: "university_of_utah",
    423: "university_of_utah",
    237: "van_cleef_arpels",
    238: "van_cleef_arpels",
    166: "vision_street_wear",
    167: "vision_street_wear",
    14: "volkswagen",
    342: "volkswagen",
    24: "zippo",
    25: "zippo",
}

SINGLETON_SLUG_OVERRIDES: dict[int, str] = {
    7: "deutsches_rotes_kreuz",
    8: "counterfeit_jerseys",
    197: "genies_perfume_atomizer",
    247: "friends",
    249: "pepsi",
    250: "pokemon",
    252: "vogue",
    253: "sesame_street",
    311: "sandmaennchen",
    416: "money_heist_la_casa_de_papel",
    445: "shein_mark",
}

FAMILY_DISPLAY_NAMES: dict[str, str] = {
    "all_blacks": "新西兰全黑队 (All Blacks)",
    "anpanman": "面包超人 (Anpanman)",
    "apple": "苹果 (Apple 产品/标识/配件)",
    "arizona_university": "亚利桑那大学 (University of Arizona)",
    "audi": "奥迪 (Audi)",
    "banana_republic": "Banana Republic",
    "band_music_general": "通用乐队/歌手召回 (Band)",
    "billionaire_boys_club": "Billionaire Boys Club",
    "bleach": "死神/境·界 (BLEACH)",
    "brawl_stars": "荒野乱斗 (Brawl Stars)",
    "brand_gemini_general": "通用品牌宿主隔离审核 (Gemini)",
    "brand_goods_consistent_multi_img": "多图商品品牌一致性审核",
    "calvin_klein": "Calvin Klein (CK)",
    "cars_automotive_general": "汽车品牌通用侵权与配件豁免 (Cars Automotive)",
    "champion": "Champion",
    "cluster_gemini": "通用聚类品牌/山寨/独立站审查 (Gemini)",
    "counterfeit_watch": "奢侈手表多品牌侵权治理",
    "crocs_charms": "洞洞鞋及鞋花配件 (Crocs Charms)",
    "dandys_world": "Dandy's World",
    "dav_pilkey_dogman": "神探狗狗 (Dav Pilkey / Dog Man)",
    "dc_comics": "DC 漫画 (DC Comics)",
    "dc_shoes": "DC Shoes",
    "demon_slayer": "鬼灭之刃 (Demon Slayer)",
    "deutsches_rotes_kreuz": "德国红十字会 / 错贴瑞士红十字会模板",
    "dior": "迪奥 (Dior)",
    "disney": "迪士尼 (Disney)",
    "duke_university": "杜克大学 (Duke University)",
    "ford": "福特汽车 (Ford)",
    "friends": "老友记 (Friends)",
    "guess": "GUESS",
    "hatsune_miku": "初音未来 (Hatsune Miku)",
    "hermes": "爱马仕 (Hermès)",
    "higuchi_yuko": "樋口裕子 (Higuchi Yuko)",
    "loewe": "罗意威 (Loewe)",
    "maison_margiela": "马丁·马吉拉 (Maison Margiela)",
    "maradona": "马拉多纳 (Diego Maradona)",
    "marilyn_monroe": "玛丽莲·梦露 (Marilyn Monroe)",
    "marvel": "漫威角色 (Marvel)",
    "michael_jackson": "迈克尔·杰克逊 (Michael Jackson)",
    "michigan_state": "密歇根州立大学斯巴达人队 (Michigan State)",
    "molson_coors": "莫尔森库尔斯啤酒 (Molson Coors / Miller)",
    "money_heist_la_casa_de_papel": "纸钞屋 / 西班牙影视 (La Casa De Papel)",
    "monopoly": "大富翁 (Monopoly)",
    "mr_men_little_miss": "奇先生妙小姐 (Mr. Men Little Miss)",
    "muhammad_ali": "穆罕默德·阿里 (Muhammad Ali)",
    "my_hero_academia": "我的英雄学院 (My Hero Academia)",
    "nba": "NBA 美职篮",
    "nhl": "NHL 北美职业冰球联盟",
    "nike": "耐克 (Nike)",
    "nike_jordan": "乔丹 (Nike Jordan)",
    "nin1_game_console": "N-in-1 怀旧游戏机/内置游戏",
    "nirvana": "涅槃乐队 (Nirvana)",
    "oakley": "欧克利 (Oakley)",
    "oklahoma_university": "俄克拉荷马大学 (University of Oklahoma)",
    "one_piece": "海贼王 (One Piece)",
    "paw_patrol": "汪汪队立大功 (PAW Patrol)",
    "pepsi": "百事可乐 (Pepsi)",
    "pikmin": "皮克敏 (Pikmin)",
    "pokemon": "宝可梦 (Pokémon)",
    "ralph_lauren": "拉夫劳伦 (Ralph Lauren)",
    "rezero": "Re:从零开始的异世界生活 (Re:Zero)",
    "rfef": "西班牙皇家足协 (RFEF)",
    "risk_evaluation": "通用多模态商品/广告风险评估",
    "sandmaennchen": "沙人 (Unser Sandmännchen)",
    "sesame_street": "芝麻街 (Sesame Street)",
    "shein_mark": "SHEIN 水印检测",
    "sports_ball_general": "通用体育俱乐部/联盟/球星 IP",
    "super_mario": "超级马里奥 (Super Mario)",
    "supreme": "Supreme",
    "tommy_hilfiger": "Tommy Hilfiger",
    "uga": "佐治亚大学斗牛犬队 (UGA)",
    "ugg": "UGG Australia",
    "university_of_michigan": "密歇根大学 (University of Michigan)",
    "university_of_utah": "犹他大学 (University of Utah)",
    "van_cleef_arpels": "梵克雅宝 (Van Cleef & Arpels)",
    "vision_street_wear": "Vision Street Wear",
    "vogue": "VOGUE 杂志",
    "volkswagen": "大众汽车 (Volkswagen)",
    "zippo": "Zippo 打火机",
}

PARALLEL_SUB_SCOPE_FAMILIES: set[str] = {
    "apple",
    "calvin_klein",
    "cluster_gemini",
    "dior",
    "ford",
    "hermes",
    "paw_patrol",
    "risk_evaluation",
}

# ---------------------------------------------------------------------------
# Export Artifact Cleaner (cleans runtime-injected SKUs back to placeholders)
# ---------------------------------------------------------------------------
SPEC_ARRAY_RE = re.compile(
    r"(?:\[\s*\{\s*\"p_spec_name\"[^\n]*?\}\s*\](?:\s*\.\s*\[\s*\{\s*\"p_spec_name\"[^\n]*?\}\s*\])*)",
)
PROP_CHAIN_RE = re.compile(
    r"\[\s*\"[^\"\n]{1,40}\"\s*,\s*\"[^\"\n]{0,100}\"\s*\](?:\s*\.\s*\[\s*\"[^\"\n]{1,40}\"\s*,\s*\"[^\"\n]{0,100}\"\s*\])+",
)
REPEATED_SKU_RE = re.compile(
    r"([A-Z0-9][A-Za-z0-9\s,\-&'\"/|+.:()]{35,}?)\.\1(?:\.\1)?",
)

ALREADY_PLACEHOLDER_RE = re.compile(r"#GOODS_|#BRAND_LIST#|\{goods|#goods|#brand", re.I)

CHINESE_RULE_VERBS_RE = re.compile(
    r"(?:是否|判断|分析|出现|包含|存在|满足|如果|请|若|当|必须|严禁|输出|判定|不能|不得|属于|排除|豁免|案例|示例)"
)

LABELED_END_CLAUSE_PAT = (
    r"(?="
    r"[，,]?\s*(?:分别回答|推测|分析|结合|请|并|回答|结果|进行|如果|若|在\s*reason|给出|然后|首先|判断|同时|中是否|是否|来确定|与商品)"
    r"|。\s*(?:请|若|如果|结果|注意|输出|以下|第一|第1|判断)"
    r"|来进行判断|来判断|的(?:商品|文本|信息)|与商品|相关(?:信息|元素)|以\s*json|请以\s*(?:json|dict|default)"
    r"|\n|$"
    r")"
)

MID_SENTENCE_INJECTION_RES: list[tuple[str, re.Pattern[str]]] = [
    (
        "known_goods_and_brand_list",
        re.compile(
            r'(已知售卖商品的标题是\s*[：:]\s*)["“]([^"”\n]{4,})["”](\s*[；;]\s*【填写品牌/公司列表】为\s*)["“]([^"”\n]{2,})["”]'
        ),
    ),
    (
        "known_goods_quoted",
        re.compile(r'(已知售卖商品的(?:名称|标题|goods\s*name)\s*(?:是|为)?\s*[：:]\s*)["“]([^"”\n]{2,})["”]'),
    ),
    (
        "bracketed_goods_title_arr",
        re.compile(r'(【商品标题】\s*[：:]\s*\[\s*["“])([^"”\n]{8,})(["”]\s*\])'),
    ),
    (
        "bracketed_goods_title",
        re.compile(r'(【商品标题】\s*[：:]\s*)([^\n]{8,})'),
    ),
    (
        "goods_prop_line",
        re.compile(r'(商品属性信息为\s*)(?!#GOODS)([^\n]{8,})'),
    ),
    (
        "task_provided_sku",
        re.compile(
            r'(任务\s*[：:]\s*(?:根据提供的|分析提供的商品标题)\s*)([A-Z0-9][^\n]{18,}?)'
            + r'(?=[，,。]?\s*(?:推测|分析|判断|结合|进行|如果|若|注意|请|输出|以下|第)|来进行|的(?:类别|商品|名称)|\n|$)'
        ),
    ),
    (
        "audi_prep_sku",
        re.compile(
            r'((?:你要通过|售卖主体本身\s*[：:]\s*根据|这一条仅看)\s*)([A-Z0-9][^\n]{18,}?)'
            + r'(?=的商品名称|来确定|与商品图片|\n|$)'
        ),
    ),
    (
        "mid_clause_provided_text",
        re.compile(
            r'(提供的商品文本信息\s+)([A-Z0-9][^\n]{12,}?)'
            + r'(?=[\s，。]*(?:中的|进行|来|判断|是|的|是否|并|\n|$))'
        ),
    ),
    (
        "labeled_inline_sku",
        re.compile(
            r'(请认真观察图片和商品标题\s*|请结合以下商品文本信息进行判断\s*[：:]\s*|'
            r'结合商品(?:图案|图片)(?:和|或者|、|,|，)\s*商标标题\s*|'
            r'结合商品标题\s+|标题滥用\s*[：:]\s*商品标题\s+|'
            r'已知商品名称为\s*|现在[，,]?\s*请对输入的商品名称\s*|根据提供的商品名称\s*|'
            r'商品标题信息为\s*|商品文本信息为\s*|商品信息文本为\s*|商品标题为\s*|商品名称为\s*|'
            r'商品标题\s*[：:]\s*|商品名称\s*[：:]\s*|商品\s*[：:]\s*)'
            r'([^\n]{12,}?)'
            + LABELED_END_CLAUSE_PAT
        ),
    ),
    (
        "trailing_sentence_sku",
        re.compile(
            r'((?:给出最终的结果|给出解释|并给出解释|回答true或false|是否侵权)\s*[。！]\s*)'
            r'([A-Z0-9][^\n]{25,}?)$',
            re.MULTILINE,
        ),
    ),
]


def _find_balanced_paren_end(text: str, open_idx: int) -> int | None:
    open_ch = text[open_idx]
    close_ch = "）" if open_ch == "（" else ")"
    depth = 0
    for i in range(open_idx, len(text)):
        ch = text[i]
        if ch in ("(", "（"):
            depth += 1
        elif ch in (")", "）"):
            depth -= 1
            if depth == 0:
                return i
        elif ch == "\n":
            return None
    return None


def _looks_like_injected_sku(snippet: str) -> bool:
    s = snippet.strip().strip(",. ")
    if not s or len(s) < 6 or ALREADY_PLACEHOLDER_RE.search(s):
        return False
    # Protect legal case docs or explicit rule examples
    if re.search(r"Case\s+(?:No\.?\s*)?\d+:\d+-cv-|UNITED STATES DISTRICT COURT", s, re.I):
        return False
    if re.search(r"listing text|goods\s*(?:name|text)", s, re.I):
        return False
    if re.search(r"^(?:示例|案例)", s):
        return False
    # Concrete single Chinese/English placeholder like 展示架
    if s in {"展示架"}:
        return True
    ascii_letters = sum(1 for c in s if c.isascii() and c.isalpha())
    zh_chars = sum(1 for c in s if "\u4e00" <= c <= "\u9fff")
    if zh_chars > 12 and CHINESE_RULE_VERBS_RE.search(s):
        return False
    if ascii_letters >= 10 or "#GOODS_" in s:
        return True
    return False


def clean_export_artifacts(text: str, record_id: int) -> tuple[str, list[dict[str, str]]]:
    """Removes runtime-injected e-commerce SKU titles/specs while preserving rules."""
    # Skip legal / auxiliary non-product-title docs (432 Case report, 445 SHEIN detector, etc.)
    if record_id in {254, 255, 277, 292, 357, 358, 359, 360, 361, 432, 445, 455, 456, 457, 458}:
        return text, []

    cleanups: list[dict[str, str]] = []
    out = text

    # 1. Spec JSON arrays & dot-chained property arrays
    def _rep_spec(m: re.Match[str]) -> str:
        cleanups.append({"rule": "spec_json_array", "before_preview": m.group(0)[:80], "after_token": "#GOODS_SPEC#"})
        return "#GOODS_SPEC#"

    def _rep_prop(m: re.Match[str]) -> str:
        cleanups.append({"rule": "property_array_chain", "before_preview": m.group(0)[:80], "after_token": "#GOODS_PROPERTIES#"})
        return "#GOODS_PROPERTIES#"

    out = SPEC_ARRAY_RE.sub(_rep_spec, out)
    out = PROP_CHAIN_RE.sub(_rep_prop, out)

    def _rep_repeated_sku(m: re.Match[str]) -> str:
        inner = m.group(1)
        if not _looks_like_injected_sku(inner):
            return m.group(0)
        cleanups.append({"rule": "repeated_sku_title", "before_preview": inner[:80], "after_token": "#GOODS_TEXT_INFO#"})
        return "#GOODS_TEXT_INFO#"

    out = REPEATED_SKU_RE.sub(_rep_repeated_sku, out)

    # 2. Balanced parenthesized goods title/text slots: 商品标题（...） / 商品文本信息(...)
    paren_trigger = re.compile(r"(?:商品标题|商品文本信息|商品信息文本)\s*[（(]")
    pos = 0
    rebuilt: list[str] = []
    while True:
        m = paren_trigger.search(out, pos)
        if not m:
            rebuilt.append(out[pos:])
            break
        open_idx = m.end() - 1
        end_idx = _find_balanced_paren_end(out, open_idx)
        if end_idx is None:
            rebuilt.append(out[pos : m.end()])
            pos = m.end()
            continue
        inner = out[open_idx + 1 : end_idx]
        if _looks_like_injected_sku(inner):
            rebuilt.append(out[pos : open_idx + 1])
            rebuilt.append("#GOODS_TEXT_INFO#")
            rebuilt.append(out[end_idx])
            cleanups.append({"rule": "parenthesized_goods_title", "before_preview": inner[:80], "after_token": "#GOODS_TEXT_INFO#"})
            pos = end_idx + 1
        else:
            rebuilt.append(out[pos : end_idx + 1])
            pos = end_idx + 1
    out = "".join(rebuilt)

    # 3. Known regex slots
    for rule_name, pat in MID_SENTENCE_INJECTION_RES:
        if rule_name == "known_goods_and_brand_list":
            def _rep_kgb(m: re.Match[str]) -> str:
                if ALREADY_PLACEHOLDER_RE.search(m.group(2)):
                    return m.group(0)
                cleanups.append({"rule": rule_name, "before_preview": m.group(2)[:70], "after_token": "#GOODS_TEXT_INFO# + #BRAND_LIST#"})
                return f'{m.group(1)}"#GOODS_TEXT_INFO#"{m.group(3)}"#BRAND_LIST#"'
            out = pat.sub(_rep_kgb, out)
        elif rule_name in {"known_goods_quoted", "bracketed_goods_title_arr"}:
            def _rep_q(m: re.Match[str], rn: str = rule_name) -> str:
                inner = m.group(2)
                if not _looks_like_injected_sku(inner):
                    return m.group(0)
                cleanups.append({"rule": rn, "before_preview": inner[:80], "after_token": "#GOODS_TEXT_INFO#"})
                tail = m.group(3) if m.lastindex and m.lastindex >= 3 else '"'
                return f"{m.group(1)}#GOODS_TEXT_INFO#{tail}"
            out = pat.sub(_rep_q, out)
        elif rule_name == "goods_prop_line":
            def _rep_gp(m: re.Match[str]) -> str:
                val = m.group(2).strip()
                if ALREADY_PLACEHOLDER_RE.search(val):
                    return m.group(0)
                if _looks_like_injected_sku(val) or "#GOODS_PROPERTIES#" in val:
                    cleanups.append({"rule": "goods_prop_line", "before_preview": val[:80], "after_token": "#GOODS_PROPERTIES#"})
                    return f"{m.group(1)}#GOODS_PROPERTIES#"
                return m.group(0)
            out = pat.sub(_rep_gp, out)
        else:
            def _rep_std(m: re.Match[str], rn: str = rule_name) -> str:
                val = m.group(2)
                if not _looks_like_injected_sku(val):
                    return m.group(0)
                cleanups.append({"rule": rn, "before_preview": val.strip()[:80], "after_token": "#GOODS_TEXT_INFO#"})
                return f"{m.group(1)}#GOODS_TEXT_INFO#"
            out = pat.sub(_rep_std, out)

    # 4. Line-level cleanup for `规则N:` injected SKU context lines, pure comma residue, and role-prefix SKU leaks
    lines = out.splitlines()
    cleaned_lines: list[str] = []
    after_rule_header = False
    for line in lines:
        stripped = line.strip()

        # Pure comma residue inside blockquote (e.g. `> ,,,` or `> ,`)
        if re.match(r"^>\s*,{1,6}\s*$", line):
            cleanups.append({"rule": "empty_comma_residue", "before_preview": stripped, "after_token": "(removed)"})
            continue

        # Leading SKU before `是西班牙电视剧...` (id=416)
        m_role_leak = re.match(r"^(>\s*)([A-Z0-9][A-Za-z0-9\s,\-&'\"/|+.:()]{25,}?)\s+(是[\u4e00-\u9fff].*治理专家.*)$", line)
        if m_role_leak:
            cleanups.append({"rule": "role_prefix_sku_leak", "before_preview": m_role_leak.group(2)[:80], "after_token": "#GOODS_TEXT_INFO#"})
            cleaned_lines.append(f"{m_role_leak.group(1)}[商品文本: #GOODS_TEXT_INFO#] 你{m_role_leak.group(3)}")
            after_rule_header = False
            continue

        # Line immediately following `> 规则N:` that is an injected runtime SKU / spec / prop
        if after_rule_header and line.startswith(">"):
            body_part = line[1:].strip()
            has_spec = "#GOODS_SPEC#" in body_part or "#GOODS_PROPERTIES#" in body_part
            looks_sku = (
                body_part.startswith(",")
                or has_spec
                or (
                    len(body_part) > 35
                    and sum(c.isascii() and c.isalpha() for c in body_part) > 25
                    and not CHINESE_RULE_VERBS_RE.search(body_part)
                    and not re.search(r"TEST-DO-NOT-BUY|Pyytest|CHILDREN'S PRODUCT CERT|Price-tracked", body_part)
                )
            )
            if looks_sku:
                cleanups.append({"rule": "rule_header_injected_sku", "before_preview": body_part[:80], "after_token": "#GOODS_CONTEXT#"})
                cleaned_lines.append("> #GOODS_CONTEXT#")
                after_rule_header = False
                continue

        # Standalone trailing injected SKU line in prompt body (not example/list/rule)
        if line.startswith(">") and not re.match(r"^>\s*(?:[-*]|\d+[\.、])", line):
            body_part = line[1:].strip()
            if (
                len(body_part) >= 48
                and (body_part.startswith(",") or _looks_like_injected_sku(body_part))
                and sum(1 for c in body_part if "\u4e00" <= c <= "\u9fff") == 0
                and not re.search(r"^(?:Role|Task|Step|Context|Output|Note|Example|JSON|Case\s+No)", body_part, re.I)
                and not re.search(r"TEST-DO-NOT-BUY|Pyytest|CHILDREN'S PRODUCT CERT|Price-tracked", body_part)
                and not re.search(r"T-shirt$|hoodie$|phone case$", body_part, re.I)
                and re.search(r"(?:1pc|2pcs|3pcs|50pcs|32pcs|100sets|2D Flat|Plus Size|Men's|Women's|Phone Case|Blanket|Backdrop|Wall Art|Display Cabinet|T-Shirt|Sweatshirt|Backpack|Bottle|Switch|Lighter|Stickers|Table|Chair|Shoes|Clogs|Socks|Jacket|Perfume|Fragrance|Bookshelf|For |Compatible|Suitable|Ideal for|WHERETHERE'S A WILL)", body_part, re.I)
            ):
                cleanups.append({"rule": "standalone_injected_sku", "before_preview": body_part[:80], "after_token": "#GOODS_TEXT_INFO#"})
                cleaned_lines.append("> #GOODS_TEXT_INFO#")
                after_rule_header = False
                continue

        # Deduplicate consecutive `#GOODS_TEXT_INFO#` / `#GOODS_CONTEXT#` lines
        if cleaned_lines and cleaned_lines[-1].strip() in {"> #GOODS_TEXT_INFO#", "> #GOODS_CONTEXT#"} and stripped == cleaned_lines[-1].strip():
            continue

        cleaned_lines.append(line)
        after_rule_header = bool(re.match(r"^>\s*规则\s*\d+\s*[:：]\s*$", line))

    # Clean residual leading `,` right before `#GOODS_TEXT_INFO#` or trailing `,` after `#GOODS_SPEC#`
    final_text = "\n".join(cleaned_lines)
    final_text = re.sub(r"#GOODS_(?:SPEC|PROPERTIES)#(?:\s*[.,]\s*#GOODS_(?:SPEC|PROPERTIES)#)+", "#GOODS_SPEC# #GOODS_PROPERTIES#", final_text)
    if text.endswith("\n") and not final_text.endswith("\n"):
        final_text += "\n"
    return final_text, cleanups


# ---------------------------------------------------------------------------
# Hygiene, Paste-Bug, Metadata & Rubric Vulnerability Patterns
# ---------------------------------------------------------------------------
VERSION_HEADER_RE = re.compile(r"\*\*同一对象的\s*\d+\s*个版本\*\*[：:]\s*([^\n]+)")

CROSS_ENTITY_PASTE_SIGNATURES: list[tuple[int, str | None, str, str]] = [
    (7, None, "deutsches_vs_swiss_red_cross", "标题为德国红十字会 (Deutsches Rotes Kreuz e.V)，正文却写“管控瑞士红十字会Logo / Swiss Red Cross”。"),
    (108, "IP_marvel", "marvel_vs_disney", "子版本 IP_marvel 正文误写为“是否包含迪士尼元素的信息”（同记录另一版本 IP_MARVEL_IMAGE 正常）。"),
    (179, None, "generic_title_hardcoded_adidas", "标题为泛用名 IP_brand，正文硬编码限定单一品牌 adidas。"),
    (231, None, "tintin_vs_rusty_copy_paste", "《丁丁历险记》模板正文混入“是否符合rusty判断的核心特征”（复制粘贴残留）。"),
    (248, None, "nike_keyword_vs_generic_dict", "标题为 IP组-nike-关键词召回识别，正文却是通用未限定 IP 字典模板。"),
    (296, None, "guess_vs_generic_dict", "标题为 guessprompt，正文却是通用未限定 IP 字典模板（未出现 GUESS）。"),
    (346, None, "allblacks_vs_belgium_fa", "标题为 ip_allblakcs（拼写误写），示例 JSON reason 混入“是否出现比利时足协相关元素”。"),
    (415, None, "south_carolina_vs_usc", "标题与细则面向南卡罗来纳大学 (South Carolina)，但括注误写为南加州大学 (University of Southern California)。"),
]

KNOWN_BAD_REL_BY_TITLE_HINT: list[tuple[re.Pattern[str], set[str], str]] = [
    (re.compile(r"selfmodel", re.I), {"FMOD"}, "`rel` 中的 `FMOD` 疑似来自模板名/方法名 `selfmodel` 误匹配"),
    (re.compile(r"gemini|_DC$", re.I), {"Mini"}, "`rel` 中的 `Mini` 来自 `gemini` 或误绑"),
    (re.compile(r"audit", re.I), {"Audi"}, "`rel` 中的 `Audi` 为 `audit` 子串误匹配"),
    (re.compile(r"cars", re.I), {"汽车总动员（Cars）"}, "模板实为汽车品牌/配件侵权，并非皮克斯动画《汽车总动员》"),
    (re.compile(r"BILLIONAIRE", re.I), {"Lion Air"}, "`rel` 中的 `Lion Air` 为 `billionaire` 子串误匹配"),
    (re.compile(r"Positive", re.I), {"Posit"}, "`rel` 中的 `Posit` 为 `Positive` 子串误匹配"),
    (re.compile(r"OLYMPIC|monopoly", re.I), {"Poly"}, "`rel` 中的 `Poly` 为子串误匹配"),
    (re.compile(r"STEAL", re.I), {"Teal"}, "`rel` 中的 `Teal` 为 `steal` 子串误匹配"),
    (re.compile(r"metallica", re.I), {"Meta"}, "`rel` 中的 `Meta` 为 `metallica` 子串误匹配"),
    (re.compile(r"vancleefarpels_all", re.I), {"艾莎（Elsa）"}, "`rel` 中的 `艾莎（Elsa）` 为 `arpels_all` 子串误匹配"),
    (re.compile(r"consistent", re.I), {"NSIS"}, "`rel` 中的 `NSIS` 为 `consistent` 子串误匹配"),
    (re.compile(r"royale", re.I), {"Yale"}, "`rel` 中的 `Yale` 为 `royale` 子串误匹配"),
    (re.compile(r"infringement", re.I), {"Ring"}, "`rel` 中的 `Ring` 为 `infringement` 子串误匹配"),
    (re.compile(r"anti_risk", re.I), {"IRIS"}, "`rel` 中的 `IRIS` 为 `anti_risk` 子串误匹配"),
    (re.compile(r"discoverer", re.I), {"Discover"}, "`rel` 中的 `Discover` 为方法名误匹配"),
    (re.compile(r"llm[-_]?black|allblacks|black_word", re.I), {"Black"}, "`rel` 中的 `Black` 为后缀/队名子串误匹配"),
    (re.compile(r"TwentyOnePilots", re.I), {"Twenty"}, "`rel` 中的 `Twenty` 为局部切词误匹配"),
    (re.compile(r"CORALINE", re.I), {"Cora"}, "`rel` 中的 `Cora` 为 `coraline` 子串误匹配"),
    (re.compile(r"megaman", re.I), {"MEGA"}, "`rel` 中的 `MEGA` 为 `megaman` 子串误匹配，非 Mattel MEGA 积木"),
    (re.compile(r"Rilakkuma", re.I), {"Kuma"}, "`rel` 中的 `Kuma` 为局部切词误匹配"),
    (re.compile(r"Plexaderm", re.I), {"Plex"}, "`rel` 中的 `Plex` 为 `Plexaderm` 子串误匹配"),
    (re.compile(r"rusty", re.I), {"Rust"}, "`rel` 中的 `Rust` 为编程语言子串误匹配"),
    (re.compile(r"glassangelofficial", re.I), {"Glass"}, "`rel` 中的 `Glass` 为局部切词误匹配"),
    (re.compile(r"totto", re.I), {"Otto"}, "`rel` 中的 `Otto` 为 `totto` 子串误匹配"),
    (re.compile(r"similar_goods", re.I), {"Argo"}, "`rel` 中的 `Argo` 为无关误匹配"),
    (re.compile(r"taylorswift", re.I), {"Swift"}, "`rel` 中的 `Swift` 为姓氏局部切词误匹配"),
    (re.compile(r"MonsterHigh|monsterenergy", re.I), {"Monster"}, "`rel` 使用了泛化词 `Monster`，未区分具体品牌/作品"),
    (re.compile(r"spirit", re.I), {"spirit"}, "`rel` 过于泛化，未绑定 DreamWorks《小马王 Spirit》"),
]

EMPTY_PLACEHOLDER_RE = re.compile(
    r"(?:根据\s+来判断|商品名称为\s*[，,]|而非\s*来进行判断|商户标题[（(]\s*[）)])",
    re.MULTILINE,
)

BROKEN_JSON_RE = re.compile(
    r"(?:(?<![a-zA-Z])jason(?![a-zA-Z])|(?<![a-zA-Z])(?:ture|treue)(?![a-zA-Z])|default形式|\(\"res\"|【\"res\"|（\"res\"|\(\"reason\"|\"reason\"：|\"res\"：|\"res\":\s*true\)|\"res\":\s*xxx|请以js\b)",
    re.IGNORECASE,
)

TYPO_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bMaga Man\b"), "错别字：`Maga Man`（应为 Mega Man）"),
    (re.compile(r"密歇嘎大学"), "错别字：`密歇嘎大学`（应为密歇根大学）"),
    (re.compile(r"\bConfi请以"), "残留乱码前缀：`Confi`"),
    (re.compile(r"主管涂抹"), "错别字：`主管涂抹`（应为主观涂抹）"),
    (re.compile(r"oklahomo", re.I), "拼写错误：`oklahomo`（应为 oklahoma）"),
    (re.compile(r"spian", re.I), "拼写错误：`spian`（应为 spanish）"),
    (re.compile(r"allblakcs", re.I), "拼写错误：`allblakcs`（应为 allblacks）"),
    (re.compile(r"\bREFE\b"), "拼写错误：`REFE`（应为 RFEF）"),
    (re.compile(r"higuchiyoko", re.I), "拼写错误：`higuchiyoko`（应为 higuchiyuko）"),
    (re.compile(r"excepmtion", re.I), "拼写错误：`excepmtion`（应为 exception）"),
    (re.compile(r"universityu", re.I), "拼写错误：`universityu`（应为 university）"),
    (re.compile(r"以尺规则"), "错别字：`以尺规则`（应为以下规则）"),
    (re.compile(r"商品主题是否"), "错别字：`商品主题`（应为商品主体）"),
    (re.compile(r"包含时尚品牌guess的信。"), "缺字错漏：`的信。`（应为的信息）"),
    (re.compile(r"间断一句话"), "错别字：`间断一句话`（应为简短一句话）"),
    (re.compile(r"仅判断主体是否出现"), "检查表达完整性"),
]

# Full-text inter-class rubric vulnerability detectors
STYLE_ONLY_TRIGGER_RE = re.compile(
    r"(?:符合.*?(?:独特|典型|核心)?艺术风格.*?其他角色|符合.*画风的二创|即使没有出现主角|辛普森化|全局风格检测)",
    re.IGNORECASE,
)
ESCAPE_HATCH_RE = re.compile(
    r"(?:除非直观可判断|合理理解为指向|合理识别或推断|只要可以合理|只要.*看起来像)",
    re.IGNORECASE,
)
EXCLUSION_GUARD_RE = re.compile(
    r"(?:排除|免审|不构成|不相关|背景|反向剔除|过滤规则|豁免|不适用|不作为商标|输出\s*false|判定为\s*false|判为\s*(?:false|否)|无风险)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Archetypes & Inter-Class Risk Classification
# ---------------------------------------------------------------------------
ARCHETYPE_PATTERNS: dict[str, re.Pattern[str]] = {
    "anime_derivative_two_step": re.compile(
        r"(?:全局风格检测|核心角色档案|二次创作|二创|同人|动漫|漫画|游戏角色|动漫宇宙|Q版|演绎|魔改|借鉴)",
        re.IGNORECASE,
    ),
    "subject_host_isolation": re.compile(
        r"(?:售卖主体|商品主体|宿主|背景中|包装盒|透明保护壳|展示架|模特.*身上|不出现在背景|透出|主体一致性|宿主隔离)",
        re.IGNORECASE,
    ),
    "image_title_conflict": re.compile(
        r"(?:只有商品文本|商品图片未出现|标题.*图片.*矛盾|绝对不要.*参考.*标题|商品名称仅做参考|未出现.*(?:false|否)|图文一致|不用关注标题|仅结合商品图案)",
        re.IGNORECASE,
    ),
    "common_word_disambiguation": re.compile(
        r"(?:单独出现|唯一出现|最大那个|最大的那一个|普通贝壳|人名|26\s*letters|单词里|不作为商标|常见词|帕尼尼三明治|真实意义|大小写|普通.*词)",
        re.IGNORECASE,
    ),
    "auto_parts_compatibility_obfuscation": re.compile(
        r"(?:适配关键词|suitable\s+for|汽车配件|后备箱垫|汽车品牌|涂抹规避|打码|carparts|car\s*mat|车标|车型|主观涂抹)",
        re.IGNORECASE,
    ),
    "design_patent_trade_dress": re.compile(
        r"(?:外观专利|专利|视觉装潢|trade\s*dress|斜纹老花|四角缝线|工程缝线|五金|锁扣|C.{0,3}字形|嵌套管|网格结构|包型|螺旋.*拉链|灌装结构|抽绳设计|双头设计|蜡融灯)",
        re.IGNORECASE,
    ),
    "sports_collegiate_celebrity": re.compile(
        r"(?:大学|university|ncaa|足协|橄榄球|体育联盟|nba|mlb|nhl|nfl|球队|队徽|球衣|乐队|歌手|明星|肖像|名人|wwe)",
        re.IGNORECASE,
    ),
    "boolean_rule_reverse_elim": re.compile(
        r"(?:反向剔除|免审|排除标准|规则\s*1|条件\s*1|满足以下所有|满足任意一条|满足任一|（规则\d+=是）)",
        re.IGNORECASE,
    ),
    "multi_image_open_set": re.compile(
        r"(?:商品主图|轮播图|sku图|第\d+到第\d+张|tro|多图|全图扫描|开放|多规格组合图|ip_names|ip_content)",
        re.IGNORECASE,
    ),
    "fuzzy_ocr_deformation": re.compile(
        r"(?:音节|拼写近似|ocr|遮挡|裁剪|断裂|倒写|变形|模糊|被遮盖|变体|涂抹)",
        re.IGNORECASE,
    ),
}

DERIVATIVE_RE = re.compile(r"(?:二创|二次创作|同人|Q版|衍生|借鉴|风格化|辛普森化)", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            if s:
                rows.append(json.loads(s))
    return rows


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def atomic_write_json(path: Path, obj: Any) -> None:
    atomic_write_text(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def atomic_write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    text = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    if rows:
        text += "\n"
    atomic_write_text(path, text)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_filename(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff._-]+", "_", text.strip())
    return slug.strip("_") or "template"


def normalize_match_key(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"^\d+_", "", s)
    s = re.sub(r"^(?:ip[-_]|ip组-|ip(?=[a-z]))", "", s)
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", s)
    return s


def parse_inline_versions(body_text: str) -> list[str]:
    m = VERSION_HEADER_RE.search(body_text)
    if not m:
        return []
    return [p.strip() for p in re.split(r"[、,\s]+", m.group(1).strip()) if p.strip()]


def compute_family_slug(record: dict[str, Any]) -> str:
    tid = int(record["id"])
    if tid in EXPLICIT_FAMILY_BY_ID:
        return EXPLICIT_FAMILY_BY_ID[tid]
    if tid in SINGLETON_SLUG_OVERRIDES:
        return SINGLETON_SLUG_OVERRIDES[tid]

    title = str(record.get("title") or "").strip()
    s = title
    s = re.sub(r"^(?:IP组-|ip组-|Ip_|IP_|IP-|ip_|ip-)", "", s)
    for _ in range(3):
        nxt = re.sub(
            r"(?:[-_ ](?:prompt|selfmodel|strategy\d*|coarse_recall|highaccuracy|accuracyimprove|"
            r"llm(?:[-_ ]black)?|black|auto|quanliang|img|word|ocr|penalty|copy\d*|background|"
            r"exception|excepmtion|trademark|tradename|copyright|positive|test\d*|ceshi\d*|bushangxian|"
            r"allrule|patent|patentpunish|ver\d+|v\d+|\d{4})|selfmodel|prompt)$",
            "",
            s,
            flags=re.IGNORECASE,
        ).strip()
        if nxt == s or not nxt:
            break
        s = nxt
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", s.lower()).strip("_")
    if not slug:
        slug = f"tpl_{tid:03d}"
    return slug


def unpack_record_versions(raw_record: dict[str, Any], cleaned_body: str) -> list[dict[str, Any]]:
    """Splits records containing `**同一对象的 N 个版本**` into individual versions."""
    raw_id = int(raw_record["id"])
    raw_title = str(raw_record.get("title") or "").strip()
    raw_chars = int(raw_record.get("chars") or 0)
    rel = [str(x) for x in (raw_record.get("rel") or [])]

    inline_hdr = parse_inline_versions(cleaned_body)
    sec_matches = list(re.finditer(r"(?m)^##\s+([^\n]+)\s*$", cleaned_body))

    if inline_hdr and sec_matches:
        versions: list[dict[str, Any]] = []
        for idx, m in enumerate(sec_matches, start=1):
            sub_title = m.group(1).strip()
            start = m.end()
            end = sec_matches[idx].start() if idx < len(sec_matches) else len(cleaned_body)
            sec_body = cleaned_body[start:end].strip()
            versions.append(
                {
                    "id": raw_id,
                    "version_key": f"{raw_id}::{idx}",
                    "sub_index": idx,
                    "title": sub_title,
                    "source_record_title": raw_title,
                    "raw_record_chars": raw_chars,
                    "rel": rel,
                    "cleaned_body": f"## {sub_title}\n\n{sec_body}\n",
                    "inline_versions": inline_hdr,
                    "unpacked_from_inline": True,
                }
            )
        return versions

    return [
        {
            "id": raw_id,
            "version_key": str(raw_id),
            "sub_index": 1,
            "title": raw_title,
            "source_record_title": raw_title,
            "raw_record_chars": raw_chars,
            "rel": rel,
            "cleaned_body": cleaned_body.strip() + "\n",
            "inline_versions": inline_hdr,
            "unpacked_from_inline": False,
        }
    ]


# ---------------------------------------------------------------------------
# Assert Reference Asset Indexer (Read-Only Cross-Check)
# ---------------------------------------------------------------------------
class AssertAssetIndex:
    """Indexes Assert's approved refs, supplements, and backlog for matching."""

    def __init__(self, root: Path) -> None:
        self.by_template_norm: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.by_name_norm: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._load(root)

    def _add_key(self, mapping: dict[str, list[dict[str, Any]]], key: str, item: dict[str, Any]) -> None:
        if len(key) < 3:
            return
        mapping[key].append(item)

    def _load(self, root: Path) -> None:
        approved_by_ent: dict[str, dict[str, Any]] = {}
        approved_by_canon: dict[str, dict[str, Any]] = {}
        for row in load_jsonl(root / "manifests" / "standard_images_1119" / "approved_references.jsonl"):
            approved_by_ent[str(row.get("entity_id") or "")] = row
            approved_by_canon[str(row.get("canonical_entity_id") or "")] = row

        sch_path = root / "manifests" / "sch96_ip_supplement.json"
        if sch_path.exists():
            sch = json.loads(sch_path.read_text(encoding="utf-8"))
            for ent in sch.get("entities", []):
                eid = str(ent.get("entity_id") or "")
                item = {
                    "source": "sch96_ip_supplement",
                    "entity_id": eid,
                    "name_en": ent.get("name_en"),
                    "name_zh": ent.get("name_zh"),
                    "fetch_ok": bool(ent.get("fetch_ok")),
                    "local_path": ent.get("local_path") or "",
                    "raw_svg_path": ent.get("raw_svg_path") or "",
                    "template_ids": ent.get("template_ids") or [],
                    "approved": False,
                }
                for t in ent.get("template_ids") or []:
                    self._add_key(self.by_template_norm, normalize_match_key(str(t)), item)
                for n in (eid, str(ent.get("name_en") or ""), str(ent.get("name_zh") or "")):
                    self._add_key(self.by_name_norm, normalize_match_key(n), item)

        sp_path = root / "manifests" / "sports_crests_supplement.json"
        if sp_path.exists():
            sp = json.loads(sp_path.read_text(encoding="utf-8"))
            for lg in sp.get("leagues", []):
                item = {
                    "source": "sports_crests_supplement_league",
                    "entity_id": lg.get("entity_id"),
                    "name_en": lg.get("name_en"),
                    "name_zh": lg.get("name_zh"),
                    "fetch_ok": bool(lg.get("fetch_ok")),
                    "local_path": lg.get("local_path") or "",
                    "template_ids": lg.get("template_ids") or [],
                    "approved": False,
                }
                for t in lg.get("template_ids") or []:
                    self._add_key(self.by_template_norm, normalize_match_key(str(t)), item)
                for n in (str(lg.get("league_id") or ""), str(lg.get("name_en") or "")):
                    self._add_key(self.by_name_norm, normalize_match_key(n), item)

        for row in load_jsonl(root / "manifests" / "standard_image_links.jsonl"):
            eid = str(row.get("entity_id") or "")
            canon = str(row.get("canonical_entity_id") or "")
            app = approved_by_ent.get(eid) or approved_by_canon.get(canon)
            status = str(row.get("status") or "")
            item = {
                "source": "standard_image_links",
                "entity_id": eid,
                "canonical_entity_id": canon or None,
                "title": row.get("title"),
                "source_domain": row.get("source_domain"),
                "status": status,
                "approved": bool(app) or status == "approved_reference",
                "images": (app or {}).get("images") or [],
                "template_ids": row.get("template_ids") or [],
            }
            for t in row.get("template_ids") or []:
                self._add_key(self.by_template_norm, normalize_match_key(str(t)), item)
            title = str(row.get("title") or "")
            for part in re.split(r"[（）()／/]", title):
                k = normalize_match_key(part)
                if len(k) >= 4:
                    self._add_key(self.by_name_norm, k, item)

    def match_family(self, family_slug: str, members: list[dict[str, Any]]) -> dict[str, Any]:
        if family_slug.startswith("test_") or family_slug.startswith("aux_"):
            return {
                "coverage_status": "not_applicable_non_ip_or_test",
                "approved_matches": [],
                "supplement_matches": [],
                "backlog_matches": [],
            }

        keys: set[str] = {normalize_match_key(family_slug)}
        for m in members:
            keys.add(normalize_match_key(m["title"]))
            for iv in m.get("inline_versions") or []:
                keys.add(normalize_match_key(iv))
        keys = {k for k in keys if len(k) >= 3}

        seen: set[tuple[str, str]] = set()
        matches: list[dict[str, Any]] = []
        for k in sorted(keys):
            for hit in self.by_template_norm.get(k, []) + self.by_name_norm.get(k, []):
                sig = (str(hit.get("source")), str(hit.get("entity_id")))
                if sig not in seen:
                    seen.add(sig)
                    matches.append(hit)

        approved = [m for m in matches if m.get("approved")][:10]
        supplements = [
            m
            for m in matches
            if m.get("source", "").startswith("sch96_") or m.get("source", "").startswith("sports_")
        ][:10]
        backlog = [
            m
            for m in matches
            if m.get("source") == "standard_image_links" and not m.get("approved")
        ][:12]

        if approved:
            status = "approved_in_assert"
        elif any(s.get("fetch_ok") for s in supplements):
            status = "supplement_asset_available_pending_approval"
        elif backlog:
            status = "backlog_needs_review"
        else:
            status = "no_assert_match"

        return {
            "coverage_status": status,
            "approved_matches": approved,
            "supplement_matches": supplements,
            "backlog_matches": backlog,
        }


# ---------------------------------------------------------------------------
# Full-Text Template Diagnosis & Latest-Version Selection
# ---------------------------------------------------------------------------
def diagnose_template(
    ver: dict[str, Any],
    family_slug: str,
    version_cleanups: list[dict[str, str]],
) -> dict[str, Any]:
    tid = int(ver["id"])
    title = str(ver["title"]).strip()
    rel = list(ver.get("rel") or [])
    cleaned_body = str(ver["cleaned_body"])
    body_no_hdr = re.sub(r"^##\s+[^\n]+\n+", "", cleaned_body).strip()
    body_plain = re.sub(r"(?m)^>\s?", "", body_no_hdr).strip()
    chars = len(body_plain)
    raw_chars = int(ver.get("raw_record_chars") or chars)

    hygiene_flags: list[str] = []
    findings: list[str] = []

    # Cross-entity paste bugs
    paste_bugs = [
        msg
        for bug_id, sub_title, _code, msg in CROSS_ENTITY_PASTE_SIGNATURES
        if bug_id == tid and (sub_title is None or sub_title == title)
    ]
    if paste_bugs:
        hygiene_flags.append("cross_entity_paste_bug")
        findings.extend(paste_bugs)

    # Trivial / empty body
    if chars < 20:
        hygiene_flags.append("empty_or_trivial_body")
        findings.append(f"正文过短（清洗后 {chars} 字），实质仅为标题占位，无法用于审核执行。")

    # False `rel` entity bindings
    bad_rels: list[str] = []
    for pat, bad_set, msg in KNOWN_BAD_REL_BY_TITLE_HINT:
        if (pat.search(title) or pat.search(str(ver.get("source_record_title") or ""))) and (set(rel) & bad_set):
            bad_rels.append(msg)
    if bad_rels:
        hygiene_flags.append("rel_metadata_mismatch")
        findings.extend(bad_rels)

    # Empty variable placeholders
    if EMPTY_PLACEHOLDER_RE.search(body_no_hdr):
        hygiene_flags.append("empty_placeholder_variable")
        findings.append("存在未填充空占位符（如 `根据 来判断`、`名称为 ，`、`商户标题（）`）。")

    # Broken JSON schema / output contract
    if BROKEN_JSON_RE.search(body_no_hdr):
        hygiene_flags.append("broken_json_schema")
        findings.append("JSON 输出契约存在语法或拼写错误（如 `jason`、`ture`/`treue`、`default形式`、圆括号/中文冒号等）。")

    # Typos & logic bugs
    for pat, msg in TYPO_PATTERNS:
        if msg == "检查表达完整性":
            continue
        if pat.search(title) or pat.search(body_no_hdr):
            if "typo_or_logic_defect" not in hygiene_flags:
                hygiene_flags.append("typo_or_logic_defect")
            findings.append(msg)

    if tid == 138:
        hygiene_flags.append("typo_or_logic_defect")
        findings.append("逻辑自相矛盾：正文只有“问题1”，结尾却要求“汇总问题1和问题2的结果”。")
    if tid in (398, 399, 400):
        hygiene_flags.append("typo_or_logic_defect")
        findings.append("布尔逻辑高危缺陷：Molson 多个子品牌（Miller / Lite 等）本应为“满足任一 (OR)”，模板误写成“满足以下所有条件 (AND)”。")
    if tid in (442, 443):
        hygiene_flags.append("duplicate_role_header")
        findings.append("角色设定段落重复粘贴了两遍。")
    if tid == 445 and raw_chars == 4:
        findings.append("注：原始台账记录 `chars=4` 元数据失真，实盘完整正文为 4,272 字符（非截断）。")

    # Disposition
    if family_slug.startswith("test_"):
        disposition = "quarantine_test_junk"
    elif "cross_entity_paste_bug" in hygiene_flags:
        disposition = "quarantine_paste_bug"
    elif "empty_or_trivial_body" in hygiene_flags:
        disposition = "needs_body_completion"
    elif family_slug.startswith("aux_"):
        disposition = "route_auxiliary_non_ip"
    else:
        disposition = "active_ip"

    # Archetypes
    combined = f"{title}\n{body_no_hdr}"
    if disposition == "route_auxiliary_non_ip":
        archetypes = ["non_ip_auxiliary"]
    else:
        archetypes = [k for k, pat in ARCHETYPE_PATTERNS.items() if pat.search(combined)]
        if not archetypes:
            archetypes = ["brand_logo_trademark"]

    supports_derivative = bool(DERIVATIVE_RE.search(combined))

    # Full-text rubric vulnerabilities (specific to inter-class separation)
    if disposition == "active_ip" and chars < 110:
        hygiene_flags.append("underspecified_rubric")
        findings.append(f"判据过于笼统（清洗后 {chars} 字）：仅一句宽泛提问，缺少专属强锚点、排除词与宿主边界定义。")

    if disposition == "active_ip":
        if STYLE_ONLY_TRIGGER_RE.search(body_no_hdr):
            hygiene_flags.append("style_only_trigger_risk")
            findings.append("类间误杀风险（唯画风触发）：条款允许仅凭“符合作品独特艺术风格/画风二创”判定侵权，易将同画风原创 OC 误判。")
        if ESCAPE_HATCH_RE.search(body_no_hdr):
            hygiene_flags.append("weak_anchor_or_escape_hatch")
            findings.append("兜底松弛风险（主观逃生舱）：条款含“除非直观可判断 / 合理理解为指向”等模糊兜底，易架空前置特征组合约束。")
        if (
            chars >= 110
            and not EXCLUSION_GUARD_RE.search(body_no_hdr)
            and (set(archetypes) & {"anime_derivative_two_step", "common_word_disambiguation", "design_patent_trade_dress", "sports_collegiate_celebrity"} or supports_derivative)
        ):
            hygiene_flags.append("missing_exclusion_clause")
            findings.append("缺少反向排除/豁免条款：全文未明确背景宿主隔离、通用属性排除或证据不足判 false 的边界。")

    # Inter-class risk assessment
    high_risk_arches = {
        "anime_derivative_two_step",
        "common_word_disambiguation",
        "design_patent_trade_dress",
    }
    if disposition in {"quarantine_test_junk", "needs_body_completion"}:
        inter_class_risk = "blocked_hygiene"
    elif (
        (set(archetypes) & high_risk_arches)
        or supports_derivative
        or (set(hygiene_flags) & {"underspecified_rubric", "style_only_trigger_risk", "weak_anchor_or_escape_hatch"})
    ):
        inter_class_risk = "high"
    elif set(archetypes) & {
        "auto_parts_compatibility_obfuscation",
        "subject_host_isolation",
        "sports_collegiate_celebrity",
        "fuzzy_ocr_deformation",
    }:
        inter_class_risk = "medium"
    else:
        inter_class_risk = "low"

    return {
        "id": tid,
        "version_key": ver["version_key"],
        "sub_index": ver["sub_index"],
        "title": title,
        "source_record_title": ver["source_record_title"],
        "chars": chars,
        "raw_record_chars": raw_chars,
        "is_truncated": False,
        "rel": rel,
        "family_slug": family_slug,
        "inline_versions": ver.get("inline_versions") or [],
        "unpacked_from_inline": bool(ver.get("unpacked_from_inline")),
        "export_cleanups_count": len(version_cleanups),
        "export_cleanups": version_cleanups,
        "cleaned_body": cleaned_body,
        "disposition": disposition,
        "hygiene_flags": sorted(set(hygiene_flags)),
        "findings": findings,
        "archetypes": archetypes,
        "supports_derivative": supports_derivative,
        "inter_class_risk": inter_class_risk,
    }


def score_member_for_latest(diag: dict[str, Any]) -> tuple[tuple[int, int, int, int, int, int, int, int], str]:
    """Ranks unpacked versions inside a family so the latest, cleanest version wins."""
    t_lower = diag["title"].lower()
    disp = diag["disposition"]
    flags = set(diag["hygiene_flags"])

    is_healthy = 1 if disp in {"active_ip", "route_auxiliary_non_ip"} else 0
    is_test_or_copy = (
        1
        if re.search(r"(?:^test|[_-]test\b|ceshi|copy\d*|coarse_recall|bushangxian|_test_)", t_lower)
        else 0
    )

    ver_num = 1
    m_v = re.search(r"(?:^|[_-]|(?<=[a-z]))v(?:er)?(\d+)\b", t_lower)
    m_trail = re.search(
        r"(?:mianshen|charms|pikmin|nirvana|ralphlauren|tommy|myheroacademia|onepiece|band|utah|logo|anpanman)(\d+)$",
        t_lower,
    )
    if m_v:
        ver_num = int(m_v.group(1))
    elif m_trail:
        ver_num = int(m_trail.group(1))

    spec_score = 0
    if re.search(r"(?:1103|0511|0409|0325)", t_lower):
        spec_score += 4
    if re.search(r"(?:highaccuracy|accuracyimprove|strict|allrule|patent|exception|excepmtion)", t_lower):
        spec_score += 3
    if re.search(r"(?:selfmodel|strategy|new|grounding|consistent)", t_lower):
        spec_score += 2

    severe_defects = len(flags & {"cross_entity_paste_bug", "empty_or_trivial_body", "underspecified_rubric", "broken_json_schema"})
    cleanliness = -severe_defects
    chars = int(diag["chars"])
    tid = int(diag["id"])
    sub_idx = int(diag["sub_index"])

    score_tuple = (is_healthy, 1 - is_test_or_copy, ver_num, spec_score, cleanliness, chars, tid, sub_idx)

    reasons: list[str] = []
    if is_healthy:
        reasons.append("状态健康（非错贴/非空壳）")
    else:
        reasons.append(f"存在阻塞缺陷（{disp}）")
    if is_test_or_copy == 0:
        reasons.append("非 test/ceshi/copy 测试分支")
    if ver_num > 1:
        reasons.append(f"显式版本号 v{ver_num}")
    if spec_score > 0:
        reasons.append(f"含生产专项/迭代后缀（加权 +{spec_score}）")
    reasons.append(f"清洗后正文长度 chars={chars}")

    return score_tuple, "；".join(reasons)


def build_inter_class_recommendations(family_diag: dict[str, Any]) -> list[str]:
    arches = set(family_diag["archetypes"])
    flags = set(family_diag["all_hygiene_flags"])
    recs: list[str] = []
    if "anime_derivative_two_step" in arches or family_diag["supports_derivative"]:
        recs.append(
            "【二创类间防混淆】将特征拆分为 T1 独占强锚点（专属徽记/标志性发饰/瞳纹/武器）+ T2 结构骨架（刘海分流/非对称配色）+ T3 泛化属性（发色/瞳色/校服/画风）；"
            "造数时配套构造「锁 T1/T2 换装或 Q 版正例」与「锁画风/锁 T3 属性词但无 T1 的近邻角色/原创 OC 负例」，严禁仅凭画风或发色判侵权。"
        )
    if "style_only_trigger_risk" in flags:
        recs.append(
            "【收紧唯画风触发条款】删除或降级“仅凭画风/艺术风格即可认定二创”的分支，要求至少 1 个 T1 独占锚点或 2 个 T2 结构拓扑组合成立方可判 true。"
        )
    if "weak_anchor_or_escape_hatch" in flags:
        recs.append(
            "【去除主观逃生舱】替换“除非直观可判断 / 合理理解为指向”等主观逃生短语，将其固化为具体的无色彩轮廓/结构拓扑检验条件。"
        )
    if "missing_exclusion_clause" in flags:
        recs.append(
            "【补充反向排除条款】建议显式补齐「仅命中发色/服装等通用 T3 特征」「背景/宿主道具出现」「局部裁切或遮挡导致证据不足」均应判定为 false。"
        )
    if "common_word_disambiguation" in arches:
        recs.append(
            "【常见词/单字母消歧】成对构造「独立放大商标使用」vs「普通英文句子修饰/26字母通用吊坠/地名日常义（贝壳、帕尼尼三明治、单词内字母）」硬负例。"
        )
    if "design_patent_trade_dress" in arches:
        recs.append(
            "【无 Logo 外观专利/Trade Dress】列出必备结构件的几何合取（ALL-AND）验证清单，并补充“轮廓相近但缺少专属五金/缝线/连接方式”的行业通款负例。"
        )
    if "subject_host_isolation" in arches:
        recs.append(
            "【宿主与背景隔离】补充“标识仅出现在包装盒、展示架、模特服饰或透明手机壳透出底层设备”的对照负例，强制先定位售卖商品主体边界。"
        )
    if "auto_parts_compatibility_obfuscation" in arches:
        recs.append(
            "【汽配适配豁免 vs 涂抹规避】区分标题中合理的 `for / fits / suitable for <品牌>` 适配说明（主体干净 -> false）与主体实物商标/涂抹马赛克规避（-> true）。"
        )
    if "image_title_conflict" in arches:
        recs.append(
            "【图文冲突优先视觉】加入“标题堆砌品牌词但图片主体完全干净”的负例，绑定 `image_overrides_title` 规则避免标题关键词抢答。"
        )
    if "fuzzy_ocr_deformation" in arches:
        recs.append(
            "【遮挡与变形 OCR】加入局部遮挡、字母倒写、形近词替换的正负对照对，区分恶意形近仿冒与语义无关的常规词汇。"
        )
    if "sports_collegiate_celebrity" in arches:
        recs.append(
            "【体育/高校/名人】补充同配色普通运动条纹/通用球衣编号（无专属队徽/校徽/肖像组合）负例，避免普通校园风或数字球衣误罚。"
        )
    if "underspecified_rubric" in flags:
        recs.append(
            "【规则补全】当前主模板仅一句宽泛提问，类间边界完全未定义；建议先补充正例必需锚点清单与常见误召回排除条款，再进入训练或线上评测。"
        )
    if not recs:
        recs.append(
            "【常规商标/版权控制】建议配对同载体标准参考图与高相似近邻商标/普通图案负例，并校验商品主体归属与 JSON 输出格式一致性。"
        )
    return recs


# ---------------------------------------------------------------------------
# Rendering Family Files
# ---------------------------------------------------------------------------
def render_latest_template_md(
    family_slug: str,
    display_name: str,
    selected: dict[str, Any],
    members: list[dict[str, Any]],
    selection_reason: str,
    is_parallel: bool,
) -> str:
    lines: list[str] = [
        f"# {display_name}（默认主模板 · 清洗后完整全文）",
        "",
        f"- **同族目录 (`family_slug`)**: `{family_slug}`",
        f"- **默认选中版本**: `id={selected['id']}` (`{selected['version_key']}`) · `{selected['title']}`",
        f"- **选中依据**: {selection_reason}",
        f"- **当前处置状态**: `{selected['disposition']}`",
        f"- **清洗后字符数**: `{selected['chars']}` 字（导出硬编码清理 `{selected['export_cleanups_count']}` 处）",
    ]
    if is_parallel and len(members) > 1:
        others = [f"`{m['version_key']}` `{m['title']}`" for m in members if m["version_key"] != selected["version_key"]]
        lines.append(f"- **同族并行子场景（非简单替代关系）**: {', '.join(others)}")
    lines.extend(["", "---", "", selected["cleaned_body"].strip(), ""])
    return "\n".join(lines)


def render_family_diagnosis_md(
    family_diag: dict[str, Any],
    members: list[dict[str, Any]],
    version_filenames: dict[str, str],
) -> str:
    slug = family_diag["family_slug"]
    display = family_diag["display_name"]
    sel_key = family_diag["selected_latest_version_key"]
    sel_id = family_diag["selected_latest_id"]
    sel_title = family_diag["selected_latest_title"]
    asset_cov = family_diag["assert_asset_coverage"]

    lines: list[str] = [
        f"# 审核模板诊断报告：{display} (`{slug}`)",
        "",
        "## 1. 同族与版本选择概览",
        "",
        f"- **同族成员数**: {len(members)} 个独立版本（来源记录 ID: {', '.join(str(i) for i in family_diag['source_record_ids'])}）",
        f"- **默认采用版本**: `id={sel_id}` (`{sel_title}`)",
        f"- **版本判定置信度**: `{family_diag['version_selection_confidence']}`",
        f"- **版本选择理由**: {family_diag['version_selection_reason']}",
        f"- **导出商品硬编码清理**: 共自动将 {family_diag['total_export_cleanups']} 处导出时注入的商品标题/属性还原为 `#GOODS_TEXT_INFO#` 等占位符（不计入模板缺陷）",
        f"- **并行子场景标记**: {'是（该审核对象下存在不同品类/任务边界的子模板，请结合 `versions/` 一并查看）' if family_diag['parallel_sub_scopes'] else '否（同族主要为同一任务的迭代版本或别名）'}",
        "",
        "## 2. 逐版本完整诊断明细",
        "",
        "| 版本键 | 模板标题 | 选中 | 清洗后字数 | 导出清理 | 处置结论 | 审核原型 | 模板自身缺陷与风险 |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]

    for m in members:
        mark = "✅" if m["version_key"] == sel_key else ""
        arches = ", ".join(m["archetypes"])
        issue_txt = "；".join(m["findings"]) if m["findings"] else "无明显模板缺陷"
        issue_txt = issue_txt.replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| `{m['version_key']}` | `{m['title']}` | {mark} | {m['chars']} | {m['export_cleanups_count']} 处 | `{m['disposition']}` | `{arches}` | {issue_txt} |"
        )

    lines.extend(
        [
            "",
            "## 3. 判断方案与类间区分风险评估",
            "",
            f"- **主要审核原型**: {', '.join(f'`{a}`' for a in family_diag['archetypes'])}",
            f"- **是否显式涉及二创/同人/借鉴**: {'是' if family_diag['supports_derivative'] else '否'}",
            f"- **类间混淆风险等级**: `{family_diag['inter_class_risk']}`",
            f"- **模板自身缺陷标签**: {', '.join(f'`{f}`' for f in family_diag['all_hygiene_flags']) if family_diag['all_hygiene_flags'] else '无'}",
            "",
            "### 规则与数据构造建议",
            "",
        ]
    )
    for rec in family_diag["recommendations"]:
        lines.append(f"- {rec}")

    lines.extend(
        [
            "",
            "## 4. Assert 标准图库资产对齐状态",
            "",
            f"- **覆盖状态**: `{asset_cov['coverage_status']}`",
        ]
    )
    if asset_cov["approved_matches"]:
        lines.append("- **已批准标准参考图**:")
        for item in asset_cov["approved_matches"]:
            lines.append(f"  - `{item.get('entity_id')}` (`{item.get('canonical_entity_id')}`) → `{item.get('images')}`")
    if asset_cov["supplement_matches"]:
        lines.append("- **补充参考图（待正式批准入标）**:")
        for item in asset_cov["supplement_matches"]:
            lines.append(
                f"  - `{item.get('entity_id')}` ({item.get('name_zh')} / {item.get('name_en')}) · fetch_ok=`{item.get('fetch_ok')}` · `{item.get('local_path')}`"
            )
    if asset_cov["backlog_matches"]:
        lines.append(f"- **1119 待办清单命中 ({len(asset_cov['backlog_matches'])} 条展示)**:")
        for item in asset_cov["backlog_matches"][:8]:
            lines.append(f"  - `{item.get('entity_id')}` · `{item.get('title')}` · status=`{item.get('status')}`")
    if (
        not asset_cov["approved_matches"]
        and not asset_cov["supplement_matches"]
        and not asset_cov["backlog_matches"]
    ):
        lines.append("- 当前 Assert 清单中未检索到同名/同模板已建档参考图（或属于非特定实体通用模板）。")

    if len(members) >= 2:
        lines.extend(["", "## 5. 同族版本文件索引", ""])
        for m in members:
            fname = version_filenames[m["version_key"]]
            tag = "（默认采用）" if m["version_key"] == sel_key else ""
            lines.append(f"- [`{fname}`]({fname}) — `{m['version_key']}`, `chars={m['chars']}` {tag}")

    return "\n".join(lines) + "\n"


def render_version_file_md(diag: dict[str, Any], is_selected: bool) -> str:
    lines = [
        f"# 模板版本：`{diag['title']}` (`{diag['version_key']}`)",
        "",
        f"- **所属同族**: `{diag['family_slug']}`",
        f"- **是否默认主版本**: {'是' if is_selected else '否'}",
        f"- **处置结论**: `{diag['disposition']}`",
        f"- **清洗后字符数**: `{diag['chars']}`（导出清理 `{diag['export_cleanups_count']}` 处）",
        f"- **关联实体 (`rel`)**: `{diag['rel']}`",
        f"- **模板自身缺陷标签**: `{diag['hygiene_flags']}`",
        "",
        "## 诊断要点",
        "",
    ]
    if diag["findings"]:
        for f in diag["findings"]:
            lines.append(f"- {f}")
    else:
        lines.append("- 未发现明显模板结构或逻辑缺陷。")
    if diag["export_cleanups"]:
        lines.extend(["", "## 导出硬编码清理记录（非模板缺陷）", ""])
        for c in diag["export_cleanups"]:
            lines.append(f"- `{c['rule']}`: `{c['before_preview']}` → `{c['after_token']}`")
    lines.extend(["", "---", "", diag["cleaned_body"].strip(), ""])
    return "\n".join(lines)


def render_root_readme(
    families: list[dict[str, Any]],
    all_diags: list[dict[str, Any]],
    manifest: dict[str, Any],
) -> str:
    disp_counts = manifest["disposition_counts"]
    flag_counts = manifest["hygiene_flag_counts"]
    risk_counts = manifest["inter_class_risk_counts"]
    cov_counts = manifest["assert_coverage_counts"]

    lines: list[str] = [
        "# Assert 审核模板整理与诊断总库 (`templete/`) — 461 原始记录 / 全量完整版",
        "",
        (
            f"> 生成时间：{manifest['generated_at']} · 原始记录：**{manifest['total_raw_records']}** 条 → 拆包独立版本：**{manifest['total_unpacked_versions']}** 个 · "
            f"归并同族目录：**{manifest['total_families']}** 个 · 导出硬编码清理：**{manifest['total_export_cleanups']}** 处（涉及 {manifest['records_with_export_cleanups']} 条原始记录） · "
            f"可视化审核画廊：[`review_dashboard.html`](review_dashboard.html)"
        ),
        "",
        "## 1. 全量清理与归并规则",
        "",
        "- **导出残留自动清洗**：原始导出文件在部分模板中混入了运行时注入的商品标题、`p_spec_name` 规格 JSON 及商品属性数组；脚本已在 [`audit_prompts_461_full_cleaned.jsonl`](../manifests/audit_prompts_461_full_cleaned.jsonl) 中将其统一还原为 `#GOODS_TEXT_INFO#` / `#GOODS_PROPERTIES#` / `#GOODS_SPEC#` / `#GOODS_CONTEXT#` / `#BRAND_LIST#`，且**不再计为模板自身缺陷**。",
        "- **内联多版本完整拆包**：将 54 条包含 `**同一对象的 N 个版本**` 的合并记录拆包为各自独立的完整模板正文（共 **535** 个独立版本），按同审核对象归并至 **352** 个同族目录，严格隔离同名撞车（如 `dc_comics` vs `dc_shoes`、`university_of_michigan` vs `michigan_state`）。",
        "- **默认最新版本优先**：按「健康可用 > 非 `test/ceshi/copy` 分支 > 显式版本号 > 生产专项/日期后缀 > 清洗后正文长度」自动选出默认主模板写入 `latest_template.md`。",
        "",
        "## 2. 全库汇总统计",
        "",
        "### 2.1 模板处置分布（535 个独立版本逐条统计）",
        "",
        "| 处置状态 | 数量 | 说明 |",
        "|---|---:|---|",
        f"| `active_ip` | {disp_counts.get('active_ip', 0)} | 有效 IP 审核模板（含全量规则文本） |",
        f"| `route_auxiliary_non_ip` | {disp_counts.get('route_auxiliary_non_ip', 0)} | 非具体商品视觉 IP 的辅助/法务/反爬/品牌关联模板 |",
        f"| `quarantine_paste_bug` | {disp_counts.get('quarantine_paste_bug', 0)} | 存在跨实体错贴 Bug（标题与正文目标冲突，必须隔离修复） |",
        f"| `quarantine_test_junk` | {disp_counts.get('quarantine_test_junk', 0)} | 测试垃圾模板（`5678`、`NyeTest*`、`test111`、`lingjinglan_test`、`IPgeneraltest`） |",
        f"| `needs_body_completion` | {disp_counts.get('needs_body_completion', 0)} | 空壳占位模板（如 `397 ip_molson_mianshen`） |",
        "",
        "### 2.2 模板自身缺陷与类间边界隐患（已排除导出硬编码干扰）",
        "",
        "| 缺陷/隐患类型 | 命中版本数 | 典型表现 |",
        "|---|---:|---|",
    ]
    flag_notes = {
        "missing_exclusion_clause": "高风险域/二创模板缺少宿主隔离、通用属性排除或证据不足判 false 的边界条款",
        "rel_metadata_mismatch": "关联实体字段 `rel` 存在机械子串误绑（如 `FMOD`、`Mini`、`Audi`、`Lion Air`、`Poly`、`艾莎` 等）",
        "underspecified_rubric": "正文字数过短（<110字），只有泛问句而无判据锚点或排除条件",
        "broken_json_schema": "`jason`、`ture`/`treue`、`default形式`、缺引号/全角冒号/圆括号等输出契约损坏",
        "typo_or_logic_defect": "拼写错误、前后题号矛盾（如 `IP_RATT`）、或把 OR 误写成 ALL-AND（如 `molson_mianshen2~4`）",
        "weak_anchor_or_escape_hatch": "含“除非直观可判断 / 合理理解为指向”等模糊逃生舱，易架空前置特征约束",
        "style_only_trigger_risk": "允许仅凭“符合作品独特艺术风格/画风二创”触发，易将同画风原创 OC 误判",
        "cross_entity_paste_bug": "跨实体复制粘贴错误（标题与正文检查目标完全不一致）",
        "empty_placeholder_variable": "变量槽位空缺（如 `根据 来判断`、`商户标题（）`）",
        "duplicate_role_header": "角色设定段落重复粘贴",
        "empty_or_trivial_body": "实质无规则正文",
    }
    for flag, cnt in sorted(flag_counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"| `{flag}` | {cnt} | {flag_notes.get(flag, '')} |")

    lines.extend(
        [
            "",
            "### 2.3 类间混淆风险 & Assert 参考图对齐统计（按 352 个同族）",
            "",
            f"- **类间风险等级分布**: `high` = **{risk_counts.get('high', 0)}** · `medium` = **{risk_counts.get('medium', 0)}** · `low` = **{risk_counts.get('low', 0)}** · `blocked_hygiene` = **{risk_counts.get('blocked_hygiene', 0)}**",
            f"- **Assert 标准参考图对齐**: `approved_in_assert` = **{cov_counts.get('approved_in_assert', 0)}** · `supplement_asset_available_pending_approval` = **{cov_counts.get('supplement_asset_available_pending_approval', 0)}** · `backlog_needs_review` = **{cov_counts.get('backlog_needs_review', 0)}** · `no_assert_match` = **{cov_counts.get('no_assert_match', 0)}** · `not_applicable_non_ip_or_test` = **{cov_counts.get('not_applicable_non_ip_or_test', 0)}**",
            "",
            "## 3. 跨实体错贴 Bug（必修清单）",
            "",
            "| 版本键 | 模板标题 | 同族目录 | 错贴诊断 |",
            "|---|---|---|---|",
        ]
    )
    for d in all_diags:
        if "cross_entity_paste_bug" in d["hygiene_flags"]:
            msg = "；".join(d["findings"])
            lines.append(f"| `{d['version_key']}` | `{d['title']}` | [`{d['family_slug']}/`]({d['family_slug']}/diagnosis.md) | {msg} |")

    lines.extend(
        [
            "",
            f"## 4. 全部同族目录索引（共 {len(families)} 个子目录）",
            "",
            "| 同族目录 | 审核对象 | 版本数 | 默认主版本 | 类间风险 | Assert 状态 | 文档 |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for fam in families:
        lines.append(
            f"| `{fam['family_slug']}` | {fam['display_name']} | {fam['member_count']} | `{fam['selected_latest_version_key']}` `{fam['selected_latest_title']}` | `{fam['inter_class_risk']}` | `{fam['assert_asset_coverage']['coverage_status']}` | [主模板]({fam['family_slug']}/latest_template.md) · [诊断]({fam['family_slug']}/diagnosis.md) |"
        )

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------
def build_template_library(
    raw_path: Path = DEFAULT_RAW_PATH,
    cleaned_path: Path = DEFAULT_CLEANED_PATH,
    cleanup_report_path: Path = DEFAULT_CLEANUP_REPORT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    manifest_out: Path = DEFAULT_MANIFEST_OUT,
) -> dict[str, Any]:
    raw_records = load_jsonl(raw_path)
    if not raw_records:
        raise ValueError(f"No records loaded from {raw_path}")

    ids = [int(r["id"]) for r in raw_records]
    expected_ids = list(range(1, len(raw_records) + 1))
    missing_ids = sorted(set(expected_ids) - set(ids))
    duplicate_ids = sorted(tid for tid, cnt in Counter(ids).items() if cnt > 1)
    if len(raw_records) != 461 or missing_ids or duplicate_ids:
        raise ValueError(
            f"Input integrity check failed: count={len(raw_records)}, missing={missing_ids}, dup={duplicate_ids}"
        )

    asset_index = AssertAssetIndex(PROJECT_ROOT)

    cleaned_records: list[dict[str, Any]] = []
    cleanup_entries: list[dict[str, Any]] = []
    cleanup_rule_counts: Counter[str] = Counter()
    total_cleanups = 0

    raw_by_id: dict[int, dict[str, Any]] = {}
    cleaned_by_id: dict[int, dict[str, Any]] = {}
    cleanups_by_id: dict[int, list[dict[str, str]]] = {}
    groups_raw: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for r in raw_records:
        tid = int(r["id"])
        raw_text = str(r.get("body") if r.get("body") is not None else r.get("body_head") or "")
        cleaned_text, cleanups = clean_export_artifacts(raw_text, tid)
        raw_by_id[tid] = r
        cleanups_by_id[tid] = cleanups
        cleaned_rec = {
            **r,
            "body": cleaned_text,
            "chars_cleaned": len(cleaned_text),
            "export_cleanups_count": len(cleanups),
        }
        cleaned_records.append(cleaned_rec)
        cleaned_by_id[tid] = cleaned_rec

        if cleanups:
            total_cleanups += len(cleanups)
            for c in cleanups:
                cleanup_rule_counts[c["rule"]] += 1
            cleanup_entries.append(
                {
                    "id": tid,
                    "title": r["title"],
                    "cleanups_count": len(cleanups),
                    "cleanups": cleanups,
                }
            )

        slug = compute_family_slug(r)
        groups_raw[slug].append(r)

    atomic_write_jsonl(cleaned_path, cleaned_records)
    atomic_write_json(
        cleanup_report_path,
        {
            "schema": "export_cleanup_report_v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_raw_records": len(raw_records),
            "records_cleaned": len(cleanup_entries),
            "total_cleanups": total_cleanups,
            "rule_counts": dict(sorted(cleanup_rule_counts.items(), key=lambda x: (-x[1], x[0]))),
            "records": cleanup_entries,
        },
    )

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_diags: list[dict[str, Any]] = []
    family_summaries: list[dict[str, Any]] = []
    disp_counts: Counter[str] = Counter()
    flag_counts: Counter[str] = Counter()
    risk_counts: Counter[str] = Counter()
    cov_counts: Counter[str] = Counter()

    for slug in sorted(groups_raw.keys()):
        fam_raw_rows = sorted(groups_raw[slug], key=lambda r: int(r["id"]))
        fam_cleaned_rows = [cleaned_by_id[int(r["id"])] for r in fam_raw_rows]

        members_diag: list[dict[str, Any]] = []
        for raw_r, clean_r in zip(fam_raw_rows, fam_cleaned_rows):
            tid = int(raw_r["id"])
            raw_text = str(raw_r.get("body") if raw_r.get("body") is not None else raw_r.get("body_head") or "")
            raw_versions = unpack_record_versions(raw_r, raw_text)
            clean_versions = unpack_record_versions(clean_r, str(clean_r["body"]))
            for rv, cv in zip(raw_versions, clean_versions):
                _, v_cleanups = clean_export_artifacts(rv["cleaned_body"], tid)
                members_diag.append(diagnose_template(cv, slug, v_cleanups))

        scored = []
        for d in members_diag:
            sc, rsn = score_member_for_latest(d)
            scored.append((sc, rsn, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        _, sel_reason, selected = scored[0]
        is_parallel = slug in PARALLEL_SUB_SCOPE_FAMILIES

        if len(members_diag) == 1:
            confidence = "single"
        elif is_parallel:
            confidence = "parallel_sub_scopes"
        elif selected["disposition"] in {"active_ip", "route_auxiliary_non_ip"}:
            confidence = "high"
        else:
            confidence = "medium"

        for d in members_diag:
            d["is_selected_latest"] = d["version_key"] == selected["version_key"]
            disp_counts[d["disposition"]] += 1
            for fl in d["hygiene_flags"]:
                flag_counts[fl] += 1
            all_diags.append(d)

        display_name = FAMILY_DISPLAY_NAMES.get(slug) or selected["title"]
        arches = sorted({a for d in members_diag for a in d["archetypes"]})
        supports_deriv = any(d["supports_derivative"] for d in members_diag)
        all_flags = sorted({fl for d in members_diag for fl in d["hygiene_flags"]})

        risk_rank = {"high": 3, "medium": 2, "low": 1, "blocked_hygiene": 0}
        active_members = [d for d in members_diag if d["disposition"] in {"active_ip", "route_auxiliary_non_ip"}]
        if active_members:
            fam_risk = max(active_members, key=lambda d: risk_rank.get(d["inter_class_risk"], 0))["inter_class_risk"]
        else:
            fam_risk = selected["inter_class_risk"]
        risk_counts[fam_risk] += 1

        asset_cov = asset_index.match_family(slug, members_diag)
        cov_counts[asset_cov["coverage_status"]] += 1

        fam_total_cleanups = sum(cleanups_by_id[int(r["id"])].__len__() for r in fam_raw_rows)
        family_diag: dict[str, Any] = {
            "schema": "assert_template_family_v2",
            "family_slug": slug,
            "display_name": display_name,
            "source_record_ids": [int(r["id"]) for r in fam_raw_rows],
            "member_count": len(members_diag),
            "selected_latest_id": selected["id"],
            "selected_latest_version_key": selected["version_key"],
            "selected_latest_title": selected["title"],
            "version_selection_confidence": confidence,
            "version_selection_reason": sel_reason,
            "parallel_sub_scopes": is_parallel,
            "total_export_cleanups": fam_total_cleanups,
            "archetypes": arches,
            "supports_derivative": supports_deriv,
            "inter_class_risk": fam_risk,
            "all_hygiene_flags": all_flags,
            "assert_asset_coverage": asset_cov,
            "members": members_diag,
        }
        family_diag["recommendations"] = build_inter_class_recommendations(family_diag)

        fam_dir = output_dir / slug
        fam_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_text(
            fam_dir / "latest_template.md",
            render_latest_template_md(
                slug,
                display_name,
                selected,
                members_diag,
                sel_reason,
                is_parallel,
            ),
        )

        version_filenames: dict[str, str] = {}
        if len(members_diag) >= 2:
            ver_dir = fam_dir / "versions"
            ver_dir.mkdir(parents=True, exist_ok=True)
            used_names: set[str] = set()
            for d in members_diag:
                base = f"{d['id']:03d}_{safe_filename(d['title'])}"
                fname = f"versions/{base}.md"
                if fname in used_names:
                    fname = f"versions/{base}_v{d['sub_index']}.md"
                used_names.add(fname)
                version_filenames[d["version_key"]] = fname
                atomic_write_text(
                    fam_dir / fname,
                    render_version_file_md(d, d["version_key"] == selected["version_key"]),
                )

        atomic_write_text(
            fam_dir / "diagnosis.md",
            render_family_diagnosis_md(family_diag, members_diag, version_filenames),
        )
        atomic_write_json(fam_dir / "family.json", family_diag)
        atomic_write_jsonl(fam_dir / "raw_records.jsonl", fam_raw_rows)
        atomic_write_jsonl(fam_dir / "cleaned_records.jsonl", fam_cleaned_rows)

        family_summaries.append(
            {
                "family_slug": slug,
                "display_name": display_name,
                "source_record_ids": [int(r["id"]) for r in fam_raw_rows],
                "member_count": len(members_diag),
                "member_version_keys": [d["version_key"] for d in members_diag],
                "selected_latest_id": selected["id"],
                "selected_latest_version_key": selected["version_key"],
                "selected_latest_title": selected["title"],
                "version_selection_confidence": confidence,
                "parallel_sub_scopes": is_parallel,
                "total_export_cleanups": fam_total_cleanups,
                "archetypes": arches,
                "supports_derivative": supports_deriv,
                "inter_class_risk": fam_risk,
                "assert_asset_coverage": {"coverage_status": asset_cov["coverage_status"]},
            }
        )

    all_diags.sort(key=lambda d: (int(d["id"]), int(d["sub_index"])))
    total_family_members = sum(f["member_count"] for f in family_summaries)
    if total_family_members != len(all_diags):
        raise AssertionError(f"Family member sum mismatch: {total_family_members} != {len(all_diags)}")

    manifest: dict[str, Any] = {
        "schema": "assert_template_library_manifest_v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "raw_input_path": str(raw_path.relative_to(PROJECT_ROOT)),
        "raw_input_sha256": sha256_file(raw_path),
        "cleaned_output_path": str(cleaned_path.relative_to(PROJECT_ROOT)),
        "cleanup_report_path": str(cleanup_report_path.relative_to(PROJECT_ROOT)),
        "output_dir": str(output_dir.relative_to(PROJECT_ROOT)),
        "total_raw_records": len(raw_records),
        "total_unpacked_versions": len(all_diags),
        "total_family_members": total_family_members,
        "total_families": len(family_summaries),
        "multi_member_families": sum(1 for f in family_summaries if f["member_count"] >= 2),
        "records_with_export_cleanups": len(cleanup_entries),
        "total_export_cleanups": total_cleanups,
        "export_cleanup_rule_counts": dict(sorted(cleanup_rule_counts.items(), key=lambda x: (-x[1], x[0]))),
        "missing_ids": missing_ids,
        "duplicate_ids": duplicate_ids,
        "disposition_counts": dict(sorted(disp_counts.items())),
        "hygiene_flag_counts": dict(sorted(flag_counts.items())),
        "inter_class_risk_counts": dict(sorted(risk_counts.items())),
        "assert_coverage_counts": dict(sorted(cov_counts.items())),
    }

    # Omit bulky cleaned_body from compact diagnostics.jsonl index (full body lives in family.json / cleaned_records.jsonl)
    compact_diags = [{k: v for k, v in d.items() if k != "cleaned_body"} for d in all_diags]
    atomic_write_jsonl(output_dir / "diagnostics.jsonl", compact_diags)
    atomic_write_json(
        output_dir / "index.json",
        {
            "schema": "assert_template_index_v2",
            "total_raw_records": len(raw_records),
            "total_unpacked_versions": len(all_diags),
            "total_families": len(family_summaries),
            "families": family_summaries,
        },
    )
    atomic_write_text(
        output_dir / "README.md",
        render_root_readme(family_summaries, compact_diags, manifest),
    )
    atomic_write_json(manifest_out, manifest)
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW_PATH)
    parser.add_argument("--cleaned-out", type=Path, default=DEFAULT_CLEANED_PATH)
    parser.add_argument("--cleanup-report", type=Path, default=DEFAULT_CLEANUP_REPORT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--manifest-out", type=Path, default=DEFAULT_MANIFEST_OUT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest = build_template_library(
        raw_path=args.raw,
        cleaned_path=args.cleaned_out,
        cleanup_report_path=args.cleanup_report,
        output_dir=args.output_dir,
        manifest_out=args.manifest_out,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
