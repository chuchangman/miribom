import os
import sys
import json
import time
import pandas as pd
from pathlib import Path
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from tqdm import tqdm

# Project root setup
project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import config

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    print("[Error] GOOGLE_API_KEY not found in .env")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)
# models/gemini-2.0-flash-lite usually has 30 RPM on free tier (double of flash)
MODEL_NAME = 'gemini-2.0-flash-lite'
model = genai.GenerativeModel(MODEL_NAME)

PROMPT_TEMPLATE = """Identify if the image is a high-quality, representative photo of a '{class_label}'.
Criteria for OK: Product is subject, mostly in frame, no heavy text.
NG: Wrong product, partial crop, text/ads, human subject.
Respond ONLY JSON: {{"status": "OK"|"NG"|"AMBIGUOUS", "reason": "code"}}
"""

def review_image(image_path, class_label):
    try:
        img = Image.open(image_path).convert('RGB')
        img.thumbnail((300, 300)) # Smaller thumbnail for speed
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_data = {"mime_type": "image/jpeg", "data": buffered.getvalue()}

        prompt = PROMPT_TEMPLATE.format(class_label=class_label)
        response = model.generate_content([prompt, img_data])
        text = response.text.strip()

        if text.startswith('```json'): text = text[7:-3].strip()
        elif text.startswith('```'): text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        return {"status": "ERROR", "note": str(e)}

def run_review(class_name, target_ok=250):
    staging_dir = Path('data/staging') / class_name
    output_csv = Path('data/metadata') / f'gemini_{class_name}_review.csv'

    if not staging_dir.exists(): return

    # Load existing
    results = []
    ok_count = 0
    if output_csv.exists():
        try:
            df = pd.read_csv(output_csv)
            results = df.to_dict('records')
            ok_count = len(df[df['status'] == 'OK'])
        except: pass

    processed_paths = {r['image_path'] for r in results if r['status'] != 'ERROR'}

    # Find all
    all_paths = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        all_paths.extend(list(staging_dir.rglob(ext)))
    all_paths = sorted(all_paths)

    print(f"\nReviewing {class_name}: OK count={ok_count}/{target_ok}")

    for path in tqdm(all_paths):
        path_str = str(path).replace('\\', '/')
        if path_str in processed_paths: continue
        if ok_count >= target_ok: break

        res = review_image(path, class_name)
        res['image_path'] = path_str
        results.append(res)

        if res['status'] == 'OK': ok_count += 1

        # Free tier delay: 30 RPM -> 2 sec/req. Let's use 2.5s for safety.
        time.sleep(2.5)

        # Save every 5 OKs or 20 total
        if len(results) % 20 == 0:
            pd.DataFrame(results).to_csv(output_csv, index=False, encoding='utf-8-sig')

    pd.DataFrame(results).to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"Saved {class_name} review. OK: {ok_count}")

if __name__ == "__main__":
    target_classes = [
        'mouse', 'rice_cooker', 'microwave', 'air_fryer', 'electric_kettle',
        'vacuum_cleaner', 'robot_vacuum', 'fan', 'air_conditioner', 'heater',
        'dehumidifier', 'humidifier', 'monitor', 'keyboard', 'beam_projector'
    ]
    for cls in target_classes:
        run_review(cls, target_ok=250)
