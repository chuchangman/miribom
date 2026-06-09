#!/usr/bin/env python3
"""
staging 정리 + HTML 재생성 (API 호출 없음)
1. 가습기_제품사진 폴더 삭제
2. phash dedup (humidifier, heater)
3. HTML 재생성
"""
import os, sys, shutil
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config
import imagehash
import pandas as pd
from PIL import Image as PILImage
from scripts.run_collection import generate_html

# ── Step 1: 가습기_제품사진 폴더 삭제 ─────────────────────────────────────────
print('=' * 60)
print('Step 1. 가습기_제품사진 폴더 삭제')
print('=' * 60)

jepum_dir = Path('data/staging/humidifier/가습기_제품사진')
if jepum_dir.exists():
    imgs = list(jepum_dir.glob('*.jpg'))
    shutil.rmtree(jepum_dir)
    print(f'  삭제 완료: {jepum_dir}  ({len(imgs)}장)')
else:
    print(f'  이미 없음: {jepum_dir}')

print()

# ── Step 2: phash dedup ───────────────────────────────────────────────────────
PHASH_THRESH = 8

def dedup_class(class_name):
    staging_dir = Path('data/staging') / class_name
    metadata_csv = Path(config.METADATA_DIR) / f'{class_name}_staging_metadata.csv'

    all_images = sorted(
        p for p in staging_dir.rglob('*')
        if p.suffix.lower() in ('.jpg', '.jpeg', '.png') and p.is_file()
    )
    total = len(all_images)
    print(f'  [{class_name}] {total}장 phash 계산 중...')

    hashes = []
    for p in all_images:
        try:
            h = imagehash.phash(PILImage.open(p))
            img = PILImage.open(p)
            area = img.size[0] * img.size[1]
        except Exception:
            h, area = None, 0
        hashes.append((p, h, area))

    removed_paths = set()
    for i in range(len(hashes)):
        p_i, h_i, a_i = hashes[i]
        if h_i is None or str(p_i) in removed_paths:
            continue
        for j in range(i + 1, len(hashes)):
            p_j, h_j, a_j = hashes[j]
            if h_j is None or str(p_j) in removed_paths:
                continue
            if h_i - h_j <= PHASH_THRESH:
                if a_i >= a_j:
                    removed_paths.add(str(p_j))
                else:
                    removed_paths.add(str(p_i))
                    break

    n_removed = 0
    for rp in removed_paths:
        try:
            os.remove(rp)
            n_removed += 1
        except Exception as e:
            print(f'  삭제 실패: {rp} — {e}')

    kept = total - n_removed

    if metadata_csv.exists() and n_removed > 0:
        df = pd.read_csv(metadata_csv, encoding='utf-8-sig')
        if 'saved_path' in df.columns:
            removed_norm = {str(Path(rp)) for rp in removed_paths}
            mask = df['saved_path'].apply(
                lambda p: str(Path(str(p))) if pd.notna(p) else ''
            ).isin(removed_norm)
            df.loc[mask, 'status'] = 'dedup_deleted'
            df.to_csv(metadata_csv, index=False, encoding='utf-8-sig')

    print(f'  [{class_name}] {total}장 → 제거 {n_removed}장 → 잔여 {kept}장')
    return total, n_removed, kept

print('=' * 60)
print('Step 2. phash dedup')
print('=' * 60)
results = {}
for cls in ['humidifier', 'heater']:
    total, removed, kept = dedup_class(cls)
    results[cls] = (total, removed, kept)

print()

# ── Step 3: HTML 재생성 ───────────────────────────────────────────────────────
print('=' * 60)
print('Step 3. HTML 재생성')
print('=' * 60)
for cls in ['humidifier', 'heater']:
    staging_dir = f'data/staging/{cls}'
    html_out = f'data/metadata/{cls}_staging_review.html'
    n = generate_html(cls, staging_dir, html_out)
    print()

print()
print('=' * 60)
print('최종 요약')
print('=' * 60)
print(f'  {"클래스":<15} {"dedup전":>8} {"제거":>6} {"잔여":>6}')
print('  ' + '-' * 38)
for cls, (total, removed, kept) in results.items():
    print(f'  {cls:<15} {total:>8} {removed:>6} {kept:>6}')

print()
print('  HTML 경로:')
for cls in ['humidifier', 'heater']:
    html = Path(f'data/metadata/{cls}_staging_review.html')
    kb = html.stat().st_size // 1024 if html.exists() else 0
    print(f'    {cls}: data/metadata/{cls}_staging_review.html  ({kb} KB)')
