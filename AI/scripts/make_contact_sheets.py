import os
import math
from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def make_grid(class_name, input_dir, output_path, cols=10, rows=10):
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        images.extend(list(Path(input_dir).rglob(ext)))
    images = sorted(images)[:cols*rows]

    if not images:
        return False

    fig, axes = plt.subplots(rows, cols, figsize=(15, 15))
    axes = axes.flatten()

    for i, ax in enumerate(axes):
        if i < len(images):
            try:
                img = Image.open(images[i]).convert('RGB')
                img.thumbnail((200, 200))
                ax.imshow(np.array(img))
                ax.set_title(f"{i}", fontsize=8)
            except:
                ax.text(0.5, 0.5, "ERR", ha='center')
        ax.axis('off')

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return True

if __name__ == "__main__":
    classes = [
        'mouse', 'rice_cooker', 'microwave', 'air_fryer', 'electric_kettle',
        'vacuum_cleaner', 'robot_vacuum', 'fan', 'air_conditioner', 'heater',
        'dehumidifier', 'humidifier', 'monitor', 'keyboard', 'beam_projector'
    ]
    os.makedirs('data/contact_sheets', exist_ok=True)
    for cls in classes:
        print(f"Generating sheet for {cls}...")
        make_grid(cls, f'data/review_temp/{cls}', f'data/contact_sheets/{cls}.png')
