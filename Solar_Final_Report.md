# Project Report: Solar Energy Adoption and National Grid Instability

**Student Name:** Syed Muhammad Abu Talib | **Student ID:** 27100315 | **Course:** AI 620: Data Engineering for AI Systems

## Thematic Focus
This project explores the **Climate Technology** domain, investigating the tension between decentralized solar energy adoption and legacy grid stability in Pakistan. To analyze this transition, I engineered a modern ELT pipeline that integrates meteorological datasets (Kaggle), financial market trends (Yahoo Finance), national macroeconomic energy statistics (PBS), and public sentiment (YouTube API).

### AI System Enablement
Beyond analytical insights, this ELT pipeline directly supports future AI development. By harmonizing heterogeneous data (meteorological, financial, and sentiment) into a unified temporal schema, the cleaned output serves as a robust feature store for predictive modeling. For example, the integrated solar irradiance features and public sentiment scores could be used to train supervised machine learning models to forecast localized grid load-shedding probability or predict future IPP stock volatility.

## Key Findings
1. **The "Utility Death Spiral":** Aggregated macroeconomic PBS data reveals a stark divergence. While the national grid has built massive generation overcapacity, its actual utilization efficiency has plummeted from ~58% to ~38%. This severe inefficiency has forced the government to issue escalating capacity subsidies—peaking at over 464 Billion PKR. This is precisely as public adoption of decentralized solar generation grows exponentially.
2. **Geographic Viability & Public Discourse:** Mathematical modeling of raw sensor telemetry proves that all four major Pakistani cities reliably exceed the 4.0 kWh/m²/day threshold required for viable off-grid solar. This meteorological reality correlates directly with public sentiment; YouTube discourse regarding "Solar" spikes aggressively during the lead-up to peak summer months, aligning perfectly with periods of maximum diurnal irradiance and severe grid load-shedding.

## Challenges Encountered
* **Temporal Alignment & Data Heterogeneity:** Harmonizing timestamps across four fundamentally distinct formats (ISO 8601 strings, UTC datetimes, annual Fiscal Year formats like "2006-07", and local sensor times) proved to be a major technical hurdle. Resolving this was critical for enabling accurate, cross-dataset relational merging in the final analytical phase.
* **Unstructured PDF Tabular Extraction:** The macroeconomic PBS data was locked in highly formatted PDF reports. While I initially attempted programmatic extraction, the complex multi-span headers and erratic spatial layouts rendered traditional, non-ML deterministic parsing libraries highly brittle and error-prone. To bridge the gap between raw unstructured PDFs and structured transformations, I engineered a 'human-in-the-loop' solution: programmatically generating empty, strongly-typed CSV templates in the staging directory to enforce downstream schema consistency while guiding manual data entry.

### 🔗 Supporting Documentation
* **[Solar_Answers.md](Solar_Answers.md)**: Contains an in-depth reflective analysis of the pipeline, including data heterogeneity, storage justifications (JSON vs. CSV), and a critical evaluation of the generated visualizations.
* **[README.md](README.md)**: Contains the pipeline setup instructions, execution steps, and the architectural directory structure.