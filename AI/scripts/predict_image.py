#!/usr/bin/env python3
"""
가전 이미지 분류 추론 스크립트 (독립 실행형 CLI)

사용법:
  python scripts/predict_image.py --image path/to/image.jpg
  python scripts/predict_image.py --image path/to/image.jpg --json
  python scripts/predict_image.py --image path/to/image.jpg --cpu
"""

import argparse
import json
import sys
from pathlib import Path

# AI/ 를 프로젝트 루트로 설정
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from core.predictor import AppliancePredictor, SUPPORTED_EXTENSIONS

DEFAULT_CKPT = PROJECT_ROOT / config.CHECKPOINTS_DIR / 'phase3_18class_service_best.pth'


def main() -> None:
    parser = argparse.ArgumentParser(
        description='가전 이미지 분류 추론 — EfficientNetV2-S Phase 3 Refined (18-class)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''\
예시:
  python scripts/predict_image.py --image data/split/test/refrigerator/naver_0000.jpg
  python scripts/predict_image.py --image photo.jpg --json
  python scripts/predict_image.py --image photo.jpg --cpu
        ''',
    )
    parser.add_argument('--image',      required=True,              help='추론할 이미지 파일 경로')
    parser.add_argument('--checkpoint', default=str(DEFAULT_CKPT),  help='체크포인트 경로')
    parser.add_argument('--json',       action='store_true',        help='JSON 형식으로 출력')
    parser.add_argument('--cpu',        action='store_true',        help='CPU 강제 사용')
    args = parser.parse_args()

    import torch
    device = torch.device('cpu') if args.cpu else \
             torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # 모델 로드
    try:
        predictor = AppliancePredictor(
            ckpt_path=args.checkpoint,
            service_label_map=config.SERVICE_LABEL_MAP,
            device=device,
        )
    except FileNotFoundError as e:
        print(f'\n[오류] {e}')
        sys.exit(1)

    # 이미지 유효성 검사
    path = Path(args.image)
    if not path.exists():
        print(f'\n[오류] 이미지 파일이 없습니다: {path}')
        sys.exit(1)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f'\n[오류] 지원하지 않는 형식: {path.suffix}')
        print(f'  → 지원 형식: {", ".join(sorted(SUPPORTED_EXTENSIONS))}')
        sys.exit(1)

    from PIL import Image as PILImage
    try:
        image = PILImage.open(path)
    except Exception as e:
        print(f'\n[오류] 이미지를 열 수 없습니다: {e}')
        sys.exit(1)

    results = predictor.predict(image, top_k=3)
    best    = results[0]

    if args.json:
        print(json.dumps(
            {'image': str(args.image), **predictor.meta,
             'prediction': best, 'top3': results},
            ensure_ascii=False, indent=2,
        ))
    else:
        sep = '─' * 44
        m   = predictor.meta
        print(sep)
        print(f'  체크포인트 : {m["checkpoint"]}')
        print(f'  phase/epoch: {m["phase"]} / epoch {m["epoch"]}')
        print(f'  classes    : {m["classes"]}')
        print(f'  device     : {m["device"]}')
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
            print(f'    {rank}. {r["fine_label"]:<16} ({r["service_label"]:<15}) '
                  f'{r["confidence"]:.4f}  {bar}')
        print(sep)


if __name__ == '__main__':
    main()
