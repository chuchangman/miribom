#!/usr/bin/env python3
"""
phase3_error_analysis.csv 집계 및 재학습 필요 여부 판단
(service_correct=False 행만 포함, error_type 수동 분류 완료)
"""
import os
import sys
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

ANALYSIS_CSV = Path('data/metadata/phase3_error_analysis.csv')

# ── CSV 로드 (line 7 trailing comma 대응)
df = pd.read_csv(
    ANALYSIS_CSV,
    encoding='utf-8-sig',
    usecols=range(9),
    names=['image_path', 'true_label', 'pred_label',
           'service_true_label', 'service_pred_label',
           'confidence', 'service_correct', 'error_type', 'note'],
    header=0,
)

# ── 전체 테스트 결과 기준값
TOTAL_TEST  = 471
SVC_CORRECT = 451
SVC_WRONG   = 20

ET_ORDER = ['model_error', 'ambiguous_product', 'bad_input', 'label_error', 'out_of_scope']

# ═══════════════════════════════════════════════════════════════════════════════
# 1. 분석 대상 행 수
# ═══════════════════════════════════════════════════════════════════════════════
print('=' * 65)
print('1. 분석 대상 행 수')
print('=' * 65)
print(f'  CSV 행 수          : {len(df)}건  (service_correct=False 전체)')
print(f'  전체 테스트        : {TOTAL_TEST}장')
print(f'  서비스 대분류 정답 : {SVC_CORRECT}장  ({SVC_CORRECT/TOTAL_TEST:.1%})')
print(f'  서비스 대분류 오답 : {len(df)}건  ({len(df)/TOTAL_TEST:.1%})')

# ═══════════════════════════════════════════════════════════════════════════════
# 2. error_type 별 개수
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('2. error_type 별 개수')
print('=' * 65)
et_counts = df['error_type'].value_counts()
for et in ET_ORDER:
    n   = et_counts.get(et, 0)
    bar = '#' * n
    pct = n / len(df) * 100
    print(f'  {et:<20}: {n:2d}건 ({pct:4.1f}%)  {bar}')
print(f'  {"합계":<20}: {len(df):2d}건')

# ═══════════════════════════════════════════════════════════════════════════════
# 3. 서비스 대분류 오답 방향별 분포
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('3. 서비스 대분류 오답 방향별 분포  (건수 내림차순)')
print('=' * 65)
svc_dir = (
    df.groupby(['service_true_label', 'service_pred_label'])
    .size()
    .reset_index(name='total')
    .sort_values('total', ascending=False)
)
for _, row in svc_dir.iterrows():
    st, sp, tot = row['service_true_label'], row['service_pred_label'], row['total']
    sub    = df[(df['service_true_label'] == st) & (df['service_pred_label'] == sp)]
    et_d   = sub['error_type'].value_counts().to_dict()
    et_str = '  '.join(f'{k}:{v}' for k, v in et_d.items())
    print(f'  {st:<30} → {sp:<28} {tot:2d}건  [{et_str}]')

# ═══════════════════════════════════════════════════════════════════════════════
# 4. model_error 기준 병목 클래스
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('4. model_error 기준 병목 클래스  (전체 목록)')
print('=' * 65)
me = df[df['error_type'] == 'model_error'].copy()
print(f'  model_error 총 {len(me)}건:\n')
print(f'  {"true_label":<22} {"pred_label":<22} {"conf":>7}  서비스 방향')
print('  ' + '-' * 78)
for _, r in me.sort_values('confidence').iterrows():
    svc = f'{r["service_true_label"]} → {r["service_pred_label"]}'
    print(f'  {r["true_label"]:<22} {r["pred_label"]:<22} {r["confidence"]:>7.3f}  {svc}')

print()
print('  [true_label 기준 집계]')
me_true = me['true_label'].value_counts()
for cls, n in me_true.items():
    rows  = me[me['true_label'] == cls]
    detail = ', '.join(f'{r.pred_label}({r.confidence:.3f})' for _, r in rows.iterrows())
    print(f'    {cls:<22}: {n}건  [{detail}]')

print()
print('  [pred_label 기준 — 어느 클래스로 흡수되는지]')
me_pred = me['pred_label'].value_counts()
for cls, n in me_pred.items():
    srcs = me[me['pred_label'] == cls]['true_label'].tolist()
    print(f'    ← {cls:<22}: {n}건  (from: {srcs})')

# ═══════════════════════════════════════════════════════════════════════════════
# 5. humidifier 오답 분석
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('5. humidifier 오답 분석  (service_correct=False 한정)')
print('=' * 65)
hum = df[df['true_label'] == 'humidifier']
print(f'  humidifier 서비스 대분류 오답: {len(hum)}건')
print()
for et in ET_ORDER:
    sub = hum[hum['error_type'] == et]
    if len(sub) == 0:
        continue
    print(f'  [{et}] {len(sub)}건:')
    for _, r in sub.sort_values('confidence', ascending=False).iterrows():
        print(f'    → {r["pred_label"]:<22}  conf={r["confidence"]:.3f}'
              f'  svc_pred={r["service_pred_label"]}')
hum_me = len(hum[hum['error_type'] == 'model_error'])
print(f'\n  model_error: {hum_me}건  /  ambiguous: '
      f'{len(hum[hum["error_type"]=="ambiguous_product"])}건  /  '
      f'bad_input: {len(hum[hum["error_type"]=="bad_input"])}건')

# ═══════════════════════════════════════════════════════════════════════════════
# 6. beam_projector 관련 오답 분석
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('6. beam_projector 관련 오답 분석')
print('=' * 65)
bp_pred = df[df['pred_label'] == 'beam_projector']
bp_true = df[df['true_label'] == 'beam_projector']
bp_me   = bp_pred[bp_pred['error_type'] == 'model_error']

print(f'  pred=beam_projector (다른 클래스가 bp로 오인): {len(bp_pred)}건')
for _, r in bp_pred.sort_values('confidence').iterrows():
    print(f'    {r["true_label"]:<22} → beam_projector  '
          f'conf={r["confidence"]:.3f}  [{r["error_type"]}]')

print()
print(f'  pred=beam_projector 중 model_error: {len(bp_me)}건')
for _, r in bp_me.sort_values('confidence').iterrows():
    print(f'    {r["true_label"]:<22} → beam_projector  conf={r["confidence"]:.3f}')

print()
print(f'  true=beam_projector (bp가 틀린 경우): {len(bp_true)}건')
for _, r in bp_true.iterrows():
    print(f'    beam_projector → {r["pred_label"]:<22}  '
          f'conf={r["confidence"]:.3f}  [{r["error_type"]}]')

# ═══════════════════════════════════════════════════════════════════════════════
# 7. refrigerator로 잘못 예측된 model_error
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('7. refrigerator로 잘못 예측된 model_error')
print('=' * 65)
ref_me = df[(df['pred_label'] == 'refrigerator') & (df['error_type'] == 'model_error')]
print(f'  pred=refrigerator & model_error: {len(ref_me)}건')
for _, r in ref_me.iterrows():
    print(f'    {r["true_label"]:<22} → refrigerator  conf={r["confidence"]:.3f}')

# ═══════════════════════════════════════════════════════════════════════════════
# 8. 정제 후 서비스 accuracy 재계산
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('8. 정제 후 서비스 대분류 accuracy 재계산')
print('=' * 65)
print(f'  [원본]  서비스 acc = {SVC_CORRECT}/{TOTAL_TEST} = {SVC_CORRECT/TOTAL_TEST:.4f} ({SVC_CORRECT/TOTAL_TEST:.1%})')
print()

excl_a = ['bad_input', 'label_error', 'out_of_scope']
excl_b = ['bad_input', 'label_error', 'out_of_scope', 'ambiguous_product']

n_a = len(df[df['error_type'].isin(excl_a)])
n_b = len(df[df['error_type'].isin(excl_b)])

eff_t_a = TOTAL_TEST - n_a
eff_t_b = TOTAL_TEST - n_b

print(f'  [기준 A] bad_input + label_error + out_of_scope 제외  ({n_a}건 제거)')
print(f'    유효 테스트 : {TOTAL_TEST} - {n_a} = {eff_t_a}장')
print(f'    서비스 정답 : {SVC_CORRECT}장  (제외된 이미지는 이미 오답)')
print(f'    유효 acc    : {SVC_CORRECT/eff_t_a:.4f}  ({SVC_CORRECT/eff_t_a:.1%})')
print()
print(f'  [기준 B] + ambiguous_product 추가 제외  ({n_b}건 총 제거)')
print(f'    유효 테스트 : {TOTAL_TEST} - {n_b} = {eff_t_b}장')
print(f'    서비스 정답 : {SVC_CORRECT}장')
print(f'    유효 acc    : {SVC_CORRECT/eff_t_b:.4f}  ({SVC_CORRECT/eff_t_b:.1%})')
print(f'    (= 순수 model_error만 남긴 실질 오류율: {len(me)}/{TOTAL_TEST} = {len(me)/TOTAL_TEST:.2%})')

# ═══════════════════════════════════════════════════════════════════════════════
# 9. 추가 수집 우선순위
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('9. 추가 수집 우선순위  (model_error 클래스 중심)')
print('=' * 65)

me_src  = me['true_label'].value_counts().to_dict()   # 오답 발생 클래스
me_sink = me['pred_label'].value_counts().to_dict()   # 오답 흡수 클래스

checks = [
    ('humidifier',       '원통형/가열식 비율 보강 — electric_kettle 혼동 2건'),
    ('heater',           '고신뢰(0.994) model_error, 타워형 이미지 보강'),
    ('beam_projector',   '흡수 4건 — 기존 학습 데이터 검수 우선'),
    ('monitor',          'model_error 2건 (→micro, →bp)'),
    ('dehumidifier',     'model_error 1건 (→refrigerator)'),
    ('vacuum_cleaner',   'model_error 1건 (→refrigerator)'),
    ('microwave',        'model_error 1건 (→beam_projector)'),
    ('air_conditioner',  'model_error 1건 (→beam_projector)'),
]

print(f'  {"클래스":<22}  {"me_src":>7}  {"me_sink":>8}  {"processed":>10}  메모')
print('  ' + '-' * 80)
for cls, memo in checks:
    proc_path = os.path.join(config.PROCESSED_DIR, cls)
    proc_n    = len(os.listdir(proc_path)) if os.path.exists(proc_path) else 0
    n_src     = me_src.get(cls, 0)
    n_sink    = me_sink.get(cls, 0)
    flag      = ' ★' if n_src >= 2 or (cls == 'beam_projector' and n_sink >= 3) else ''
    print(f'  {cls:<22}  {n_src:>7}건  {n_sink:>8}건  {proc_n:>10}장  {memo}{flag}')

print()
print('  우선순위 결론:')
print('  1순위: beam_projector 학습 데이터 검수')
print('         (4건 흡수: heater/air_cond/microwave/monitor → 다른 제품 이미지 혼입 의심)')
print('  2순위: humidifier 추가 수집 (model_error 2건, 형태 다양성 부족)')
print('  3순위: heater 추가 수집 (processed 181장 최소, 고신뢰 오답)')
print('  4순위: monitor 학습 이미지 검수 (→micro, →bp 각 1건)')

# ═══════════════════════════════════════════════════════════════════════════════
# 10. 재학습 필요 여부 + 방법 판단
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('10. 재학습 필요 여부 및 방법 판단')
print('=' * 65)
print()
print(f'  [수치 요약]')
print(f'    서비스 대분류 오답 20건 중:')
print(f'      model_error       : {len(me)}건  ({len(me)/len(df)*100:.0f}%)')
print(f'      ambiguous_product : {et_counts.get("ambiguous_product",0)}건  ({et_counts.get("ambiguous_product",0)/len(df)*100:.0f}%)')
print(f'      bad_input         : {et_counts.get("bad_input",0)}건  ({et_counts.get("bad_input",0)/len(df)*100:.0f}%)')
print(f'    model_error 서비스 오류율: {len(me)}/{TOTAL_TEST} = {len(me)/TOTAL_TEST:.2%}')
print(f'    정제 서비스 acc (B): {SVC_CORRECT/eff_t_b:.1%}  (model_error 제외 시)')
print()
print(f'  [결론 1] 전체 18-class 처음부터 재학습 → 불필요')
print(f'    근거:')
print(f'    - Phase1 backbone 수렴 충분 (val_acc 94.4%)')
print(f'    - 9건 model_error = 1.9% → 절대치 낮음')
print(f'    - 원인이 특정 클래스 데이터 문제에 집중됨 (humidifier, heater, beam_projector)')
print(f'    - 전체 재학습 시 GPU 크래시 위험 + 시간 대비 효과 낮음')
print()
print(f'  [결론 2] 추가 수집 후 Phase 2 fine-tuning → 권장')
print(f'    근거:')
print(f'    - humidifier/heater/beam_projector 3개 클래스 보강으로 model_error 크게 감소 예상')
print(f'    - Phase 1 (backbone freeze, 15 epochs)은 현재 결과가 좋으므로 재사용')
print(f'    - Phase 2만 재시작 (features.6/7/classifier 학습)')
print(f'    - 단, data/split 재생성 필요 (새 이미지 추가 후)')
print()
print(f'  [결론 3] 재학습 전 beam_projector 데이터 검수 선행')
print(f'    근거:')
print(f'    - 4개 클래스가 beam_projector로 오인 → bp 학습 이미지 자체에 노이즈 가능성')
print(f'    - 보강보다 정제가 먼저 (data/split/train/beam_projector/ 직접 확인)')
print(f'    - 노이즈 제거 후 수집 시 오답 패턴 달라질 수 있음')
print()
print(f'  [현재 서비스 품질 판단]')
print(f'    서비스 대분류 95.8% — 정제 기준 98.0%')
print(f'    washing_drying 100% / kitchen 98.1% / pc_peripheral 96.9%')
print(f'    dehumidifier_humidifier 87.5% (humidifier 혼동 집중)')
print(f'    seasonal_appliance     94.8% (heater 오답 집중)')
print(f'    → 즉시 프로덕션 가능 여부는 서비스 정책 기준에 따라 결정')

# ═══════════════════════════════════════════════════════════════════════════════
# 11. 다음 작업 권고
# ═══════════════════════════════════════════════════════════════════════════════
print()
print('=' * 65)
print('11. 다음 작업 순서 (우선순위)')
print('=' * 65)
print()
print('  Step 1. beam_projector 학습 데이터 검수 [즉시]')
print('          data/split/train/beam_projector/ 내 이미지 육안 확인')
print('          → 다른 제품(heater/monitor/microwave 형태) 포함 여부 파악')
print()
print('  Step 2. humidifier 추가 수집 [1순위]')
print('          11_collect_universal.ipynb → CLASS_NAME="humidifier"')
print('          수집 목표: +50~100장 (원통형, 가열식, 소형 비율 강화)')
print('          검수 후 approved 이동')
print()
print('  Step 3. heater 추가 수집 [2순위]')
print('          현재 181장 → 목표 250장')
print('          타워형/세라믹히터/컨벡션 비율 강화')
print()
print('  Step 4. data/split 재생성 [수집 완료 후]')
print('          run_split.py 실행 (18-class 동일 구성)')
print()
print('  Step 5. Phase 2 fine-tune 재시작')
print('          resume_phase3.py — CKPT_INPUT을 phase1 best로 교체 후 실행')
print('          (또는 run_training_phase3.py 전체 재실행)')
print()
print('  ★ Step 1~3은 재학습과 무관하게 즉시 진행 가능')
