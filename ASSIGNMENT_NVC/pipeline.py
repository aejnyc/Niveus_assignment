import os
import re
import json
import sqlite3
import hashlib
from difflib import get_close_matches
from datetime import datetime
from config import (
    TEST_NAME_LOOKUP, 
    CANONICAL_TARGET_TESTS, 
    CANONICAL_UNITS, 
    TEST_BOUNDARIES
)

DB_PATH = "veritas.db"

class VeritasLocalPipeline:
    def __init__(self):
        self.seen_hashes = set()
        self.init_db()

    def init_db(self):
        """Creates SQLite database table with fixed schema structure."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims_analytics (
                db_id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id TEXT,
                patient_id TEXT,
                clinic_id TEXT,
                ingestion_timestamp TEXT,
                raw_payload TEXT,
                
                -- FR-2.2: Fixed 5 columns for Hemoglobin
                Hemoglobin_Name TEXT,
                Hemoglobin_Result REAL,
                Hemoglobin_Range TEXT,
                Hemoglobin_Unit TEXT,
                Hemoglobin_Analytics TEXT,
                
                -- FR-2.2: Fixed 5 columns for WBC
                WBC_Name TEXT,
                WBC_Result REAL,
                WBC_Range TEXT,
                WBC_Unit TEXT,
                WBC_Analytics TEXT,
                
                -- FR-2.2: Fixed 5 columns for Platelets
                Platelets_Name TEXT,
                Platelets_Result REAL,
                Platelets_Range TEXT,
                Platelets_Unit TEXT,
                Platelets_Analytics TEXT
            )
        """)
        conn.commit()
        conn.close()

    def normalize_test_name(self, raw_name):
        """FR-2.1: Test Name Normalisation via direct lookup and fuzzy matching fallback."""
        if not raw_name:
            return None
        
        cleaned = str(raw_name).strip().lower()
        if cleaned in TEST_NAME_LOOKUP:
            return TEST_NAME_LOOKUP[cleaned]
        
        matches = get_close_matches(cleaned, TEST_NAME_LOOKUP.keys(), n=1, cutoff=0.7)
        if matches:
            return TEST_NAME_LOOKUP[matches[0]]
        
        return raw_name.title()

    def extract_numeric(self, raw_value):
        """FR-2.3: Converts mixed text+numeric values to numeric floats."""
        if raw_value is None:
            return None
        
        if isinstance(raw_value, (int, float)):
            return float(raw_value)
        
        val_str = str(raw_value).strip()
        if not val_str or val_str.lower() in ["null", "none", "n/a", ""]:
            return None

        match = re.search(r"[-+]?\d*\.\d+|\d+", val_str)
        if match:
            try:
                return float(match.group())
            except ValueError:
                return None
        
        return None

    def classify_analytics(self, test_name, numeric_value):
        """Classifies numeric results into target range/outlier flags."""
        if numeric_value is None:
            return "Invalid"

        bounds = TEST_BOUNDARIES.get(test_name)
        if not bounds:
            return "Within Range"

        if numeric_value < bounds["min_outlier"] or numeric_value > bounds["max_outlier"]:
            return "Outlier"
        elif numeric_value < bounds["min_range"]:
            return "Below Range"
        elif numeric_value > bounds["max_range"]:
            return "Above Range"
        else:
            return "Within Range"

    def process_record(self, raw_json):
        """Processes a single raw claim JSON into the fixed 5-column schema per test."""
        record_id = str(raw_json.get("record_id", raw_json.get("id", "")))
        patient_id = str(raw_json.get("patient_id", raw_json.get("uhid", "")))
        
        raw_hash = hashlib.md5(f"{patient_id}_{record_id}_{json.dumps(raw_json)}".encode('utf-8')).hexdigest()
        if raw_hash in self.seen_hashes:
            return None
        self.seen_hashes.add(raw_hash)

        processed_row = {
            "record_id": record_id,
            "patient_id": patient_id,
            "clinic_id": str(raw_json.get("clinic_id", raw_json.get("hospital_name", "Unknown"))),
            "ingestion_timestamp": datetime.utcnow().isoformat(),
            "raw_payload": json.dumps(raw_json)
        }

        lab_results = raw_json.get("lab_results") or raw_json.get("tests") or raw_json.get("report_details") or []
        extracted_by_canonical = {}

        for test_item in lab_results:
            raw_name = test_item.get("name") or test_item.get("test_name") or test_item.get("report_details_test_name")
            if not raw_name:
                continue

            canonical_name = self.normalize_test_name(raw_name)
            raw_val = test_item.get("value") or test_item.get("result") or test_item.get("report_details_result")
            numeric_val = self.extract_numeric(raw_val)

            unit = test_item.get("unit") or test_item.get("report_details_unit") or CANONICAL_UNITS.get(canonical_name, "")
            
            # Unit correction: Update mil/cu.cm strictly to mil/cu.mm
            if unit and "mil/cu.cm" in str(unit).lower():
                unit = re.sub(r"mil/cu\.cm", "mil/cu.mm", str(unit), flags=re.IGNORECASE)

            bounds = TEST_BOUNDARIES.get(canonical_name, {})
            formatted_range = f"{bounds.get('min_range', '')}-{bounds.get('max_range', '')}" if bounds else ""

            extracted_by_canonical[canonical_name] = {
                "result": numeric_val,
                "range": formatted_range,
                "unit": unit,
                "analytics": self.classify_analytics(canonical_name, numeric_val)
            }

        # FR-2.2 Fixed 5-Column Schema Generation
        for target_test in CANONICAL_TARGET_TESTS:
            test_data = extracted_by_canonical.get(target_test)
            
            if test_data:
                processed_row[f"{target_test}_Name"] = target_test
                processed_row[f"{target_test}_Result"] = test_data["result"]
                processed_row[f"{target_test}_Range"] = test_data["range"]
                processed_row[f"{target_test}_Unit"] = test_data["unit"]
                processed_row[f"{target_test}_Analytics"] = test_data["analytics"]
            else:
                processed_row[f"{target_test}_Name"] = None
                processed_row[f"{target_test}_Result"] = None
                processed_row[f"{target_test}_Range"] = None
                processed_row[f"{target_test}_Unit"] = None
                processed_row[f"{target_test}_Analytics"] = None

        return processed_row

    def run_local_ingestion(self, folder_path="raw_data"):
        if not os.path.exists(folder_path):
            print(f"Directory '{folder_path}' not found.")
            return

        records_to_insert = []
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".json"):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    records = content if isinstance(content, list) else [content]
                    for rec in records:
                        processed = self.process_record(rec)
                        if processed:
                            records_to_insert.append(processed)

        if records_to_insert:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            insert_sql = """
            INSERT INTO claims_analytics (
                record_id, patient_id, clinic_id, ingestion_timestamp, raw_payload,
                Hemoglobin_Name, Hemoglobin_Result, Hemoglobin_Range, Hemoglobin_Unit, Hemoglobin_Analytics,
                WBC_Name, WBC_Result, WBC_Range, WBC_Unit, WBC_Analytics,
                Platelets_Name, Platelets_Result, Platelets_Range, Platelets_Unit, Platelets_Analytics
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            rows = [list(r.values()) for r in records_to_insert]
            cursor.executemany(insert_sql, rows)
            conn.commit()
            conn.close()
            print(f"Successfully loaded {len(records_to_insert)} records into 'veritas.db'.")

if __name__ == "__main__":
    pipeline = VeritasLocalPipeline()
    pipeline.run_local_ingestion("raw_data")