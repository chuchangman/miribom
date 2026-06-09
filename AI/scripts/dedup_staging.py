"""
staging 폴더 내 중복 이미지 제거 스크립트 (phash 기반)

- data/staging/{class_name}/ 하위 이미지에 대해 phash 중복 검사
- 중복 판정 기준: phash 해밍거리 <= PHASH_THRESH (기본값 8)
- 중복 발견 시 해상도가 낮은 쪽 삭제 (같으면 나중 파일 삭제)
- metadata CSV의 status를 'dedup_deleted' 로 업데이트
- data/processed/ 는 절대 건드리지 않음

사용법:
    python scripts/dedup_staging.py                          # 전체 18클래스
    python scripts/dedup_staging.py refrigerator washer_dryer  # 특정 클래스만
"""

import os
import sys
import argparse
from pathlib import Path

import pandas as pd
import imagehash
from PIL import Image as PILImage
from tqdm import tqdm

# ── 프로젝트 루트 설정 ────────────────────────────────────────────────────────────
project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

PHASH_THRESH = 8   # 해밍거리 임계값 (0=완전동일, 클수록 관대) — main()에서 args로 덮어씀


def get_image_area(path: str) -> int:
    try:
        img = PILImage.open(path)
        w, h = img.size
        return w * h
    except Exception:
        return 0


def dedup_class(class_name: str, thresh: int = PHASH_THRESH) -> dict:
    staging_dir = Path('data') / 'staging' / class_name
    metadata_csv = Path(config.METADATA_DIR) / f'{class_name}_staging_metadata.csv'

    if not staging_dir.exists():
        print(f'  [{class_name}] staging 폴더 없음 — 건너뜀')
        return {'class_name': class_name, 'total': 0, 'removed': 0, 'kept': 0}

    # 이미지 목록 수집
    all_images = sorted(
        p for p in staging_dir.rglob('*')
        if p.suffix.lower() in ('.jpg', '.jpeg', '.png') and p.is_file()
    )
    total = len(all_images)
    print(f'\n[{class_name}] 총 {total}장 phash 계산 중...')

    # phash 계산
    hashes = []   # [(path, hash, area)]
    for p in tqdm(all_images, desc=f'  {class_name}', leave=False):
        try:
            h = imagehash.phash(PILImage.open(p))
            area = get_image_area(str(p))
            hashes.append((p, h, area))
        except Exception:
            hashes.append((p, None, 0))

    # 중복 탐지 — O(n²) but n은 최대 1600장이므로 허용
    removed_paths = set()
    for i in range(len(hashes)):
        p_i, h_i, a_i = hashes[i]
        if h_i is None or str(p_i) in removed_paths:
            continue
        for j in range(i + 1, len(hashes)):
            p_j, h_j, a_j = hashes[j]
            if h_j is None or str(p_j) in removed_paths:
                continue
            dist = h_i - h_j
            if dist <= thresh:
                # 해상도가 낮은 쪽 삭제 (같으면 j 삭제)
                if a_i >= a_j:
                    removed_paths.add(str(p_j))
                else:
                    removed_paths.add(str(p_i))
                    break   # i가 삭제됐으니 i 루프 탈출

    # 실제 삭제
    n_removed = 0
    for rp in removed_paths:
        try:
            os.remove(rp)
            n_removed += 1
        except Exception as e:
            print(f'  삭제 실패: {rp} — {e}')

    kept = total - n_removed

    # metadata CSV 업데이트
    if metadata_csv.exists() and n_removed > 0:
        df = pd.read_csv(metadata_csv, encoding='utf-8-sig')
        if 'saved_path' in df.columns:
            removed_norm = {str(Path(p)) for p in removed_paths}
            def _norm(p):
                try:
                    return str(Path(str(p))) if pd.notna(p) else ''
                except Exception:
                    return ''
            mask = df['saved_path'].apply(_norm).isin(removed_norm)
            df.loc[mask, 'status'] = 'dedup_deleted'
            df.to_csv(metadata_csv, index=False, encoding='utf-8-sig')

    print(f'  [{class_name}] 완료: {total}장 → 제거 {n_removed}장 → 잔여 {kept}장')
    return {'class_name': class_name, 'total': total, 'removed': n_removed, 'kept': kept}


def main():
    parser = argparse.ArgumentParser(description='staging 중복 이미지 제거')
    parser.add_argument('classes', nargs='*', help='대상 클래스 (생략 시 전체)')
    parser.add_argument('--thresh', type=int, default=PHASH_THRESH,
                        help=f'phash 해밍거리 임계값 (기본 {PHASH_THRESH})')
    args = parser.parse_args()

    all_classes = list(config.NAVER_SEARCH_QUERIES.keys())
    thresh = args.thresh
    target = args.classes if args.classes else all_classes

    invalid = [c for c in target if c not in all_classes]
    if invalid:
        print(f'[오류] 알 수 없는 클래스: {invalid}')
        sys.exit(1)

    print(f'중복 제거 대상: {len(target)}개 클래스  (phash 임계값: {thresh})')

    results = [dedup_class(cls, thresh) for cls in target]

    # 최종 요약
    print('\n' + '='*60)
    print('중복 제거 완료 요약')
    print('='*60)
    print(f'{"클래스":<20} {"원본":>6} {"제거":>6} {"잔여":>6}')
    print('-'*60)
    total_orig = total_rm = total_kept = 0
    for r in results:
        print(f'{r["class_name"]:<20} {r["total"]:>6} {r["removed"]:>6} {r["kept"]:>6}')
        total_orig += r['total']
        total_rm   += r['removed']
        total_kept += r['kept']
    print('-'*60)
    print(f'{"합계":<20} {total_orig:>6} {total_rm:>6} {total_kept:>6}')
    print(f'\n제거율: {total_rm/total_orig*100:.1f}%  ({total_rm}장 삭제)')


if __name__ == '__main__':
    main()
