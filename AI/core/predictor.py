"""
가전 이미지 분류 추론 코어 모듈
CLI(scripts/predict_image.py)와 API 서버(app.py) 양쪽에서 공용으로 사용한다.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_v2_s
from PIL import Image as PILImage

# valid/test 와 동일한 전처리 (augmentation 없음)
_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
SUPPORTED_MIME_TYPES  = {'image/jpeg', 'image/png'}


class AppliancePredictor:
    """EfficientNetV2-S 기반 가전 이미지 분류기.

    서버 시작 시 1회만 인스턴스화해 재사용한다.
    """

    def __init__(
        self,
        ckpt_path: Path | str,
        service_label_map: dict[str, str],
        device: Optional[torch.device] = None,
    ) -> None:
        ckpt_path = Path(ckpt_path)
        if not ckpt_path.exists():
            raise FileNotFoundError(
                f'체크포인트 파일이 없습니다: {ckpt_path}\n'
                '  → AI/checkpoints/phase2_service_best_model.pth 를 확인해주세요.'
            )

        if device is None:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.device           = device
        self.service_label_map = service_label_map

        ckpt             = torch.load(ckpt_path, map_location=device, weights_only=False)
        self.classes: list[str] = ckpt['classes']
        self.meta: dict = {
            'checkpoint': ckpt_path.name,
            'phase':      ckpt['phase'],
            'epoch':      ckpt['epoch'],
            'val_acc':    round(float(ckpt['val_acc']), 4),
            'device':     str(device),
            'classes':    self.classes,
        }

        num_classes = len(self.classes)
        model = efficientnet_v2_s(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
        model.load_state_dict(ckpt['model_state_dict'])
        model = model.to(device)
        model.eval()
        self._model = model

    def predict(self, image: PILImage.Image, top_k: int = 3) -> list[dict]:
        """PIL 이미지를 받아 상위 top_k 예측 결과를 반환한다.

        Returns:
            [{'fine_label': str, 'service_label': str, 'confidence': float}, ...]
        """
        img    = image.convert('RGB')
        tensor = _TRANSFORM(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            probs = torch.softmax(self._model(tensor), dim=1)[0]

        k = min(top_k, len(self.classes))
        top_probs, top_idx = probs.topk(k)

        return [
            {
                'fine_label':    self.classes[idx.item()],
                'service_label': self.service_label_map[self.classes[idx.item()]],
                'confidence':    round(prob.item(), 6),
            }
            for prob, idx in zip(top_probs, top_idx)
        ]
