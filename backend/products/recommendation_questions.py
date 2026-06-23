"""
카테고리별 계층형 질문 정의.

각 질문은 type: 'single' 을 가지며,
옵션마다 follow_up 으로 하위 질문을 중첩할 수 있습니다.
"""

CATEGORY_QUESTIONS = {

    # ── 세탁·건조 ────────────────────────────────────────────────
    1: [
        {
            "id": "product_type",
            "text": "어떤 제품이 필요하신가요?",
            "type": "single",
            "options": [
                {
                    "value": "washer",
                    "label": "세탁기",
                    "follow_up": [
                        {
                            "id": "washer_type",
                            "text": "세탁 방식을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "drum", "label": "드럼"},
                                {"value": "agitator", "label": "통돌이"},
                            ],
                        },
                        {
                            "id": "washer_capacity",
                            "text": "용량을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "small", "label": "소형 (~8kg)"},
                                {"value": "medium", "label": "중형 (9~12kg)"},
                                {"value": "large", "label": "대형 (13kg 이상)"},
                            ],
                        },
                    ],
                },
                {
                    "value": "dryer",
                    "label": "건조기",
                    "follow_up": [
                        {
                            "id": "dryer_type",
                            "text": "건조 방식을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "heat_pump", "label": "히트펌프 (저온·절전)"},
                                {"value": "condenser", "label": "콘덴서 (일반)"},
                            ],
                        },
                        {
                            "id": "dryer_capacity",
                            "text": "용량을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "small", "label": "소형 (~8kg)"},
                                {"value": "medium", "label": "중형 (9~12kg)"},
                                {"value": "large", "label": "대형 (13kg 이상)"},
                            ],
                        },
                    ],
                },
                {
                    "value": "combo",
                    "label": "세탁건조 일체형",
                    "follow_up": [
                        {
                            "id": "combo_capacity",
                            "text": "용량을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "small", "label": "소형 (~8kg)"},
                                {"value": "medium", "label": "중형 (9~12kg)"},
                                {"value": "large", "label": "대형 (13kg 이상)"},
                            ],
                        },
                    ],
                },
            ],
        },
    ],

    # ── 냉장고 ───────────────────────────────────────────────────
    2: [
        {
            "id": "fridge_type",
            "text": "어떤 타입의 냉장고를 원하시나요?",
            "type": "single",
            "options": [
                {
                    "value": "standard",
                    "label": "일반형",
                    "follow_up": [
                        {
                            "id": "family_size",
                            "text": "가족 인원을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "1", "label": "1인"},
                                {"value": "2", "label": "2인"},
                                {"value": "3_4", "label": "3~4인"},
                                {"value": "5+", "label": "5인 이상"},
                            ],
                        },
                    ],
                },
                {
                    "value": "side_by_side",
                    "label": "양문형",
                    "follow_up": [
                        {
                            "id": "family_size",
                            "text": "가족 인원을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "2", "label": "2인"},
                                {"value": "3_4", "label": "3~4인"},
                                {"value": "5+", "label": "5인 이상"},
                            ],
                        },
                    ],
                },
                {
                    "value": "french_door",
                    "label": "프렌치도어",
                    "follow_up": [
                        {
                            "id": "family_size",
                            "text": "가족 인원을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "2", "label": "2인"},
                                {"value": "3_4", "label": "3~4인"},
                                {"value": "5+", "label": "5인 이상"},
                            ],
                        },
                    ],
                },
                {
                    "value": "mini",
                    "label": "미니(소형)",
                    "follow_up": [
                        {
                            "id": "mini_purpose",
                            "text": "주 사용 용도를 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "oneroom", "label": "원룸용"},
                                {"value": "office", "label": "사무실용"},
                                {"value": "sub", "label": "보조 냉장고"},
                            ],
                        },
                    ],
                },
            ],
        },
    ],

    # ── 주방소가전 ───────────────────────────────────────────────
    3: [
        {
            "id": "kitchen_products",
            "text": "필요한 제품을 선택해주세요",
            "type": "single",
            "options": [
                {
                    "value": "microwave",
                    "label": "전자레인지",
                    "follow_up": [
                        {
                            "id": "microwave_type",
                            "text": "전자레인지 타입을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "basic", "label": "단순 전자레인지"},
                                {"value": "oven", "label": "오븐 겸용"},
                                {"value": "light_wave", "label": "광파오븐"},
                            ],
                        },
                    ],
                },
                {
                    "value": "air_fryer",
                    "label": "에어프라이어",
                    "follow_up": [
                        {
                            "id": "air_fryer_capacity",
                            "text": "용량을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "small", "label": "소형 (1~2인)"},
                                {"value": "medium", "label": "중형 (3~4인)"},
                                {"value": "large", "label": "대형 (5인 이상)"},
                            ],
                        },
                    ],
                },
                {
                    "value": "coffee",
                    "label": "커피머신",
                    "follow_up": [
                        {
                            "id": "coffee_type",
                            "text": "커피머신 타입을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "capsule", "label": "캡슐형"},
                                {"value": "auto", "label": "원두 전자동"},
                                {"value": "semi_auto", "label": "원두 반자동"},
                                {"value": "drip", "label": "드립"},
                            ],
                        },
                    ],
                },
                {
                    "value": "rice_cooker",
                    "label": "밥솥",
                    "follow_up": [
                        {
                            "id": "rice_cooker_capacity",
                            "text": "용량을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "small", "label": "소형 (3인 이하)"},
                                {"value": "medium", "label": "중형 (4~6인)"},
                                {"value": "large", "label": "대형 (7인 이상)"},
                            ],
                        },
                    ],
                },
                {
                    "value": "blender",
                    "label": "믹서기·블렌더",
                    "follow_up": [
                        {
                            "id": "blender_type",
                            "text": "타입을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "blender", "label": "블렌더"},
                                {"value": "juicer", "label": "주서기"},
                                {"value": "mixer", "label": "일반 믹서기"},
                            ],
                        },
                    ],
                },
            ],
        },
    ],

    # ── 청소기 ───────────────────────────────────────────────────
    4: [
        {
            "id": "vacuum_type",
            "text": "어떤 타입의 청소기를 원하시나요?",
            "type": "single",
            "options": [
                {
                    "value": "wireless",
                    "label": "무선 청소기",
                    "follow_up": [
                        {
                            "id": "battery",
                            "text": "배터리 지속 시간이 중요한가요?",
                            "type": "single",
                            "options": [
                                {"value": "important", "label": "중요 (45분 이상)"},
                                {"value": "normal", "label": "보통 (30분 내외)"},
                            ],
                        },
                        {
                            "id": "pet",
                            "text": "반려동물이 있으신가요?",
                            "type": "single",
                            "options": [
                                {"value": "yes", "label": "있음"},
                                {"value": "no", "label": "없음"},
                            ],
                        },
                    ],
                },
                {
                    "value": "robot",
                    "label": "로봇청소기",
                    "follow_up": [
                        {
                            "id": "mop",
                            "text": "물걸레 기능이 필요하신가요?",
                            "type": "single",
                            "options": [
                                {"value": "yes", "label": "필요"},
                                {"value": "no", "label": "불필요"},
                            ],
                        },
                        {
                            "id": "auto_empty",
                            "text": "자동 먼지 비움 기능이 필요하신가요?",
                            "type": "single",
                            "options": [
                                {"value": "yes", "label": "필요"},
                                {"value": "no", "label": "불필요"},
                            ],
                        },
                    ],
                },
                {
                    "value": "wired",
                    "label": "유선 청소기",
                    "follow_up": [
                        {
                            "id": "wired_feature",
                            "text": "필요한 기능을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "pet", "label": "반려동물 털 전용"},
                                {"value": "mop", "label": "물걸레 겸용"},
                                {"value": "standard", "label": "일반"},
                            ],
                        },
                    ],
                },
                {
                    "value": "handy",
                    "label": "핸디형(소형)",
                    "follow_up": [],
                },
            ],
        },
    ],

    # ── 계절가전 ─────────────────────────────────────────────────
    5: [
        {
            "id": "seasonal_type",
            "text": "어떤 제품이 필요하신가요?",
            "type": "single",
            "options": [
                {
                    "value": "aircon",
                    "label": "에어컨",
                    "follow_up": [
                        {
                            "id": "aircon_install",
                            "text": "설치 타입을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "wall", "label": "벽걸이형"},
                                {"value": "stand", "label": "스탠드형"},
                                {"value": "portable", "label": "이동형 (설치 불필요)"},
                                {"value": "window", "label": "창문형"},
                            ],
                        },
                    ],
                },
                {
                    "value": "fan",
                    "label": "선풍기",
                    "follow_up": [
                        {
                            "id": "fan_type",
                            "text": "타입을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "stand", "label": "스탠드형"},
                                {"value": "circulator", "label": "서큘레이터"},
                                {"value": "desk", "label": "탁상형"},
                            ],
                        },
                    ],
                },
                {
                    "value": "heater",
                    "label": "히터·온풍기",
                    "follow_up": [
                        {
                            "id": "heater_type",
                            "text": "타입을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "fan_heater", "label": "온풍기"},
                                {"value": "electric", "label": "전기히터"},
                                {"value": "radiator", "label": "라디에이터"},
                                {"value": "panel", "label": "패널히터"},
                            ],
                        },
                    ],
                },
            ],
        },
    ],

    # ── 제습기·가습기 ────────────────────────────────────────────
    6: [
        {
            "id": "humidifier_type",
            "text": "어떤 제품이 필요하신가요?",
            "type": "single",
            "options": [
                {
                    "value": "dehumidifier",
                    "label": "제습기",
                    "follow_up": [
                        {
                            "id": "dehumidifier_space",
                            "text": "사용 공간 크기를 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "small", "label": "소형 (원룸·침실)"},
                                {"value": "medium", "label": "중형 (거실)"},
                                {"value": "large", "label": "대형 (넓은 공간)"},
                            ],
                        },
                    ],
                },
                {
                    "value": "humidifier",
                    "label": "가습기",
                    "follow_up": [
                        {
                            "id": "humidifier_method",
                            "text": "가습 방식을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "ultrasonic", "label": "초음파식"},
                                {"value": "heated", "label": "가열식"},
                                {"value": "complex", "label": "복합식"},
                            ],
                        },
                        {
                            "id": "humidifier_space",
                            "text": "주로 사용할 공간을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "bedroom", "label": "침실"},
                                {"value": "living", "label": "거실"},
                                {"value": "office", "label": "사무실"},
                            ],
                        },
                    ],
                },
                {
                    "value": "both",
                    "label": "둘 다 필요",
                    "follow_up": [
                        {
                            "id": "both_priority",
                            "text": "더 급한 것은 무엇인가요?",
                            "type": "single",
                            "options": [
                                {"value": "dehumidifier", "label": "제습기가 더 급함"},
                                {"value": "humidifier", "label": "가습기가 더 급함"},
                            ],
                        },
                    ],
                },
            ],
        },
    ],

    # ── PC주변기기 ───────────────────────────────────────────────
    7: [
        {
            "id": "pc_products",
            "text": "필요한 제품을 선택해주세요",
            "type": "single",
            "options": [
                {
                    "value": "monitor",
                    "label": "모니터",
                    "follow_up": [
                        {
                            "id": "monitor_purpose",
                            "text": "주 사용 목적을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "office", "label": "업무·문서"},
                                {"value": "gaming", "label": "게임"},
                                {"value": "editing", "label": "영상·사진 편집"},
                                {"value": "media", "label": "영화·미디어"},
                            ],
                        },
                        {
                            "id": "monitor_size",
                            "text": "화면 크기를 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "small", "label": "24인치 이하"},
                                {"value": "medium", "label": "27인치"},
                                {"value": "large", "label": "32인치 이상"},
                            ],
                        },
                    ],
                },
                {
                    "value": "keyboard",
                    "label": "키보드",
                    "follow_up": [
                        {
                            "id": "keyboard_type",
                            "text": "키보드 타입을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "membrane", "label": "멤브레인"},
                                {"value": "mechanical", "label": "기계식"},
                                {"value": "wireless", "label": "무선"},
                            ],
                        },
                    ],
                },
                {
                    "value": "mouse",
                    "label": "마우스",
                    "follow_up": [
                        {
                            "id": "mouse_type",
                            "text": "마우스 타입을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "wired", "label": "유선"},
                                {"value": "wireless", "label": "무선"},
                                {"value": "vertical", "label": "버티컬 (손목 보호)"},
                            ],
                        },
                    ],
                },
                {
                    "value": "headset",
                    "label": "헤드셋",
                    "follow_up": [
                        {
                            "id": "headset_purpose",
                            "text": "주 사용 목적을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "gaming", "label": "게이밍"},
                                {"value": "conference", "label": "화상회의"},
                                {"value": "music", "label": "음악감상"},
                            ],
                        },
                    ],
                },
                {
                    "value": "webcam",
                    "label": "웹캠",
                    "follow_up": [
                        {
                            "id": "webcam_resolution",
                            "text": "해상도를 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "fhd", "label": "FHD (1080p)"},
                                {"value": "4k", "label": "4K"},
                            ],
                        },
                    ],
                },
            ],
        },
    ],

    # ── 빔프로젝터 ───────────────────────────────────────────────
    8: [
        {
            "id": "projector_purpose",
            "text": "주 사용 목적을 선택해주세요",
            "type": "single",
            "options": [
                {
                    "value": "home_theater",
                    "label": "영화감상·홈시어터",
                    "follow_up": [
                        {
                            "id": "projector_env",
                            "text": "설치 환경을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "wall", "label": "벽면 투사"},
                                {"value": "screen", "label": "스크린 보유"},
                                {"value": "undecided", "label": "미정"},
                            ],
                        },
                        {
                            "id": "projector_light",
                            "text": "사용 환경 밝기를 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "dark", "label": "암실 가능"},
                                {"value": "dim", "label": "약간 어두운 환경"},
                                {"value": "bright", "label": "밝은 환경"},
                            ],
                        },
                    ],
                },
                {
                    "value": "gaming",
                    "label": "게임",
                    "follow_up": [
                        {
                            "id": "projector_env",
                            "text": "설치 환경을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "wall", "label": "벽면 투사"},
                                {"value": "screen", "label": "스크린 보유"},
                                {"value": "undecided", "label": "미정"},
                            ],
                        },
                    ],
                },
                {
                    "value": "presentation",
                    "label": "업무 발표",
                    "follow_up": [
                        {
                            "id": "projector_portability",
                            "text": "휴대성이 중요한가요?",
                            "type": "single",
                            "options": [
                                {"value": "portable", "label": "휴대용 (소형)"},
                                {"value": "fixed", "label": "고정형"},
                            ],
                        },
                    ],
                },
                {
                    "value": "multipurpose",
                    "label": "다용도",
                    "follow_up": [
                        {
                            "id": "projector_env",
                            "text": "설치 환경을 선택해주세요",
                            "type": "single",
                            "options": [
                                {"value": "wall", "label": "벽면 투사"},
                                {"value": "screen", "label": "스크린 보유"},
                                {"value": "undecided", "label": "미정"},
                            ],
                        },
                    ],
                },
            ],
        },
    ],
}
