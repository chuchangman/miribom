#!/usr/bin/env python3
"""
Gemini 검수 결과(OK + non-duplicate)를 processed에 반영.
모든 15개 클래스에 대해 자동으로 실행하도록 수정됨.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd
import imagehash
from PIL import Image as PILImage
from tqdm import tqdm

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

PHASH_THRESH = 8
APPROVED_AT  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ── 유틸 ──────────────────────────────────────────────────────────────────────

def load_proc_hashes(proc_dir: Path):
    hashes = []
    if not proc_dir.exists():
        return hashes
    for p in sorted(proc_dir.glob('*.jpg')):
        try:
            # Open and close explicitly to avoid file handle issues
            with PILImage.open(p) as img:
                h = imagehash.phash(img)
            hashes.append((str(p), h))
        except Exception:
            pass
    return hashes


def is_dup(h_new, proc_hashes):
    for _, h_proc in proc_hashes:
        if h_new - h_proc <= PHASH_THRESH:
            return True
    return False


def get_next_idx(proc_dir: Path):
    if not proc_dir.exists():
        return 0
    naver_nums = [
        int(f.stem[6:]) for f in proc_dir.iterdir()
        if f.name.startswith('naver_') and f.stem[6:].isdigit()
    ]
    return (max(naver_nums) + 1) if naver_nums else 0


# ── 클래스별 처리 ──────────────────────────────────────────────────────────────

def process_class(class_name: str):
    print(f'\n{"="*60}')
    print(f'처리 중: {class_name}')
    print(f'{"="*60}')

    csv_path     = Path(f'data/metadata/gemini_{class_name}_review.csv')
    meta_csv     = Path(config.METADATA_DIR) / f'{class_name}_staging_metadata.csv'
    proc_dir     = Path(f'data/processed/{class_name}')
    log_csv_path = Path(config.METADATA_DIR) / f'approval_log_{class_name}.csv'

    if not csv_path.exists():
        print(f'  [건너뜀] Gemini 리뷰 CSV 없음: {csv_path}')
        return None

    proc_dir.mkdir(parents=True, exist_ok=True)

    df_gemini = pd.read_csv(csv_path)
    # status가 OK인 것만 필터링 (ERROR, NG, AMBIGUOUS 제외)
    ok_df     = df_gemini[df_gemini.status == 'OK'].copy()
    ng_df     = df_gemini[df_gemini.status.isin(['NG', 'AMBIGUOUS', 'ERROR'])]

    print(f'  Gemini 결과: OK={len(ok_df)}, 기타={len(ng_df)}')

    # processed phash 로딩
    print(f'  processed phash 로딩 중... ', end='', flush=True)
    proc_hashes = load_proc_hashes(proc_dir)
    print(f'{len(proc_hashes)}장')

    # 다음 인덱스
    start_idx = get_next_idx(proc_dir)
    print(f'  시작 인덱스: naver_{start_idx:04d}')

    # phash 판정
    new_images  = []   # (source_path, note)
    dup_images  = []   # source_path

    for _, row in ok_df.iterrows():
        src = Path(row.image_path)
        if not src.exists():
            continue
        try:
            with PILImage.open(src) as img:
                h = imagehash.phash(img)
        except Exception:
            continue

        if is_dup(h, proc_hashes):
            dup_images.append(str(src))
        else:
            new_images.append((str(src), row.get('note', '')))
            # 배치 내 중복 방지를 위해 추가
            proc_hashes.append((str(src), h))

    print(f'  phash 중복 제외: {len(dup_images)}장  |  이동 대상: {len(new_images)}장')

    # ── 복사 실행 ──────────────────────────────────────────────────────────────
    log_rows = []
    n_copied = 0

    for i, (src_str, note) in enumerate(new_images):
        idx     = start_idx + i
        dst     = proc_dir / f'naver_{idx:04d}.jpg'
        try:
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
        except Exception as e:
            print(f'  [ERROR] 복사 실패 {src_str}: {e}')

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

    # 로그 저장
    if log_rows:
        log_df = pd.DataFrame(log_rows)
        log_df.to_csv(log_csv_path, index=False, encoding='utf-8-sig')

    return {
        'class_name':   class_name,
        'copied':       n_copied,
        'dup':          len(dup_images),
        'before':       len(proc_hashes) - n_copied,
        'after':        len(proc_hashes),
    }


# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    target_classes = [
        'mouse', 'rice_cooker', 'microwave', 'air_fryer', 'electric_kettle',
        'vacuum_cleaner', 'robot_vacuum', 'fan', 'air_conditioner', 'heater',
        'dehumidifier', 'humidifier', 'monitor', 'keyboard', 'beam_projector'
    ]

    results = []
    for cls in target_classes:
        res = process_class(cls)
        if res:
            results.append(res)

    # 요약 출력
    if results:
        print('\n' + '='*60)
        print(f'{"클래스":<20} {"이전":>6} {"승인":>6} {"중복":>6} {"최종":>6}')
        print('-'*60)
        for r in results:
            print(f'{r["class_name"]:<20} {r["before"]:>8} {r["copied"]:>8} {r["dup"]:>8} {r["after"]:>8}')
        print('='*60)
