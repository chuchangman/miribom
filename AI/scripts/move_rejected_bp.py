#!/usr/bin/env python3
import os
import sys
import shutil
import pandas as pd
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)

PROCESSED_BP = Path('data/processed/beam_projector')
REJECTED_BASE = Path('data/rejected/beam_projector')
LOG_CSV = Path('data/metadata/beam_projector_rejected_log.csv')

moves = [
    # wrong_product (7장)
    ('data/processed/beam_projector/naver_0014.jpg', 'wrong_product', '히터처럼 생긴 세로 박스형 제품'),
    ('data/processed/beam_projector/naver_0090.jpg', 'wrong_product', '모니터형 LCD 패널'),
    ('data/processed/beam_projector/naver_0181.jpg', 'wrong_product', '에어컨 본체형'),
    ('data/processed/beam_projector/naver_0188.jpg', 'wrong_product', '전자레인지형 정면 문'),
    ('data/processed/beam_projector/naver_0230.jpg', 'wrong_product', '히터형 세로 본체'),
    ('data/processed/beam_projector/naver_0250.jpg', 'wrong_product', '히터형 세로 본체'),
    ('data/processed/beam_projector/naver_0252.jpg', 'wrong_product', '모니터형 가로 패널'),
    # ambiguous_product (6장)
    ('data/processed/beam_projector/naver_0096.jpg', 'ambiguous_product', '렌즈 미확인, 히터 유사'),
    ('data/processed/beam_projector/naver_0121.jpg', 'ambiguous_product', '렌즈 미확인, 에어컨 유사'),
    ('data/processed/beam_projector/naver_0123.jpg', 'ambiguous_product', '렌즈 미확인, 경계선'),
    ('data/processed/beam_projector/naver_0200.jpg', 'ambiguous_product', '여러 제품 세트 사진'),
    ('data/processed/beam_projector/naver_0202.jpg', 'ambiguous_product', '외형 경계선'),
    ('data/processed/beam_projector/naver_0214.jpg', 'ambiguous_product', '렌즈 미확인'),
    # bad_input (1장)
    ('data/processed/beam_projector/naver_0242.jpg', 'bad_input', '제품 일부만 찍힌 크롭'),
    # text_image (1장)
    ('data/processed/beam_projector/naver_0291.jpg', 'text_image', '광고 배너 텍스트 이미지'),
]

# 폴더 생성
for reason in ['wrong_product', 'ambiguous_product', 'bad_input', 'text_image']:
    (REJECTED_BASE / reason).mkdir(parents=True, exist_ok=True)
    print(f'  폴더 생성: {REJECTED_BASE / reason}')

print()

log_rows = []
moved_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
errors = []

for src_str, reason, note in moves:
    src = Path(src_str)
    dst = REJECTED_BASE / reason / src.name
    if not src.exists():
        print(f'  [SKIP] 파일 없음: {src}')
        errors.append(src_str)
        continue
    shutil.move(str(src), str(dst))
    print(f'  [MOVE] {src}  ->  {dst}')
    log_rows.append({
        'original_path': src_str,
        'rejected_path': str(dst),
        'class_label':   'beam_projector',
        'reject_reason': reason,
        'note':          note,
        'moved_at':      moved_at,
    })

print()

# 로그 CSV 저장
log_df = pd.DataFrame(log_rows)
LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
log_df.to_csv(LOG_CSV, index=False, encoding='utf-8-sig')
print(f'  로그 저장: {LOG_CSV}  ({len(log_df)}행)')

# 검증
remaining = sorted(f for f in PROCESSED_BP.iterdir() if f.suffix.lower() in {'.jpg', '.jpeg', '.png'})
print()
print('=' * 55)
print('검증')
print('=' * 55)
print(f'  processed/beam_projector 잔여: {len(remaining)}장  (예상 290장)')
print()

reason_counts = {}
for _, reason, _ in moves:
    reason_counts[reason] = reason_counts.get(reason, 0) + 1

print('  reason별 이동 수량:')
for reason, cnt in sorted(reason_counts.items()):
    actual = len(list((REJECTED_BASE / reason).iterdir()))
    print(f'    {reason:<22} 이동 {cnt}장  /  폴더 내 현재 {actual}장')

if errors:
    print()
    print(f'  [경고] 파일 없음으로 SKIP된 항목: {len(errors)}건')
    for e in errors:
        print(f'    {e}')
else:
    print()
    print('  오류 없음 — 전체 이동 완료')
