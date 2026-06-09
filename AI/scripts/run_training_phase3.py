"""
18-class baseline 학습 스크립트 (Phase 3)
체크포인트: checkpoints/phase3_18class_best.pth  (phase2 모델과 충돌 없음)
결과 CSV  : data/metadata/test_predictions_phase3.csv
"""

import os
import sys
import json
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
from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights

print(f'PyTorch  : {torch.__version__}')
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'Device   : {device}')
if device.type == 'cuda':
    print(f'GPU      : {torch.cuda.get_device_name(0)}')

CKPT_PATH    = os.path.join(config.CHECKPOINTS_DIR, 'phase3_18class_best.pth')
CSV_PATH     = os.path.join(config.METADATA_DIR, 'test_predictions_phase3.csv')
CM_FINE_PATH = os.path.join(config.METADATA_DIR, 'phase3_cm_fine.png')
CM_SVC_PATH  = os.path.join(config.METADATA_DIR, 'phase3_cm_service.png')

IMG_SIZE   = 224
BATCH_SIZE = 32

# ── Dataset ───────────────────────────────────────────────────────────────────
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

classes     = train_ds.classes
num_classes = len(classes)

print(f'\n클래스  : {num_classes}개')
print(f'Train   : {len(train_ds)}장')
print(f'Valid   : {len(valid_ds)}장')
print(f'Test    : {len(test_ds)}장')

# WeightedRandomSampler for class imbalance
train_counts = [
    len(os.listdir(os.path.join(config.SPLIT_DIR, 'train', c))) for c in classes
]
weights_per_class = [1.0 / max(c, 1) for c in train_counts]
sample_weights = [weights_per_class[label] for _, label in train_ds.imgs]
sampler = torch.utils.data.WeightedRandomSampler(
    sample_weights, num_samples=len(sample_weights), replacement=True
)

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=sampler,
                          num_workers=0, pin_memory=True)
valid_loader = DataLoader(valid_ds, batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=0, pin_memory=True)
test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=0, pin_memory=True)

# ── 모델 ─────────────────────────────────────────────────────────────────────
criterion = nn.CrossEntropyLoss()

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

def save_history_plot(history, title, path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(history['train_loss'], label='train')
    ax1.plot(history['val_loss'],   label='valid')
    ax1.set_title(f'{title} Loss'); ax1.legend(); ax1.grid(True)
    ax2.plot(history['train_acc'], label='train')
    ax2.plot(history['val_acc'],   label='valid')
    ax2.set_title(f'{title} Acc'); ax2.legend(); ax2.grid(True)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()

# ── Phase 1: backbone freeze, classifier head 학습 ──────────────────────────
print('\n' + '='*60)
print('Phase 1: backbone freeze, classifier head 학습')
print('='*60)

model = efficientnet_v2_s(weights=EfficientNet_V2_S_Weights.DEFAULT)
in_features = model.classifier[1].in_features
model.classifier[1] = nn.Linear(in_features, num_classes)

for param in model.parameters():
    param.requires_grad = False
for param in model.classifier.parameters():
    param.requires_grad = True

model = model.to(device)
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total_p   = sum(p.numel() for p in model.parameters())
print(f'Trainable: {trainable:,} / {total_p:,} ({100*trainable/total_p:.2f}%)')

NUM_EPOCHS_P1 = 15
optimizer_p1  = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3
)
scheduler_p1 = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer_p1, mode='min', factor=0.5, patience=3
)

history_p1   = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
best_val_loss = float('inf')

for epoch in range(1, NUM_EPOCHS_P1 + 1):
    tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer_p1)
    vl_loss, vl_acc = evaluate(model, valid_loader)
    scheduler_p1.step(vl_loss)

    history_p1['train_loss'].append(tr_loss)
    history_p1['train_acc'].append(tr_acc)
    history_p1['val_loss'].append(vl_loss)
    history_p1['val_acc'].append(vl_acc)

    marker = ' ★' if vl_loss < best_val_loss else ''
    if vl_loss < best_val_loss:
        best_val_loss = vl_loss
        torch.save({
            'epoch': epoch, 'phase': 'phase1',
            'model_state_dict': model.state_dict(),
            'val_loss': vl_loss, 'val_acc': vl_acc,
            'classes': classes,
        }, CKPT_PATH)

    print(f'  Ep {epoch:2d}/{NUM_EPOCHS_P1} | '
          f'tr_loss={tr_loss:.4f} tr_acc={tr_acc:.4f} | '
          f'vl_loss={vl_loss:.4f} vl_acc={vl_acc:.4f}{marker}')

save_history_plot(history_p1, 'Phase1',
                  os.path.join(config.METADATA_DIR, 'phase3_history_p1.png'))
ckpt = torch.load(CKPT_PATH)
print(f'\nPhase1 best: epoch={ckpt["epoch"]} val_loss={ckpt["val_loss"]:.4f} val_acc={ckpt["val_acc"]:.4f}')

# ── Phase 2: features.6, features.7, classifier unfreeze ────────────────────
print('\n' + '='*60)
print('Phase 2: features.6 / features.7 / classifier unfreeze')
print('='*60)

model.load_state_dict(torch.load(CKPT_PATH)['model_state_dict'])

for param in model.parameters():
    param.requires_grad = False
for name, param in model.named_parameters():
    if any(k in name for k in ['features.6', 'features.7', 'classifier']):
        param.requires_grad = True

model = model.to(device)
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f'Trainable: {trainable:,} / {total_p:,} ({100*trainable/total_p:.2f}%)')

NUM_EPOCHS_P2 = 10
optimizer_p2  = optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()), lr=1e-4
)
scheduler_p2 = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer_p2, mode='min', factor=0.5, patience=3
)

history_p2       = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
best_val_loss_p2 = float('inf')

for epoch in range(1, NUM_EPOCHS_P2 + 1):
    tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer_p2)
    vl_loss, vl_acc = evaluate(model, valid_loader)
    scheduler_p2.step(vl_loss)

    history_p2['train_loss'].append(tr_loss)
    history_p2['train_acc'].append(tr_acc)
    history_p2['val_loss'].append(vl_loss)
    history_p2['val_acc'].append(vl_acc)

    marker = ' ★' if vl_loss < best_val_loss_p2 else ''
    if vl_loss < best_val_loss_p2:
        best_val_loss_p2 = vl_loss
        torch.save({
            'epoch': epoch, 'phase': 'phase2',
            'model_state_dict': model.state_dict(),
            'val_loss': vl_loss, 'val_acc': vl_acc,
            'classes': classes,
        }, CKPT_PATH)

    print(f'  Ep {epoch:2d}/{NUM_EPOCHS_P2} | '
          f'tr_loss={tr_loss:.4f} tr_acc={tr_acc:.4f} | '
          f'vl_loss={vl_loss:.4f} vl_acc={vl_acc:.4f}{marker}')

save_history_plot(history_p2, 'Phase2',
                  os.path.join(config.METADATA_DIR, 'phase3_history_p2.png'))

ckpt = torch.load(CKPT_PATH)
print(f'\nPhase3 best: phase={ckpt["phase"]} epoch={ckpt["epoch"]} '
      f'val_loss={ckpt["val_loss"]:.4f} val_acc={ckpt["val_acc"]:.4f}')

# ── Test 평가 ─────────────────────────────────────────────────────────────────
print('\n' + '='*60)
print('Test 평가')
print('='*60)

model.load_state_dict(torch.load(CKPT_PATH)['model_state_dict'])
model.eval()

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

# ── 결과 DataFrame ────────────────────────────────────────────────────────────
result_df = pd.DataFrame({
    'image_path':  all_paths,
    'true_label':  [classes[t] for t in all_targets],
    'pred_label':  [classes[p] for p in all_preds],
    'confidence':  [round(c, 6) for c in all_confs],
    'is_correct':  [t == p for t, p in zip(all_targets, all_preds)],
})
result_df['service_true'] = result_df['true_label'].map(config.SERVICE_LABEL_MAP)
result_df['service_pred'] = result_df['pred_label'].map(config.SERVICE_LABEL_MAP)
result_df['service_ok']   = result_df['service_true'] == result_df['service_pred']

result_df.to_csv(CSV_PATH, index=False, encoding='utf-8-sig')

# ── 세부 라벨 accuracy ────────────────────────────────────────────────────────
n_total   = len(result_df)
fine_acc  = result_df['is_correct'].mean()
svc_acc   = result_df['service_ok'].mean()

print(f'\n세부 라벨 Test Acc  : {fine_acc:.4f}  ({fine_acc*100:.1f}%)')
print(f'서비스 대분류 Test Acc: {svc_acc:.4f}  ({svc_acc*100:.1f}%)')
print(f'Test 샘플 수       : {n_total}장\n')

# ── 클래스별 accuracy ─────────────────────────────────────────────────────────
print(f'{"클래스":<22} {"정답":>5} {"전체":>5} {"acc":>7}  {"서비스 카테고리":<25}')
print('-'*70)

class_accs = {}
for cls in sorted(classes):
    sub = result_df[result_df['true_label'] == cls]
    if len(sub) == 0:
        continue
    n_ok  = sub['is_correct'].sum()
    n_tot = len(sub)
    acc   = n_ok / n_tot
    svc   = config.SERVICE_LABEL_MAP.get(cls, '?')
    class_accs[cls] = acc
    flag = '' if acc >= 0.80 else (' ⚠' if acc >= 0.60 else ' ❌')
    print(f'{cls:<22} {n_ok:>5} {n_tot:>5} {acc*100:>6.1f}%{flag:<3}  {svc:<25}')

print('-'*70)
print(f'{"전체 평균":<22} {"":>5} {n_total:>5} {fine_acc*100:>6.1f}%')

# ── 서비스 대분류별 accuracy ──────────────────────────────────────────────────
print(f'\n{"서비스 카테고리":<28} {"정답":>5} {"전체":>5} {"acc":>7}')
print('-'*50)
for svc in sorted(result_df['service_true'].unique()):
    sub  = result_df[result_df['service_true'] == svc]
    n_ok = sub['service_ok'].sum()
    n_t  = len(sub)
    acc  = n_ok / n_t
    flag = '' if acc >= 0.80 else (' ⚠' if acc >= 0.60 else ' ❌')
    print(f'{svc:<28} {n_ok:>5} {n_t:>5} {acc*100:>6.1f}%{flag}')

# ── 오답 분석 ─────────────────────────────────────────────────────────────────
wrong_df = result_df[~result_df['is_correct']].copy()
print(f'\n오답 총 {len(wrong_df)}건 / {n_total}건')

if len(wrong_df) > 0:
    print(f'\n[오답 패턴 Top 15] (true → pred)')
    patterns = wrong_df.groupby(['true_label', 'pred_label']).size() \
                        .reset_index(name='count') \
                        .sort_values('count', ascending=False)
    for _, row in patterns.head(15).iterrows():
        print(f'  {row["true_label"]:<22} → {row["pred_label"]:<22}  {row["count"]}건')

# ── low confidence 분석 ───────────────────────────────────────────────────────
low_conf = result_df[result_df['confidence'] < 0.7]
print(f'\n[low confidence < 0.70] {len(low_conf)}건')
if len(low_conf) > 0:
    lc_cls = low_conf['true_label'].value_counts()
    for cls, cnt in lc_cls.items():
        print(f'  {cls:<22}: {cnt}건')

# ── Confusion Matrix 저장 ─────────────────────────────────────────────────────
n = num_classes
cm = [[0]*n for _ in range(n)]
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
       title=f'Phase3 18-class Confusion Matrix (Test {n_total}장)')
ax.tick_params(axis='x', rotation=45)
max_v = max(max(r) for r in cm)
for i in range(n):
    for j in range(n):
        col = 'white' if cm[i][j] > max_v/2 else 'black'
        ax.text(j, i, cm[i][j], ha='center', va='center', color=col, fontsize=8)
plt.tight_layout()
plt.savefig(CM_FINE_PATH, dpi=120, bbox_inches='tight')
plt.close()
print(f'\nConfusion Matrix 저장: {CM_FINE_PATH}')

# ── 서비스 대분류 CM ─────────────────────────────────────────────────────────
svc_classes = sorted(result_df['service_true'].unique())
ns = len(svc_classes)
svc_idx_map = {c: i for i, c in enumerate(svc_classes)}
cm_svc = [[0]*ns for _ in range(ns)]
for _, row in result_df.iterrows():
    cm_svc[svc_idx_map[row['service_true']]][svc_idx_map[row['service_pred']]] += 1

svc_short = [c[:12] for c in svc_classes]
fig, ax = plt.subplots(figsize=(10, 9))
im = ax.imshow(cm_svc, interpolation='nearest', cmap=plt.cm.Blues)
plt.colorbar(im)
ax.set(xticks=range(ns), yticks=range(ns),
       xticklabels=svc_short, yticklabels=svc_short,
       ylabel='True', xlabel='Pred',
       title=f'Phase3 Service-level Confusion Matrix')
ax.tick_params(axis='x', rotation=30)
max_vs = max(max(r) for r in cm_svc)
for i in range(ns):
    for j in range(ns):
        col = 'white' if cm_svc[i][j] > max_vs/2 else 'black'
        ax.text(j, i, cm_svc[i][j], ha='center', va='center', color=col, fontsize=10)
plt.tight_layout()
plt.savefig(CM_SVC_PATH, dpi=120, bbox_inches='tight')
plt.close()
print(f'서비스 CM 저장: {CM_SVC_PATH}')

# ── 추가 수집 필요 클래스 제안 ───────────────────────────────────────────────
print('\n' + '='*60)
print('추가 수집 필요 클래스 제안')
print('='*60)
need_boost = [(cls, acc) for cls, acc in class_accs.items() if acc < 0.85]
need_boost.sort(key=lambda x: x[1])

if not need_boost:
    print('모든 클래스 85% 이상 — 추가 수집 불필요')
else:
    print(f'{"클래스":<22} {"acc":>7}  {"현재 processed":>14}  {"판단"}')
    print('-'*65)
    for cls, acc in need_boost:
        proc_cnt = len(os.listdir(os.path.join(config.PROCESSED_DIR, cls)))
        priority = '긴급' if acc < 0.70 else ('권장' if acc < 0.80 else '선택')
        print(f'{cls:<22} {acc*100:>6.1f}%  {proc_cnt:>14}장  {priority}')

print(f'\n완료: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print(f'체크포인트: {CKPT_PATH}')
print(f'결과 CSV  : {CSV_PATH}')
