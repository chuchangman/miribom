#!/usr/bin/env python3
"""
Gemini 검수 결과(OK + non-duplicate)를 processed에 반영.
- OK + phash non-duplicate → processed/{class}/ 복사 (naver_XXXX.jpg)
- OK + phash duplicate     → staging metadata: skipped_duplicate
- NG / AMBIGUOUS           → 복사하지 않음
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pandas as pd
import imagehash
from PIL import Image as PILImage

import config

PHASH_THRESH = 8
APPROVED_AT  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ── 유틸 ──────────────────────────────────────────────────────────────────────

def load_proc_hashes(proc_dir: Path):
    hashes = []
    for p in sorted(proc_dir.glob('*.jpg')):
        try:
            h = imagehash.phash(PILImage.open(p))
            hashes.append((str(p), h))
        except Exception:
            pass
    return hashes


def is_dup(h_new, proc_hashes):
    for _, h_proc in proc_hashes:
        if h_new - h_proc <= PHASH_THRESH:
            return True
    return False


# ── 클래스별 처리 ──────────────────────────────────────────────────────────────

def process_class(class_name: str, start_idx: int, expected_new: int):
    print(f'\n{"="*60}')
    print(f'{class_name}  (naver_{start_idx:04d} 부터 {expected_new}장 예상)')
    print(f'{"="*60}')

    csv_path     = Path(f'data/metadata/gemini_{class_name}_review.csv')
    meta_csv     = Path(config.METADATA_DIR) / f'{class_name}_staging_metadata.csv'
    proc_dir     = Path(f'data/processed/{class_name}')
    log_csv_path = Path(config.METADATA_DIR) / f'approval_log_{class_name}.csv'

    df_gemini = pd.read_csv(csv_path)
    ok_df     = df_gemini[df_gemini.status == 'OK'].copy()
    ng_df     = df_gemini[df_gemini.status == 'NG']
    amb_df    = df_gemini[df_gemini.status == 'AMBIGUOUS']

    print(f'  Gemini CSV: OK={len(ok_df)}, NG={len(ng_df)}, AMBIGUOUS={len(amb_df)}')

    # processed phash 로딩
    print(f'  processed phash 로딩 중... ', end='', flush=True)
    proc_hashes = load_proc_hashes(proc_dir)
    print(f'{len(proc_hashes)}장')

    # phash 판정
    new_images  = []   # (source_path, note)
    dup_images  = []   # source_path

    for _, row in ok_df.iterrows():
        src = Path(row.image_path)
        if not src.exists():
            print(f'  [WARN] 파일 없음: {src}')
            continue
        try:
            h = imagehash.phash(PILImage.open(src))
        except Exception:
            print(f'  [WARN] 이미지 읽기 실패: {src}')
            continue
        if is_dup(h, proc_hashes):
            dup_images.append(str(src))
        else:
            new_images.append((str(src), row.get('note', '')))

    print(f'  phash 중복: {len(dup_images)}장  |  이동 후보: {len(new_images)}장')

    if len(new_images) != expected_new:
        print(f'  [WARN] 예상 {expected_new}장과 실제 {len(new_images)}장 불일치 — 계속 진행')

    # ── 복사 실행 ──────────────────────────────────────────────────────────────
    log_rows = []
    n_copied = 0

    for i, (src_str, note) in enumerate(new_images):
        idx     = start_idx + i
        dst     = proc_dir / f'naver_{idx:04d}.jpg'
        shutil.copy2(src_str, dst)
        log_rows.append({
            'source_path':  src_str,
            'saved_path':   str(dst),
            'class_label':  class_name,
            'status':       'approved',
            'note':         note,
            'approved_at':  APPROVED_AT,
        })
        n_copied += 1
        print(f'  [COPY] {Path(src_str).parent.name}/{Path(src_str).name}  →  {dst.name}')

    # ── staging metadata 업데이트 ──────────────────────────────────────────────
    if meta_csv.exists():
        meta_df = pd.read_csv(meta_csv, encoding='utf-8-sig')
        if 'saved_path' in meta_df.columns:
            def norm(p):
                return str(Path(str(p))) if pd.notna(p) else ''

            # approved
            approved_set = {str(Path(s)) for s, _ in new_images}
            mask_approved = meta_df['saved_path'].apply(norm).isin(approved_set)
            meta_df.loc[mask_approved, 'status'] = 'approved'

            # skipped_duplicate
            dup_set = {str(Path(s)) for s in dup_images}
            mask_dup = meta_df['saved_path'].apply(norm).isin(dup_set)
            meta_df.loc[mask_dup, 'status'] = 'skipped_duplicate'

            meta_df.to_csv(meta_csv, index=False, encoding='utf-8-sig')
            print(f'\n  staging metadata 업데이트: {meta_csv.name}')
            print(f'    approved: {mask_approved.sum()}행')
            print(f'    skipped_duplicate: {mask_dup.sum()}행')

    # ── 로그 CSV ───────────────────────────────────────────────────────────────
    # dup / NG / AMBIGUOUS도 로그에 기록
    for src_str in dup_images:
        row = df_gemini[df_gemini.image_path == src_str.replace('\\', '/')]
        note_val = row.note.values[0] if len(row) > 0 else ''
        log_rows.append({
            'source_path':  src_str,
            'saved_path':   '',
            'class_label':  class_name,
            'status':       'skipped_duplicate',
            'note':         note_val,
            'approved_at':  APPROVED_AT,
        })

    for _, row in ng_df.iterrows():
        log_rows.append({
            'source_path':  row.image_path,
            'saved_path':   '',
            'class_label':  class_name,
            'status':       f'NG_{row.reason}',
            'note':         row.get('note', ''),
            'approved_at':  APPROVED_AT,
        })

    for _, row in amb_df.iterrows():
        log_rows.append({
            'source_path':  row.image_path,
            'saved_path':   '',
            'class_label':  class_name,
            'status':       f'AMBIGUOUS_{row.reason}',
            'note':         row.get('note', ''),
            'approved_at':  APPROVED_AT,
        })

    log_df = pd.DataFrame(log_rows)
    log_df.to_csv(log_csv_path, index=False, encoding='utf-8-sig')
    print(f'  로그 저장: {log_csv_path}  ({len(log_df)}행)')

    # ── 수량 검증 ───────────────────────────────────────────────────────────────
    final_count = len(list(proc_dir.glob('*.jpg')))
    print(f'\n  processed/{class_name}: {len(proc_hashes)}장 → {final_count}장  (+{n_copied})')

    return {
        'class_name':   class_name,
        'copied':       n_copied,
        'dup':          len(dup_images),
        'ng':           len(ng_df),
        'ambiguous':    len(amb_df),
        'before':       len(proc_hashes),
        'after':        final_count,
        'log_path':     str(log_csv_path),
    }


# ═════════════════════════════════════════════════════════════════════════════

results = []
results.append(process_class('humidifier', start_idx=323, expected_new=13))
results.append(process_class('heater',     start_idx=181, expected_new=77))

# ── 전체 processed 총합 ────────────────────────────────────────────────────────
print()
print('='*60)
print('전체 processed 수량 변화')
print('='*60)
total_before = total_after = 0
for cls in config.PROJECT_LABELS:
    d = Path(f'data/processed/{cls}')
    if d.exists():
        n = len(list(d.glob('*.jpg')))
        total_after += n
        # before: 이번 작업에서 변경된 클래스만 보정
        changed = next((r for r in results if r['class_name'] == cls), None)
        n_before = n - changed['copied'] if changed else n
        total_before += n_before
        marker = '  ← 변경' if changed else ''
        print(f'  {cls:<20} {n_before:>5}장 → {n:>5}장{marker}')

print(f'  {"합계":<20} {total_before:>5}장 → {total_after:>5}장  (+{total_after - total_before})')

# ── 최종 요약 ──────────────────────────────────────────────────────────────────
print()
print('='*60)
print('최종 요약')
print('='*60)
for r in results:
    print(f'[{r["class_name"]}]')
    print(f'  processed 반영:   {r["copied"]}장')
    print(f'  skipped_dup:      {r["dup"]}장')
    print(f'  NG 제외:          {r["ng"]}장')
    print(f'  AMBIGUOUS 제외:   {r["ambiguous"]}장')
    print(f'  processed 최종:   {r["after"]}장')
    print(f'  로그:             {r["log_path"]}')
    print()
