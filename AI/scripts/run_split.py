"""
04_split_dataset.ipynb 로직을 그대로 구현한 독립 실행 스크립트.
data/processed/{class}/ → data/split/{train,valid,test}/{class}/
비율: 8 : 1 : 1  |  Stratified  |  Seed: 42
"""

import os
import sys
import shutil
from pathlib import Path

from PIL import Image
import imagehash
from sklearn.model_selection import train_test_split
from tqdm import tqdm

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

SPLIT_DIR = config.SPLIT_DIR
SEED      = config.SPLIT_SEED

print(f'PROCESSED_DIR : {config.PROCESSED_DIR}')
print(f'SPLIT_DIR     : {SPLIT_DIR}')
print(f'SEED          : {SEED}')
print(f'PROJECT_LABELS: {len(config.PROJECT_LABELS)}개')

# ── PROJECT_LABELS vs processed 폴더 일치 확인 ─────────────────────────────────
actual_labels = sorted([
    d for d in os.listdir(config.PROCESSED_DIR)
    if os.path.isdir(os.path.join(config.PROCESSED_DIR, d))
    and any(f.lower().endswith(('.jpg', '.jpeg', '.png'))
            for f in os.listdir(os.path.join(config.PROCESSED_DIR, d)))
])
expected_labels = sorted(config.PROJECT_LABELS)

assert actual_labels == expected_labels, (
    f'PROJECT_LABELS와 실제 processed 폴더가 다릅니다.\n'
    f'PROJECT_LABELS : {expected_labels}\n'
    f'processed 폴더 : {actual_labels}'
)
print(f'PROJECT_LABELS 일치 확인 OK: {len(actual_labels)}개 클래스\n')

# ── 파일 목록 수집 ────────────────────────────────────────────────────────────
print('=== Split 대상 이미지 현황 ===')
class_files = {}
for cls in sorted(os.listdir(config.PROCESSED_DIR)):
    cls_path = os.path.join(config.PROCESSED_DIR, cls)
    if not os.path.isdir(cls_path):
        continue
    files = sorted(
        os.path.join(cls_path, f)
        for f in os.listdir(cls_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    )
    if not files:
        continue
    class_files[cls] = files
    print(f'  {cls:<22}: {len(files):4d}장')

total_before = sum(len(v) for v in class_files.values())
print(f'\n합계: {total_before}장 | 클래스: {len(class_files)}개')

# ── Corrupt / 소형 이미지 제외 ────────────────────────────────────────────────
print('\n=== 이미지 유효성 검사 ===')
valid_files  = {}
corrupt_log  = []
small_log    = []

for cls, files in class_files.items():
    ok = []
    for fpath in tqdm(files, desc=f'  {cls}', leave=False):
        try:
            img = Image.open(fpath).convert('RGB')
            w, h = img.size
            if w < config.MIN_CROP_SIZE or h < config.MIN_CROP_SIZE:
                small_log.append((fpath, w, h))
            else:
                ok.append(fpath)
        except Exception as e:
            corrupt_log.append((fpath, str(e)))
    valid_files[cls] = ok

if corrupt_log:
    print(f'[경고] 손상된 이미지 {len(corrupt_log)}개 (split 제외):')
    for p, e in corrupt_log:
        print(f'  {os.path.basename(p)}: {e}')
else:
    print('손상된 이미지: 없음 OK')

if small_log:
    print(f'[경고] 소형 이미지 {len(small_log)}개 (<{config.MIN_CROP_SIZE}px, split 제외)')
else:
    print('소형 이미지: 없음 OK')

total_valid = sum(len(v) for v in valid_files.values())
excluded    = total_before - total_valid
print(f'\n유효 이미지: {total_valid}장 | 제외: {excluded}장')

# ── 기존 split 폴더 초기화 ────────────────────────────────────────────────────
if os.path.exists(SPLIT_DIR):
    shutil.rmtree(SPLIT_DIR)
    print(f'\n기존 {SPLIT_DIR} 삭제 후 재생성')

for split in ('train', 'valid', 'test'):
    for cls in valid_files:
        os.makedirs(os.path.join(SPLIT_DIR, split, cls), exist_ok=True)

# ── Stratified 8:1:1 split + 파일 복사 ────────────────────────────────────────
print('\n=== Split 실행 (8:1:1 stratified) ===')
split_counts = {split: {} for split in ('train', 'valid', 'test')}

for cls, files in valid_files.items():
    if len(files) < 3:
        print(f'  [건너뜀] {cls}: {len(files)}장 (최소 3장 필요)')
        continue

    # 80% train, 나머지 20%
    train_files, temp_files = train_test_split(
        files, test_size=0.2, random_state=SEED
    )
    # 나머지 50:50 → 각 10%
    valid_files_split, test_files = train_test_split(
        temp_files, test_size=0.5, random_state=SEED
    )

    for fpath in train_files:
        shutil.copy2(fpath, os.path.join(SPLIT_DIR, 'train', cls, os.path.basename(fpath)))
    for fpath in valid_files_split:
        shutil.copy2(fpath, os.path.join(SPLIT_DIR, 'valid', cls, os.path.basename(fpath)))
    for fpath in test_files:
        shutil.copy2(fpath, os.path.join(SPLIT_DIR, 'test',  cls, os.path.basename(fpath)))

    split_counts['train'][cls] = len(train_files)
    split_counts['valid'][cls] = len(valid_files_split)
    split_counts['test'][cls]  = len(test_files)

# ── 결과 출력 ──────────────────────────────────────────────────────────────────
print(f'\n{"클래스":<22} {"train":>6} {"valid":>6} {"test":>6} {"합계":>6}')
print('-' * 50)
t_tr = t_vl = t_te = 0
for cls in sorted(split_counts['train']):
    tr = split_counts['train'][cls]
    vl = split_counts['valid'][cls]
    te = split_counts['test'][cls]
    print(f'{cls:<22} {tr:>6} {vl:>6} {te:>6} {tr+vl+te:>6}')
    t_tr += tr; t_vl += vl; t_te += te

print('-' * 50)
print(f'{"합계":<22} {t_tr:>6} {t_vl:>6} {t_te:>6} {t_tr+t_vl+t_te:>6}')
print(f'\nSplit 완료: data/split/ 생성됨')
