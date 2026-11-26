#!/usr/bin/env python3
"""按固定版本元数据收集宝可梦原始立绘，支持缓存与断点续跑。"""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import http.client
import io
import json
from pathlib import Path
import re
import time
import threading
import urllib.error
import urllib.parse
import urllib.request
import unicodedata

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache' / 'pokemon'
OUT = ROOT / 'manifests' / 'standard_images_1119'
CONNECTIONS = threading.local()


def normalized_name(name):
    # 仅统一本批出现的繁简混写与全角字母；不修改原条目名称。
    return unicodedata.normalize('NFKC', name).translate(str.maketrans('負電纏紅鐵轍跡邊獸', '负电缠红铁辙迹边兽'))


def get(url, destination, limit=10_000_000):
    if destination.is_file():
        return destination.read_bytes()
    for attempt in range(3):
        try:
            parsed = urllib.parse.urlsplit(url)
            if parsed.scheme != 'https':
                raise ValueError('仅允许 HTTPS 来源')
            if not hasattr(CONNECTIONS, 'hosts'):
                CONNECTIONS.hosts = {}
            connection = CONNECTIONS.hosts.setdefault(parsed.netloc, http.client.HTTPSConnection(parsed.netloc, timeout=30))
            connection.request('GET', parsed.path + ('?' + parsed.query if parsed.query else ''),
                               headers={'User-Agent': 'Assert-reference-collector/1.0'})
            response = connection.getresponse()
            data = response.read(limit + 1)
            if response.status != 200:
                raise urllib.error.HTTPError(url, response.status, response.reason, response.headers, None)
            if len(data) > limit:
                raise ValueError('响应超过大小限制')
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(destination.suffix + '.part')
            temporary.write_bytes(data)
            temporary.replace(destination)
            return data
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raise
            if attempt == 2:
                raise
        except (OSError, TimeoutError, http.client.HTTPException):
            if hasattr(CONNECTIONS, 'hosts'):
                for connection in CONNECTIONS.hosts.values():
                    connection.close()
                CONNECTIONS.hosts = {}
            if attempt == 2:
                raise
        time.sleep(1 + attempt)


def write_jsonl(path, rows):
    tmp = path.with_suffix('.jsonl.part')
    tmp.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
    tmp.replace(path)


def metadata():
    versions_file = OUT / 'pokemon_source_versions.json'
    if versions_file.exists():
        versions = json.loads(versions_file.read_text())
    else:
        versions = {}
        for repo in ['sprites', 'pokeapi']:
            data = get(f'https://api.github.com/repos/PokeAPI/{repo}/commits/master', CACHE / f'{repo}_commit.json')
            versions[repo] = json.loads(data)['sha']
        versions_file.write_text(json.dumps(versions, indent=2) + '\n')
    tables = {}
    for name in ['pokemon', 'pokemon_species_names']:
        url = f'https://raw.githubusercontent.com/PokeAPI/pokeapi/{versions["pokeapi"]}/data/v2/csv/{name}.csv'
        raw = get(url, CACHE / versions['pokeapi'] / f'{name}.csv')
        tables[name] = list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
    get(f'https://raw.githubusercontent.com/PokeAPI/sprites/{versions["sprites"]}/LICENCE.txt', OUT / 'pokemon_source_license.txt')
    return versions, tables


def build_plan(backlog, tables):
    species_names = {}
    english = {}
    for row in tables['pokemon_species_names']:
        sid = int(row['pokemon_species_id'])
        species_names.setdefault(sid, {})[row['local_language_id']] = row['name']
        if row['local_language_id'] == '9':
            english[row['name'].casefold()] = sid
    defaults = {int(r['species_id']): r for r in tables['pokemon'] if r['is_default'] == '1'}
    identifiers = {r['identifier']: r for r in tables['pokemon']}
    plans, unresolved = {}, []
    for row in backlog:
        if row['image_route'] not in {'pokemon_artwork', 'pokemon_identity_review'}:
            continue
        title = row['title']
        match = re.fullmatch(r'No\.(\d+)\s+(.+)', title)
        target = None
        evidence = None
        if match:
            sid = int(match[1])
            # 编号和简体／繁体名称必须同时匹配，避免只凭编号抓错图。
            if normalized_name(match[2]) in {normalized_name(n) for n in species_names.get(sid, {}).values()}:
                target = defaults.get(sid)
                evidence = 'national_dex_number_and_localized_name_nfkc_limited_script_normalization'
        else:
            alias = re.search(r'[（(]([^）)]+)[）)]', title)
            name = alias[1].casefold() if alias else ''
            if name.startswith('galarian '):
                target = identifiers.get(name.removeprefix('galarian ').replace(' ', '-') + '-galar')
            elif name.startswith('mega '):
                target = identifiers.get(name.removeprefix('mega ').replace(' ', '-') + '-mega')
            elif name in english:
                target = defaults.get(english[name])
            if target:
                sid = int(target['species_id'])
                chinese = re.split(r'[（(]', title)[0].strip()
                normal_name = re.sub(r'^(伽勒尔|超级)', '', chinese)
                if normalized_name(normal_name) not in {normalized_name(n) for n in species_names.get(sid, {}).values()}:
                    target = None
                else:
                    evidence = 'english_species_and_localized_name_with_explicit_form'
        if not target:
            unresolved.append({'entity_id': row['entity_id'], 'title': title,
                               'status': 'ambiguous', 'reason': '未同时确认物种名称与编号／形态，或条目为总 IP。'})
            continue
        pokemon_id = int(target['id'])
        plans.setdefault(pokemon_id, {'pokemon_id': pokemon_id, 'species_id': int(target['species_id']),
                                     'identifier': target['identifier'], 'links': []})
        plans[pokemon_id]['links'].append({'entity_id': row['entity_id'], 'title': title, 'identity_evidence': evidence})
    return sorted(plans.values(), key=lambda x: x['pokemon_id']), unresolved


def download(plan, version):
    pid, sid, slug = plan['pokemon_id'], plan['species_id'], plan['identifier']
    relative = f'assets/standard_images/pokemon_artwork/{sid:04d}_{slug}/pokeapi_official_artwork/source.png'
    source_url = f'https://raw.githubusercontent.com/PokeAPI/sprites/{version}/sprites/pokemon/other/official-artwork/{pid}.png'
    path = ROOT / relative
    data = get(source_url, path)
    with Image.open(io.BytesIO(data)) as image:
        image.verify()
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        if image.format != 'PNG':
            raise ValueError('源文件并非 PNG')
        width, height = image.size
        rgba = image.convert('RGBA')
        alpha = rgba.getchannel('A')
        bounds = alpha.getbbox()
        if bounds is None or width < 64 or height < 64:
            raise ValueError('图片为空或尺寸异常')
        image_info = {'width': width, 'height': height, 'mode': image.mode,
                      'alpha_bbox': list(bounds), 'alpha_extrema': list(alpha.getextrema())}
    digest = hashlib.sha256(data).hexdigest()
    asset = {'asset_id': 'sha256_' + digest, 'sha256': digest, 'asset_kind': 'pokemon_artwork',
             'canonical_entity_id': f'pokemon:{sid:04d}:{slug}', 'variant_id': 'pokeapi_official_artwork',
             'pokemon_id': pid, 'species_id': sid, 'identifier': slug, 'local_path': relative,
             'source_page_url': f'https://github.com/PokeAPI/sprites/blob/{version}/sprites/pokemon/other/official-artwork/{pid}.png',
             'download_url': source_url, 'publisher': 'PokeAPI/sprites mirror',
             'source_tier': 'third_party_mirror_official_artwork_directory',
             'source_revision': version, 'fetched_at': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
             'license': 'Image copyright: The Pokémon Company; repository license does not establish image permission.',
             'license_evidence': 'manifests/standard_images_1119/pokemon_source_license.txt',
             'is_synthetic_image': False, 'transform_history': [], 'bytes': len(data), **image_info,
             'file_integrity': 'verified', 'review_status': 'identity_verified_pending_visual_review',
             'quality_flags': ['native_resolution_below_512'] if max(width, height) < 512 else [],
             'review_note': '编号／名称／形态与固定版本数据一致；原图通过完整解码与非空检查，尚未逐张人工视觉验收。'}
    links = [{'entity_id': x['entity_id'], 'title': x['title'], 'canonical_entity_id': asset['canonical_entity_id'],
              'candidate_asset_ids': [asset['asset_id']], 'approved_asset_ids': [],
              'status': asset['review_status'], 'identity_evidence': x['identity_evidence'],
              'template_ids': []} for x in plan['links']]
    return asset, links


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4, choices=range(1, 9))
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    versions, tables = metadata()
    backlog = [json.loads(line) for line in (OUT / 'backlog.jsonl').read_text().splitlines()]
    plans, unresolved = build_plan(backlog, tables)
    if args.limit:
        plans = plans[:args.limit]
    write_jsonl(OUT / 'pokemon_download_plan.jsonl', plans)
    write_jsonl(OUT / 'pokemon_identity_unresolved.jsonl', unresolved)
    assets, links, failures = [], [], []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download, plan, versions['sprites']): plan for plan in plans}
        for completed, future in enumerate(as_completed(futures), 1):
            plan = futures[future]
            try:
                asset, related = future.result()
                assets.append(asset)
                links.extend(related)
            except Exception as error:
                failures.append({'pokemon_id': plan['pokemon_id'], 'identifier': plan['identifier'], 'error': str(error)})
            if completed % 50 == 0 or completed == len(plans):
                print(f'{completed}/{len(plans)} 图片完成；成功 {len(assets)}，失败 {len(failures)}', flush=True)
    write_jsonl(OUT / 'pokemon_assets.jsonl', sorted(assets, key=lambda r: r['pokemon_id']))
    write_jsonl(OUT / 'pokemon_links.jsonl', sorted(links, key=lambda r: r['entity_id']))
    write_jsonl(OUT / 'pokemon_download_failures.jsonl', sorted(failures, key=lambda r: r['pokemon_id']))
    print(json.dumps({'assets': len(assets), 'mapped_rows': len(links), 'unresolved': len(unresolved),
                      'failures': len(failures), 'bytes': sum(a['bytes'] for a in assets)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
