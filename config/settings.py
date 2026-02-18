import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
    PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')
    CLEANED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'cleaned')

    PDF_URL = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/Trends_in_Electricity_Generation_2006-07_to_2020-21.pdf"

    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    if not YOUTUBE_API_KEY:
        raise ValueError("Set YOUTUBE_API_KEY in .env")

    KAGGLE_API_TOKEN = os.getenv('KAGGLE_API_TOKEN')
    if not KAGGLE_API_TOKEN:
        raise ValueError("Set KAGGLE_API_TOKEN in .env")

    CHANNELS = ["https://www.youtube.com/@dawnnewsenglish", "https://www.youtube.com/@Samaatv", "https://www.youtube.com/@BOLNewsofficial", 
                "https://www.youtube.com/ArynewsTvofficial", "https://www.youtube.com/@DunyanewsOfficial", 
                "https://www.youtube.com/@SolarInformationGR", "https://www.youtube.com/@RaftarNow", "https://www.youtube.com/@UrduPointNetwork",
                "https://www.youtube.com/@geonews", "https://www.youtube.com/@HUMNewsPakistan"]
    
    KEYWORDS = ["Solar"]

    TICKERS = ['HUBC.KA', 'PAEL.KA', 'OGDC.KA', 'PPL.KA', 'MARI.KA', 'ENGRO.KA', 'PSO.KA', 'SNGP.KA', 'SSGC.KA', 'ATRL.KA']

    @staticmethod
    def ensure_directories():
        """Creates data directories if they don't exist."""
        os.makedirs(Config.RAW_DATA_DIR, exist_ok=True)
        os.makedirs(Config.PROCESSED_DATA_DIR, exist_ok=True)
        os.makedirs(Config.CLEANED_DATA_DIR, exist_ok=True)