#!/usr/bin/env python3
"""
Phase 3 18-class 오답 분석 스크립트

생성 파일:
  data/metadata/phase3_wrong_contact.png        — 전체 35건 contact sheet
  data/metadata/phase3_wrong_humidifier.png     — humidifier 관련 오답
  data/metadata/phase3_wrong_heater.png         — heater 관련 오답
  data/metadata/phase3_low_conf_contact.png     — low confidence (<0.70) 22건
  data/metadata/phase3_error_analysis.csv       — 오답 분석 CSV (error_type 빈칸)
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
import matplotlib.patches as mpatches
from PIL import Image as PILImage

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

# ── 경로 ─────────────────────────────────────────────────────────────────────
PRED_CSV        = Path('data/metadata/test_predictions_phase3.csv')
OUT_ALL         = Path('data/metadata/phase3_wrong_contact.png')
OUT_HUMID       = Path('data/metadata/phase3_wrong_humidifier.png')
OUT_HEATER      = Path('data/metadata/phase3_wrong_heater.png')
OUT_LOWCONF     = Path('data/metadata/phase3_low_conf_contact.png')
ANALYSIS_CSV    = Path('data/metadata/phase3_error_analysis.csv')

LOW_CONF_THRESH = 0.70

# ── 색상 정의 ──────────────────────────────────────────────────────────────────
COLOR_SVC_WRONG  = '#D32F2F'   # 빨강  — 서비스 대분류 오답 (심각)
COLOR_SVC_OK     = '#E65100'   # 주황  — 세부 오답이나 서비스 대분류 정답
COLOR_CORRECT    = '#2E7D32'   # 초록  — 정답 (low conf 시트에서 사용)
COLOR_LOW_CONF   = '#1565C0'   # 파랑  — 정답이지만 low confidence

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
df = pd.read_csv(PRED_CSV)
total   = len(df)
wrong   = df[~df['is_correct']].reset_index(drop=True)
low_conf_all = df[df['confidence'] < LOW_CONF_THRESH].reset_index(drop=True)

n_wrong    = len(wrong)
n_low_conf = len(low_conf_all)

print(f'전체: {total}장  |  오답: {n_wrong}건  |  low conf(<{LOW_CONF_THRESH}): {n_low_conf}건')

# ── 공통 유틸 ─────────────────────────────────────────────────────────────────
def load_img_safe(path_str):
    """PIL 이미지 로드, 실패 시 None 반환"""
    try:
        return PILImage.open(path_str).convert('RGB')
    except Exception:
        return None

def border_color(row, is_correct=False):
    """테두리 색상 결정"""
    if is_correct:
        svc_match = row.get('service_ok', True) or (row['service_true'] == row['service_pred'])
        return COLOR_CORRECT if svc_match else COLOR_CORRECT
    svc_match = (row['service_true'] == row['service_pred'])
    return COLOR_SVC_OK if svc_match else COLOR_SVC_WRONG

def make_contact_sheet(rows_df, title, save_path, ncols=5,
                       cell_w=3.8, cell_h=5.2, show_correct_col=False):
    """
    오답/low-conf contact sheet 생성.
    show_correct_col=True 이면 is_correct 컬럼을 참조해 정답/오답 구분.
    """
    n = len(rows_df)
    if n == 0:
        print(f'  [SKIP] 해당 이미지 없음 ({save_path})')
        return

    ncols = min(ncols, n)
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(nrows, ncols,
                              figsize=(ncols * cell_w, nrows * cell_h))
    axes_flat = np.array(axes).flatten()

    for idx, row in rows_df.iterrows():
        ax = axes_flat[idx]

        # 이미지 로드
        img = load_img_safe(row['image_path'])
        if img is not None:
            ax.imshow(img, aspect='auto')
        else:
            ax.set_facecolor('#1a1a1a')
            ax.text(0.5, 0.5, 'load error', ha='center', va='center',
                    transform=ax.transAxes, fontsize=8, color='#aaa')

        # 메타데이터
        fname    = Path(row['image_path']).name
        folder   = Path(row['image_path']).parent.name
        true_lbl = row['true_label']
        pred_lbl = row['pred_label']
        svc_t    = row['service_true']
        svc_p    = row['service_pred']
        conf     = row['confidence']
        is_ok    = bool(row.get('is_correct', True))
        svc_ok   = (svc_t == svc_p)

        # 색상 선택
        if show_correct_col:
            if is_ok:
                color = COLOR_LOW_CONF   # 정답이지만 conf 낮음
            else:
                color = COLOR_SVC_OK if svc_ok else COLOR_SVC_WRONG
        else:
            color = COLOR_SVC_OK if svc_ok else COLOR_SVC_WRONG

        # 타이틀 (세부 정보 6줄)
        svc_flag = '' if svc_ok else ' [SVC!]'
        title_txt = (
            f'{fname}  [{folder}]\n'
            f'True : {true_lbl}\n'
            f'Pred : {pred_lbl}{svc_flag}\n'
            f'SvcT : {svc_t}\n'
            f'SvcP : {svc_p}\n'
            f'Conf : {conf:.3f}'
        )
        ax.set_title(title_txt, fontsize=6.2, color=color, pad=3,
                     fontfamily='monospace', loc='left')

        # 테두리
        for spine in ax.spines.values():
            spine.set_edgecolor(color)
            spine.set_linewidth(2.5)
        ax.set_xticks([])
        ax.set_yticks([])

    # 빈 슬롯 숨기기
    for idx in range(n, len(axes_flat)):
        axes_flat[idx].set_visible(False)

    # 범례
    patches = [
        mpatches.Patch(color=COLOR_SVC_WRONG, label='Service wrong (severe)'),
        mpatches.Patch(color=COLOR_SVC_OK,    label='Fine-label wrong only'),
    ]
    if show_correct_col:
        patches.append(mpatches.Patch(color=COLOR_LOW_CONF, label='Correct but low conf'))

    fig.suptitle(title, fontsize=11, fontweight='bold', y=1.002)
    fig.legend(handles=patches, loc='lower center', ncol=len(patches),
               bbox_to_anchor=(0.5, -0.01), fontsize=8, framealpha=0.7)

    plt.tight_layout(pad=0.8)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  저장: {save_path}  ({n}장, {nrows}x{ncols})')


# ═══════════════════════════════════════════════════════════════════════════════
# 1. 전체 오답 contact sheet (35건)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n[1] 전체 오답 contact sheet')
wrong_indexed = wrong.reset_index(drop=True)
make_contact_sheet(
    wrong_indexed,
    f'Phase3 18-class — All Wrong Predictions  {n_wrong}/{total}  '
    f'(fine acc {(total-n_wrong)/total:.1%})\n'
    f'Red=service wrong  Orange=fine-label wrong only',
    OUT_ALL, ncols=5
)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. humidifier 관련 오답 contact sheet
#    (true=humidifier OR pred=humidifier)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n[2] humidifier 관련 오답 contact sheet')
humid_wrong = wrong[
    (wrong['true_label'] == 'humidifier') | (wrong['pred_label'] == 'humidifier')
].reset_index(drop=True)

print(f'  humidifier 관련 오답: {len(humid_wrong)}건')
print('  패턴:')
for _, r in humid_wrong.iterrows():
    arrow = '→'
    svc_flag = ''  if r['service_true'] == r['service_pred'] else '  [SVC!]'
    print(f'    {r["true_label"]:<22} {arrow} {r["pred_label"]:<22}  conf={r["confidence"]:.3f}{svc_flag}')

make_contact_sheet(
    humid_wrong,
    f'Phase3 — humidifier Wrong Predictions  ({len(humid_wrong)}건)\n'
    f'Red=service wrong  Orange=fine-label wrong only',
    OUT_HUMID, ncols=4
)

# ═══════════════════════════════════════════════════════════════════════════════
# 3. heater 관련 오답 contact sheet
#    (true=heater OR pred=heater)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n[3] heater 관련 오답 contact sheet')
heater_wrong = wrong[
    (wrong['true_label'] == 'heater') | (wrong['pred_label'] == 'heater')
].reset_index(drop=True)

print(f'  heater 관련 오답: {len(heater_wrong)}건')
print('  패턴:')
for _, r in heater_wrong.iterrows():
    svc_flag = '' if r['service_true'] == r['service_pred'] else '  [SVC!]'
    print(f'    {r["true_label"]:<22} → {r["pred_label"]:<22}  conf={r["confidence"]:.3f}{svc_flag}')

make_contact_sheet(
    heater_wrong,
    f'Phase3 — heater Wrong Predictions  ({len(heater_wrong)}건)\n'
    f'Red=service wrong  Orange=fine-label wrong only',
    OUT_HEATER, ncols=min(4, len(heater_wrong))
)

# ═══════════════════════════════════════════════════════════════════════════════
# 4. low confidence contact sheet (conf < 0.70, 정답+오답 포함)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n[4] low confidence contact sheet')
low_conf_indexed = low_conf_all.reset_index(drop=True)

n_lc_wrong   = int((~low_conf_all['is_correct']).sum())
n_lc_correct = int(low_conf_all['is_correct'].sum())
print(f'  low conf(<{LOW_CONF_THRESH}): {n_low_conf}건  '
      f'(오답 {n_lc_wrong}건 + 정답 {n_lc_correct}건)')
print('  목록 (confidence 오름차순):')
for _, r in low_conf_indexed.sort_values('confidence').iterrows():
    ok_str   = 'OK  ' if r['is_correct'] else 'WRONG'
    svc_str  = '' if r['service_true'] == r['service_pred'] else ' [SVC!]'
    print(f'    [{ok_str}] {r["true_label"]:<22} → {r["pred_label"]:<22}  '
          f'conf={r["confidence"]:.3f}{svc_str}')

make_contact_sheet(
    low_conf_indexed.sort_values('confidence').reset_index(drop=True),
    f'Phase3 — Low Confidence (<{LOW_CONF_THRESH}) Images  {n_low_conf}건\n'
    f'Green=correct-but-uncertain  Orange=fine wrong  Red=service wrong',
    OUT_LOWCONF, ncols=5, show_correct_col=True
)

# ═══════════════════════════════════════════════════════════════════════════════
# 5. 오답 분석 CSV 생성
# ═══════════════════════════════════════════════════════════════════════════════
print('\n[5] 오답 분석 CSV 생성')

analysis_df = pd.DataFrame({
    'image_path':       wrong['image_path'].values,
    'true_label':       wrong['true_label'].values,
    'pred_label':       wrong['pred_label'].values,
    'service_true_label': wrong['service_true'].values,
    'service_pred_label': wrong['service_pred'].values,
    'confidence':       wrong['confidence'].round(6).values,
    'service_correct':  wrong['service_ok'].values,
    'error_type':       '',   # 사람이 직접 채움
    'note':             '',
})
# 분석 우선순위를 위해 confidence 낮은 순으로 정렬 (불확실한 것 먼저)
analysis_df = analysis_df.sort_values('confidence').reset_index(drop=True)

analysis_df.to_csv(ANALYSIS_CSV, index=False, encoding='utf-8-sig')

print(f'  저장: {ANALYSIS_CSV}  ({len(analysis_df)}건)')
print(f'\n  error_type 후보:')
print(f'    label_error       — 이미지가 잘못된 클래스에 할당됨 (수집/검수 오류)')
print(f'    bad_input         — 이미지 품질 불량 또는 제품 식별 불가')
print(f'    ambiguous_product — 여러 클래스로 해석 가능한 제품')
print(f'    model_error       — 모델이 명확한 이미지를 틀림 (학습 부족)')
print(f'    out_of_scope      — 학습 분포 외 이미지 (실사용 후기, 부분 사진 등)')

# ═══════════════════════════════════════════════════════════════════════════════
# 6. 오답 패턴 심층 요약
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('6. humidifier 오답 패턴 요약')
print('=' * 60)

hum_all = df[df['true_label'] == 'humidifier']
hum_wrong_only = hum_all[~hum_all['is_correct']]

print(f'  전체 humidifier 테스트: {len(hum_all)}장')
print(f'  정답: {int(hum_all["is_correct"].sum())}장  |  오답: {len(hum_wrong_only)}장')
print(f'  accuracy: {hum_all["is_correct"].mean()*100:.1f}%')
print()
print(f'  오답 패턴:')
for _, r in hum_wrong_only.sort_values('confidence', ascending=False).iterrows():
    svc_flag = '' if r['service_true'] == r['service_pred'] else '  ★ 서비스 대분류 오답'
    print(f'    → {r["pred_label"]:<22}  conf={r["confidence"]:.3f}{svc_flag}')

print()
print(f'  핵심 관찰:')
hum_to_kettle = len(hum_wrong_only[hum_wrong_only['pred_label'] == 'electric_kettle'])
hum_to_dehum  = len(hum_wrong_only[hum_wrong_only['pred_label'] == 'dehumidifier'])
hum_svc_wrong = len(hum_wrong_only[hum_wrong_only['service_ok'] == False])
print(f'    - humidifier → electric_kettle: {hum_to_kettle}건  (가장 심각, 서비스 대분류 오답)')
print(f'    - humidifier → dehumidifier   : {hum_to_dehum}건  (서비스 대분류 정답)')
print(f'    - 서비스 대분류까지 오답        : {hum_svc_wrong}건 / {len(hum_wrong_only)}건')
print(f'    - 가설: 원형/실린더형 가습기가 전기포트와 형태 유사')
print(f'    - 가설: 학습 데이터 내 초음파 가습기 비율이 높아 형태 다양성 부족')

print()
print('=' * 60)
print('7. heater 오답 패턴 요약')
print('=' * 60)

heat_all = df[df['true_label'] == 'heater']
heat_wrong_only = heat_all[~heat_all['is_correct']]

print(f'  전체 heater 테스트: {len(heat_all)}장')
print(f'  정답: {int(heat_all["is_correct"].sum())}장  |  오답: {len(heat_wrong_only)}장')
print(f'  accuracy: {heat_all["is_correct"].mean()*100:.1f}%')
print()
print(f'  오답 패턴:')
for _, r in heat_wrong_only.sort_values('confidence', ascending=False).iterrows():
    svc_flag = '' if r['service_true'] == r['service_pred'] else '  ★ 서비스 대분류 오답'
    print(f'    → {r["pred_label"]:<22}  conf={r["confidence"]:.3f}{svc_flag}')

print()
heat_to_beam = len(heat_wrong_only[heat_wrong_only['pred_label'] == 'beam_projector'])
heat_to_fan  = len(heat_wrong_only[heat_wrong_only['pred_label'] == 'fan'])
heat_svc_wrong = len(heat_wrong_only[heat_wrong_only['service_ok'] == False])
print(f'  핵심 관찰:')
print(f'    - heater → beam_projector: {heat_to_beam}건  (서비스 대분류 오답)')
print(f'      - conf=0.460 (low conf, 불확실)  →  label_error 또는 ambiguous 가능성 높음')
print(f'      - conf=0.994 (high conf, 확신)   →  model_error 가능성 높음')
print(f'    - heater → fan            : {heat_to_fan}건   (서비스 대분류 정답, seasonal_appliance)')
print(f'    - 가설: 타워형/세로형 히터가 빔프로젝터 바디와 실루엣 유사')
print(f'    - 가설: 히터 학습 이미지 수 부족 (processed {len(os.listdir(os.path.join(config.PROCESSED_DIR,"heater")))}장)')

print()
print('=' * 60)
print('8. 다음 판단 기준')
print('=' * 60)
n_svc_wrong_total = int((~wrong['service_ok']).sum())
n_svc_ok_total    = n_wrong - n_svc_wrong_total

print(f'\n  [전체 오답 35건 구조]')
print(f'    서비스 대분류 오답   : {n_svc_wrong_total}건  '
      f'({n_svc_wrong_total/n_wrong*100:.0f}%)  — 실사용 영향 있음')
print(f'    세부 라벨만 오답     : {n_svc_ok_total}건  '
      f'({n_svc_ok_total/n_wrong*100:.0f}%)  — 서비스 노출에 무영향')
print()
print(f'  [판단 기준 제안]')
print(f'    Step 1. error_type 수동 분류')
print(f'            → {ANALYSIS_CSV}')
print(f'            → label_error / bad_input / out_of_scope 비율 확인')
print()
print(f'    Step 2. label_error + out_of_scope 합산 비율이 오답의 50% 초과')
print(f'            → 데이터 품질 문제이므로 재학습보다 데이터 정제 우선')
print()
print(f'    Step 3. model_error 가 5건 이상이고 acc < 85% 클래스가 2개 이상')
print(f'            → 해당 클래스 추가 수집 후 Phase 3 fine-tune')
print()
print(f'    Step 4. 현재 서비스 대분류 95.8% 허용 기준 확인')
print(f'            → washing_drying 100%  / kitchen 98.1%  / pc_peripheral 96.9%')
print(f'            → 서비스 기준으로는 이미 충분히 우수')
print()
print(f'    주요 관심 클래스:')
print(f'      humidifier 75.8%: contact sheet 검토 후 label_error 비율 먼저 파악')
print(f'      heater     84.2%: high conf 오답(0.994) 이미지 직접 확인 필요')
print(f'      washer_dryer ↔ wash_tower: 서비스 기준 100% → 추가 조치 불필요')

# ═══════════════════════════════════════════════════════════════════════════════
# 최종 요약
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('완료')
print('=' * 60)
print(f'  {OUT_ALL}')
print(f'  {OUT_HUMID}')
print(f'  {OUT_HEATER}')
print(f'  {OUT_LOWCONF}')
print(f'  {ANALYSIS_CSV}')
print(f'  완료 시각: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
