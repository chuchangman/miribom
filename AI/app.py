"""
가전 이미지 분류 API 서버

실행:
  cd AI
  uvicorn app:app --reload --host 0.0.0.0 --port 8001
"""

from __future__ import annotations

import io
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image as PILImage
from pydantic import BaseModel

# AI/ 를 sys.path에 추가 (app.py 위치 기준)
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from core.predictor import AppliancePredictor, SUPPORTED_MIME_TYPES

CKPT_PATH = PROJECT_ROOT / config.CHECKPOINTS_DIR / 'phase3_18class_service_best.pth'

# ── 전역 predictor (서버 시작 시 1회 로드) ────────────────────────────────────
predictor: AppliancePredictor | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global predictor
    print('[시작] 모델 로드 중...')
    try:
        predictor = AppliancePredictor(
            ckpt_path=CKPT_PATH,
            service_label_map=config.SERVICE_LABEL_MAP,
        )
        m = predictor.meta
        print(f'[완료] {m["checkpoint"]}  phase={m["phase"]}  epoch={m["epoch"]}  '
              f'val_acc={m["val_acc"]}  device={m["device"]}')
        print(f'[완료] classes={m["classes"]}')
    except FileNotFoundError as e:
        print(f'[오류] {e}')
        raise RuntimeError(str(e))
    yield
    print('[종료] 서버 종료')


# ── FastAPI 앱 ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title='가전 이미지 분류 API',
    description='EfficientNetV2-S Phase 3 Refined — 18-class 가전 세부 분류 + 8-category 서비스 분류',
    version='3.0.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],      # 운영 환경에서는 특정 도메인으로 제한
    allow_methods=['*'],
    allow_headers=['*'],
)


# ── 응답 스키마 ────────────────────────────────────────────────────────────────
class PredictionItem(BaseModel):
    fine_label:    str
    service_label: str
    confidence:    float

class PredictResponse(BaseModel):
    fine_label:    str
    service_label: str
    confidence:    float
    top3:          list[PredictionItem]


# ── 엔드포인트 ─────────────────────────────────────────────────────────────────
@app.get('/health')
async def health():
    """서버 및 모델 상태 확인"""
    if predictor is None:
        raise HTTPException(status_code=503, detail='모델이 아직 로드되지 않았습니다.')
    return {'status': 'ok', 'model': predictor.meta}


@app.post('/api/predict-image/', response_model=PredictResponse)
async def predict_image(file: UploadFile = File(...)):
    """이미지 업로드 후 가전 종류 예측

    - **file**: jpg / jpeg / png 이미지 파일 (multipart/form-data)
    """
    # MIME 타입 검사
    if file.content_type not in SUPPORTED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f'지원하지 않는 파일 형식입니다: {file.content_type}. '
                   f'지원 형식: {", ".join(sorted(SUPPORTED_MIME_TYPES))}',
        )

    # 파일 읽기
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail='빈 파일입니다.')

    # PIL로 이미지 열기
    try:
        image = PILImage.open(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'이미지를 열 수 없습니다: {e}')

    # 추론
    results = predictor.predict(image, top_k=3)
    best    = results[0]

    return PredictResponse(
        fine_label=best['fine_label'],
        service_label=best['service_label'],
        confidence=best['confidence'],
        top3=[PredictionItem(**r) for r in results],
    )
