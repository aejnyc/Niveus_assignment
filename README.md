# Niveus_assignment

The Veritas Claims Analytics Pipeline ingests raw medical clinic lab report JSON files, standardizes heterogeneous test names and unit measurements into a unified target schema, classifies lab values into physiological risk categories (In-Range, Above/Below Range, Outlier, Invalid), and exposes daily operational ingestion metrics via a lightweight web dashboard. 

Installation Guide:
1. Ensure you have Python 3.8+ installed on your system.
2. Install Flask (SQLite and regex are built into Python's standard library):
   >pip install flask
3. Drop your input JSON files inside the raw_data folder.
4. Execute the pipeline script to process raw JSON files, apply data harmonization, and store records in veritas:
   >python pipeline.py
5. Run the Flask server to view operational metrics:
  >python app.py
