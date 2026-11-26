#!/usr/bin/env python3
"""Download sampled Fandom character portraits locally and generate review contact sheets.

Reads `manifests/character_wiki_dossiers.jsonl`, selects up to `--per-family` character
entries per B2 franchise with non-empty `portrait_url` (preferring those with rich visual
descriptions), downloads/validates/resizes portraits locally via Pillow under
`assets/standard_images/character_wiki_portraits/<family_slug>/`, records
`manifests/character_wiki_portraits.jsonl`, and builds 4x6 contact sheets under
`output/character_wiki_portraits/contact_sheets/`.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOSSIERS_JSONL = PROJECT_ROOT / "manifests" / "character_wiki_dossiers.jsonl"
DEFAULT_PORTRAITS_JSONL = PROJECT_ROOT / "manifests" / "character_wiki_portraits.jsonl"
DEFAULT_OUT_DIR = PROJECT_ROOT / "assets" / "standard_images" / "character_wiki_portraits"
DEFAULT_CONTACT_SHEETS_DIR = PROJECT_ROOT / "output" / "character_wiki_portraits" / "contact_sheets"

USER_AGENT = "AssertTemplateAuditBot/1.0 (+https://example.invalid/assert-audit; polite-portrait-sample)"
MAX_PORTRAIT_EDGE = 320
MIN_PORTRAIT_EDGE = 40


def _safe_slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(text or "").strip()).strip("._-")
    if not slug:
        slug = hashlib.sha256(str(text).encode("utf-8")).hexdigest()[:10]
    return slug[:60]


def _load_dossiers(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                rows.append(json.loads(s))
    return rows


def select_sampled_candidates(dossiers: list[dict[str, Any]], per_family: int = 2) -> list[dict[str, Any]]:
    """Selects up to `per_family` character portrait candidates per B2 family."""
    by_fam: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen_urls: dict[str, set[str]] = defaultdict(set)
    for row in dossiers:
        url = str(row.get("portrait_url") or "").strip()
        slug = str(row.get("family_slug") or "").strip()
        if not url or not slug:
            continue
        if url in seen_urls[slug]:
            continue
        seen_urls[slug].add(url)
        by_fam[slug].append(row)

    selected: list[dict[str, Any]] = []
    for slug in sorted(by_fam):
        candidates = by_fam[slug]
        candidates.sort(
            key=lambda r: (
                1 if str(r.get("visual_appearance") or "").strip() else 0,
                len(r.get("visual_anchors_extracted") or []),
                len(str(r.get("visual_appearance") or "")),
                str(r.get("character_name") or ""),
            ),
            reverse=True,
        )
        selected.extend(candidates[:per_family])
    return selected


def _download_bytes(url: str, timeout: float = 15.0) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "image/avif,image/webp,image/png,image/jpeg,image/*;q=0.8,*/*;q=0.5",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _validate_and_save_portrait(raw_bytes: bytes, base_out: Path) -> tuple[Path, int, int]:
    """Validates image via Pillow, resizes to <=320px max edge, saves PNG/JPEG."""
    with Image.open(io.BytesIO(raw_bytes)) as im:
        im.load()
        rgba = im.convert("RGBA")
        w, h = rgba.size
        if min(w, h) < MIN_PORTRAIT_EDGE:
            raise ValueError(f"image_too_small:{w}x{h}")
        if max(w, h) > MAX_PORTRAIT_EDGE:
            rgba.thumbnail((MAX_PORTRAIT_EDGE, MAX_PORTRAIT_EDGE), Image.Resampling.LANCZOS)
        rw, rh = rgba.size
        min_alpha, _ = rgba.getchannel("A").getextrema()
        base_out.parent.mkdir(parents=True, exist_ok=True)
        if min_alpha < 255:
            out_path = base_out.with_suffix(".png")
            tmp = out_path.with_name(out_path.name + ".tmp")
            rgba.save(tmp, format="PNG", optimize=True)
            tmp.replace(out_path)
            return out_path, rw, rh
        out_path = base_out.with_suffix(".jpg")
        rgb = Image.new("RGB", (rw, rh), (255, 255, 255))
        rgb.paste(rgba, mask=rgba.getchannel("A"))
        tmp = out_path.with_name(out_path.name + ".tmp")
        rgb.save(tmp, format="JPEG", quality=85, optimize=True)
        tmp.replace(out_path)
        return out_path, rw, rh


def _existing_portrait(base_out: Path) -> tuple[Path, int, int] | None:
    for ext in (".png", ".jpg", ".jpeg"):
        cand = base_out.with_suffix(ext)
        if cand.is_file():
            try:
                with Image.open(cand) as im:
                    im.load()
                    w, h = im.size
                    if min(w, h) >= MIN_PORTRAIT_EDGE:
                        return cand, w, h
            except Exception:
                continue
    return None


def run_download(
    dossiers_jsonl: Path = DEFAULT_DOSSIERS_JSONL,
    portraits_jsonl: Path = DEFAULT_PORTRAITS_JSONL,
    out_dir: Path = DEFAULT_OUT_DIR,
    per_family: int = 2,
    delay: float = 0.12,
) -> dict[str, Any]:
    dossiers = _load_dossiers(dossiers_jsonl)
    candidates = select_sampled_candidates(dossiers, per_family=per_family)

    results: list[dict[str, Any]] = []
    ok_count = 0
    cached_count = 0
    fail_count = 0
    families_ok: set[str] = set()

    for idx, row in enumerate(candidates):
        slug = str(row["family_slug"])
        char_name = str(row["character_name"])
        url = str(row["portrait_url"])
        base_out = out_dir / slug / _safe_slug(char_name)

        rec: dict[str, Any] = {
            "family_slug": slug,
            "franchise_display_name": str(row.get("franchise_display_name") or slug),
            "character_name": char_name,
            "source": str(row.get("source") or "fandom"),
            "portrait_url": url,
            "local_path": "",
            "width": 0,
            "height": 0,
            "status": "",
        }

        existing = _existing_portrait(base_out)
        if existing is not None:
            out_path, w, h = existing
            rec["local_path"] = out_path.relative_to(PROJECT_ROOT).as_posix()
            rec["width"] = w
            rec["height"] = h
            rec["status"] = "ok"
            ok_count += 1
            cached_count += 1
            families_ok.add(slug)
            results.append(rec)
            continue

        if idx > 0 and delay > 0:
            time.sleep(delay)

        try:
            raw = _download_bytes(url, timeout=15.0)
            out_path, w, h = _validate_and_save_portrait(raw, base_out)
            rec["local_path"] = out_path.relative_to(PROJECT_ROOT).as_posix()
            rec["width"] = w
            rec["height"] = h
            rec["status"] = "ok"
            ok_count += 1
            families_ok.add(slug)
        except urllib.error.HTTPError as exc:
            rec["status"] = f"http_{exc.code}"
            fail_count += 1
        except Exception as exc:
            rec["status"] = f"err_{type(exc).__name__}:{str(exc)[:80]}"
            fail_count += 1
        results.append(rec)

    portraits_jsonl.parent.mkdir(parents=True, exist_ok=True)
    tmp = portraits_jsonl.with_name(portraits_jsonl.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(portraits_jsonl)

    return {
        "candidates": len(candidates),
        "ok": ok_count,
        "cached_reused": cached_count,
        "failed": fail_count,
        "families_covered": len(families_ok),
        "manifest": str(portraits_jsonl.relative_to(PROJECT_ROOT)),
    }


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for cand in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ):
        p = Path(cand)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def run_contact_sheets(
    portraits_jsonl: Path = DEFAULT_PORTRAITS_JSONL,
    sheets_dir: Path = DEFAULT_CONTACT_SHEETS_DIR,
    cols: int = 6,
    rows_per_sheet: int = 4,
) -> dict[str, Any]:
    records = [r for r in _load_dossiers(portraits_jsonl) if r.get("status") == "ok" and r.get("local_path")]
    sheets_dir.mkdir(parents=True, exist_ok=True)
    for old in sheets_dir.glob("portraits_sheet_*.jpg"):
        old.unlink()

    per_sheet = cols * rows_per_sheet
    tile_w, tile_h = 220, 260
    img_box = 192
    pad = 16
    header_h = 46

    font_title = _load_font(18)
    font_lbl = _load_font(12)
    written: list[str] = []

    total_sheets = max(1, math.ceil(len(records) / per_sheet)) if records else 0
    for s_idx in range(total_sheets):
        chunk = records[s_idx * per_sheet : (s_idx + 1) * per_sheet]
        sheet_w = pad * 2 + cols * tile_w + (cols - 1) * 10
        rows_used = math.ceil(len(chunk) / cols)
        sheet_h = header_h + pad * 2 + rows_used * tile_h + max(0, rows_used - 1) * 10
        canvas = Image.new("RGB", (sheet_w, sheet_h), (246, 241, 231))
        draw = ImageDraw.Draw(canvas)
        draw.text(
            (pad, 14),
            f"Character Wiki Portraits Sample · Sheet {s_idx + 1}/{total_sheets} ({len(chunk)} items)",
            fill=(44, 41, 35),
            font=font_title,
        )

        for idx, item in enumerate(chunk):
            r_i = idx // cols
            c_i = idx % cols
            x0 = pad + c_i * (tile_w + 10)
            y0 = header_h + pad + r_i * (tile_h + 10)
            draw.rounded_rectangle([x0, y0, x0 + tile_w, y0 + tile_h], radius=8, fill=(252, 249, 243), outline=(218, 210, 196))

            img_path = PROJECT_ROOT / str(item["local_path"])
            try:
                with Image.open(img_path) as im:
                    im.load()
                    rgba = im.convert("RGBA")
                    rgba.thumbnail((img_box - 12, img_box - 12), Image.Resampling.LANCZOS)
                    bg = Image.new("RGB", (img_box, img_box), (255, 255, 255))
                    px = (img_box - rgba.width) // 2
                    py = (img_box - rgba.height) // 2
                    bg.paste(rgba, (px, py), mask=rgba.getchannel("A"))
                    canvas.paste(bg, (x0 + (tile_w - img_box) // 2, y0 + 8))
            except Exception:
                draw.text((x0 + 16, y0 + 80), "LOAD ERR", fill=(168, 59, 50), font=font_lbl)

            slug_lbl = str(item.get("family_slug") or "")[:24]
            char_lbl = str(item.get("character_name") or "")[:24]
            draw.text((x0 + 10, y0 + img_box + 14), slug_lbl, fill=(138, 72, 46), font=font_lbl)
            draw.text((x0 + 10, y0 + img_box + 32), char_lbl, fill=(44, 41, 35), font=font_lbl)

        out_sheet = sheets_dir / f"portraits_sheet_{s_idx + 1:02d}.jpg"
        tmp = out_sheet.with_name(out_sheet.name + ".tmp")
        canvas.save(tmp, format="JPEG", quality=88, optimize=True)
        tmp.replace(out_sheet)
        written.append(out_sheet.relative_to(PROJECT_ROOT).as_posix())

    return {"sheets_written": len(written), "paths": written}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download sampled character portraits")
    parser.add_argument("--contact-sheets", action="store_true", help="Build contact sheets from local portraits")
    parser.add_argument("--per-family", type=int, default=2, help="Max portraits to sample per B2 family")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.download and not args.contact_sheets:
        args.contact_sheets = True
    out: dict[str, Any] = {}
    if args.download:
        out["download"] = run_download(per_family=args.per_family)
    if args.contact_sheets:
        out["contact_sheets"] = run_contact_sheets()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
