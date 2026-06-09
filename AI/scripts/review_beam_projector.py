#!/usr/bin/env python3
"""
beam_projector 학습 데이터 검수용 contact sheet 생성 + rejected 후보 CSV 템플릿

생성 파일:
  data/metadata/review_bp_processed_p01~04.png  — processed/ 검수 시트 (305장)
  data/metadata/review_bp_train_p01~03.png      — split/train/ 검수 시트 (244장)
  data/metadata/review_bp_valid.png             — split/valid/ 검수 시트 (30장)
  data/metadata/review_bp_test.png              — split/test/ 검수 시트 (31장)
  data/metadata/beam_projector_reject_candidates.csv  — 거절 후보 CSV 템플릿
"""

import os
import sys
import math
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image as PILImage

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)

# ── 경로 설정 ─────────────────────────────────────────────────────────────────
PROCESSED_BP = Path('data/processed/beam_projector')
SPLIT_DIRS   = {
    'train': Path('data/split/train/beam_projector'),
    'valid': Path('data/split/valid/beam_projector'),
    'test':  Path('data/split/test/beam_projector'),
}
OUT_DIR      = Path('data/metadata')
REJECT_CSV   = OUT_DIR / 'beam_projector_reject_candidates.csv'

EXTS         = {'.jpg', '.jpeg', '.png'}

# ── 레이아웃 파라미터 ─────────────────────────────────────────────────────────
NCOLS     = 10    # 열 수
PAGE_SIZE = 80    # 페이지당 이미지 수  (NCOLS의 배수 권장: 80 = 8행×10열)
NROWS_PER = PAGE_SIZE // NCOLS
CELL_W    = 1.85  # 인치/셀
CELL_H    = 2.55  # 인치/셀 (제목 포함)
THUMB_PX  = 280   # PIL thumbnail 크기 (속도 최적화)
DPI       = 120

# ── 유틸 ─────────────────────────────────────────────────────────────────────
def get_images(directory: Path):
    """알파벳 순 정렬된 이미지 파일 목록 반환"""
    if not directory.exists():
        return []
    return sorted(f for f in directory.iterdir() if f.suffix.lower() in EXTS)


def load_thumb(path: Path):
    """PIL 썸네일 로드, 실패 시 None"""
    try:
        img = PILImage.open(path).convert('RGB')
        img.thumbnail((THUMB_PX, THUMB_PX), PILImage.LANCZOS)
        return img
    except Exception:
        return None


def make_review_page(images, page_title, save_path):
    """단일 페이지 contact sheet 생성"""
    n     = len(images)
    nrows = math.ceil(n / NCOLS)
    fig, axes = plt.subplots(nrows, NCOLS,
                              figsize=(NCOLS * CELL_W, nrows * CELL_H))
    axes_flat = np.array(axes).flatten()

    for slot, (g_idx, img_path) in enumerate(images):
        ax  = axes_flat[slot]
        img = load_thumb(img_path)

        if img is not None:
            ax.imshow(np.array(img), aspect='auto')
        else:
            ax.set_facecolor('#1c1c1c')
            ax.text(0.5, 0.5, 'ERR', ha='center', va='center',
                    transform=ax.transAxes, color='#888', fontsize=8)

        fname = img_path.name
        # 타이틀: 전역 인덱스 + 파일명 (파일명이 길면 줄임)
        short_name = fname if len(fname) <= 20 else fname[:18] + '..'
        ax.set_title(
            f'#{g_idx:04d}  {short_name}',
            fontsize=5.5, pad=2,
            fontfamily='monospace', color='#222',
        )
        for spine in ax.spines.values():
            spine.set_edgecolor('#bbbbbb')
            spine.set_linewidth(0.6)
        ax.set_xticks([])
        ax.set_yticks([])

    for slot in range(n, len(axes_flat)):
        axes_flat[slot].set_visible(False)

    fig.suptitle(page_title, fontsize=10, fontweight='bold', y=1.002)
    plt.tight_layout(pad=0.35)
    plt.savefig(save_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f'    {save_path}  ({n}장)')


def make_contact_sheets(directory: Path, label: str, out_prefix: str):
    """
    디렉토리 내 이미지 전체를 PAGE_SIZE장 단위로 나눠 PNG 저장.
    반환: 저장된 파일 목록
    """
    images = get_images(directory)
    n      = len(images)
    if n == 0:
        print(f'  [{label}] 이미지 없음 ({directory})')
        return []

    n_pages = math.ceil(n / PAGE_SIZE)
    saved   = []
    print(f'  [{label}]  {n}장  →  {n_pages}페이지')

    for page in range(n_pages):
        start = page * PAGE_SIZE
        end   = min(start + PAGE_SIZE, n)
        batch = [(start + i + 1, images[start + i]) for i in range(end - start)]
        # 전역 인덱스는 1부터 시작

        page_title = (
            f'beam_projector / {label}  —  '
            f'{n}장 중 #{start+1:04d}~#{end:04d}  '
            f'(Page {page+1}/{n_pages})\n'
            f'검수 기준: heater/monitor/microwave/air_conditioner 형태 이미지 식별'
        )
        fname   = f'{out_prefix}_p{page+1:02d}.png' if n_pages > 1 else f'{out_prefix}.png'
        outpath = OUT_DIR / fname
        make_review_page(batch, page_title, outpath)
        saved.append(str(outpath))

    return saved


# ═══════════════════════════════════════════════════════════════════════════════
# 1. processed/ contact sheets
# ═══════════════════════════════════════════════════════════════════════════════
print('=' * 65)
print('1. processed/beam_projector/ contact sheet 생성')
print('=' * 65)
saved_processed = make_contact_sheets(PROCESSED_BP, 'processed', 'review_bp_processed')

# ═══════════════════════════════════════════════════════════════════════════════
# 2. split/ contact sheets (train / valid / test)
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('2. split/beam_projector/ contact sheet 생성')
print('=' * 65)
saved_split = {}
for split_name, split_dir in SPLIT_DIRS.items():
    saved_split[split_name] = make_contact_sheets(
        split_dir, split_name, f'review_bp_{split_name}'
    )

# ═══════════════════════════════════════════════════════════════════════════════
# 3. rejected 후보 CSV 템플릿 생성
#    processed/ 기준 (정답 데이터 관리 단위)
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('3. rejected 후보 CSV 템플릿 생성')
print('=' * 65)

proc_images = get_images(PROCESSED_BP)
reject_rows = []
for idx, img_path in enumerate(proc_images, start=1):
    reject_rows.append({
        'index':        idx,
        'image_path':   str(img_path),
        'class_label':  'beam_projector',
        'reject_reason': '',   # 사람이 직접 채움
        'note':          '',
    })

reject_df = pd.DataFrame(reject_rows)
reject_df.to_csv(REJECT_CSV, index=False, encoding='utf-8-sig')
print(f'  저장: {REJECT_CSV}  ({len(reject_df)}행)')
print()
print(f'  reject_reason 후보:')
print(f'    label_noise       — beam_projector가 아닌 다른 제품 (heater/monitor/micro 등)')
print(f'    wrong_product     — 완전히 다른 카테고리 제품')
print(f'    partial_crop      — 제품 일부만 찍힌 이미지')
print(f'    text_image        — 광고 배너/텍스트 도배')
print(f'    ambiguous_product — 두 클래스 모두 해당되는 외형')
print()
print(f'  사용 방법:')
print(f'    1. contact sheet에서 의심 이미지의 index(#XXXX) 확인')
print(f'    2. CSV에서 해당 index 행의 reject_reason 입력')
print(f'    3. note에 구체적 사유 기재 (예: "히터처럼 생긴 흰색 박스형")')
print(f'    4. 검수 완료 후 reject_reason != "" 행 목록을 다음 작업에 전달')

# ═══════════════════════════════════════════════════════════════════════════════
# 4. 검수 기준 안내
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('4. 사용자 직접 확인 기준')
print('=' * 65)
print()
print('  [제거 대상 — label_noise / wrong_product]')
print('  ① heater 형태:')
print('    - 세로 직사각형 박스 형태 (히터 실루엣과 동일)')
print('    - 하단 통풍구, 손잡이, 온풍구 있는 이미지')
print('    - 브랜드: 델롱기, 다이슨 히터, 신일, 귀뚜라미 등')
print()
print('  ② monitor 형태:')
print('    - 가로 넓은 LCD 패널 + 받침대 구조')
print('    - 테두리 두꺼운 베젤, 뒷면 포트 노출 이미지')
print()
print('  ③ microwave 형태:')
print('    - 정면 문짝 + 손잡이 + 조작 패널 구조')
print('    - 내부 회전판 보이는 이미지')
print()
print('  ④ air_conditioner 형태:')
print('    - 스탠드형 세로 직사각형 본체')
print('    - 벽걸이형 가로 직사각형')
print('    - 에어컨 특유의 전면 루버(바람방향 날개) 있는 이미지')
print()
print('  [경계선 이미지 — ambiguous_product]')
print('  - 빔프로젝터와 기타 제품의 중간 형태')
print('  - 렌즈가 없지만 빔프로젝터라고 할 수 있는 이미지')
print('  - 여러 제품이 함께 찍힌 이미지 (세트 사진)')
print()
print('  [정상 beam_projector 특징]')
print('  - 렌즈 구멍이 정면/측면에 명확히 보임')
print('  - 소형/대형 프로젝터 본체 (포커스 링, 환기구 등)')
print('  - 미니빔, 피코 프로젝터, 시네마 프로젝터 등')

# ═══════════════════════════════════════════════════════════════════════════════
# 5. 최종 요약
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('5. 생성된 파일 목록')
print('=' * 65)
print()
print('  [processed/ contact sheets]')
for p in saved_processed:
    print(f'    {p}')

print()
print('  [split/ contact sheets]')
for split_name, paths in saved_split.items():
    for p in paths:
        print(f'    {p}')

print()
print(f'  [rejected 후보 CSV 템플릿]')
print(f'    {REJECT_CSV}')

print()
print('=' * 65)
print('6. 다음 작업 순서')
print('=' * 65)
print()
print('  Step 1. contact sheet 육안 검수')
print('          processed 4페이지 → train 3페이지 → valid/test 각 1페이지')
print()
print('          검수 우선순위:')
print('          - heater 형태  (세로 박스, 히터처럼 생긴 제품)')
print('          - monitor 형태 (가로 LCD 패널)')
print('          - microwave 형태 (정면 문 + 손잡이)')
print('          - air_conditioner 형태 (세로 본체)')
print()
print('  Step 2. beam_projector_reject_candidates.csv 작성')
print('          → index 번호로 이미지 특정')
print('          → reject_reason + note 입력')
print()
print('  Step 3. 거절 이미지 수 집계 후 판단')
print('          - 거절 10장 이상: processed에서 제거 후 split 재생성 권장')
print('          - 거절 10장 미만: 재학습 효과 미미 — 다른 클래스 보강 먼저')
print()
print('  Step 4. (검수 완료 후) humidifier / heater 추가 수집 진행')
print()
print(f'  완료 시각: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
