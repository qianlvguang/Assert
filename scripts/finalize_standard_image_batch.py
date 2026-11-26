#!/usr/bin/env python3
"""合并本批图片与逐条审核结果；只导出明确批准的参考图映射。"""
from collections import Counter
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'manifests' / 'standard_images_1119'

# 已查看原质检拼图；这里只批准当前图片实际表达的标识用途。
REJECT = {
    'kb_00199_米菲_Miffy_': '图片为 Miffy and Friends 节目标识／宣传图，不能代替米菲角色标准立绘。',
    'kb_05640_史努比_Snoopy_': '图片只有 Peanuts 字标，没有史努比角色。',
    'kb_00180_神探狗狗_Dog_Man_Dav_Pilkey_': '图片为 Captain Underpants 字标，与 Dog Man 不同作品。',
    'kb_03844_戴夫_皮尔奇_神探狗狗_Dav_Pilkey_Dog_Man_': '图片为 Captain Underpants 字标，与 Dog Man 不同作品。',
}
VARIANT = {
    'ip_chainsaw_man': '当前为 Reze Arc 电影版字标，需确认条目是否接受此版本。',
    'ip_dragon_ball': '当前为 Dragon Ball Z 字标，需确认是否符合总 IP 条目的用途。',
    'ip_tokyo_ghoul': '当前为 Tokyo Ghoul:re 字标，需确认续作与总 IP 的范围。',
    'ip_nirvana': '当前图含 Nevermind 专辑字样，不能作为无版本限定的乐队标准标志。',
    'ip_hatsune_miku': '当前为 Hatsune Miku V3 字标，不代表人物立绘或 V4 图形版本。',
    'ip_rilakkuma': '当前是带背景的角色插画；需确认原始来源与背景使用要求。',
    'ip_cars_aurelia_ambig': '图中明确为 Pixar Cars，可作为 Cars 作品标志候选；原模板歧义仍未解除。',
}


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def write(path, rows):
    temporary = path.with_suffix('.jsonl.part')
    temporary.write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows))
    temporary.replace(path)


def image_check(asset):
    path = ROOT / asset['local_path']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if asset['asset_id'] != 'sha256_' + digest:
        raise ValueError(f'图片哈希不一致：{path}')
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        im.load()
        return im.width, im.height


def make_preview(assets):
    # 固定抽样含首尾和地区／超级进化，不把抽检写成逐张视觉通过。
    ordered = sorted(assets, key=lambda a: a['pokemon_id'])
    selected = ordered[::max(1, len(ordered) // 30)][:30]
    selected += [a for a in ordered if a['pokemon_id'] > 10000]
    if ordered and ordered[-1] not in selected:
        selected.append(ordered[-1])
    if not selected:
        return
    cols, side, label = 6, 150, 26
    sheet = Image.new('RGB', (cols * side, ((len(selected) + cols - 1) // cols) * (side + label)), 'white')
    draw = ImageDraw.Draw(sheet)
    for i, asset in enumerate(selected):
        x, y = i % cols * side, i // cols * (side + label)
        with Image.open(ROOT / asset['local_path']) as image:
            thumb = image.convert('RGBA')
            thumb.thumbnail((side - 8, side - 8))
            sheet.paste(thumb, (x + (side - thumb.width) // 2, y + (side - thumb.height) // 2), thumb)
        draw.text((x + 4, y + side), f"{asset['species_id']:04d} {asset['identifier'][:19]}", fill='black')
    directory = ROOT / 'contact_sheets' / 'standard_images_1119'
    directory.mkdir(exist_ok=True)
    sheet.save(directory / 'pokemon_sample.jpg', quality=92)


def main():
    backlog = read(BATCH / 'backlog.jsonl')
    existing = read(BATCH / 'existing_assets.jsonl')
    assets = {row['asset_id']: row for row in existing}
    pokemon_assets = read(BATCH / 'pokemon_assets.jsonl')
    for asset in pokemon_assets:
        assets[asset['asset_id']] = asset
    pokemon_links = {row['entity_id']: row for row in read(BATCH / 'pokemon_links.jsonl')}
    unresolved = {row['entity_id']: row for row in read(BATCH / 'pokemon_identity_unresolved.jsonl')}
    links, decisions = [], []
    for row in backlog:
        link = {key: row[key] for key in ['entity_id', 'title', 'source_domain', 'image_route', 'priority',
                                         'canonical_entity_id', 'candidate_asset_ids', 'approved_asset_ids', 'template_ids', 'status']}
        if row['entity_id'] in pokemon_links:
            link.update(pokemon_links[row['entity_id']])
        elif row['entity_id'] in unresolved:
            link.update(unresolved[row['entity_id']])
        elif row['candidate_asset_ids']:
            if len(row['candidate_asset_ids']) != 1:
                raise ValueError('复用候选多于一个，需明确审核规则')
            asset = assets[row['candidate_asset_ids'][0]]
            source_id = asset['source_entity_id']
            note = REJECT.get(row['entity_id'])
            if note:
                link.update(status='rejected_mismatch', review_note=note)
            elif source_id in VARIANT:
                link.update(status='variant_review_required', review_note=VARIANT[source_id])
            else:
                if '/brands/' in asset['local_path']:
                    kind, namespace = 'brand_logo', 'brand'
                elif asset['asset_kind'] in {'team_crest', 'league_logo'}:
                    kind, namespace = asset['asset_kind'], asset['asset_kind']
                elif '/music_celebrity_sports/' in asset['local_path']:
                    kind, namespace = 'artist_wordmark', 'artist'
                else:
                    kind, namespace = 'franchise_mark', 'franchise'
                canonical = namespace + ':' + source_id.removeprefix('ip_')
                width, height = image_check(asset)
                asset.update(asset_kind=kind, canonical_entity_id=canonical, width=width, height=height,
                             review_status='approved_for_declared_reference_kind',
                             review_note='已查看现有拼图，按当前实际标志用途批准；不外推到角色立绘、商品外观或未知原模板。')
                link.update(status='approved_reference', canonical_entity_id=canonical,
                            approved_asset_ids=[asset['asset_id']], reference_kind=kind,
                            review_note='名称与图中标识一致，仅用于 reference_kind 所列用途；来源授权仍为原清单记录。')
            decisions.append(link)
        links.append(link)
    if len(links) != len({row['entity_id'] for row in links}):
        raise ValueError('重复 entity_id')
    for asset in assets.values():
        image_check(asset)
    for link in links:
        if not set(link['candidate_asset_ids'] + link['approved_asset_ids']) <= assets.keys():
            raise ValueError('引用不存在的图片')
    write(ROOT / 'manifests' / 'standard_image_assets.jsonl', list(assets.values()))
    write(ROOT / 'manifests' / 'standard_image_links.jsonl', links)
    write(BATCH / 'reuse_review_decisions.jsonl', decisions)
    export = []
    for link in links:
        if not link['approved_asset_ids']:
            continue
        export.append({'entity_id': link['entity_id'], 'canonical_entity_id': link['canonical_entity_id'],
                       'reference_kind': link['reference_kind'],
                       'images': [assets[a]['local_path'] for a in link['approved_asset_ids']],
                       'asset_ids': link['approved_asset_ids'], 'is_synthetic_image': False})
    write(BATCH / 'approved_references.jsonl', export)
    make_preview(pokemon_assets)
    summary = {'entity_count': len(links), 'asset_count': len(assets), 'new_download_count': len(pokemon_assets),
               'new_download_bytes': sum(a['bytes'] for a in pokemon_assets),
               'status_counts': dict(Counter(row['status'] for row in links)),
               'reuse_review_counts': dict(Counter(row['status'] for row in decisions)),
               'approved_reference_rows': len(export),
               'pokemon_download_failures': len(read(BATCH / 'pokemon_download_failures.jsonl')),
               'validation': '全部登记图片哈希与完整解码通过；全部实体 ID 唯一，图片引用存在。',
               'scope_note': '原资源和原训练 JSONL 未修改。新立绘只完成元数据身份与文件校验；抽样预览不代表全部视觉验收。'}
    (BATCH / 'execution_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
