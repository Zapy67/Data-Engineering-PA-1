from config.settings import Config
from extractload.extract_stocks import extract_stock_data
from extractload.extract_kaggle import extract_solar_data_kaggle
from extractload.extract_pdf_data import get_pbs_file_and_setup_for_manual_extraction
from extractload.extract_google import extract_youtube_comments

def main():
    print("--- SOLAR ENERGY ADOPTION EL PIPELINE ---")
    
    # 1. Initialize
    Config.ensure_directories()
    
    # 2. Extract (Part 1)
    print("--- EXTRACTION ---")
    get_pbs_file_and_setup_for_manual_extraction()
    extract_stock_data()
    extract_solar_data_kaggle()
    extract_youtube_comments()
    
    print("--- PIPELINE COMPLETE ---")
    print(f"Check {Config.BASE_DIR}/data/raw/ for raw data.")
    print(f"Check {Config.BASE_DIR}/data/processed/ for processed data.")

if __name__ == "__main__":
    main()