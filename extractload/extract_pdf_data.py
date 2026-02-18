import requests
import os
import csv
from config.settings import Config

def download_pdf_if_missing(file_path, url):
    if os.path.exists(file_path):
        return True
    
    print(f"File not found locally. Attempting to download from: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise error for bad status codes
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print("Download successful.")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def get_pbs_file_and_setup_for_manual_extraction():
    print("Downloading PBS document...")
    Config.ensure_directories()

    file_name = 'Trends_in_Electricity_Generation_2006-07_to_2020-21.pdf'
    pdf_path = os.path.join(Config.RAW_DATA_DIR, file_name)
    os.makedirs(os.path.join(Config.PROCESSED_DATA_DIR, 'PBS'), exist_ok=True)
    output_dir = os.path.join(Config.PROCESSED_DATA_DIR, 'PBS')
    
    # print(f"Opening PDF: {pdf_path}")
    # print(f"Output directory: {Config.RAW_DATA_DIR}")

    if not download_pdf_if_missing(pdf_path, Config.PDF_URL):
        print("CRITICAL FAILURE: Could not obtain the PDF file. Exiting...")
        return
    
    print("Initializing empty CSV templates for manual extraction...")

    csv_templates = {
        "table_1_share_installed_capacity_by_type_and_region.csv": [
            "Province/Source", "Nuclear", "Hydel", "Thermal", "Bagasse", "Solar", "Wind", "Total", "%Share"
        ],
        "table_2_electricity_generation_by_type_and_region.csv": [
            "Province/Source", "Nuclear", "Hydel", "Thermal", "Bagasse", "Solar", "Wind", "Total"
        ],
        "table_4_1_installed_capacity_2006-2021.csv": [
            "Year (On 30th June)", "Private Sector", "Private % Change", "Public Sector", 
            "Public % Change", "Total Installed Capacity", "Total % Change"
        ],
        "table_4_2_installed_capacity_by_source_2006-2021.csv": [
            "Year", "Nuclear", "Nuclear % share", "Hydel", "Hydel % share", "Thermal", 
            "Thermal % share", "Bagasse", "Bagasse % share", "Solar", "Solar % share", 
            "Wind", "Wind % share", "Total"
        ],
        "table_4_3_installed_capacity_by_province_and_source_2006-2021.csv": [
            "Plant State", "Year", "Punjab", "Sindh", "KP", "Balochistan", "AJK", "Total"
        ],
        "table_4_4_installed_capacity_renewable_nuclear_thermal.csv": [
            "Year", "Nuclear", "Thermal", "Renewable", "Total", "% Change"
        ],
        "table_4_5_electricity_generation_2006-2021.csv": [
            "Year", "Private", " % Change", "Public", " % Change", "Total", " % Change"
        ],
        "table_4_6_electricity_generation_by_source.csv": [
            "Year", "Nuclear", "Hydel", "Thermal", "Bagasse", "Solar", "Wind", "Grand Total"
        ],
        "table_4_7_electricity_generation_by_province_and_source.csv": [
            "Source\State", "Year", "Punjab", "Sindh", "KP", "Balochistan", "AJK", "Total"
        ],
        "table_4_8_gva_and_subsidy.csv": [
            "Year", "GVA (at current price)", "Subsidy", "GVA Growth rate"
        ],
        "table_4_9_capacity_utilization_rate.csv": [
            "Name of Establishment", "Province/State", "Installed Capacity", 
            "Generation (2019-20)", "Capacity Utilization Rate (19-20)", 
            "Generation (2020-21)", "Capacity Utilization Rate (20-21)", "Change"
        ],
        "table_5_1_installed_capacity_1947-2021.csv": [
            "Year", "Installed Capacity (MW)", "% Change"
        ],
        "table_5_2_electricity_generation_1947-2021.csv": [
            "Year", "Electricity Generation (GWh)", "% Change"
        ],
        "table_5_3_electricity_generation_2006-2021_by_type_of_plant.csv": [
            "Plant Type", "Year", "AJK", "Balochistan", "KPK", "Punjab", "Sindh", "Total"
        ],
        "table_5_4_electricity_generation_2020-21_by_establishment.csv": [
            "Name of Establishment", "AJK", "Balochistan", "KPK", "Punjab", "Sindh", "Total"
        ]
    }

    for filename, headers in csv_templates.items():
        file_path = os.path.join(output_dir, filename)
        # Create file with headers only
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            print(f"Created template: {filename}")
        except Exception as e:
            print(f"Failed to create {filename}: {e}")

    print("Empty CSV templates created successfully.")
    print("Please manually extract tables and store in the folder ./data/processed/PBS.")

if __name__ == "__main__":
    pass