#!/usr/bin/env python3
"""
Phase 3 18-class — Phase 2 이어서 학습 (resume from GPU crash)

상황:
  phase3_18class_best.pth 에 phase2/epoch1/val_acc=90.0% 저장 후 크래시 발생.
  Phase 1 재학습 없이 Phase 2 (epoch 2~10) 만 이어서 진행.

체크포인트 전략:
  입력  : checkpoints/phase3_18class_best.pth          (epoch1, 크래시 저장본)
  best  : checkpoints/phase3_18class_resumed_best.pth  (val_loss 기준 best)
  last  : checkpoints/phase3_18class_resumed_last.pth  (매 epoch 갱신, 크래시 대비)

결과:
  data/metadata/test_predictions_phase3.csv
  data/metadata/phase3_cm_fine.png
  data/metadata/phase3_cm_service.png
  data/metadata/phase3_history_p2_resumed.png
"""

import os
import sys
import shutil

# Windows CP949 환경에서 한글/특수문자 출력 깨짐 방지
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import efficientnet_v2_s

# ── 경로 ─────────────────────────────────────────────────────────────────────
_CKPT_ORIGIN  = os.path.join(config.CHECKPOINTS_DIR, 'phase3_18class_best.pth')
CKPT_BEST     = os.path.join(config.CHECKPOINTS_DIR, 'phase3_18class_resumed_best.pth')
CKPT_LAST     = os.path.join(config.CHECKPOINTS_DIR, 'phase3_18class_resumed_last.pth')

# 크래시 복구: resumed_last.pth 가 이미 있으면 그 파일을 입력으로 사용
CKPT_INPUT = CKPT_LAST if os.path.exists(CKPT_LAST) else _CKPT_ORIGIN
CSV_PATH      = os.path.join(config.METADATA_DIR, 'test_predictions_phase3.csv')
HIST_PNG      = os.path.join(config.METADATA_DIR, 'phase3_history_p2_resumed.png')
CM_FINE_PATH  = os.path.join(config.METADATA_DIR, 'phase3_cm_fine.png')
CM_SVC_PATH   = os.path.join(config.METADATA_DIR, 'phase3_cm_service.png')

IMG_SIZE      = 224
BATCH_SIZE    = 32
NUM_EPOCHS_P2 = 10   # Phase 2 총 에폭 수 (epoch 1은 이미 완료)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Checkpoint 로드 및 검증
# ═══════════════════════════════════════════════════════════════════════════════
print('=' * 60)
print('1. Resume 시작 — 체크포인트 로드 및 검증')
print('=' * 60)

if not os.path.exists(CKPT_INPUT):
    raise FileNotFoundError(f'입력 체크포인트 없음: {CKPT_INPUT}')

ckpt = torch.load(CKPT_INPUT, map_location='cpu', weights_only=False)
ckpt_classes  = ckpt['classes']
ckpt_epoch    = ckpt['epoch']
ckpt_phase    = ckpt.get('phase', 'unknown')
ckpt_val_acc  = ckpt.get('val_acc', 0.0)
ckpt_val_loss = ckpt.get('val_loss', float('inf'))

print(f'  파일     : {CKPT_INPUT}')
print(f'  phase    : {ckpt_phase}')
print(f'  epoch    : {ckpt_epoch}')
print(f'  val_loss : {ckpt_val_loss:.4f}')
print(f'  val_acc  : {ckpt_val_acc:.4f}  ({ckpt_val_acc*100:.2f}%)')
print(f'  classes  : {len(ckpt_classes)}개')

# classes 일치 확인
if sorted(ckpt_classes) != sorted(config.PROJECT_LABELS):
    raise ValueError(
        f'체크포인트 classes와 config.PROJECT_LABELS 불일치!\n'
        f'  checkpoint : {sorted(ckpt_classes)}\n'
        f'  config     : {sorted(config.PROJECT_LABELS)}'
    )
print(f'  [OK] 18개 classes 일치 확인')

# optimizer_state_dict 여부 확인
has_optim = 'optimizer_state_dict' in ckpt
print(f'  optimizer_state_dict: {"있음" if has_optim else "없음 → 새 optimizer 사용"}')

classes     = ckpt_classes   # checkpoint 순서 그대로 사용 (= train 시 순서)
num_classes = len(classes)
start_epoch = ckpt_epoch + 1

print(f'\n  재개 epoch : {start_epoch} ~ {NUM_EPOCHS_P2}  '
      f'(남은 에폭 {max(0, NUM_EPOCHS_P2 - ckpt_epoch)}개)')

# ── Device ───────────────────────────────────────────────────────────────────
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'\n  PyTorch : {torch.__version__}')
print(f'  Device  : {device}')
if device.type == 'cuda':
    print(f'  GPU     : {torch.cuda.get_device_name(0)}')
    print(f'  VRAM    : {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')

# CKPT_BEST 초기화 — best.pth 가 없을 때만 입력 체크포인트로 초기화
# (재실행 시 이전 best 를 유지)
if not os.path.exists(CKPT_BEST):
    shutil.copy(CKPT_INPUT, CKPT_BEST)
    print(f'\n  CKPT_BEST 초기화: {os.path.basename(CKPT_INPUT)} → {os.path.basename(CKPT_BEST)}')
else:
    print(f'\n  CKPT_BEST 기존 유지: {os.path.basename(CKPT_BEST)}')

# ═══════════════════════════════════════════════════════════════════════════════
# 2. DataLoader
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('2. DataLoader 구성')
print('=' * 60)

train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE + 32, IMG_SIZE + 32)),
    transforms.RandomCrop(IMG_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])
val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

train_ds = datasets.ImageFolder(os.path.join(config.SPLIT_DIR, 'train'), transform=train_transform)
valid_ds = datasets.ImageFolder(os.path.join(config.SPLIT_DIR, 'valid'), transform=val_transform)
test_ds  = datasets.ImageFolder(os.path.join(config.SPLIT_DIR, 'test'),  transform=val_transform)

# DataLoader 클래스 순서가 checkpoint와 일치하는지 확인 (필수)
if train_ds.classes != classes:
    raise ValueError(
        f'DataLoader 클래스 순서가 체크포인트와 불일치!\n'
        f'  checkpoint : {classes}\n'
        f'  dataloader : {train_ds.classes}\n'
        f'이 경우 모델 출력 인덱스와 라벨이 뒤바뀝니다. split 재생성 필요.'
    )
if test_ds.classes != classes:
    raise ValueError(f'test_ds 클래스 순서 불일치: {test_ds.classes}')
print(f'  [OK] 클래스 순서 일치 확인')

print(f'  train : {len(train_ds):,}장  ({len(train_ds.classes)}클래스)')
print(f'  valid : {len(valid_ds):,}장')
print(f'  test  : {len(test_ds):,}장')

# WeightedRandomSampler — 클래스 불균형 보정
train_counts      = [len(os.listdir(os.path.join(config.SPLIT_DIR, 'train', c))) for c in train_ds.classes]
weights_per_class = [1.0 / max(c, 1) for c in train_counts]
sample_weights    = [weights_per_class[label] for _, label in train_ds.imgs]
sampler = torch.utils.data.WeightedRandomSampler(
    sample_weights, num_samples=len(sample_weights), replacement=True
)

pin = device.type == 'cuda'
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler,  num_workers=0, pin_memory=pin)
valid_loader = DataLoader(valid_ds, batch_size=BATCH_SIZE, shuffle=False,    num_workers=0, pin_memory=pin)
test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False,    num_workers=0, pin_memory=pin)

# ═══════════════════════════════════════════════════════════════════════════════
# 3. 모델 생성 및 가중치 로드
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('3. 모델 생성 및 가중치 로드')
print('=' * 60)

model = efficientnet_v2_s(weights=None)
in_features = model.classifier[1].in_features
model.classifier[1] = nn.Linear(in_features, num_classes)
model.load_state_dict(ckpt['model_state_dict'])
print(f'  [OK] EfficientNetV2-S ({num_classes}-class) 가중치 로드 완료')

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Phase 2 trainable layer 설정
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('4. Phase 2 trainable layer 설정')
print('=' * 60)

for param in model.parameters():
    param.requires_grad = False

target_layers = ['features.6', 'features.7', 'classifier']
for name, param in model.named_parameters():
    if any(k in name for k in target_layers):
        param.requires_grad = True

model = model.to(device)

total_p     = sum(p.numel() for p in model.parameters())
trainable_p = sum(p.numel() for p in model.parameters() if p.requires_grad)
frozen_p    = total_p - trainable_p

print(f'  Unfrozen layers : {", ".join(target_layers)}')
print(f'  Trainable params: {trainable_p:,} / {total_p:,}  ({100*trainable_p/total_p:.2f}%)')
print(f'  Frozen params   : {frozen_p:,}')

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Optimizer 및 Criterion
# ═══════════════════════════════════════════════════════════════════════════════
criterion  = nn.CrossEntropyLoss()
optimizer  = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4
)
scheduler  = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=3
)

if has_optim:
    try:
        optimizer.load_state_dict(ckpt['optimizer_state_dict'])
        print(f'\n  [OK] optimizer_state_dict 로드')
    except Exception as e:
        print(f'\n  [WARNING] optimizer 로드 실패 ({e}), 새 optimizer (lr=1e-4) 사용')
else:
    print(f'\n  새 optimizer: Adam  lr=1e-4')

# ── 학습 함수 ─────────────────────────────────────────────────────────────────
def train_one_epoch(model, loader, optimizer):
    model.train()
    total_loss = correct = total = 0
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * inputs.size(0)
        correct    += (outputs.argmax(1) == labels).sum().item()
        total      += labels.size(0)
    return total_loss / total, correct / total

def evaluate(model, loader):
    model.eval()
    total_loss = correct = total = 0
    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss    = criterion(outputs, labels)
            total_loss += loss.item() * inputs.size(0)
            correct    += (outputs.argmax(1) == labels).sum().item()
            total      += labels.size(0)
    return total_loss / total, correct / total

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Phase 2 이어서 학습 (epoch 2 ~ 10)
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print(f'5. Phase 2 이어서 학습 — epoch {start_epoch} ~ {NUM_EPOCHS_P2}')
print('=' * 60)

history     = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

# best_val_loss 초기화: resumed_best.pth 가 있으면 그 val_loss 기준
# (재실행 시 이전 best 에폭을 유지하기 위해)
if os.path.exists(CKPT_BEST):
    _binfo = torch.load(CKPT_BEST, map_location='cpu', weights_only=False)
    best_val_loss = _binfo.get('val_loss', ckpt_val_loss)
    print(f'  best_val_loss 초기화: {best_val_loss:.4f} (CKPT_BEST epoch {_binfo.get("epoch")})')
else:
    best_val_loss = ckpt_val_loss

if start_epoch <= NUM_EPOCHS_P2:
    for epoch in range(start_epoch, NUM_EPOCHS_P2 + 1):
        t0 = datetime.now()
        tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer)
        vl_loss, vl_acc = evaluate(model, valid_loader)
        scheduler.step(vl_loss)
        elapsed = (datetime.now() - t0).total_seconds()

        history['train_loss'].append(tr_loss)
        history['train_acc'].append(tr_acc)
        history['val_loss'].append(vl_loss)
        history['val_acc'].append(vl_acc)

        is_best = vl_loss < best_val_loss
        marker  = '  ★ BEST' if is_best else ''

        print(f'  Ep {epoch:2d}/{NUM_EPOCHS_P2} | '
              f'tr_loss={tr_loss:.4f} tr_acc={tr_acc:.4f} | '
              f'vl_loss={vl_loss:.4f} vl_acc={vl_acc:.4f} | '
              f'{elapsed:.0f}s{marker}')

        # ── last checkpoint: 매 epoch 갱신 (optimizer_state_dict 포함 → 재개 가능)
        torch.save({
            'epoch':               epoch,
            'phase':               'phase2_resumed',
            'model_state_dict':    model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_loss':            vl_loss,
            'val_acc':             vl_acc,
            'classes':             classes,
            'history':             history,
        }, CKPT_LAST)

        # ── best checkpoint: val_loss 개선 시 저장
        if is_best:
            best_val_loss = vl_loss
            torch.save({
                'epoch':            epoch,
                'phase':            'phase2_resumed',
                'model_state_dict': model.state_dict(),
                'val_loss':         vl_loss,
                'val_acc':          vl_acc,
                'classes':          classes,
            }, CKPT_BEST)
            print(f'         → {CKPT_BEST} 갱신')

    # History plot (재개 구간만)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    resumed_epochs = list(range(start_epoch, NUM_EPOCHS_P2 + 1))
    ax1.plot(resumed_epochs, history['train_loss'], 'b-o', label='train', markersize=4)
    ax1.plot(resumed_epochs, history['val_loss'],   'r-o', label='valid',  markersize=4)
    ax1.set_title('Phase2 Resumed — Loss')
    ax1.set_xlabel('Epoch')
    ax1.legend(); ax1.grid(True)
    ax2.plot(resumed_epochs, history['train_acc'], 'b-o', label='train', markersize=4)
    ax2.plot(resumed_epochs, history['val_acc'],   'r-o', label='valid',  markersize=4)
    ax2.set_title('Phase2 Resumed — Accuracy')
    ax2.set_xlabel('Epoch')
    ax2.legend(); ax2.grid(True)
    plt.suptitle(f'Phase2 Resume  (ep {start_epoch}~{NUM_EPOCHS_P2})', fontsize=11)
    plt.tight_layout()
    plt.savefig(HIST_PNG, dpi=120)
    plt.close()
    print(f'\n  History plot: {HIST_PNG}')

    # best checkpoint 최종 확인
    best_info = torch.load(CKPT_BEST, map_location='cpu', weights_only=False)
    print(f'\n  ▶ Phase2 resumed best:')
    print(f'    epoch    : {best_info["epoch"]}')
    print(f'    val_loss : {best_info["val_loss"]:.4f}')
    print(f'    val_acc  : {best_info["val_acc"]:.4f}  ({best_info["val_acc"]*100:.2f}%)')
    print(f'    파일     : {CKPT_BEST}')
    print(f'    last 저장: {CKPT_LAST}')
else:
    print('  학습 건너뜀 (Phase 2 이미 완료)')

# ═══════════════════════════════════════════════════════════════════════════════
# 7. Test 평가
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('6. Test 평가')
print('=' * 60)

eval_ckpt = torch.load(CKPT_BEST, map_location=device, weights_only=False)
model.load_state_dict(eval_ckpt['model_state_dict'])
model.eval()

print(f'  평가 checkpoint : {CKPT_BEST}')
print(f'  epoch={eval_ckpt["epoch"]}  val_acc={eval_ckpt["val_acc"]:.4f}')
print(f'  test set        : {len(test_ds)}장')

all_preds   = []
all_targets = []
all_confs   = []
all_paths   = []
img_idx     = 0

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs = inputs.to(device)
        probs  = torch.softmax(model(inputs), dim=1)
        confs, preds = probs.max(dim=1)
        for i in range(inputs.size(0)):
            all_preds.append(preds[i].item())
            all_targets.append(labels[i].item())
            all_confs.append(confs[i].item())
            all_paths.append(test_ds.imgs[img_idx][0])
            img_idx += 1

result_df = pd.DataFrame({
    'image_path': all_paths,
    'true_label': [classes[t] for t in all_targets],
    'pred_label': [classes[p] for p in all_preds],
    'confidence': [round(c, 6) for c in all_confs],
    'is_correct': [t == p for t, p in zip(all_targets, all_preds)],
})
result_df['service_true'] = result_df['true_label'].map(config.SERVICE_LABEL_MAP)
result_df['service_pred'] = result_df['pred_label'].map(config.SERVICE_LABEL_MAP)
result_df['service_ok']   = result_df['service_true'] == result_df['service_pred']

os.makedirs(config.METADATA_DIR, exist_ok=True)
result_df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')
print(f'\n  CSV 저장: {CSV_PATH}')

# ═══════════════════════════════════════════════════════════════════════════════
# 8. 결과 출력
# ═══════════════════════════════════════════════════════════════════════════════
n_total  = len(result_df)
fine_acc = result_df['is_correct'].mean()
svc_acc  = result_df['service_ok'].mean()
n_cor    = int(result_df['is_correct'].sum())

print('\n' + '=' * 60)
print('7. 세부 라벨 Test Accuracy')
print('=' * 60)
print(f'  세부 라벨 (18-class) : {fine_acc:.4f}  ({fine_acc*100:.1f}%)  [{n_cor}/{n_total}]')

print('\n' + '=' * 60)
print('8. 서비스 대분류 Test Accuracy')
print('=' * 60)
n_svc_cor = int(result_df['service_ok'].sum())
print(f'  서비스 대분류        : {svc_acc:.4f}  ({svc_acc*100:.1f}%)  [{n_svc_cor}/{n_total}]')

print('\n' + '=' * 60)
print('9. 클래스별 Accuracy')
print('=' * 60)
print(f'  {"클래스":<22} {"정답":>5} {"전체":>5} {"acc":>7}  {"서비스 카테고리":<28}')
print('  ' + '-' * 72)

class_accs = {}
for cls in sorted(classes):
    sub   = result_df[result_df['true_label'] == cls]
    if len(sub) == 0:
        continue
    n_ok  = int(sub['is_correct'].sum())
    n_tot = len(sub)
    acc   = n_ok / n_tot
    svc   = config.SERVICE_LABEL_MAP.get(cls, '?')
    class_accs[cls] = acc
    flag  = '    ' if acc >= 0.80 else (' ⚠  ' if acc >= 0.60 else ' ❌  ')
    print(f'  {cls:<22} {n_ok:>5} {n_tot:>5} {acc*100:>6.1f}%{flag}  {svc:<28}')

print('  ' + '-' * 72)
print(f'  {"전체 평균":<22} {n_cor:>5} {n_total:>5} {fine_acc*100:>6.1f}%')

print('\n' + '=' * 60)
print('   서비스 대분류별 Accuracy')
print('=' * 60)
print(f'  {"서비스 카테고리":<30} {"정답":>5} {"전체":>5} {"acc":>7}')
print('  ' + '-' * 52)
for svc in sorted(result_df['service_true'].unique()):
    sub   = result_df[result_df['service_true'] == svc]
    n_ok  = int(sub['service_ok'].sum())
    n_t   = len(sub)
    acc   = n_ok / n_t
    flag  = '    ' if acc >= 0.80 else (' ⚠  ' if acc >= 0.60 else ' ❌  ')
    print(f'  {svc:<30} {n_ok:>5} {n_t:>5} {acc*100:>6.1f}%{flag}')

# ── 오답 분석 ──────────────────────────────────────────────────────────────────
print('\n' + '=' * 60)
print('10. 오답 분석')
print('=' * 60)
wrong_df = result_df[~result_df['is_correct']].copy()
print(f'  오답 총 {len(wrong_df)}건 / {n_total}건  '
      f'(세부 오류율 {len(wrong_df)/n_total*100:.1f}%)')

if len(wrong_df) > 0:
    print(f'\n  [오답 패턴 Top 15]  (true → pred)')
    patterns = (
        wrong_df
        .groupby(['true_label', 'pred_label'])
        .size()
        .reset_index(name='count')
        .sort_values('count', ascending=False)
    )
    for _, row in patterns.head(15).iterrows():
        svc_t = config.SERVICE_LABEL_MAP.get(row['true_label'], '?')
        svc_p = config.SERVICE_LABEL_MAP.get(row['pred_label'], '?')
        cross = '' if svc_t == svc_p else '  ← 서비스 대분류 오답'
        print(f'    {row["true_label"]:<22} → {row["pred_label"]:<22}  {row["count"]}건{cross}')

# ── low confidence 분석 ───────────────────────────────────────────────────────
print('\n' + '=' * 60)
print('11. Low Confidence 분석')
print('=' * 60)
low_conf = result_df[result_df['confidence'] < 0.70]
print(f'  confidence < 0.70: {len(low_conf)}건 / {n_total}장')
if len(low_conf) > 0:
    lc_cls = low_conf['true_label'].value_counts()
    print(f'\n  {"클래스":<22} {"건수":>5}  {"오답포함":>8}')
    print('  ' + '-' * 42)
    for cls, cnt in lc_cls.items():
        sub_lc  = low_conf[low_conf['true_label'] == cls]
        n_wrong_lc = int((~sub_lc['is_correct']).sum())
        print(f'  {cls:<22} {cnt:>5}  ({n_wrong_lc}건 오답)')

# ── Confusion Matrix ──────────────────────────────────────────────────────────
n         = num_classes
cm        = [[0] * n for _ in range(n)]
cls_to_idx = {c: i for i, c in enumerate(classes)}
for _, row in result_df.iterrows():
    cm[cls_to_idx[row['true_label']]][cls_to_idx[row['pred_label']]] += 1

short = [c[:8] for c in classes]
fig, ax = plt.subplots(figsize=(16, 14))
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.colorbar(im)
ax.set(xticks=range(n), yticks=range(n),
       xticklabels=short, yticklabels=short,
       ylabel='True', xlabel='Pred',
       title=f'Phase3 18-class Confusion Matrix  (Test {n_total}장  acc={fine_acc*100:.1f}%)')
ax.tick_params(axis='x', rotation=45)
max_v = max(max(r) for r in cm)
for i in range(n):
    for j in range(n):
        col = 'white' if cm[i][j] > max_v / 2 else 'black'
        ax.text(j, i, cm[i][j], ha='center', va='center', color=col, fontsize=8)
plt.tight_layout()
plt.savefig(CM_FINE_PATH, dpi=120, bbox_inches='tight')
plt.close()
print(f'\n  CM (fine-level)   : {CM_FINE_PATH}')

# Service-level CM
svc_classes  = sorted(result_df['service_true'].unique())
ns           = len(svc_classes)
svc_idx_map  = {c: i for i, c in enumerate(svc_classes)}
cm_svc       = [[0] * ns for _ in range(ns)]
for _, row in result_df.iterrows():
    cm_svc[svc_idx_map[row['service_true']]][svc_idx_map[row['service_pred']]] += 1

svc_short = [c[:14] for c in svc_classes]
fig, ax   = plt.subplots(figsize=(12, 10))
im = ax.imshow(cm_svc, interpolation='nearest', cmap=plt.cm.Blues)
plt.colorbar(im)
ax.set(xticks=range(ns), yticks=range(ns),
       xticklabels=svc_short, yticklabels=svc_short,
       ylabel='True', xlabel='Pred',
       title=f'Phase3 Service-level Confusion Matrix  (acc={svc_acc*100:.1f}%)')
ax.tick_params(axis='x', rotation=30)
max_vs = max(max(r) for r in cm_svc)
for i in range(ns):
    for j in range(ns):
        col = 'white' if cm_svc[i][j] > max_vs / 2 else 'black'
        ax.text(j, i, cm_svc[i][j], ha='center', va='center', color=col, fontsize=10)
plt.tight_layout()
plt.savefig(CM_SVC_PATH, dpi=120, bbox_inches='tight')
plt.close()
print(f'  CM (service-level): {CM_SVC_PATH}')

# ═══════════════════════════════════════════════════════════════════════════════
# 12. 추가 학습 필요 여부 판단
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 60)
print('12. 추가 학습 필요 여부 판단  (기준: 클래스별 acc < 85%)')
print('=' * 60)
need_boost = [(cls, acc) for cls, acc in class_accs.items() if acc < 0.85]
need_boost.sort(key=lambda x: x[1])

if not need_boost:
    print('  모든 클래스 85% 이상 — 추가 학습 불필요')
else:
    print(f'  {"클래스":<22} {"acc":>7}  {"processed":>10}장  {"판단"}')
    print('  ' + '-' * 56)
    for cls, acc in need_boost:
        proc_path = os.path.join(config.PROCESSED_DIR, cls)
        proc_cnt  = len(os.listdir(proc_path)) if os.path.exists(proc_path) else 0
        priority  = '긴급 (데이터 보강 + 재학습)' if acc < 0.70 else (
                    '권장 (데이터 보강 검토)'    if acc < 0.80 else
                    '선택 (Phase 3 fine-tune)')
        print(f'  {cls:<22} {acc*100:>6.1f}%  {proc_cnt:>10}장  {priority}')

# ── 최종 요약 ──────────────────────────────────────────────────────────────────
print('\n' + '=' * 60)
print('완료')
print('=' * 60)
print(f'  완료 시각         : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'  세부 라벨 acc     : {fine_acc*100:.2f}%  ({n_cor}/{n_total})')
print(f'  서비스 대분류 acc : {svc_acc*100:.2f}%  ({n_svc_cor}/{n_total})')
print(f'  CKPT best         : {CKPT_BEST}')
print(f'  CKPT last         : {CKPT_LAST}')
print(f'  결과 CSV          : {CSV_PATH}')
print(f'  CM (fine)         : {CM_FINE_PATH}')
print(f'  CM (service)      : {CM_SVC_PATH}')
print(f'  History plot      : {HIST_PNG}')
