#!/usr/bin/env python3
"""将补图 Markdown 转成候选资源索引和待办；不下载、不自动批准图片。"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata


ROOT = Path(__file__).resolve().parents[1]


def normalized(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def aliases(title):
    # 仅完整名称与括号别名；不做包含匹配或跨域自动归并。
    result = {normalized(title)}
    base = re.split(r"[（(]", title, maxsplit=1)[0].strip()
    if base:
        result.add(normalized(base))
    for part in re.findall(r"[（(]([^）)]+)[）)]", title):
        result.update(normalized(x.strip()) for x in part.split(" / ") if x.strip())
    return result


def route(domain, title):
    if domain in {"pk_move", "pk_ability"}:
        return "concept_visual_review", "P3", "先核对游戏、版本及实体含义；无统一标准视觉时保留文本或另建示意图。"
    if domain == "audit_通用规则" or any(x in title for x in ["指南", "手册", "速览", "专题长文", "图鉴", "题库", "编年"]):
        return "document_scope_review", "P3", "判断是否为集合或规则文档；必要时拆分子实体或组织示例集。"
    if domain.startswith("宝可梦 · 第"):
        return "pokemon_artwork", "P1", "核对全国图鉴编号、形态、世代及画风版本，再选择官方立绘。"
    if domain.startswith("pokemon_"):
        return "pokemon_identity_review", "P1", "先与全国图鉴条目对齐；保留地区、超级进化等形态差异。"
    if domain.startswith("图案") or domain == "lace":
        return "reference_photo_set", "P2", "材质、纹样、工艺及形制用可追溯示例集；品牌元素需核对具体图形。"
    if domain in {"anime_char", "film_char"}:
        return "character_identity_review", "P2", "域分类可能不准确；核对作品、角色、真人或动画版本，再收官方设定图。"
    if domain.startswith("audit_"):
        return "template_scope_review", "P0", "核对原模板识别目标；品牌标、角色、车型、球衣与机构标不得互相替代。"
    if domain in {"figure", "ent_人物", "ent_体育明星", "ent_音乐人", "ent_视觉艺术家"}:
        return "person_or_work_review", "P2", "先明确目标是肖像、签名、个人商标还是代表作品。"
    return "entity_identity_review", "P1", "核对实体类型与所需图形版本，再采集或复用候选图片。"


def read_needs(path):
    text = path.read_text(encoding="utf-8")
    section = re.search(r"^## 仍需标准图片的实体[^\n]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not section:
        raise ValueError("找不到待补实体章节")
    rows = []
    for block in re.split(r"^### ", section[1], flags=re.M)[1:]:
        heading, _, body = block.partition("\n")
        match = re.fullmatch(r"(.+)（(\d+)）", heading.strip())
        if not match:
            raise ValueError(f"未知分组标题：{heading}")
        domain, expected = match[1], int(match[2])
        items = re.findall(r"^- (.*?) ｜ `([^`]+)`\s*$", body, re.M)
        if len(items) != expected:
            raise ValueError(f"{domain}: 预期 {expected}，解析 {len(items)}")
        for title, entity_id in items:
            kind, priority, reason = route(domain, title)
            rows.append({"entity_id": entity_id, "title": title, "source_domain": domain,
                         "image_route": kind, "priority": priority, "routing_note": reason})
    ids = [r["entity_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("待补清单有重复 entity_id")
    expected_total = re.search(r"共\s*(\d+)", section[0].splitlines()[0])
    if expected_total and len(rows) != int(expected_total[1]):
        raise ValueError("总条数与章节声明不一致")
    return rows


def existing_assets():
    assets = []
    for filename, keys in [("sports_crests_supplement.json", ["leagues", "teams"]),
                           ("sch96_ip_supplement.json", ["entities"])]:
        manifest = json.loads((ROOT / "manifests" / filename).read_text())
        for key in keys:
            for entry in manifest[key]:
                source_path = entry.get("local_path")
                if not source_path:
                    continue
                local_path = source_path.removeprefix("assets/")
                path = ROOT / local_path
                if not path.is_file():
                    raise ValueError(f"资源缺失：{local_path}")
                content = path.read_bytes()
                md5 = entry.get("visual", {}).get("md5")
                if md5 and hashlib.md5(content).hexdigest() != md5:
                    raise ValueError(f"资源哈希不匹配：{local_path}")
                assets.append({
                    "asset_id": "sha256_" + hashlib.sha256(content).hexdigest(),
                    "source_entity_id": entry["entity_id"],
                    "name_zh": entry.get("name_zh", ""), "name_en": entry.get("name_en", ""),
                    "asset_kind": "team_crest" if key == "teams" else "league_logo" if key == "leagues" else "ip_or_brand_reference",
                    "local_path": local_path, "legacy_local_path": source_path,
                    "source_url": entry.get("source_url", ""),
                    "source_tier": entry.get("source_tier", ""),
                    "source_manifest": "manifests/" + filename,
                    "file_integrity": "verified", "review_status": "pending_semantic_review",
                    "license_status": "unrecorded", "is_synthetic_image": False,
                })
    return assets


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--needs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "manifests" / "standard_images_1119")
    args = parser.parse_args()
    rows = read_needs(args.needs)
    assets = existing_assets()
    index = defaultdict(set)
    for i, asset in enumerate(assets):
        for name in [asset["name_zh"], asset["name_en"]]:
            if name:
                for alias in aliases(name):
                    index[alias].add(i)
    for row in rows:
        matches = set()
        # 抽象、人物、角色、纹样或审核模板不按品牌名称自动检索，避免跨类型误配。
        if row["image_route"] == "entity_identity_review":
            for name in aliases(row["title"]):
                matches.update(index.get(name, set()))
        row["candidate_asset_ids"] = sorted({assets[i]["asset_id"] for i in matches})
        row["status"] = "reuse_candidate" if matches else "needs_identity_review"
        row["canonical_entity_id"] = None
        row["approved_asset_ids"] = []
        row["template_ids"] = []
        row["review_status"] = "pending"
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    write_jsonl(output / "existing_assets.jsonl", assets)
    write_jsonl(output / "backlog.jsonl", rows)
    summary = {
        "schema": "standard_image_backlog_v1", "input_name": args.needs.name,
        "input_sha256": hashlib.sha256(args.needs.read_bytes()).hexdigest(),
        "entity_count": len(rows), "existing_asset_count": len(assets),
        "counts_by_route": dict(Counter(r["image_route"] for r in rows)),
        "counts_by_status": dict(Counter(r["status"] for r in rows)),
        "approved_entity_count": 0,
        "scope_note": "仅解析仍需图片章节；未验证附录排除的 4024 项，也未检查其他独立图库。路由和名称匹配均为待审候选。",
    }
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
