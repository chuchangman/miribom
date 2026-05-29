#!/usr/bin/env python3
"""
Phase 3 18-class — Refined Fine-tuning
입력  : checkpoints/phase3_18class_resumed_best.pth  (epoch7, val_acc=94.36%)
출력  : checkpoints/phase3_18class_refined_{best,last}.pth
데이터: 새 split (beam_projector -15, heater +77, humidifier +13 반영)
학습  : Phase 2 방식 (features.6/7 + classifier unfreeze, Adam lr=1e-4)
       크래시 복구 지원 (refined_last.pth 존재 시 자동 재개)

결과 파일:
  data/metadata/test_predictions_phase3_refined.csv
  data/metadata/phase3_refined_cm_fine.png
  data/metadata/phase3_refined_cm_service.png
  data/metadata/phase3_refined_history.png
"""

import os
import sys

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

# ── 경로 ──────────────────────────────────────────────────────────────────────
_CKPT_ORIGIN   = os.path.join(config.CHECKPOINTS_DIR, 'phase3_18class_resumed_best.pth')
CKPT_REFINED_BEST = os.path.join(config.CHECKPOINTS_DIR, 'phase3_18class_refined_best.pth')
CKPT_REFINED_LAST = os.path.join(config.CHECKPOINTS_DIR, 'phase3_18class_refined_last.pth')
BASELINE_CSV   = os.path.join(config.METADATA_DIR, 'test_predictions_phase3.csv')
CSV_PATH       = os.path.join(config.METADATA_DIR, 'test_predictions_phase3_refined.csv')
HIST_PNG       = os.path.join(config.METADATA_DIR, 'phase3_refined_history.png')
CM_FINE_PATH   = os.path.join(config.METADATA_DIR, 'phase3_refined_cm_fine.png')
CM_SVC_PATH    = os.path.join(config.METADATA_DIR, 'phase3_refined_cm_service.png')

IMG_SIZE      = 224
BATCH_SIZE    = 32
NUM_EPOCHS    = 10

# 크래시 복구: refined_last 가 있으면 그 파일에서 재개, 없으면 원점에서 시작
is_crash_recovery = os.path.exists(CKPT_REFINED_LAST)
CKPT_INPUT = CKPT_REFINED_LAST if is_crash_recovery else _CKPT_ORIGIN

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Checkpoint 로드 및 검증
# ═══════════════════════════════════════════════════════════════════════════════
print('=' * 65)
print('1. Checkpoint 로드')
print('=' * 65)

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
print(f'  모드     : {"크래시 복구" if is_crash_recovery else "새 fine-tuning"}')

if sorted(ckpt_classes) != sorted(config.PROJECT_LABELS):
    raise ValueError(
        f'체크포인트 classes != config.PROJECT_LABELS\n'
        f'  checkpoint : {sorted(ckpt_classes)}\n'
        f'  config     : {sorted(config.PROJECT_LABELS)}'
    )
print(f'  [OK] 18개 classes 일치')

has_optim   = 'optimizer_state_dict' in ckpt
classes     = ckpt_classes
num_classes = len(classes)

# start_epoch 결정
# - 크래시 복구: last 체크포인트 다음 에폭부터
# - 새 실행: 1부터
start_epoch = (ckpt_epoch + 1) if is_crash_recovery else 1
print(f'  start_epoch : {start_epoch}  (NUM_EPOCHS={NUM_EPOCHS})')

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'\n  PyTorch : {torch.__version__}')
print(f'  Device  : {device}')
if device.type == 'cuda':
    print(f'  GPU     : {torch.cuda.get_device_name(0)}')
    print(f'  VRAM    : {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')

# ═══════════════════════════════════════════════════════════════════════════════
# 2. DataLoader
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('2. DataLoader 구성')
print('=' * 65)

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

if train_ds.classes != classes:
    raise ValueError(
        f'DataLoader 클래스 순서 != checkpoint classes!\n'
        f'  checkpoint : {classes}\n'
        f'  dataloader : {train_ds.classes}'
    )
if test_ds.classes != classes:
    raise ValueError(f'test_ds 클래스 순서 불일치')
print(f'  [OK] 클래스 순서 일치 ({len(classes)}개)')

print(f'  train : {len(train_ds):,}장  ({len(train_ds.classes)}클래스)')
print(f'  valid : {len(valid_ds):,}장')
print(f'  test  : {len(test_ds):,}장')
print(f'\n  클래스별 train 수:')
train_counts = [len(os.listdir(os.path.join(config.SPLIT_DIR, 'train', c))) for c in train_ds.classes]
for cls, cnt in zip(train_ds.classes, train_counts):
    print(f'    {cls:<22}: {cnt}')

weights_per_class = [1.0 / max(c, 1) for c in train_counts]
sample_weights    = [weights_per_class[label] for _, label in train_ds.imgs]
sampler = torch.utils.data.WeightedRandomSampler(
    sample_weights, num_samples=len(sample_weights), replacement=True
)

pin = device.type == 'cuda'
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler,
                          num_workers=0, pin_memory=pin)
valid_loader = DataLoader(valid_ds, batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=0, pin_memory=pin)
test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=0, pin_memory=pin)

# ═══════════════════════════════════════════════════════════════════════════════
# 3. 모델 로드 및 Phase 2 layer 설정
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('3. 모델 로드 및 Phase 2 layer 설정')
print('=' * 65)

model = efficientnet_v2_s(weights=None)
in_features = model.classifier[1].in_features
model.classifier[1] = nn.Linear(in_features, num_classes)
model.load_state_dict(ckpt['model_state_dict'])
print(f'  [OK] EfficientNetV2-S ({num_classes}-class) 가중치 로드')

for param in model.parameters():
    param.requires_grad = False

target_layers = ['features.6', 'features.7', 'classifier']
for name, param in model.named_parameters():
    if any(k in name for k in target_layers):
        param.requires_grad = True

model = model.to(device)

total_p     = sum(p.numel() for p in model.parameters())
trainable_p = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f'  Unfrozen: {", ".join(target_layers)}')
print(f'  Trainable: {trainable_p:,} / {total_p:,}  ({100*trainable_p/total_p:.2f}%)')

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Optimizer
# ═══════════════════════════════════════════════════════════════════════════════
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4
)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='min', factor=0.5, patience=3
)

# 크래시 복구 시 optimizer 상태 복원
if is_crash_recovery and has_optim:
    try:
        optimizer.load_state_dict(ckpt['optimizer_state_dict'])
        print(f'\n  [OK] optimizer_state_dict 복원 (크래시 복구)')
    except Exception as e:
        print(f'\n  [WARN] optimizer 복원 실패 ({e}), lr=1e-4 새 optimizer')
else:
    print(f'\n  새 optimizer: Adam  lr=1e-4  (refined 시작)')


def train_one_epoch(model, loader, optimizer):
    model.train()
    total_loss = correct = total = 0
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
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
            loss = criterion(outputs, labels)
            total_loss += loss.item() * inputs.size(0)
            correct    += (outputs.argmax(1) == labels).sum().item()
            total      += labels.size(0)
    return total_loss / total, correct / total

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Fine-tuning
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print(f'4. Refined Fine-tuning  (ep {start_epoch} ~ {NUM_EPOCHS})')
print('=' * 65)

history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

# best_val_loss 초기화
if os.path.exists(CKPT_REFINED_BEST) and is_crash_recovery:
    _b = torch.load(CKPT_REFINED_BEST, map_location='cpu', weights_only=False)
    best_val_loss = _b.get('val_loss', float('inf'))
    print(f'  best_val_loss 초기화: {best_val_loss:.4f} (refined_best ep{_b.get("epoch")})')
else:
    best_val_loss = float('inf')
    print(f'  best_val_loss 초기화: inf (새 fine-tuning)')

if start_epoch <= NUM_EPOCHS:
    for epoch in range(start_epoch, NUM_EPOCHS + 1):
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
        marker  = '  BEST' if is_best else ''
        lr_now  = optimizer.param_groups[0]['lr']

        print(f'  Ep {epoch:2d}/{NUM_EPOCHS} | '
              f'tr_loss={tr_loss:.4f} tr_acc={tr_acc:.4f} | '
              f'vl_loss={vl_loss:.4f} vl_acc={vl_acc:.4f} | '
              f'lr={lr_now:.2e} | {elapsed:.0f}s{marker}')

        # last checkpoint (매 epoch, 크래시 복구용)
        torch.save({
            'epoch':                epoch,
            'phase':                'phase2_refined',
            'model_state_dict':     model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'val_loss':             vl_loss,
            'val_acc':              vl_acc,
            'classes':              classes,
            'history':              history,
        }, CKPT_REFINED_LAST)

        # best checkpoint
        if is_best:
            best_val_loss = vl_loss
            torch.save({
                'epoch':            epoch,
                'phase':            'phase2_refined',
                'model_state_dict': model.state_dict(),
                'val_loss':         vl_loss,
                'val_acc':          vl_acc,
                'classes':          classes,
            }, CKPT_REFINED_BEST)
            print(f'         -> {os.path.basename(CKPT_REFINED_BEST)} 갱신')

    # History plot
    ep_range = list(range(start_epoch, NUM_EPOCHS + 1))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4))
    ax1.plot(ep_range, history['train_loss'], 'b-o', label='train', markersize=4)
    ax1.plot(ep_range, history['val_loss'],   'r-o', label='valid',  markersize=4)
    ax1.set_title('Refined Fine-tuning — Loss')
    ax1.set_xlabel('Epoch'); ax1.legend(); ax1.grid(True)
    ax2.plot(ep_range, history['train_acc'], 'b-o', label='train', markersize=4)
    ax2.plot(ep_range, history['val_acc'],   'r-o', label='valid',  markersize=4)
    ax2.set_title('Refined Fine-tuning — Accuracy')
    ax2.set_xlabel('Epoch'); ax2.legend(); ax2.grid(True)
    plt.suptitle(f'Refined Fine-tuning (beam_projector -15 / heater +77 / humidifier +13)', fontsize=10)
    plt.tight_layout()
    plt.savefig(HIST_PNG, dpi=120)
    plt.close()
    print(f'\n  History plot: {HIST_PNG}')

    best_info = torch.load(CKPT_REFINED_BEST, map_location='cpu', weights_only=False)
    print(f'\n  Refined best:')
    print(f'    epoch    : {best_info["epoch"]}')
    print(f'    val_loss : {best_info["val_loss"]:.4f}')
    print(f'    val_acc  : {best_info["val_acc"]:.4f}  ({best_info["val_acc"]*100:.2f}%)')
else:
    print('  학습 건너뜀 (이미 완료)')

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Test 평가
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('5. Test 평가')
print('=' * 65)

eval_ckpt = torch.load(CKPT_REFINED_BEST, map_location=device, weights_only=False)
model.load_state_dict(eval_ckpt['model_state_dict'])
model.eval()

print(f'  평가 checkpoint: {os.path.basename(CKPT_REFINED_BEST)}')
print(f'  epoch={eval_ckpt["epoch"]}  val_acc={eval_ckpt["val_acc"]:.4f}')
print(f'  test set: {len(test_ds)}장')

all_preds = []; all_targets = []; all_confs = []; all_paths = []
img_idx = 0

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

# ── 수치 계산 ───────────────────────────────────────────────────────────────────
n_total  = len(result_df)
fine_acc = result_df['is_correct'].mean()
svc_acc  = result_df['service_ok'].mean()
n_cor    = int(result_df['is_correct'].sum())
n_svc    = int(result_df['service_ok'].sum())

# ═══════════════════════════════════════════════════════════════════════════════
# 7. 세부 라벨 결과
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('6. 세부 라벨 Test Accuracy')
print('=' * 65)
print(f'  18-class acc: {fine_acc:.4f}  ({fine_acc*100:.1f}%)  [{n_cor}/{n_total}]')

print(f'\n  {"클래스":<22} {"정답":>5} {"전체":>5} {"acc":>7}')
print('  ' + '-' * 44)
class_accs = {}
for cls in sorted(classes):
    sub   = result_df[result_df['true_label'] == cls]
    if len(sub) == 0: continue
    n_ok  = int(sub['is_correct'].sum())
    n_t   = len(sub)
    acc   = n_ok / n_t
    class_accs[cls] = acc
    flag = '' if acc >= 0.85 else (' ⚠' if acc >= 0.70 else ' ❌')
    print(f'  {cls:<22} {n_ok:>5} {n_t:>5} {acc*100:>6.1f}%{flag}')
print('  ' + '-' * 44)
print(f'  {"평균":<22} {n_cor:>5} {n_total:>5} {fine_acc*100:>6.1f}%')

# ═══════════════════════════════════════════════════════════════════════════════
# 8. 서비스 대분류 결과
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('7. 서비스 대분류 Test Accuracy')
print('=' * 65)
print(f'  서비스 acc: {svc_acc:.4f}  ({svc_acc*100:.1f}%)  [{n_svc}/{n_total}]')

print(f'\n  {"서비스 카테고리":<30} {"정답":>5} {"전체":>5} {"acc":>7}')
print('  ' + '-' * 52)
for svc in sorted(result_df['service_true'].unique()):
    sub  = result_df[result_df['service_true'] == svc]
    n_ok = int(sub['service_ok'].sum())
    n_t  = len(sub)
    acc  = n_ok / n_t
    flag = '' if acc >= 0.85 else (' ⚠' if acc >= 0.70 else ' ❌')
    print(f'  {svc:<30} {n_ok:>5} {n_t:>5} {acc*100:>6.1f}%{flag}')

# ═══════════════════════════════════════════════════════════════════════════════
# 9. 오답 분석
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('8. 오답 분석')
print('=' * 65)
wrong_df = result_df[~result_df['is_correct']].copy()
print(f'  오답: {len(wrong_df)}건 / {n_total}건  ({len(wrong_df)/n_total*100:.1f}%)')
if len(wrong_df) > 0:
    patterns = (
        wrong_df.groupby(['true_label', 'pred_label'])
        .size().reset_index(name='count')
        .sort_values('count', ascending=False)
    )
    print(f'\n  [오답 패턴 Top 15]  (true → pred)')
    for _, row in patterns.head(15).iterrows():
        svc_t  = config.SERVICE_LABEL_MAP.get(row['true_label'], '?')
        svc_p  = config.SERVICE_LABEL_MAP.get(row['pred_label'], '?')
        cross  = '' if svc_t == svc_p else '  <- 서비스 오답'
        print(f'    {row["true_label"]:<22} -> {row["pred_label"]:<22}  {row["count"]}건{cross}')

# ═══════════════════════════════════════════════════════════════════════════════
# 10. Low Confidence
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('9. Low Confidence (< 0.70)')
print('=' * 65)
low_conf = result_df[result_df['confidence'] < 0.70]
print(f'  confidence < 0.70: {len(low_conf)}건 / {n_total}장')
if len(low_conf) > 0:
    for cls, cnt in low_conf['true_label'].value_counts().items():
        n_wrong = int((~low_conf[low_conf['true_label'] == cls]['is_correct']).sum())
        print(f'    {cls:<22}: {cnt}건 ({n_wrong}건 오답)')

# ═══════════════════════════════════════════════════════════════════════════════
# 11. Confusion Matrix
# ═══════════════════════════════════════════════════════════════════════════════
n = num_classes
cm = [[0]*n for _ in range(n)]
cls_to_idx = {c: i for i, c in enumerate(classes)}
for _, row in result_df.iterrows():
    cm[cls_to_idx[row['true_label']]][cls_to_idx[row['pred_label']]] += 1

short = [c[:8] for c in classes]
fig, ax = plt.subplots(figsize=(16, 14))
im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.colorbar(im)
ax.set(xticks=range(n), yticks=range(n), xticklabels=short, yticklabels=short,
       ylabel='True', xlabel='Pred',
       title=f'Refined 18-class CM  (Test {n_total}장  acc={fine_acc*100:.1f}%)')
ax.tick_params(axis='x', rotation=45)
max_v = max(max(r) for r in cm)
for i in range(n):
    for j in range(n):
        col = 'white' if cm[i][j] > max_v/2 else 'black'
        ax.text(j, i, cm[i][j], ha='center', va='center', color=col, fontsize=8)
plt.tight_layout()
plt.savefig(CM_FINE_PATH, dpi=120, bbox_inches='tight')
plt.close()

svc_classes = sorted(result_df['service_true'].unique())
ns = len(svc_classes)
svc_idx_map = {c: i for i, c in enumerate(svc_classes)}
cm_svc = [[0]*ns for _ in range(ns)]
for _, row in result_df.iterrows():
    cm_svc[svc_idx_map[row['service_true']]][svc_idx_map[row['service_pred']]] += 1

svc_short = [c[:14] for c in svc_classes]
fig, ax = plt.subplots(figsize=(12, 10))
im = ax.imshow(cm_svc, interpolation='nearest', cmap=plt.cm.Blues)
plt.colorbar(im)
ax.set(xticks=range(ns), yticks=range(ns), xticklabels=svc_short, yticklabels=svc_short,
       ylabel='True', xlabel='Pred',
       title=f'Refined Service-level CM  (acc={svc_acc*100:.1f}%)')
ax.tick_params(axis='x', rotation=30)
max_vs = max(max(r) for r in cm_svc)
for i in range(ns):
    for j in range(ns):
        col = 'white' if cm_svc[i][j] > max_vs/2 else 'black'
        ax.text(j, i, cm_svc[i][j], ha='center', va='center', color=col, fontsize=10)
plt.tight_layout()
plt.savefig(CM_SVC_PATH, dpi=120, bbox_inches='tight')
plt.close()
print(f'\n  CM (fine)    : {CM_FINE_PATH}')
print(f'  CM (service) : {CM_SVC_PATH}')

# ═══════════════════════════════════════════════════════════════════════════════
# 12. Baseline 비교
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('10. Baseline 비교  (baseline=phase3_18class_resumed_best)')
print('=' * 65)

if os.path.exists(BASELINE_CSV):
    base_df = pd.read_csv(BASELINE_CSV, encoding='utf-8-sig')
    base_fine = base_df['is_correct'].mean()
    base_svc  = base_df['service_ok'].mean()
    base_low  = (base_df['confidence'] < 0.70).sum()
    base_n    = len(base_df)

    d_fine = (fine_acc - base_fine) * 100
    d_svc  = (svc_acc  - base_svc)  * 100
    d_low  = len(low_conf) - base_low

    print(f'\n  {"항목":<30} {"baseline":>10} {"refined":>10} {"변화":>10}')
    print('  ' + '-' * 65)
    print(f'  {"세부 라벨 acc":<30} {base_fine*100:>9.1f}% {fine_acc*100:>9.1f}%'
          f' {"+" if d_fine>=0 else ""}{d_fine:>8.1f}%')
    print(f'  {"서비스 대분류 acc":<30} {base_svc*100:>9.1f}% {svc_acc*100:>9.1f}%'
          f' {"+" if d_svc>=0 else ""}{d_svc:>8.1f}%')
    print(f'  {"test 총 이미지수":<30} {base_n:>10} {n_total:>10}')
    print(f'  {"low conf (<0.70)":<30} {base_low:>10} {len(low_conf):>10}'
          f' {"+" if d_low>=0 else ""}{d_low:>10}')

    # beam_projector 관련
    print(f'\n  [beam_projector 관련 오답]')
    base_bp_pred = base_df[(base_df['pred_label']=='beam_projector') & (~base_df['is_correct'])]
    new_bp_pred  = result_df[(result_df['pred_label']=='beam_projector') & (~result_df['is_correct'])]
    print(f'    pred=beam_projector 오답: {len(base_bp_pred)}건 -> {len(new_bp_pred)}건'
          f'  ({"+" if len(new_bp_pred)-len(base_bp_pred)>=0 else ""}{len(new_bp_pred)-len(base_bp_pred)}건)')
    if len(new_bp_pred) > 0:
        for _, r in new_bp_pred.iterrows():
            print(f'    {r.true_label:<22} -> beam_projector  conf={r.confidence:.3f}')

    # humidifier 관련
    print(f'\n  [humidifier 관련 오답]')
    base_hum_w = base_df[(base_df['true_label']=='humidifier') & (~base_df['service_ok'])]
    new_hum_w  = result_df[(result_df['true_label']=='humidifier') & (~result_df['service_ok'])]
    print(f'    humidifier 서비스 오답: {len(base_hum_w)}건 -> {len(new_hum_w)}건')
    if len(new_hum_w) > 0:
        for _, r in new_hum_w.iterrows():
            print(f'    humidifier -> {r.pred_label:<22}  conf={r.confidence:.3f}')

    # heater 관련
    print(f'\n  [heater 관련 오답]')
    base_htr_w = base_df[(base_df['true_label']=='heater') & (~base_df['service_ok'])]
    new_htr_w  = result_df[(result_df['true_label']=='heater') & (~result_df['service_ok'])]
    print(f'    heater 서비스 오답: {len(base_htr_w)}건 -> {len(new_htr_w)}건')
    if len(new_htr_w) > 0:
        for _, r in new_htr_w.iterrows():
            print(f'    heater -> {r.pred_label:<22}  conf={r.confidence:.3f}')

    # 클래스별 acc 변화
    print(f'\n  [클래스별 acc 변화]')
    print(f'  {"클래스":<22} {"baseline":>9} {"refined":>9} {"변화":>8}')
    print('  ' + '-' * 53)
    for cls in sorted(classes):
        base_sub = base_df[base_df['true_label'] == cls]
        new_sub  = result_df[result_df['true_label'] == cls]
        if len(base_sub) == 0 or len(new_sub) == 0:
            continue
        b_acc = base_sub['is_correct'].mean()
        n_acc = class_accs.get(cls, 0.0)
        d     = (n_acc - b_acc) * 100
        mark  = ' <--' if abs(d) >= 5 else ''
        print(f'  {cls:<22} {b_acc*100:>8.1f}% {n_acc*100:>8.1f}% {"+" if d>=0 else ""}{d:>6.1f}%{mark}')
else:
    print(f'  baseline CSV 없음: {BASELINE_CSV}')

# ═══════════════════════════════════════════════════════════════════════════════
# 13. 추가 학습 필요 여부 판단
# ═══════════════════════════════════════════════════════════════════════════════
print('\n' + '=' * 65)
print('11. 추가 학습 필요 여부 (기준: 클래스별 acc < 85%)')
print('=' * 65)
need_boost = sorted([(c, a) for c, a in class_accs.items() if a < 0.85], key=lambda x: x[1])
if not need_boost:
    print('  모든 클래스 85% 이상 — 추가 학습 불필요')
else:
    for cls, acc in need_boost:
        proc_cnt = len(list(Path(config.PROCESSED_DIR, cls).glob('*.jpg')))
        print(f'  {cls:<22} {acc*100:.1f}%  ({proc_cnt}장)')

# ── 최종 요약 ──────────────────────────────────────────────────────────────────
print('\n' + '=' * 65)
print('완료')
print('=' * 65)
print(f'  완료 시각         : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'  세부 라벨 acc     : {fine_acc*100:.2f}%  ({n_cor}/{n_total})')
print(f'  서비스 acc        : {svc_acc*100:.2f}%  ({n_svc}/{n_total})')
print(f'  refined best      : {CKPT_REFINED_BEST}')
print(f'  refined last      : {CKPT_REFINED_LAST}')
print(f'  결과 CSV          : {CSV_PATH}')
