"""
staging에 남아 있는 이미지 전부를 approved로 처리 → data/processed/{class_name}/

사용법:
    python scripts/approve_all_staging.py refrigerator washer_dryer wash_tower
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

import pandas as pd
import imagehash
from PIL import Image as PILImage
from tqdm import tqdm

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

PHASH_THRESH = 5


def approve_class(class_name: str) -> dict:
    print(f'\n{"="*60}')
    print(f'승인 처리: {class_name}')
    print(f'{"="*60}')

    staging_dir  = Path('data') / 'staging' / class_name
    proc_dir     = Path(config.PROCESSED_DIR) / class_name
    metadata_csv = Path(config.METADATA_DIR) / f'{class_name}_staging_metadata.csv'

    if not staging_dir.exists():
        print(f'  [건너뜀] staging 폴더 없음: {staging_dir}')
        return {'class_name': class_name, 'moved': 0, 'dedup': 0, 'error': 0}

    proc_dir.mkdir(parents=True, exist_ok=True)

    # 남아 있는 staging 이미지 전부 수집
    remaining = []
    for d in sorted(staging_dir.iterdir()):
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
                remaining.append(f)

    print(f'  staging 잔여 이미지: {len(remaining)}장')

    # 기존 processed phash 계산
    print('  기존 processed phash 계산 중...')
    proc_hashes = {}
    existing = [f for f in proc_dir.iterdir()
                if f.suffix.lower() in ('.jpg', '.jpeg', '.png')]
    for f in tqdm(existing, desc='  processed phash', leave=False):
        try:
            proc_hashes[f.name] = imagehash.phash(PILImage.open(f))
        except Exception:
            pass

    # 다음 인덱스 결정
    naver_nums = [
        int(f.stem[6:]) for f in proc_dir.iterdir()
        if f.name.startswith('naver_') and f.stem[6:].isdigit()
    ]
    next_idx = (max(naver_nums) + 1) if naver_nums else 0

    # metadata 로드
    if metadata_csv.exists():
        meta_df = pd.read_csv(metadata_csv, encoding='utf-8-sig')
    else:
        meta_df = pd.DataFrame()

    def _norm(p):
        try:
            return str(Path(str(p))) if pd.notna(p) else ''
        except Exception:
            return ''

    moved_list  = []
    dedup_list  = []
    error_list  = []

    for src in tqdm(remaining, desc=f'  {class_name} 이동', unit='장'):
        try:
            h = imagehash.phash(PILImage.open(src))
        except Exception as e:
            print(f'  [오류] {src.name}: {e}')
            error_list.append(src)
            continue

        # phash 중복 검사
        dup = [(name, h - ph) for name, ph in proc_hashes.items() if h - ph <= PHASH_THRESH]
        if dup:
            dup.sort(key=lambda x: x[1])
            dedup_list.append((src, dup[0]))
            continue

        new_name = f'naver_{next_idx:04d}.jpg'
        dst = proc_dir / new_name
        shutil.move(str(src), str(dst))
        proc_hashes[new_name] = h
        moved_list.append((src, dst))
        next_idx += 1

    # metadata 업데이트
    if not meta_df.empty and 'saved_path' in meta_df.columns:
        norm_col = meta_df['saved_path'].apply(_norm)

        # 이동된 파일 → approved
        for src, dst in moved_list:
            mask = norm_col == _norm(src)
            meta_df.loc[mask, 'status']     = 'approved'
            meta_df.loc[mask, 'saved_path'] = str(dst)

        # 잔여 staged 중 실제 파일이 없는 것 → deleted (사람이 삭제한 것)
        remaining_paths = {_norm(p) for p in remaining}
        staged_mask  = meta_df['status'] == 'staged'
        norm_fresh   = meta_df['saved_path'].apply(_norm)
        deleted_mask = staged_mask & ~norm_fresh.isin(remaining_paths)
        n_deleted    = int(deleted_mask.sum())
        meta_df.loc[deleted_mask, 'status'] = 'deleted'

        meta_df.to_csv(metadata_csv, index=False, encoding='utf-8-sig')
        print(f'  metadata 업데이트: {metadata_csv}')
        if n_deleted:
            print(f'    수동 삭제 기록: {n_deleted}건 → status=deleted')

    # 결과 출력
    proc_total = len([f for f in proc_dir.iterdir()
                      if f.suffix.lower() in ('.jpg', '.jpeg', '.png')])

    print(f'\n  결과 ─ 이동 {len(moved_list)}장 | phash중복 {len(dedup_list)}장 | 오류 {len(error_list)}장')
    print(f'  processed/{class_name}: 누적 {proc_total}장')

    return {
        'class_name': class_name,
        'moved':      len(moved_list),
        'dedup':      len(dedup_list),
        'error':      len(error_list),
        'proc_total': proc_total,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('classes', nargs='+')
    args = parser.parse_args()

    results = []
    for cls in args.classes:
        results.append(approve_class(cls))

    print(f'\n{"="*60}')
    print('승인 처리 완료 요약')
    print('="*60')
    print(f'{"클래스":<20} {"이동":>6} {"중복제외":>8} {"오류":>6} {"processed합계":>13}')
    print('-'*60)
    for r in results:
        print(f'{r["class_name"]:<20} {r["moved"]:>6} {r["dedup"]:>8} '
              f'{r["error"]:>6} {r.get("proc_total", 0):>13}')

    print()
    print('다음 단계:')
    print('  1. data/processed/ 확인 후 이상 없으면')
    print('  2. config.py 에서 PROJECT_LABELS 18개로 변경')
    print('  3. 04_split_dataset.ipynb 실행 (split 재생성)')
    print('  4. 05_train_efficientnetv2.ipynb 실행 (18-class 학습)')


if __name__ == '__main__':
    main()
