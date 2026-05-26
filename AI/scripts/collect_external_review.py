#!/usr/bin/env python3
"""
외부 테스트 이미지 수집 — 실사용후기 (Naver Image Search API)
Shopping API(카탈로그)가 아닌 Image Search API를 써서
블로그/카페 등 실사용 맥락 이미지를 수집한다.

저장 위치:
  data/external_test/refrigerator/
  data/external_test/washing_drying/

processed/ 이미지와 phash 중복 시 저장 제외.
"""

import os, re, sys, requests, time
from io import BytesIO
from pathlib import Path
from PIL import Image as PILImage
import imagehash
from datetime import datetime
import pandas as pd

project_root = Path(__file__).parent.parent  # AI/
os.chdir(project_root)
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

NAVER_ID     = os.getenv('NAVER_CLIENT_ID', '')
NAVER_SECRET = os.getenv('NAVER_CLIENT_SECRET', '')
if not NAVER_ID or not NAVER_SECRET:
    raise EnvironmentError('.env에 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 없음')

# ── 설정 ──────────────────────────────────────────────────────────────────────
EXT_TEST_DIR    = Path('data/external_test')
PROCESSED_DIR   = Path('data/processed')
LOG_CSV         = Path('data/metadata/external_test_collection_log.csv')
TARGET_PER_SVC  = 80       # 서비스 카테고리당 목표 이미지 수
IMAGES_PER_Q    = 10       # 쿼리당 API 결과 수 — 낮춰서 여러 쿼리에서 분산 수집
MIN_IMG_PX      = 200      # 단변 최소 픽셀
PHASH_THRESH    = 5        # ≤ 이 값이면 중복으로 판단
TIMEOUT         = 20
SLEEP_BETWEEN_Q = 0.3      # API 호출 간격 (초)

# ── 실사용후기 검색 쿼리 (서비스 라벨별) ──────────────────────────────────────
# Shopping API와 달리 Image Search API는 웹 전체 검색 → 블로그/카페 실사용 사진 포함
REVIEW_QUERIES = {
    'refrigerator': [
        '냉장고 실사용후기',
        '냉장고 구매후기',
        '냉장고 설치후기',
        '양문형 냉장고 후기',
        '4도어 냉장고 후기',
        '삼성 냉장고 실사용',
        'LG 냉장고 실사용',
        '비스포크 냉장고 후기',
        '오브제 냉장고 후기',
        '소형 냉장고 후기',
    ],
    'washing_drying': [
        '세탁기 실사용후기',
        '건조기 실사용후기',
        '워시타워 실사용후기',
        '드럼세탁기 구매후기',
        '건조기 구매후기',
        '통돌이 세탁기 후기',
        '워시타워 설치후기',
        '세탁기 건조기 세트 후기',
        '세탁건조기 일체형 후기',
        'LG 워시타워 실사용',
    ],
}

# ── processed/ phash 인덱스 구축 ──────────────────────────────────────────────
print('processed/ phash 인덱스 구축 중...')
processed_hashes = []
for cls_dir in sorted(PROCESSED_DIR.iterdir()):
    if not cls_dir.is_dir():
        continue
    files = list(cls_dir.glob('*.jpg')) + list(cls_dir.glob('*.jpeg')) + list(cls_dir.glob('*.png'))
    for f in files:
        try:
            processed_hashes.append(imagehash.phash(PILImage.open(f).convert('RGB')))
        except Exception:
            pass
print(f'  processed/ {len(processed_hashes)}장 인덱싱 완료')

def is_dup(h, hash_list):
    return any(h - ph <= PHASH_THRESH for ph in hash_list)

# ── Naver Image Search API ────────────────────────────────────────────────────
def fetch_image_items(query, display):
    r = requests.get(
        'https://openapi.naver.com/v1/search/image',
        headers={
            'X-Naver-Client-Id':     NAVER_ID,
            'X-Naver-Client-Secret': NAVER_SECRET,
        },
        params={
            'query':   query,
            'display': display,
            'sort':    'sim',
            'filter':  'large',   # 큰 이미지 우선 — 실사용 사진은 보통 고해상도
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get('items', [])

def download_image(url):
    try:
        resp = requests.get(
            url, timeout=TIMEOUT,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
        )
        if resp.status_code != 200:
            return None
        ct = resp.headers.get('Content-Type', '')
        if 'image' not in ct:
            return None
        img = PILImage.open(BytesIO(resp.content)).convert('RGB')
        w, h = img.size
        if min(w, h) < MIN_IMG_PX:
            return None
        return img
    except Exception:
        return None

# ── 수집 루프 ──────────────────────────────────────────────────────────────────
all_records = []
summary     = {}

for svc_label, queries in REVIEW_QUERIES.items():
    save_dir = EXT_TEST_DIR / svc_label
    save_dir.mkdir(parents=True, exist_ok=True)

    # 이미 저장된 이미지 phash 로드
    existing_files = sorted(
        list(save_dir.glob('*.jpg')) +
        list(save_dir.glob('*.jpeg')) +
        list(save_dir.glob('*.png'))
    )
    ext_hashes = []
    for ef in existing_files:
        try:
            ext_hashes.append(imagehash.phash(PILImage.open(ef).convert('RGB')))
        except Exception:
            pass

    saved   = len(existing_files)
    n_dup   = 0
    n_small = 0
    n_err   = 0

    print(f'\n[{svc_label}] 기존 {saved}장 → 목표 {TARGET_PER_SVC}장')

    for query in queries:
        if saved >= TARGET_PER_SVC:
            break

        print(f'  검색: "{query}"', end='', flush=True)
        try:
            items = fetch_image_items(query, IMAGES_PER_Q)
        except Exception as e:
            print(f' → API 오류: {e}')
            continue
        time.sleep(SLEEP_BETWEEN_Q)

        q_saved = 0
        for item in items:
            if saved >= TARGET_PER_SVC:
                break

            img_url = item.get('link', '')  # Image API: 'link' = 실제 이미지 URL
            if not img_url:
                continue

            img = download_image(img_url)
            if img is None:
                n_err += 1
                continue

            h = imagehash.phash(img)

            if is_dup(h, processed_hashes) or is_dup(h, ext_hashes):
                n_dup += 1
                continue

            fname     = f'ext_{saved:04d}.jpg'
            save_path = save_dir / fname
            img.save(save_path, 'JPEG', quality=95)
            ext_hashes.append(h)
            saved    += 1
            q_saved  += 1

            all_records.append({
                'service_label': svc_label,
                'query':         query,
                'image_url':     img_url,
                'saved_path':    str(save_path),
                'width':         img.size[0],
                'height':        img.size[1],
                'collected_at':  datetime.now().isoformat(timespec='seconds'),
            })

        print(f' → {q_saved}장 저장  (누적 {saved}/{TARGET_PER_SVC}장, 중복 {n_dup}, 오류/소형 {n_err})')

    summary[svc_label] = saved
    print(f'[{svc_label}] 완료: {saved}장')

# ── 수집 로그 저장 ─────────────────────────────────────────────────────────────
if all_records:
    new_df = pd.DataFrame(all_records)
    if LOG_CSV.exists():
        old_df = pd.read_csv(LOG_CSV)
        combined = pd.concat([old_df, new_df], ignore_index=True)
        combined.drop_duplicates(subset=['image_url'], keep='last', inplace=True)
    else:
        combined = new_df
    combined.to_csv(LOG_CSV, index=False, encoding='utf-8-sig')
    print(f'\n수집 로그: {LOG_CSV}  ({len(combined)}건)')

print('\n=== 수집 완료 ===')
for svc, cnt in summary.items():
    print(f'  {svc}: {cnt}장')
print('\n다음 단계: notebooks/06_external_test.ipynb 실행')
