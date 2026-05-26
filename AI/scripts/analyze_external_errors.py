#!/usr/bin/env python3
"""
External test 오답 17건 분석 스크립트
- 오답 contact sheet PNG 생성
- 오답 원인 분류용 CSV 생성 (error_type 빈칸)
- confidence 구간별 정확도 출력
"""

import os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image as PILImage

project_root = Path(__file__).parent.parent  # AI/
os.chdir(project_root)

PRED_CSV     = Path('data/metadata/external_test_predictions.csv')
CONTACT_PNG  = Path('data/metadata/external_test_wrong_contact.png')
ANALYSIS_CSV = Path('data/metadata/external_test_error_analysis.csv')

# ── 데이터 로드 ────────────────────────────────────────────────────────────────
df      = pd.read_csv(PRED_CSV)
wrong   = df[~df['service_correct']].reset_index(drop=True)
total   = len(df)
n_wrong = len(wrong)

print(f'전체: {total}장  |  오답: {n_wrong}건  |  정확도: {(total-n_wrong)/total:.1%}')
print()
print('오답 목록:')
for _, row in wrong.iterrows():
    fname = Path(row['image_path']).name
    folder = Path(row['image_path']).parent.name
    print(f'  [{folder}] {fname}  true={row["service_true_label"]}  '
          f'pred={row["service_pred_label"]} ({row["fine_pred_label"]})  '
          f'conf={row["confidence"]:.3f}')

# ── 1. Contact Sheet PNG ───────────────────────────────────────────────────────
NCOLS = 4
NROWS = int(np.ceil(n_wrong / NCOLS))

fig, axes = plt.subplots(NROWS, NCOLS, figsize=(NCOLS * 3.8, NROWS * 4.4))
axes_flat = axes.flatten()

for idx, (_, row) in enumerate(wrong.iterrows()):
    ax = axes_flat[idx]

    # 이미지 로드
    try:
        img = PILImage.open(row['image_path']).convert('RGB')
        ax.imshow(img, aspect='auto')
    except Exception as e:
        ax.set_facecolor('#222')
        ax.text(0.5, 0.5, f'load error\n{e}', ha='center', va='center',
                transform=ax.transAxes, fontsize=7, color='white')

    fname   = Path(row['image_path']).name
    folder  = Path(row['image_path']).parent.name
    true_   = row['service_true_label']
    pred_   = row['service_pred_label']
    fine_   = row['fine_pred_label']
    conf_   = row['confidence']

    # 오답 방향에 따라 색상 구분
    # ref→wd: 주황 / wd→ref: 빨강
    color = '#E65100' if true_ == 'refrigerator' else '#B71C1C'

    title = (
        f'{fname}  [{folder}]\n'
        f'True : {true_}\n'
        f'Pred : {pred_}  ({fine_})\n'
        f'Conf : {conf_:.3f}'
    )
    ax.set_title(title, fontsize=7.2, color=color, pad=4,
                 fontfamily='monospace', loc='left')

    # 테두리 강조
    for spine in ax.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(2.5)
    ax.set_xticks([])
    ax.set_yticks([])

# 빈 슬롯 숨기기
for idx in range(n_wrong, len(axes_flat)):
    axes_flat[idx].set_visible(False)

fig.suptitle(
    f'External Test  —  Service-level Wrong Predictions  '
    f'{n_wrong} / {total}  (acc {(total-n_wrong)/total:.1%})\n'
    f'Orange = ref→wd    Red = wd→ref',
    fontsize=12, fontweight='bold', y=1.005
)
plt.tight_layout(pad=1.2)
plt.savefig(CONTACT_PNG, dpi=150, bbox_inches='tight')
plt.close()
print(f'\n[1] Contact sheet: {CONTACT_PNG}')

# ── 2. 오답 원인 분류 CSV ──────────────────────────────────────────────────────
analysis_df = pd.DataFrame({
    'image_path':      wrong['image_path'].values,
    'true_label':      wrong['service_true_label'].values,
    'pred_label':      wrong['service_pred_label'].values,
    'pred_fine_label': wrong['fine_pred_label'].values,
    'confidence':      wrong['confidence'].round(6).values,
    'error_type':      '',   # 사람이 직접 채움: label_error / bad_input / ambiguous_product / model_error
    'note':            '',
})
analysis_df.to_csv(ANALYSIS_CSV, index=False, encoding='utf-8-sig')
print(f'[2] 분석 CSV  : {ANALYSIS_CSV}')

# ── 3. Confidence 구간별 정확도 ────────────────────────────────────────────────
bins   = [0.0, 0.50, 0.70, 0.80, 0.90, 0.95, 1.001]
labels = ['<0.50', '0.50~0.70', '0.70~0.80', '0.80~0.90', '0.90~0.95', '>=0.95']
df['conf_bin'] = pd.cut(df['confidence'], bins=bins, labels=labels, right=False)

print()
print('=== Confidence 구간별 정확도 ===')
print(f"{'구간':>12}  {'전체':>5}  {'정답':>5}  {'오답':>5}  {'정확도':>8}")
print('─' * 48)
for lbl in labels:
    sub   = df[df['conf_bin'] == lbl]
    n_tot = len(sub)
    n_cor = int(sub['service_correct'].sum())
    n_err = n_tot - n_cor
    acc   = f'{n_cor/n_tot:.1%}' if n_tot > 0 else 'N/A'
    print(f'{lbl:>12}  {n_tot:>5}  {n_cor:>5}  {n_err:>5}  {acc:>8}')
print('─' * 48)
n_cor_all = int(df['service_correct'].sum())
print(f'{"합계":>12}  {total:>5}  {n_cor_all:>5}  {total-n_cor_all:>5}  '
      f'{n_cor_all/total:.1%}')
