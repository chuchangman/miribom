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
# Phase 2 (3-class 모델, 학습 완료):
# PROJECT_LABELS = ["refrigerator", "washer_dryer", "wash_tower"]
#
# Phase 3 (18-class baseline — 학습 직전에 아래 주석 해제):
# PROJECT_LABELS = [
#     "refrigerator",
#     "washer_dryer", "wash_tower",
#     "rice_cooker", "microwave", "air_fryer", "electric_kettle",
#     "vacuum_cleaner", "robot_vacuum",
#     "fan", "air_conditioner", "heater",
#     "dehumidifier", "humidifier",
#     "monitor", "keyboard", "mouse",
#     "beam_projector",
# ]
#
# 현재 활성 (Phase 3 — 18-class baseline 학습):
PROJECT_LABELS = [
    "refrigerator",
    "washer_dryer", "wash_tower",
    "rice_cooker", "microwave", "air_fryer", "electric_kettle",
    "vacuum_cleaner", "robot_vacuum",
    "fan", "air_conditioner", "heater",
    "dehumidifier", "humidifier",
    "monitor", "keyboard", "mouse",
    "beam_projector",
]
#
# 라벨 정의:
#   refrigerator    — 가정용 냉장고 (스탠드형, 양문형, 4도어 등)
#   washer_dryer    — 드럼/통돌이 세탁기, 건조기, 세탁건조 일체형 모두 포함
#   wash_tower      — 세탁기 위에 건조기가 얹힌 상하 결합형 (예: LG 워시타워)
#   rice_cooker     — 가정용 전기밥솥 (압력, IH 포함)
#   microwave       — 전자레인지 (단독 및 오븐 복합형)
#   air_fryer       — 에어프라이어 (오븐형 포함)
#   electric_kettle — 무선 전기포트 / 전기주전자
#   vacuum_cleaner  — 무선 스틱/핸디 청소기 (로봇청소기 제외)
#   robot_vacuum    — 원형 로봇청소기
#   fan             — 선풍기, 서큘레이터, 에어서큘레이터
#   air_conditioner — 스탠드/벽걸이/이동식 에어컨
#   heater          — 전기히터, 온풍기, 세라믹/컨벡션 히터
#   dehumidifier    — 가정용 제습기
#   humidifier      — 가습기 (초음파, 스팀 등)
#   monitor         — PC/게이밍 모니터
#   keyboard        — 유선/무선/기계식 키보드
#   mouse           — 유선/무선/게이밍 마우스
#   beam_projector  — 빔프로젝터 (소형/미니 포함)

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
    ],
    # ── Phase 3 추가 클래스 ────────────────────────────────────────────────────────
    "rice_cooker": [
        "전기밥솥",
        "압력밥솥",
        "IH 전기밥솥",
        "쿠쿠 밥솥",
        "쿠첸 밥솥",
        "소형 전기밥솥",
    ],
    "microwave": [
        "전자레인지",
        "오븐 전자레인지",
        "삼성 전자레인지",
        "LG 전자레인지",
        "소형 전자레인지",
        "전자레인지 정면",
    ],
    "air_fryer": [
        "에어프라이어",
        "에어프라이어 오븐",
        "필립스 에어프라이어",
        "대용량 에어프라이어",
        "소형 에어프라이어",
    ],
    "electric_kettle": [
        "전기포트",
        "전기주전자",
        "무선 전기포트",
        "미니 전기포트",
        "스마트 전기주전자",
    ],
    "vacuum_cleaner": [
        "무선청소기",
        "삼성 무선청소기",
        "LG 무선청소기",
        "스틱청소기",
        "핸디청소기",
    ],
    "robot_vacuum": [
        "로봇청소기",
        "삼성 로봇청소기",
        "LG 로봇청소기",
        "AI 로봇청소기",
    ],
    "fan": [
        "선풍기",
        "서큘레이터",
        "스탠드 선풍기",
        "타워 선풍기",
        "에어서큘레이터",
    ],
    "air_conditioner": [
        "스탠드 에어컨",
        "삼성 에어컨",
        "LG 에어컨",
        "벽걸이 에어컨",
        "이동식 에어컨",
    ],
    "heater": [
        # ☆☆☆ 기존 — 기본 커버
        "전기히터",
        "온풍기",
        "세라믹 히터",
        "컨벡션 히터",
        "스탠드 히터",
        "전기온풍기",
        # ★★★ 추가 — beam_projector 혼동 대응 (형태 다양화)
        "타워형 히터",       # 타워형 (세로 길고 좁음)
        "다이슨 히터",       # 모던 디자인 (빔프로젝터와 외형 명확히 다름)
        "소형 전기히터",     # 소형 박스형 (beam_projector와 경계 강화)
        "라디에이터 히터",   # 방열기형 (전혀 다른 형태, 다양성 확보)
    ],
    "dehumidifier": [
        "제습기",
        "삼성 제습기",
        "LG 제습기",
        "가정용 제습기",
        "이동식 제습기",
    ],
    "humidifier": [
        # ☆☆☆ 기존 — 기본 커버
        "가습기",
        "초음파 가습기",
        "스팀 가습기",
        "LG 퓨리케어 가습기",
        "무드등 가습기",
        # ★★★ 추가 — electric_kettle/rice_cooker 혼동 대응 (형태 다양화)
        "가열식 가습기",     # 가열식 (스팀 발생 노즐 형태 명확)
        "타워형 가습기",     # 타워형 (원통형 전기포트와 구분)
        "원통형 가습기",     # 원통형이지만 가습기 특징 명확한 제품 확보
        "대용량 가습기",     # 대용량 납작형 (밥솥과 형태 차이 강조)
    ],
    "monitor": [
        "컴퓨터 모니터",
        "LG 모니터",
        "삼성 모니터",
        "게이밍 모니터",
        "UHD 모니터",
    ],
    "keyboard": [
        "기계식 키보드",
        "무선 키보드",
        "블루투스 키보드",
        "게이밍 키보드",
    ],
    "mouse": [
        "무선 마우스",
        "게이밍 마우스",
        "로지텍 마우스",
        "블루투스 마우스",
    ],
    "beam_projector": [
        "빔프로젝터",
        "소형 빔프로젝터",
        "미니 빔프로젝터",
        "스마트 빔프로젝터",
        "LG 빔프로젝터",
        "삼성 빔프로젝터",
    ],
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
    # Phase 2
    "refrigerator":   "refrigerator",
    "washer_dryer":   "washing_drying",
    "wash_tower":     "washing_drying",
    # Phase 3 추가
    "rice_cooker":    "kitchen_appliance",
    "microwave":      "kitchen_appliance",
    "air_fryer":      "kitchen_appliance",
    "electric_kettle":"kitchen_appliance",
    "vacuum_cleaner": "vacuum_cleaner",
    "robot_vacuum":   "vacuum_cleaner",
    "fan":            "seasonal_appliance",
    "air_conditioner":"seasonal_appliance",
    "heater":         "seasonal_appliance",
    "dehumidifier":   "dehumidifier_humidifier",
    "humidifier":     "dehumidifier_humidifier",
    "monitor":        "pc_peripheral",
    "keyboard":       "pc_peripheral",
    "mouse":          "pc_peripheral",
    "beam_projector": "beam_projector",
}
