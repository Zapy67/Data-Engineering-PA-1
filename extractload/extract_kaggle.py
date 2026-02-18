import os
import pandas as pd
import kagglehub
from config.settings import Config

def extract_solar_data_kaggle():
    Config.ensure_directories()
    print("\n--- Starting Public Dataset Extraction (Kaggle) ---")

    datasets = {
        'pakistan-electricity-generation-by-solar-kaggle': 'ahmadwaleed1/pakistan-electricity-generation-by-solar',
        'pakistan-solar-radiation-kaggle': 'muhammadusmanfarooq/pakistan-solar-radiation-dataset'
               }

    for file_name, dataset_id in datasets.items():
        if not dataset_id:
            continue
            
        print(f"Downloading {dataset_id}...")
        try:
            kagglehub.dataset_download(
                dataset_id, 
                output_dir=os.path.join(Config.RAW_DATA_DIR, file_name),
                force_download=True
            )
            print(f"Successfully downloaded {dataset_id} to {Config.RAW_DATA_DIR}")
            
            
        except Exception as e:
            print(f"Error downloading {dataset_id}: {e}")

    return None