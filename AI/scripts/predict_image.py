#!/usr/bin/env python3
"""
가전 이미지 분류 추론 스크립트 (독립 실행형)

사용법:
  python scripts/predict_image.py --image path/to/image.jpg
  python scripts/predict_image.py --image path/to/image.jpg --json
  python scripts/predict_image.py --image path/to/image.jpg --checkpoint checkpoints/other.pth
"""

import argparse
import json
import sys
from pathlib import Path

# AI/ 를 프로젝트 루트로 설정 (scripts/ 한 단계 위)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
import config

import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_v2_s
from PIL import Image as PILImage

# 기본 체크포인트 경로
DEFAULT_CKPT = PROJECT_ROOT / config.CHECKPOINTS_DIR / 'phase2_service_best_model.pth'

# valid/test 와 동일한 전처리 (augmentation 없음)
TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def load_model(ckpt_path: Path, device: torch.device):
    if not ckpt_path.exists():
        print(f'\n[오류] 모델 파일을 찾을 수 없습니다.')
        print(f'  경로: {ckpt_path}')
        print(f'  → AI/checkpoints/ 폴더에 phase2_service_best_model.pth 가 있는지 확인해주세요.')
        print(f'  → 학습이 완료된 체크포인트 파일이 필요합니다.')
        sys.exit(1)

    ckpt        = torch.load(ckpt_path, map_location=device, weights_only=False)
    classes     = ckpt['classes']          # 체크포인트 내부 클래스 순서 사용
    num_classes = len(classes)

    model = efficientnet_v2_s(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(ckpt['model_state_dict'])
    model = model.to(device)
    model.eval()

    return model, classes, ckpt


def predict(image_path: str, model, classes, device):
    path = Path(image_path)
    if not path.exists():
        print(f'\n[오류] 이미지 파일을 찾을 수 없습니다: {path}')
        sys.exit(1)
    if path.suffix.lower() not in ('.jpg', '.jpeg', '.png', '.bmp', '.webp'):
        print(f'\n[오류] 지원하지 않는 파일 형식입니다: {path.suffix}')
        print('  → .jpg .jpeg .png .bmp .webp 형식만 지원합니다.')
        sys.exit(1)

    try:
        img = PILImage.open(path).convert('RGB')
    except Exception as e:
        print(f'\n[오류] 이미지를 열 수 없습니다: {e}')
        sys.exit(1)

    tensor = TRANSFORM(img).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0]

    top_k = min(3, len(classes))
    top_probs, top_idx = probs.topk(top_k)

    results = []
    for prob, idx in zip(top_probs.tolist(), top_idx.tolist()):
        fine = classes[idx]
        svc  = config.SERVICE_LABEL_MAP[fine]
        results.append({
            'fine_label':    fine,
            'service_label': svc,
            'confidence':    round(prob, 6),
        })

    return results


def main():
    parser = argparse.ArgumentParser(
        description='가전 이미지 분류 추론 — EfficientNetV2-S Phase 2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''\
예시:
  python scripts/predict_image.py --image data/external_test/refrigerator/ext_0000.jpg
  python scripts/predict_image.py --image photo.jpg --json
  python scripts/predict_image.py --image photo.jpg --checkpoint checkpoints/other.pth
        ''',
    )
    parser.add_argument('--image',      required=True,          help='추론할 이미지 파일 경로')
    parser.add_argument('--checkpoint', default=str(DEFAULT_CKPT), help='체크포인트 경로 (기본: phase2_service_best_model.pth)')
    parser.add_argument('--json',       action='store_true',    help='JSON 형식으로 출력')
    parser.add_argument('--cpu',        action='store_true',    help='GPU 무시하고 CPU 강제 사용')
    args = parser.parse_args()

    device    = torch.device('cpu') if args.cpu else \
                torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    ckpt_path = Path(args.checkpoint)

    model, classes, ckpt = load_model(ckpt_path, device)
    results               = predict(args.image, model, classes, device)
    best                  = results[0]

    if args.json:
        output = {
            'image':      str(args.image),
            'device':     str(device),
            'checkpoint': ckpt_path.name,
            'prediction': best,
            'top3':       results,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        sep = '─' * 44
        print(sep)
        print(f'  체크포인트 : {ckpt_path.name}')
        print(f'  phase/epoch: {ckpt["phase"]} / epoch {ckpt["epoch"]}')
        print(f'  classes    : {classes}')
        print(f'  device     : {device}')
        print(sep)
        print(f'  이미지     : {args.image}')
        print(sep)
        print(f'  fine_label    : {best["fine_label"]}')
        print(f'  service_label : {best["service_label"]}')
        print(f'  confidence    : {best["confidence"]:.4f}')
        print(sep)
        print('  Top-3 예측:')
        for rank, r in enumerate(results, 1):
            bar = '█' * int(r['confidence'] * 30)
            print(f'    {rank}. {r["fine_label"]:<16} ({r["service_label"]:<15})  '
                  f'{r["confidence"]:.4f}  {bar}')
        print(sep)


if __name__ == '__main__':
    main()
