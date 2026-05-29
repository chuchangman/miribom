"""
범용 이미지 수집 스크립트 (Naver Shopping API → data/staging)
11_collect_universal.ipynb 와 동일한 로직. jupyter 없이 직접 실행 가능.

사용법:
    python scripts/run_collection.py refrigerator washer_dryer wash_tower

    # 단일 클래스
    python scripts/run_collection.py rice_cooker

    # 지원 클래스 목록
    python scripts/run_collection.py --list
"""

import os
import sys
import re
import base64
import argparse
import requests
from io import BytesIO
from pathlib import Path
from datetime import datetime

import pandas as pd
from PIL import Image as PILImage

# ── 프로젝트 루트 설정 ────────────────────────────────────────────────────────────
project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except ImportError:
    # dotenv 없으면 .env를 직접 파싱
    env_path = project_root / '.env'
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())

NAVER_ID     = os.getenv('NAVER_CLIENT_ID', '')
NAVER_SECRET = os.getenv('NAVER_CLIENT_SECRET', '')

IMAGES_PER_QUERY = 100
MIN_IMG_SIZE     = 150


# ── API / 다운로드 함수 ──────────────────────────────────────────────────────────

def fetch_items(query: str, display: int) -> list:
    r = requests.get(
        'https://openapi.naver.com/v1/search/shop.json',
        headers={
            'X-Naver-Client-Id':     NAVER_ID,
            'X-Naver-Client-Secret': NAVER_SECRET,
        },
        params={'query': query, 'display': display, 'start': 1},
        timeout=config.DOWNLOAD_TIMEOUT,
    )
    r.raise_for_status()
    return r.json().get('items', [])


def download_and_validate(url: str, save_path: str, min_px: int):
    try:
        r = requests.get(url, timeout=config.DOWNLOAD_TIMEOUT)
        if r.status_code != 200 or 'image' not in r.headers.get('Content-Type', ''):
            return False, 0, 0
        img = PILImage.open(BytesIO(r.content)).convert('RGB')
        w, h = img.size
        if w < min_px or h < min_px:
            return False, w, h
        img.save(save_path, 'JPEG', quality=95)
        return True, w, h
    except Exception:
        return False, 0, 0


# ── HTML 생성 ────────────────────────────────────────────────────────────────────

def img_b64(fpath, px=220) -> str:
    try:
        img = PILImage.open(str(fpath)).convert('RGB')
        img.thumbnail((px, px), PILImage.LANCZOS)
        buf = BytesIO()
        img.save(buf, 'JPEG', quality=82)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return ''


CSS = (
    '<style>'
    '*{box-sizing:border-box;margin:0;padding:0}'
    'body{font-family:sans-serif;background:#0f0f0f;color:#ccc;padding:16px}'
    'h1{color:#fff;margin-bottom:4px;font-size:22px}'
    '.sub{color:#888;font-size:12px;margin-bottom:14px}'
    '.warn{background:#2a1010;border:2px solid #c0392b;border-radius:6px;'
    'padding:12px 16px;margin-bottom:18px;font-size:13px;line-height:1.9}'
    '.warn b{color:#e74c3c}'
    '.qh{background:#1a2a3a;color:#7ec8e3;font-size:13px;font-weight:bold;'
    'padding:7px 12px;border-radius:6px 6px 0 0;'
    'border-left:4px solid #7ec8e3;margin-top:18px}'
    '.grid{display:flex;flex-wrap:wrap;gap:5px;padding:8px;'
    'background:#161616;border-radius:0 0 6px 6px}'
    '.card{width:140px;background:#1e1e1e;border-radius:3px;'
    'overflow:hidden;border:1px solid #2a2a2a;position:relative}'
    '.card:hover{border-color:#7ec8e3}'
    '.card img{width:140px;height:120px;object-fit:contain;'
    'background:#0a0a0a;display:block}'
    '.noimg{width:140px;height:120px;display:flex;align-items:center;'
    'justify-content:center;color:#444;font-size:11px}'
    '.idx{position:absolute;top:2px;left:2px;background:rgba(0,0,0,.75);'
    'color:#fff;padding:1px 5px;border-radius:3px;font-size:10px}'
    '.m{padding:4px;font-size:8px;color:#555;word-break:break-all;line-height:1.4}'
    '</style>'
)

WARN_HTML = (
    '<div class="warn">'
    '<b>검수 기준 — staging 폴더에서 직접 파일 경로 복사</b><br>'
    '✅ 제품 전체가 찍힌 이미지 (정면·측면·비스듬 OK)<br>'
    '✅ 단일 제품, 배경 있어도 무관<br>'
    '❌ 여러 제품 동시 노출 (세트 사진)<br>'
    '❌ 광고 배너 / 텍스트 도배 / 사람이 주체<br>'
    '❌ 다른 클래스 제품이 메인<br>'
    '❌ 상품 일부만 잘린 이미지 (partial crop)<br>'
    '<br>이미지 경로를 <b>08_approve_staging.ipynb → APPROVED 리스트</b>에 붙여넣으세요.'
    '</div>'
)


def generate_html(class_name: str, staging_dir: str, html_out: str):
    staging_root = Path(staging_dir)
    by_q = {}
    for d in sorted(staging_root.iterdir()):
        if d.is_dir():
            fs = sorted(list(d.glob('*.jpg')) + list(d.glob('*.jpeg')) + list(d.glob('*.png')))
            if fs:
                by_q[d.name] = fs

    total_img = sum(len(v) for v in by_q.values())
    print(f'  HTML 생성 중 ({total_img}장)...')

    parts = []
    global_i = 0
    for slug, files in by_q.items():
        cards = []
        for fp in files:
            b = img_b64(fp)
            rel = str(fp).replace('\\', '/')
            img_tag = (
                f'<img src="data:image/jpeg;base64,{b}" loading="lazy">'
                if b else '<div class="noimg">ERR</div>'
            )
            cards.append(
                f'<div class="card">'
                f'<div class="idx">#{global_i}</div>'
                f'{img_tag}'
                f'<div class="m">{fp.name}<br>'
                f'<span style="color:#333">{slug}</span></div>'
                f'</div>'
            )
            global_i += 1
        parts.append(
            f'<div class="qh">{slug} '
            f'<span style="color:#888;font-size:11px">({len(files)}장)</span></div>'
            f'<div class="grid">{"".join(cards)}</div>'
        )

    html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<title>{class_name} staging review</title>'
        + CSS + '</head><body>'
        f'<h1>{class_name} Staging 검수</h1>'
        f'<div class="sub">총 {total_img}장 | Naver Shopping API | '
        f'approved 이후 08_approve_staging.ipynb 실행</div>'
        + WARN_HTML + ''.join(parts) + '</body></html>'
    )

    with open(html_out, 'w', encoding='utf-8') as fh:
        fh.write(html)

    size_kb = os.path.getsize(html_out) // 1024
    print(f'  HTML 저장: {html_out}  ({size_kb} KB)')
    return total_img


# ── 클래스별 수집 메인 로직 ──────────────────────────────────────────────────────

def collect_class(class_name: str) -> dict:
    print(f'\n{"="*60}')
    print(f'수집 시작: {class_name}')
    print(f'{"="*60}')

    queries     = config.NAVER_SEARCH_QUERIES[class_name]
    staging_dir = os.path.join('data', 'staging', class_name)
    metadata_csv = os.path.join(config.METADATA_DIR, f'{class_name}_staging_metadata.csv')
    html_out    = os.path.join(config.METADATA_DIR, f'{class_name}_staging_review.html')

    print(f'쿼리 {len(queries)}개 | 쿼리당 최대 {IMAGES_PER_QUERY}장 | 총 최대 {len(queries)*IMAGES_PER_QUERY}장')
    os.makedirs(config.METADATA_DIR, exist_ok=True)

    records = []
    n_saved = n_skip = n_exist = 0
    n_error_img = 0

    for q_i, query in enumerate(queries, 1):
        slug = re.sub(r'[^\w가-힣]', '_', query)
        qdir = os.path.join(staging_dir, slug)
        os.makedirs(qdir, exist_ok=True)

        try:
            items = fetch_items(query, IMAGES_PER_QUERY)
        except Exception as e:
            print(f'  [{q_i:2d}/{len(queries)}] {query}: API 오류 -> {e}')
            continue

        saved_q = exist_q = skip_q = 0

        for idx, item in enumerate(items):
            img_url = item.get('image', '')
            if not img_url:
                skip_q += 1
                continue

            fname     = f'stg_{idx:04d}.jpg'
            save_path = os.path.join(qdir, fname)
            title_clean = re.sub(r'<[^>]+>', '', item.get('title', ''))

            if os.path.exists(save_path):
                try:
                    img = PILImage.open(save_path)
                    w, h = img.size
                except Exception:
                    w, h = 0, 0
                    n_error_img += 1
                records.append({
                    'query': query, 'title': title_clean[:120],
                    'link': item.get('link', ''), 'image_url': img_url,
                    'saved_path': save_path, 'width': w, 'height': h,
                    'status': 'staged',
                    'collected_at': datetime.now().isoformat(timespec='seconds'),
                })
                exist_q += 1; n_exist += 1
                continue

            ok, w, h = download_and_validate(img_url, save_path, MIN_IMG_SIZE)
            if ok:
                records.append({
                    'query': query, 'title': title_clean[:120],
                    'link': item.get('link', ''), 'image_url': img_url,
                    'saved_path': save_path, 'width': w, 'height': h,
                    'status': 'staged',
                    'collected_at': datetime.now().isoformat(timespec='seconds'),
                })
                saved_q += 1; n_saved += 1
            else:
                skip_q += 1; n_skip += 1

        print(f'  [{q_i:2d}/{len(queries)}] {query:30s} -> 저장 {saved_q:3d}장 | 기존 {exist_q:3d}장 | 스킵 {skip_q:3d}장')

    print(f'\n  수집 완료: 신규 {n_saved}장 | 기존유지 {n_exist}장 | 스킵 {n_skip}장')

    # 메타데이터 저장
    new_df = pd.DataFrame(records)
    if os.path.exists(metadata_csv):
        old_df = pd.read_csv(metadata_csv, encoding='utf-8-sig')
        combined = pd.concat([old_df, new_df], ignore_index=True)
        combined.drop_duplicates(subset=['image_url'], keep='last', inplace=True)
    else:
        combined = new_df
    combined.to_csv(metadata_csv, index=False, encoding='utf-8-sig')
    print(f'  메타데이터: {metadata_csv}  ({len(combined)}행)')

    # staging 현황
    total_staged = 0
    for slug in sorted(os.listdir(staging_dir)):
        d = os.path.join(staging_dir, slug)
        if not os.path.isdir(d):
            continue
        imgs = [f for f in os.listdir(d) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        total_staged += len(imgs)

    # HTML 생성
    total_html = generate_html(class_name, staging_dir, html_out)

    return {
        'class_name':    class_name,
        'total_staged':  total_staged,
        'n_saved':       n_saved,
        'n_exist':       n_exist,
        'n_skip':        n_skip,
        'n_error_img':   n_error_img,
        'metadata_csv':  metadata_csv,
        'html_out':      html_out,
    }


# ── 엔트리포인트 ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Naver Shopping 이미지 수집')
    parser.add_argument('classes', nargs='*', help='수집할 클래스명 (복수 가능)')
    parser.add_argument('--list', action='store_true', help='지원 클래스 목록 출력')
    args = parser.parse_args()

    if args.list:
        print('지원 클래스:')
        for k in config.NAVER_SEARCH_QUERIES:
            print(f'  {k}')
        return

    if not NAVER_ID or NAVER_ID == '여기에_Client_ID_입력':
        print('[오류] NAVER_CLIENT_ID 가 설정되지 않았습니다.')
        print('       .env 파일에 실제 키를 입력하세요:')
        print('       NAVER_CLIENT_ID=실제키값')
        print('       NAVER_CLIENT_SECRET=실제키값')
        sys.exit(1)

    target_classes = args.classes if args.classes else list(config.NAVER_SEARCH_QUERIES.keys())

    invalid = [c for c in target_classes if c not in config.NAVER_SEARCH_QUERIES]
    if invalid:
        print(f'[오류] 알 수 없는 클래스: {invalid}')
        sys.exit(1)

    print(f'수집 대상: {target_classes}')
    results = []
    for cls in target_classes:
        result = collect_class(cls)
        results.append(result)

    # 최종 요약
    print('\n' + '='*60)
    print('수집 완료 요약')
    print('='*60)
    print(f'{"클래스":<20} {"staging":>8} {"신규":>6} {"기존":>6} {"스킵":>6} {"오류":>6}')
    print('-'*60)
    for r in results:
        print(f'{r["class_name"]:<20} {r["total_staged"]:>8} {r["n_saved"]:>6} '
              f'{r["n_exist"]:>6} {r["n_skip"]:>6} {r["n_error_img"]:>6}')

    print()
    print('검수용 HTML 경로:')
    for r in results:
        print(f'  {r["class_name"]:20s}: {r["html_out"]}')

    print()
    print('다음 단계:')
    print('  1. 위 HTML 파일을 브라우저에서 열어 이미지 검수')
    print('  2. 08_approve_staging.ipynb 열기')
    print('  3. CLASS_NAME 설정 → APPROVED 리스트 작성 → Cell 6 실행')


if __name__ == '__main__':
    main()
