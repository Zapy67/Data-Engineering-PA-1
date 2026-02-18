# Summary of current work

## Solar Energy & Grid Instability ELT Pipeline

### Thematic Domain
**Climate Technology:** Focusing on the interaction between decentralized solar generation (GHI/Temp data) and the financial performance of legacy power providers (Hub Power, Pak Elektron).

This project implements an ELT pipeline to analyze the relationship between solar energy adoption (meteorological data) and national grid instability (financial/stock data) in Pakistan.

### [Data Sources](/extractload/README.md)

### Setup Instructions for EL Pipeline
1.  Install dependencies: `pip install -r requirements.txt`
2.  Create a `.env` file with your Kaggle and Google Cloud API key:
    ```
    KAGGLE_API_TOKEN=your_key_here
    YOUTUBE_API_KEY=your_key_here
    ```
3.  Run the pipeline: `python run_solar_pipeline.py`

### Data Storage Strategy
* **Raw Data:** Stored in `data/raw/`.
* **Processed Data:** Stored in `data/processed`.
* **Transformed Data:** Stored in `data/cleaned`.
