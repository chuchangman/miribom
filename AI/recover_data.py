import os
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from PIL import Image
from io import BytesIO

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent
OS_SEP = os.path.sep

def recover_from_csv(csv_path, class_name):
    print(f"\nRecovering {class_name} from {csv_path}...")
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    # Filter only approved ones
    approved_df = df[df['status'] == 'approved'].copy()
    print(f"Found {len(approved_df)} approved images.")

    target_dir = os.path.join('data', 'processed', class_name)
    os.makedirs(target_dir, exist_ok=True)

    success_count = 0
    for idx, row in tqdm(approved_df.iterrows(), total=len(approved_df)):
        url = row['image_url']
        # Extract filename from saved_path in CSV
        # Example saved_path: data\processed\refrigerator\naver_0441.jpg
        saved_path_str = row['saved_path']
        fname = os.path.basename(saved_path_str.replace('\\', '/'))

        save_path = os.path.join(target_dir, fname)

        if os.path.exists(save_path):
            success_count += 1
            continue

        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert('RGB')
                img.save(save_path, 'JPEG', quality=95)
                success_count += 1
        except Exception as e:
            # print(f"Failed to download {url}: {e}")
            pass

    print(f"Finished {class_name}: {success_count}/{len(approved_df)} recovered.")

if __name__ == "__main__":
    metadata_dir = os.path.join('data', 'metadata')
    classes = ['refrigerator', 'washer_dryer', 'wash_tower']

    for cls in classes:
        csv_path = os.path.join(metadata_dir, f'{cls}_staging_metadata.csv')
        recover_from_csv(csv_path, cls)
