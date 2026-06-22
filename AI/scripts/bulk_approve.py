import os
import shutil
from pathlib import Path

def approve_batch(class_name, limit=200):
    src_dir = Path(f'data/review_temp/{class_name}')
    dst_dir = Path(f'data/processed/{class_name}')
    dst_dir.mkdir(parents=True, exist_ok=True)

    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        images.extend(list(src_dir.rglob(ext)))
    images = sorted(images)[:limit]

    # Get current max index in processed
    naver_nums = [
        int(f.stem[6:]) for f in dst_dir.iterdir()
        if f.name.startswith('naver_') and f.stem[6:].isdigit()
    ]
    start_idx = (max(naver_nums) + 1) if naver_nums else 0

    count = 0
    for i, src in enumerate(images):
        dst = dst_dir / f"naver_{start_idx + i:04d}.jpg"
        try:
            shutil.copy2(src, dst)
            count += 1
        except Exception as e:
            print(f"Error copying {src}: {e}")

    return count

if __name__ == "__main__":
    classes = [
        'mouse', 'rice_cooker', 'microwave', 'air_fryer', 'electric_kettle',
        'vacuum_cleaner', 'robot_vacuum', 'fan', 'air_conditioner', 'heater',
        'dehumidifier', 'humidifier', 'monitor', 'keyboard', 'beam_projector'
    ]
    for cls in classes:
        c = approve_batch(cls)
        print(f"Approved {c} images for {cls}")
