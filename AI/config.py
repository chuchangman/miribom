import os

# ── Open Images 수집 설정 ────────────────────────────────────────────────────────
# Open Images 공식 클래스명 (01_download_metadata.ipynb 에서 사용)
# 반드시 OI class-descriptions CSV의 ClassName 값과 정확히 일치해야 한다.
OI_TARGET_CLASSES     = ["Washing machine", "Refrigerator"]
MAX_SAMPLES_PER_CLASS = 100   # 클래스당 최대 bbox 수
MIN_CROP_SIZE         = 64    # 이 픽셀 미만의 crop은 저장하지 않음

# ── 프로젝트 내부 학습 라벨 ─────────────────────────────────────────────────────
# data/processed/{label}/ 폴더명, split 폴더명, checkpoint classes 와 일치해야 한다.
#
# Phase 1:
# PROJECT_LABELS = ["refrigerator", "washer_dryer"]
#
# Phase 2 (현재 활성):
PROJECT_LABELS = ["refrigerator", "washer_dryer", "wash_tower"]
#
# 라벨 정의:
#   refrigerator — 가정용 냉장고 (스탠드형, 양문형, 4도어 등)
#   washer_dryer — 드럼/통돌이 세탁기, 건조기, 세탁건조 일체형 모두 포함
#   wash_tower   — 세탁기 위에 건조기가 얹힌 상하 결합형 (예: LG 워시타워)

# ── 네이버 쇼핑 검색어 (내부 라벨별) ──────────────────────────────────────────
# 보조 이미지 수집 시 사용 (나버 쇼핑 API query 파라미터)
NAVER_SEARCH_QUERIES = {
    "refrigerator": [
        # ☆☆☆ 기존 — 다양한 형태 기본 커버
        "냉장고",
        "스탠드형 냉장고",
        "양문형 냉장고",
        "4도어 냉장고",
        "삼성 냉장고",
        "LG 냉장고",
        # ★★★ 단문/소형 — 정면이 건조기와 가장 유사한 유형 (오답 원인 1순위)
        "단문냉장고",
        "소형냉장고",
        "원룸냉장고",
        "미니냉장고",
        # ★★☆ 냉동고 — 세로 직사각형, 건조기 정면과 형태 유사
        "냉동고",
        "스탠드형냉동고",
        # ★☆☆ 정면 뷰 강화 — partial crop 대응
        "냉장고 정면",
        "냉장고 제품사진",
        # ☆☆☆ 특징 명확한 제품 — 구별 단서 강화
        "삼성 비스포크 냉장고",
        "LG 오브제 냉장고",
    ],
    "washer_dryer": [
        # ★★★ 통돌이 (porthole 없음 — 냉장고와 혼동 위험 최고, 최우선 보강)
        "통돌이세탁기",
        "삼성 통돌이세탁기",
        "LG 통돌이세탁기",
        # ★★☆ 건조기 단독 (정면 직사각형 — 혼동 위험 높음)
        "건조기",
        "히트펌프건조기",
        "드럼건조기",
        "삼성 건조기",
        "LG 건조기",
        # ★☆☆ 세탁건조기 일체형 (porthole 있으나 키 작음)
        "세탁건조기",
        "세탁건조기 일체형",
        # ☆☆☆ 드럼세탁기 (porthole 명확 — 모델 구분 단서 강화)
        "드럼세탁기",
        "드럼세탁기 정면",
    ],
    "wash_tower": [
        # ★★★ LG 공식 브랜드명 — 가장 구체적, 노이즈 최소
        "워시타워",
        "LG 워시타워",
        "LG 워시타워 슬림",
        "LG 워시타워 오브제",
        # ★★★ 삼성 동급 제품 — 공식명 사용
        "삼성 비스포크 그랑데 AI",
        "삼성 그랑데 AI 세탁건조기",
        # ★★☆ 타워형 일반어 — wash_tower 특화, 소량 노이즈 가능
        "세탁건조타워",
        "타워형 세탁건조기",
        "일체형 세탁건조기 타워",
        # ★☆☆ 검수 필수 — 옆으로 나란히 세트 포함 가능성 높음
        "세탁기 건조기 세트 타워형",
        "상하 결합 세탁기 건조기",
    ],   # Phase 2
}

# ── 경로 ────────────────────────────────────────────────────────────────────────
DATA_DIR      = "data"
METADATA_DIR  = os.path.join(DATA_DIR, "metadata")
RAW_DIR       = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MANIFEST_PATH = os.path.join(METADATA_DIR, "manifest.csv")

# ── Open Images 공식 CSV URL ─────────────────────────────────────────────────────
OI_URLS = {
    "class_descriptions": "https://storage.googleapis.com/openimages/v6/oidv6-class-descriptions.csv",
    "validation_bbox":    "https://storage.googleapis.com/openimages/v5/validation-annotations-bbox.csv",
    "test_bbox":          "https://storage.googleapis.com/openimages/v5/test-annotations-bbox.csv",
    "validation_images":  "https://storage.googleapis.com/openimages/2018_04/validation/validation-images-with-rotation.csv",
    "test_images":        "https://storage.googleapis.com/openimages/2018_04/test/test-images-with-rotation.csv",
}

# ── 다운로드 설정 ────────────────────────────────────────────────────────────────
DOWNLOAD_TIMEOUT = 30   # 요청당 타임아웃(초)
MAX_WORKERS      = 8    # 병렬 다운로드 스레드 수

# ── Split / 학습 설정 ─────────────────────────────────────────────────────────────
SPLIT_DIR       = os.path.join(DATA_DIR, "split")
SPLIT_SEED      = 42
CHECKPOINTS_DIR = "checkpoints"

# ── 서비스 대분류 매핑 ─────────────────────────────────────────────────────────────
# 세부 학습 라벨 → 서비스 노출 카테고리
# washer_dryer, wash_tower 는 서비스에서 모두 washing_drying 단일 카테고리로 노출
# wash_tower 항목은 Phase 2 이후 유효 (Phase 1에서는 참조되지 않음)
SERVICE_LABEL_MAP = {
    "refrigerator": "refrigerator",
    "washer_dryer": "washing_drying",
    "wash_tower":   "washing_drying",   # Phase 2
}
