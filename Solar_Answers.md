# Assignment 1: Reflective Analysis & Answers

## Part 1: Extract and Load (EL) Questions

### (a) Data Heterogeneity
**Question:** Explain how your chosen data sources represent different data types (structured, semi-structured, unstructured). Provide concrete examples.

**Answer:**
My pipeline integrates three distinct data types to capture a holistic view of Pakistan's solar transition:
1.  **Semi-Structured (JSON):** The YouTube Data API returns data in a deeply nested JSON format. For example, comment threads contain top-level snippets and recursive arrays of replies (e.g., `item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]`). This requires dynamic parsing to extract author names, timestamps, and the text itself.
2.  **Structured (CSV):** The Yahoo Finance data (via `yfinance`) and the Kaggle Pakistan Solar Radiation dataset are highly structured tabular formats. They possess a fixed schema with defined data types (e.g., Float64 for closing prices and solar irradiance) and can be mapped directly to relational data structures.
3.  **Unstructured (PDF & Text):** The primary unstructured data comes from two places: the PBS "Trends in Electricity Generation" PDF report (which requires manual visual extraction into CSV templates) and the raw, natural-language text of the YouTube comments (which contains slang, varied lengths, and requires filtering for keywords).

### (b) Extraction Challenges
**Question:** Discuss specific technical or practical challenges encountered while accessing different data sources.

**Answer:**
* **API Pagination & Quotas:** Extracting YouTube comments required handling recursive pagination. I had to manage separate `pageToken` requests for both the high-level comment threads and the nested replies to ensure no data was dropped, all while staying within Google's API quota limits. Furthermore, to adhere to Google's API quota constraints and avoid HTTP 429 Too Many Requests errors, I had to architect the extraction script to respect rate limits, ensuring stable data ingestion without connection drops.
* **Unstructured PDF Tabular Extraction:** The macroeconomic PBS data was locked in highly formatted PDF reports. While I initially attempted programmatic extraction, the complex multi-span headers and erratic spatial layouts rendered traditional, non-ML deterministic parsing libraries highly brittle and error-prone. To bridge the gap between raw unstructured PDFs and structured transformations, I engineered a 'human-in-the-loop' solution: programmatically generating empty, strongly-typed CSV templates in the staging directory to enforce downstream schema consistency while guiding manual data entry.

### (c) Storage Justification
**Question:** Explain why storing data in multiple formats (CSV, JSON) is valuable. When would you choose one over another?

**Answer:**
* **JSON (Raw API Data):** I chose JSON to store the raw YouTube Data API responses because JSON natively supports hierarchical, deeply nested, and semi-structured data. In an "Extract and Load" paradigm, forcing nested comment replies into a flat CSV immediately during extraction risks data loss and requires brittle parsing logic. Furthermore, JSON enables Schema-on-Read and provides resilience against upstream schema drift; if YouTube adds a new metadata field to their API tomorrow, my extraction script will safely capture it in the JSON dump without breaking a rigid table structure.

* **CSV (Processed/Financial Data):** I chose CSVs for the Kaggle meteorological data and Yahoo Finance stock data because these sources are inherently tabular and two-dimensional. CSVs represent a Schema-on-Write approach that enforces a flat structure. They are highly valuable in the intermediate staging phase because they are universally supported, human-readable for quick visual debugging, and lightweight enough for Pandas to ingest seamlessly during the Transformation phase.

* **Future Optimization (Parquet for Analytics):** I choose JSON for flexible, nested ingestion, and CSV for flat, human-readable staging. However, in a fully mature, production-scale pipeline, I would transition the final data/cleaned/ outputs into Parquet rather than CSV. Parquet is a columnar format that strictly enforces data types (preventing the date-parsing issues common with CSVs) and offers high compression, making it the optimal choice for the final analytical layer feeding into machine learning models or BI dashboards.

---

## Part 2: Transform, Clean, and Analyze Questions

### (a) Cleaning Rationale
**Question:** Justify your data cleaning decisions. Why were specific approaches chosen for handling missing data or outliers?

**Answer:**
* **Stock Data (Forward Fill):** I used `ffill` (forward fill) to handle missing stock data. In financial time-series, missing values typically indicate weekends or non-trading holidays. Carrying the previous day's closing price forward is the standard convention, as the asset's valuation remains static until the next trading session. This was crucial for temporally aligning the 5-day trading week with the 7-day continuous meteorological and social datasets. Additionally, I normalized the data to a "Base 100" scale, allowing for an accurate visual comparison of relative percentage growth between stocks of vastly different price magnitudes.
* **Solar Radiation Data (Anomaly Filtering & Mathematical Aggregation):** The raw weather data consisted of nearly 480,000 rows of 10-minute sensor pings. I first filtered out physical impossibilities and outliers (e.g., ghi_pyr < 0 to remove negative irradiance anomalies caused by sensor calibration errors). To handle missing ping data and reduce noise, I aggregated the telemetry by City, Month, and Hour. This smoothed the data into robust hourly averages, enabling the calculation of the mathematical integral of daily solar insolation (kWh/m²/day) while successfully reducing a massive, noisy dataset into a lightweight, 1,152-row feature store suitable for modeling.
* **YouTube Discourse (Noise Reduction):** Raw API comment streams are heavily polluted. I explicitly dropped duplicate Comment IDs to handle pagination overlaps inherent to recursive API extraction. Furthermore, I applied a length filter (Comment Length > 5) which successfully stripped out over 150 instances of low-value spam or emojis (e.g., "nice", "ok") that would otherwise skew downstream text analytics.

### (b) Visualization Insights
**Question:** What key insights or patterns emerge from your visualizations? How do they relate to your chosen thematic domain?

**Answer:**
* **The "Utility Death Spiral" (Macro Trends):** The dual-panel PBS macro visualization perfectly illustrates the core theme of Pakistan's grid instability. It reveals a stark divergence: while the national grid has built massive generation overcapacity, actual utilization efficiency has plummeted (dropping from a peak of ~58% down to ~38%). This severe inefficiency forces the government to issue escalating subsidies—peaking at over 464 Billion PKR—at the exact same time the public's adoption of decentralized solar generation is growing exponentially.
* **Geographic Viability Driving Public Action:** The "Geographic Solar Viability" visualization proves the physical catalyst behind this transition. The seasonal insolation bar charts demonstrate that all four major cities reliably hit or exceed the 4.0 kWh/m²/day threshold required for viable off-grid solar. This meteorological reality is mirrored perfectly by the "YouTube Discourse Timeline," which shows aggressive spikes in public engagement regarding "Solar" during the lead-up to peak summer months, aligning precisely with the periods when diurnal irradiance is highest and grid load-shedding is at its worst.

### (c) Visualization Critique
**Question:** What limitations exist in your current visualizations? How could they be improved for different audiences?

**Answer:**
* **Limitations:** 
    1. **Volume vs. Context (YouTube):** The YouTube area chart effectively captures the volume of public discourse, but it is purely quantitative. It treats a comment praising solar savings identically to a comment complaining about expensive inverter batteries.

    2. **Library Limitations (Static vs. Interactive Analysis):** The current visualizations, built with `matplotlib` and `seaborn`, are entirely static. As a result, the datasets (PBS macro data, financial markets, and meteorological outputs) remain visually insular and disconnected. Static plots prevent cross-filtering; a viewer cannot easily correlate events across charts to see how a spike in one domain impacts another.
* **Improvements:**
    * **For Technical Audiences:** I would integrate an NLP pipeline (e.g., using VADER or a fine-tuned transformer model) to apply Sentiment Polarity scores to the YouTube data. The visualization would then plot "Net Positive vs. Net Negative Sentiment" over time, providing a much richer feature for predictive modeling.
    * **For Business Stakeholders:** I would upgrade the static matplotlib charts into an interactive, cross-filtered dashboard (e.g., using Plotly or Streamlit). This would allow a grid planner to click on a specific high-insolation summer month and instantly see the corresponding dip in traditional IPP stock performance and the exact geographic breakdown of solar output.